using System.Collections.Generic;
using Ink.Runtime;

namespace Ink.Parsed;

public abstract class FlowBase : Object, INamedContent
{
	public class Argument
	{
		public Identifier identifier;

		public bool isByReference;

		public bool isDivertTarget;
	}

	public struct VariableResolveResult
	{
		public bool found;

		public bool isGlobal;

		public bool isArgument;

		public bool isTemporary;

		public FlowBase ownerFlow;
	}

	public Dictionary<string, VariableAssignment> variableDeclarations;

	private Weave _rootWeave;

	private Dictionary<string, FlowBase> _subFlowsByName;

	private Ink.Runtime.Divert _startingSubFlowDivert;

	private Ink.Runtime.Object _startingSubFlowRuntime;

	private FlowBase _firstChildFlow;

	public string name => identifier?.name;

	public Identifier identifier { get; set; }

	public List<Argument> arguments { get; protected set; }

	public bool hasParameters
	{
		get
		{
			if (arguments != null)
			{
				return arguments.Count > 0;
			}
			return false;
		}
	}

	public abstract FlowLevel flowLevel { get; }

	public bool isFunction { get; protected set; }

	protected Dictionary<string, FlowBase> subFlowsByName => _subFlowsByName;

	public override string typeName
	{
		get
		{
			if (isFunction)
			{
				return "Function";
			}
			return flowLevel.ToString();
		}
	}

	public FlowBase(Identifier name = null, List<Object> topLevelObjects = null, List<Argument> arguments = null, bool isFunction = false, bool isIncludedStory = false)
	{
		identifier = name;
		if (topLevelObjects == null)
		{
			topLevelObjects = new List<Object>();
		}
		PreProcessTopLevelObjects(topLevelObjects);
		topLevelObjects = SplitWeaveAndSubFlowContent(topLevelObjects, this is Story && !isIncludedStory);
		AddContent(topLevelObjects);
		this.arguments = arguments;
		this.isFunction = isFunction;
		variableDeclarations = new Dictionary<string, VariableAssignment>();
	}

	private List<Object> SplitWeaveAndSubFlowContent(List<Object> contentObjs, bool isRootStory)
	{
		List<Object> list = new List<Object>();
		List<Object> list2 = new List<Object>();
		_subFlowsByName = new Dictionary<string, FlowBase>();
		foreach (Object contentObj in contentObjs)
		{
			FlowBase flowBase = contentObj as FlowBase;
			if ((bool)flowBase)
			{
				if (_firstChildFlow == null)
				{
					_firstChildFlow = flowBase;
				}
				list2.Add(contentObj);
				_subFlowsByName[flowBase.identifier?.name] = flowBase;
			}
			else
			{
				list.Add(contentObj);
			}
		}
		if (isRootStory)
		{
			list.Add(new Gather(null, 1));
			list.Add(new Divert(new Path(Identifier.Done)));
		}
		List<Object> list3 = new List<Object>();
		if (list.Count > 0)
		{
			_rootWeave = new Weave(list, 0);
			list3.Add(_rootWeave);
		}
		if (list2.Count > 0)
		{
			list3.AddRange(list2);
		}
		return list3;
	}

	protected virtual void PreProcessTopLevelObjects(List<Object> topLevelObjects)
	{
	}

	public VariableResolveResult ResolveVariableWithName(string varName, Object fromNode)
	{
		VariableResolveResult result = default(VariableResolveResult);
		FlowBase flowBase = ((fromNode == null) ? this : fromNode.ClosestFlowBase());
		if (flowBase.arguments != null)
		{
			foreach (Argument argument in flowBase.arguments)
			{
				if (argument.identifier.name.Equals(varName))
				{
					result.found = true;
					result.isArgument = true;
					result.ownerFlow = flowBase;
					return result;
				}
			}
		}
		Story story = base.story;
		if (flowBase != story && flowBase.variableDeclarations.ContainsKey(varName))
		{
			result.found = true;
			result.ownerFlow = flowBase;
			result.isTemporary = true;
			return result;
		}
		if (story.variableDeclarations.ContainsKey(varName))
		{
			result.found = true;
			result.ownerFlow = story;
			result.isGlobal = true;
			return result;
		}
		result.found = false;
		return result;
	}

