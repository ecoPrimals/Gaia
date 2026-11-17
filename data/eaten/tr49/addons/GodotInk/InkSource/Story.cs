using System;
using System.Collections.Generic;
using System.Text;
using Ink.Runtime;

namespace Ink.Parsed;

public class Story : FlowBase
{
	public enum SymbolType : uint
	{
		Knot,
		List,
		ListItem,
		Var,
		SubFlowAndWeave,
		Arg,
		Temp
	}

	public Dictionary<string, Expression> constants;

	public Dictionary<string, ExternalDeclaration> externals;

	public bool countAllVisits;

	private ErrorHandler _errorHandler;

	private bool _hadError;

	private bool _hadWarning;

	private HashSet<Container> _dontFlattenContainers = new HashSet<Container>();

	private Dictionary<string, ListDefinition> _listDefs;

	public override FlowLevel flowLevel => FlowLevel.Story;

	internal bool hadError => _hadError;

	internal bool hadWarning => _hadWarning;

	public Story(List<Object> toplevelObjects, bool isInclude = false)
		: base(null, toplevelObjects, null, isFunction: false, isInclude)
	{
	}

	protected override void PreProcessTopLevelObjects(List<Object> topLevelContent)
	{
		List<FlowBase> list = new List<FlowBase>();
		int num = 0;
		while (num < topLevelContent.Count)
		{
			Object obj = topLevelContent[num];
			if (obj is IncludedFile)
			{
				IncludedFile includedFile = (IncludedFile)obj;
				topLevelContent.RemoveAt(num);
				if (!includedFile.includedStory)
				{
					continue;
				}
				List<Object> list2 = new List<Object>();
				Story includedStory = includedFile.includedStory;
				if (includedStory.content == null)
				{
					continue;
				}
				foreach (Object item in includedStory.content)
				{
					if (item is FlowBase)
					{
						list.Add((FlowBase)item);
					}
					else
					{
						list2.Add(item);
					}
				}
				list2.Add(new Text("\n"));
				topLevelContent.InsertRange(num, list2);
				num += list2.Count;
			}
			else
			{
				num++;
			}
		}
		topLevelContent.AddRange(list.ToArray());
	}

	public Ink.Runtime.Story ExportRuntime(ErrorHandler errorHandler = null)
	{
		_errorHandler = errorHandler;
		constants = new Dictionary<string, Expression>();
		foreach (ConstantDeclaration item in FindAll<ConstantDeclaration>())
		{
			Expression value = null;
			if (constants.TryGetValue(item.constantName, out value) && !value.Equals(item.expression))
			{
				string message = $"CONST '{item.constantName}' has been redefined with a different value. Multiple definitions of the same CONST are valid so long as they contain the same value. Initial definition was on {value.debugMetadata}.";
				Error(message, item, isWarning: false);
			}
			constants[item.constantName] = item.expression;
		}
		_listDefs = new Dictionary<string, ListDefinition>();
		foreach (ListDefinition item2 in FindAll<ListDefinition>())
		{
			_listDefs[item2.identifier?.name] = item2;
		}
		externals = new Dictionary<string, ExternalDeclaration>();
		ResolveWeavePointNaming();
		Container container = base.runtimeObject as Container;
		Container container2 = new Container();
		container2.AddContent(ControlCommand.EvalStart());
		List<Ink.Runtime.ListDefinition> list = new List<Ink.Runtime.ListDefinition>();
		foreach (KeyValuePair<string, VariableAssignment> variableDeclaration in variableDeclarations)
		{
			string key = variableDeclaration.Key;
			VariableAssignment value2 = variableDeclaration.Value;
			if (value2.isGlobalDeclaration)
			{
				if (value2.listDefinition != null)
				{
					_listDefs[key] = value2.listDefinition;
					container2.AddContent(value2.listDefinition.runtimeObject);
					list.Add(value2.listDefinition.runtimeListDefinition);
				}
				else
				{
					value2.expression.GenerateIntoContainer(container2);
				}
				Ink.Runtime.VariableAssignment variableAssignment = new Ink.Runtime.VariableAssignment(key, isNewDeclaration: true);
				variableAssignment.isGlobal = true;
				container2.AddContent(variableAssignment);
			}
		}
		container2.AddContent(ControlCommand.EvalEnd());
		container2.AddContent(ControlCommand.End());
		if (variableDeclarations.Count > 0)
		{
			container2.name = "global decl";
			container.AddToNamedContentOnly(container2);
		}
		container.AddContent(ControlCommand.Done());
		Ink.Runtime.Story story = (Ink.Runtime.Story)(base.runtimeObject = new Ink.Runtime.Story(container, list));
		if (_hadError)
		{
			return null;
		}
		FlattenContainersIn(container);
		ResolveReferences(this);
		if (_hadError)
		{
			return null;
		}
		story.ResetState();
		return story;
	}