	public void TryAddNewVariableDeclaration(VariableAssignment varDecl)
	{
		string variableName = varDecl.variableName;
		if (variableDeclarations.ContainsKey(variableName))
		{
			string text = "";
			if (variableDeclarations[variableName].debugMetadata != null)
			{
				text = " (" + variableDeclarations[variableName].debugMetadata?.ToString() + ")";
			}
			Error("found declaration variable '" + variableName + "' that was already declared" + text, varDecl);
		}
		else
		{
			variableDeclarations[varDecl.variableName] = varDecl;
		}
	}

	public void ResolveWeavePointNaming()
	{
		if ((bool)_rootWeave)
		{
			_rootWeave.ResolveWeavePointNaming();
		}
		if (_subFlowsByName == null)
		{
			return;
		}
		foreach (KeyValuePair<string, FlowBase> item in _subFlowsByName)
		{
			item.Value.ResolveWeavePointNaming();
		}
	}

	public override Ink.Runtime.Object GenerateRuntimeObject()
	{
		Return obj = null;
		if (isFunction)
		{
			CheckForDisallowedFunctionFlowControl();
		}
		else if (flowLevel == FlowLevel.Knot || flowLevel == FlowLevel.Stitch)
		{
			obj = Find<Return>();
			if (obj != null)
			{
				Error("Return statements can only be used in knots that are declared as functions: == function " + identifier?.ToString() + " ==", obj);
			}
		}
		Container container = new Container();
		container.name = identifier?.name;
		if (base.story.countAllVisits)
		{
			container.visitsShouldBeCounted = true;
		}
		GenerateArgumentVariableAssignments(container);
		int num = 0;
		while (base.content != null && num < base.content.Count)
		{
			Object obj2 = base.content[num];
			if (obj2 is FlowBase)
			{
				FlowBase flowBase = (FlowBase)obj2;
				Ink.Runtime.Object obj3 = flowBase.runtimeObject;
				if (num == 0 && !flowBase.hasParameters && flowLevel == FlowLevel.Knot)
				{
					_startingSubFlowDivert = new Ink.Runtime.Divert();
					container.AddContent(_startingSubFlowDivert);
					_startingSubFlowRuntime = obj3;
				}
				Ink.Runtime.INamedContent namedContent = (Ink.Runtime.INamedContent)obj3;
				Ink.Runtime.INamedContent value = null;
				if (container.namedContent.TryGetValue(namedContent.name, out value))
				{
					string message = $"{GetType().Name} already contains flow named '{namedContent.name}' (at {(value as Ink.Runtime.Object).debugMetadata})";
					Error(message, flowBase);
				}
				container.AddToNamedContentOnly(namedContent);
			}
			else
			{
				container.AddContent(obj2.runtimeObject);
			}
			num++;
		}
		if (flowLevel != FlowLevel.Story && !isFunction && _rootWeave != null && obj == null)
		{
			_rootWeave.ValidateTermination(WarningInTermination);
		}
		return container;
	}

	private void GenerateArgumentVariableAssignments(Container container)
	{
		if (arguments != null && arguments.Count != 0)
		{
			for (int num = arguments.Count - 1; num >= 0; num--)
			{
				Ink.Runtime.VariableAssignment contentObj = new Ink.Runtime.VariableAssignment(arguments[num].identifier?.name, isNewDeclaration: true);
				container.AddContent(contentObj);
			}
		}
	}