	public ListDefinition ResolveList(string listName)
	{
		if (!_listDefs.TryGetValue(listName, out var value))
		{
			return null;
		}
		return value;
	}

	public ListElementDefinition ResolveListItem(string listName, string itemName, Object source = null)
	{
		ListDefinition value = null;
		if (listName != null)
		{
			if (!_listDefs.TryGetValue(listName, out value))
			{
				return null;
			}
			return value.ItemNamed(itemName);
		}
		ListElementDefinition listElementDefinition = null;
		ListDefinition listDefinition = null;
		foreach (KeyValuePair<string, ListDefinition> listDef in _listDefs)
		{
			ListDefinition value2 = listDef.Value;
			ListElementDefinition listElementDefinition2 = value2.ItemNamed(itemName);
			if ((bool)listElementDefinition2)
			{
				if (listElementDefinition != null)
				{
					Error("Ambiguous item name '" + itemName + "' found in multiple sets, including " + listDefinition.identifier?.ToString() + " and " + value2.identifier, source, isWarning: false);
				}
				else
				{
					listElementDefinition = listElementDefinition2;
					listDefinition = value2;
				}
			}
		}
		return listElementDefinition;
	}

	private void FlattenContainersIn(Container container)
	{
		HashSet<Container> hashSet = new HashSet<Container>();
		foreach (Ink.Runtime.Object item in container.content)
		{
			Container container2 = item as Container;
			if ((bool)container2)
			{
				hashSet.Add(container2);
			}
		}
		if (container.namedContent != null)
		{
			foreach (KeyValuePair<string, Ink.Runtime.INamedContent> item2 in container.namedContent)
			{
				Container container3 = item2.Value as Container;
				if ((bool)container3)
				{
					hashSet.Add(container3);
				}
			}
		}
		foreach (Container item3 in hashSet)
		{
			TryFlattenContainer(item3);
			FlattenContainersIn(item3);
		}
	}

	private void TryFlattenContainer(Container container)
	{
		if (container.namedContent.Count > 0 || container.hasValidName || _dontFlattenContainers.Contains(container))
		{
			return;
		}
		Container container2 = container.parent as Container;
		if (!container2)
		{
			return;
		}
		int num = container2.content.IndexOf(container);
		container2.content.RemoveAt(num);
		DebugMetadata ownDebugMetadata = container.ownDebugMetadata;
		foreach (Ink.Runtime.Object item in container.content)
		{
			item.parent = null;
			if (ownDebugMetadata != null && item.ownDebugMetadata == null)
			{
				item.debugMetadata = ownDebugMetadata;
			}
			container2.InsertContent(item, num);
			num++;
		}
	}

	public override void Error(string message, Object source, bool isWarning)
	{
		ErrorType errorType = (isWarning ? ErrorType.Warning : ErrorType.Error);
		StringBuilder stringBuilder = new StringBuilder();
		if (source is AuthorWarning)
		{
			stringBuilder.Append("TODO: ");
			errorType = ErrorType.Author;
		}
		else if (isWarning)
		{
			stringBuilder.Append("WARNING: ");
		}
		else
		{
			stringBuilder.Append("ERROR: ");
		}
		if ((bool)source && source.debugMetadata != null && source.debugMetadata.startLineNumber >= 1)
		{
			if (source.debugMetadata.fileName != null)
			{
				stringBuilder.AppendFormat("'{0}' ", source.debugMetadata.fileName);
			}
			stringBuilder.AppendFormat("line {0}: ", source.debugMetadata.startLineNumber);
		}
		stringBuilder.Append(message);
		message = stringBuilder.ToString();
		if (_errorHandler != null)
		{
			_hadError = errorType == ErrorType.Error;
			_hadWarning = errorType == ErrorType.Warning;
			_errorHandler(message, errorType);
			return;
		}
		throw new Exception(message);
	}

	public void ResetError()
	{
		_hadError = false;
		_hadWarning = false;
	}

	public bool IsExternal(string namedFuncTarget)
	{
		return externals.ContainsKey(namedFuncTarget);
	}

	public void AddExternal(ExternalDeclaration decl)
	{
		if (externals.ContainsKey(decl.name))
		{
			Error("Duplicate EXTERNAL definition of '" + decl.name + "'", decl, isWarning: false);
		}
		else
		{
			externals[decl.name] = decl;
		}
	}

	public void DontFlattenContainer(Container container)
	{
		_dontFlattenContainers.Add(container);
	}

	private void NameConflictError(Object obj, string name, Object existingObj, string typeNameToPrint)
	{
		obj.Error(typeNameToPrint + " '" + name + "': name has already been used for a " + existingObj.typeName.ToLower() + " on " + existingObj.debugMetadata);
	}

	public static bool IsReservedKeyword(string name)
	{
		switch (name)
		{
		case "else":
		case "true":
		case "LIST":
		case "temp":
		case "CONST":
		case "false":
		case "VAR":
		case "not":
		case "return":
		case "function":
			return true;
		default:
			return false;
		}
	}

	public void CheckForNamingCollisions(Object obj, Identifier identifier, SymbolType symbolType, string typeNameOverride = null)
	{
		string text = typeNameOverride ?? obj.typeName;
		if (IsReservedKeyword(identifier?.name))
		{
			obj.Error("'" + base.name + "' cannot be used for the name of a " + text.ToLower() + " because it's a reserved keyword");
			return;
		}
		if (FunctionCall.IsBuiltIn(identifier?.name))
		{
			obj.Error("'" + base.name + "' cannot be used for the name of a " + text.ToLower() + " because it's a built in function");
			return;
		}
		FlowBase flowBase = ContentWithNameAtLevel(identifier?.name, FlowLevel.Knot) as FlowBase;
		if ((bool)flowBase && (flowBase != obj || symbolType == SymbolType.Arg))
		{
			NameConflictError(obj, identifier?.name, flowBase, text);
		}
		else
		{
			if (symbolType < SymbolType.List)
			{
				return;
			}
			foreach (KeyValuePair<string, ListDefinition> listDef in _listDefs)
			{
				string key = listDef.Key;
				ListDefinition value = listDef.Value;
				if (identifier?.name == key && obj != value && value.variableAssignment != obj)
				{
					NameConflictError(obj, identifier?.name, value, text);
				}
				if (obj is ListElementDefinition)
				{
					continue;
				}
				foreach (ListElementDefinition itemDefinition in value.itemDefinitions)
				{
					if (identifier?.name == itemDefinition.name)
					{
						NameConflictError(obj, identifier?.name, itemDefinition, text);
					}
				}
			}
			if (symbolType <= SymbolType.Var)
			{
				return;
			}
			VariableAssignment value2 = null;
			if (variableDeclarations.TryGetValue(identifier?.name, out value2) && value2 != obj && value2.isGlobalDeclaration && value2.listDefinition == null)
			{
				NameConflictError(obj, identifier?.name, value2, text);
			}
			if (symbolType < SymbolType.SubFlowAndWeave)
			{
				return;
			}
			Object obj2 = new Path(identifier).ResolveFromContext(obj);
			if ((bool)obj2 && obj2 != obj)
			{
				NameConflictError(obj, identifier?.name, obj2, text);
			}
			else
			{
				if (symbolType < SymbolType.Arg || symbolType == SymbolType.Arg)
				{
					return;
				}
				FlowBase flowBase2 = obj as FlowBase;
				if (flowBase2 == null)
				{
					flowBase2 = obj.ClosestFlowBase();
				}
				if (!flowBase2 || !flowBase2.hasParameters)
				{
					return;
				}
				foreach (Argument argument in flowBase2.arguments)
				{
					if (argument.identifier?.name == identifier?.name)
					{
						obj.Error(text + " '" + base.name + "': Name has already been used for a argument to " + flowBase2.identifier?.ToString() + " on " + flowBase2.debugMetadata);
						break;
					}
				}
			}
		}
	}
}