	public Object ContentWithNameAtLevel(string name, FlowLevel? level = null, bool deepSearch = false)
	{
		if ((level == flowLevel || !level.HasValue) && name == identifier?.name)
		{
			return this;
		}
		if (level == FlowLevel.WeavePoint || !level.HasValue)
		{
			Object obj = null;
			if ((bool)_rootWeave)
			{
				obj = (Object)_rootWeave.WeavePointNamed(name);
				if ((bool)obj)
				{
					return obj;
				}
			}
			if (level == FlowLevel.WeavePoint)
			{
				if (!deepSearch)
				{
					return null;
				}
				return DeepSearchForAnyLevelContent(name);
			}
		}
		if (level.HasValue && level < flowLevel)
		{
			return null;
		}
		FlowBase value = null;
		if (_subFlowsByName.TryGetValue(name, out value) && (!level.HasValue || level == value.flowLevel))
		{
			return value;
		}
		if (!deepSearch)
		{
			return null;
		}
		return DeepSearchForAnyLevelContent(name);
	}

	private Object DeepSearchForAnyLevelContent(string name)
	{
		Object obj = ContentWithNameAtLevel(name, FlowLevel.WeavePoint);
		if ((bool)obj)
		{
			return obj;
		}
		foreach (KeyValuePair<string, FlowBase> item in _subFlowsByName)
		{
			Object obj2 = item.Value.ContentWithNameAtLevel(name, null, deepSearch: true);
			if ((bool)obj2)
			{
				return obj2;
			}
		}
		return null;
	}

	public override void ResolveReferences(Story context)
	{
		if ((bool)_startingSubFlowDivert)
		{
			_startingSubFlowDivert.targetPath = _startingSubFlowRuntime.path;
		}
		base.ResolveReferences(context);
		if (arguments != null)
		{
			foreach (Argument argument in arguments)
			{
				context.CheckForNamingCollisions(this, argument.identifier, Story.SymbolType.Arg, "argument");
			}
			for (int i = 0; i < arguments.Count; i++)
			{
				for (int j = i + 1; j < arguments.Count; j++)
				{
					if (arguments[i].identifier?.name == arguments[j].identifier?.name)
					{
						Error("Multiple arguments with the same name: '" + arguments[i].identifier?.ToString() + "'");
					}
				}
			}
		}
		if (flowLevel != FlowLevel.Story)
		{
			Story.SymbolType symbolType = ((flowLevel != FlowLevel.Knot) ? Story.SymbolType.SubFlowAndWeave : Story.SymbolType.Knot);
			context.CheckForNamingCollisions(this, identifier, symbolType);
		}
	}

	private void CheckForDisallowedFunctionFlowControl()
	{
		if (!(this is Knot))
		{
			Error("Functions cannot be stitches - i.e. they should be defined as '== function myFunc ==' rather than public to another knot.");
		}
		foreach (KeyValuePair<string, FlowBase> item in _subFlowsByName)
		{
			string key = item.Key;
			FlowBase value = item.Value;
			Error("Functions may not contain stitches, but saw '" + key + "' within the function '" + identifier?.ToString() + "'", value);
		}
		foreach (Divert item2 in _rootWeave.FindAll<Divert>())
		{
			if (!item2.isFunctionCall && !(item2.parent is DivertTarget))
			{
				Error("Functions may not contain diverts, but saw '" + item2.ToString() + "'", item2);
			}
		}
		foreach (Choice item3 in _rootWeave.FindAll<Choice>())
		{
			Error("Functions may not contain choices, but saw '" + item3.ToString() + "'", item3);
		}
	}

	private void WarningInTermination(Object terminatingObject)
	{
		string text = "Apparent loose end exists where the flow runs out. Do you need a '-> DONE' statement, choice or divert?";
		if (terminatingObject.parent == _rootWeave && (bool)_firstChildFlow)
		{
			text = text + " Note that if you intend to enter '" + _firstChildFlow.identifier?.ToString() + "' next, you need to divert to it explicitly.";
		}
		Divert divert = terminatingObject as Divert;
		if ((bool)divert && divert.isTunnel)
		{
			text = text + " When final tunnel to '" + divert.target?.ToString() + " ->' returns it won't have anywhere to go.";
		}
		Warning(text, terminatingObject);
	}

	public override string ToString()
	{
		return typeName + " '" + identifier?.ToString() + "'";
	}
}
