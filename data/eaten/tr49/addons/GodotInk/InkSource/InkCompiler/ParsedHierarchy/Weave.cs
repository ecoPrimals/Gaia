using System;
using System.Collections.Generic;
using Ink.Runtime;

namespace Ink.Parsed;

public class Weave : Object
{
	public class GatherPointToResolve
	{
		public Ink.Runtime.Divert divert;

		public Ink.Runtime.Object targetRuntimeObj;
	}

	public delegate void BadTerminationHandler(Object terminatingObj);

	public List<IWeavePoint> looseEnds;

	public List<GatherPointToResolve> gatherPointsToResolve;

	private IWeavePoint previousWeavePoint;

	private bool addContentToPreviousWeavePoint;

	private bool hasSeenChoiceInSection;

	private int _unnamedGatherCount;

	private int _choiceCount;

	private Container _rootContainer;

	private Dictionary<string, IWeavePoint> _namedWeavePoints;

	public Container rootContainer
	{
		get
		{
			if (_rootContainer == null)
			{
				GenerateRuntimeObject();
			}
			return _rootContainer;
		}
	}

	private Container currentContainer { get; set; }

	public int baseIndentIndex { get; private set; }

	public Object lastParsedSignificantObject
	{
		get
		{
			if (base.content.Count == 0)
			{
				return null;
			}
			Object obj = null;
			for (int num = base.content.Count - 1; num >= 0; num--)
			{
				obj = base.content[num];
				Text text = obj as Text;
				if ((!text || !(text.text == "\n")) && !IsGlobalDeclaration(obj))
				{
					break;
				}
			}
			Weave weave = obj as Weave;
			if ((bool)weave)
			{
				obj = weave.lastParsedSignificantObject;
			}
			return obj;
		}
	}

	public Weave(List<Object> cont, int indentIndex = -1)
	{
		if (indentIndex == -1)
		{
			baseIndentIndex = DetermineBaseIndentationFromContent(cont);
		}
		else
		{
			baseIndentIndex = indentIndex;
		}
		AddContent(cont);
		ConstructWeaveHierarchyFromIndentation();
	}

	public void ResolveWeavePointNaming()
	{
		List<IWeavePoint> list = FindAll((IWeavePoint w) => !string.IsNullOrEmpty(w.name));
		_namedWeavePoints = new Dictionary<string, IWeavePoint>();
		foreach (IWeavePoint item in list)
		{
			if (_namedWeavePoints.TryGetValue(item.name, out var value))
			{
				string text = ((value is Gather) ? "gather" : "choice");
				Object obj = (Object)value;
				Error("A " + text + " with the same label name '" + item.name + "' already exists in this context on line " + obj.debugMetadata.startLineNumber, (Object)item);
			}
			_namedWeavePoints[item.name] = item;
		}
	}

	private void ConstructWeaveHierarchyFromIndentation()
	{
		for (int i = 0; i < base.content.Count; i++)
		{
			Object obj = base.content[i];
			if (!(obj is IWeavePoint))
			{
				continue;
			}
			int num = ((IWeavePoint)obj).indentationDepth - 1;
			if (num > baseIndentIndex)
			{
				int num2 = i;
				for (; i < base.content.Count && (!(base.content[i] is IWeavePoint weavePoint) || weavePoint.indentationDepth - 1 > baseIndentIndex); i++)
				{
				}
				int count = i - num2;
				List<Object> range = base.content.GetRange(num2, count);
				base.content.RemoveRange(num2, count);
				Weave subContent = new Weave(range, num);
				InsertContent(num2, subContent);
				i = num2;
			}
		}
	}

	public int DetermineBaseIndentationFromContent(List<Object> contentList)
	{
		foreach (Object content in contentList)
		{
			if (content is IWeavePoint)
			{
				return ((IWeavePoint)content).indentationDepth - 1;
			}
		}
		return 0;
	}

	public override Ink.Runtime.Object GenerateRuntimeObject()
	{
		Container container = (currentContainer = new Container());
		_rootContainer = container;
		looseEnds = new List<IWeavePoint>();
		gatherPointsToResolve = new List<GatherPointToResolve>();
		foreach (Object item in base.content)
		{
			if (item is IWeavePoint)
			{
				AddRuntimeForWeavePoint((IWeavePoint)item);
			}
			else if (item is Weave)
			{
				Weave weave = (Weave)item;
				AddRuntimeForNestedWeave(weave);
				gatherPointsToResolve.AddRange(weave.gatherPointsToResolve);
			}
			else
			{
				AddGeneralRuntimeContent(item.runtimeObject);
			}
		}
		PassLooseEndsToAncestors();
		return _rootContainer;
	}

	private void AddRuntimeForGather(Gather gather)
	{
		bool num = !hasSeenChoiceInSection;
		hasSeenChoiceInSection = false;
		Container runtimeContainer = gather.runtimeContainer;
		if (gather.name == null)
		{
			runtimeContainer.name = "g-" + _unnamedGatherCount;
			_unnamedGatherCount++;
		}
		if (num)
		{
			currentContainer.AddContent(runtimeContainer);
		}
		else
		{
			_rootContainer.AddToNamedContentOnly(runtimeContainer);
		}
		foreach (Object looseEnd in looseEnds)
		{
			if (!(looseEnd is Gather) || ((Gather)looseEnd).indentationDepth != gather.indentationDepth)
			{
				Ink.Runtime.Divert divert = null;
				if (looseEnd is Divert)
				{
					divert = (Ink.Runtime.Divert)looseEnd.runtimeObject;
				}
				else
				{
					divert = new Ink.Runtime.Divert();
					(looseEnd as IWeavePoint).runtimeContainer.AddContent(divert);
				}
				gatherPointsToResolve.Add(new GatherPointToResolve
				{
					divert = divert,
					targetRuntimeObj = runtimeContainer
				});
			}
		}
		looseEnds.Clear();
		currentContainer = runtimeContainer;
	}

	private void AddRuntimeForWeavePoint(IWeavePoint weavePoint)
	{
		if (weavePoint is Gather)
		{
			AddRuntimeForGather((Gather)weavePoint);
		}
		else if (weavePoint is Choice)
		{
			if (previousWeavePoint is Gather)
			{
				looseEnds.Remove(previousWeavePoint);
			}
			Choice choice = (Choice)weavePoint;
			currentContainer.AddContent(choice.runtimeObject);
			choice.innerContentContainer.name = "c-" + _choiceCount;
			currentContainer.AddToNamedContentOnly(choice.innerContentContainer);
			_choiceCount++;
			hasSeenChoiceInSection = true;
		}
		addContentToPreviousWeavePoint = false;
		if (WeavePointHasLooseEnd(weavePoint))
		{
			looseEnds.Add(weavePoint);
			if ((bool)(weavePoint as Choice))
			{
				addContentToPreviousWeavePoint = true;
			}
		}
		previousWeavePoint = weavePoint;
	}

	public void AddRuntimeForNestedWeave(Weave nestedResult)
	{
		AddGeneralRuntimeContent(nestedResult.rootContainer);
		if (previousWeavePoint != null)
		{
			looseEnds.Remove(previousWeavePoint);
			addContentToPreviousWeavePoint = false;
		}
	}

	private void AddGeneralRuntimeContent(Ink.Runtime.Object content)
	{
		if (!(content == null))
		{
			if (addContentToPreviousWeavePoint)
			{
				previousWeavePoint.runtimeContainer.AddContent(content);
			}
			else
			{
				currentContainer.AddContent(content);
			}
		}
	}

	private void PassLooseEndsToAncestors()
	{
		if (looseEnds.Count == 0)
		{
			return;
		}
		Weave weave = null;
		Weave weave2 = null;
		bool flag = false;
		Object obj = base.parent;
		while (obj != null)
		{
			Weave weave3 = obj as Weave;
			if (weave3 != null)
			{
				if (!flag && weave == null)
				{
					weave = weave3;
				}
				if (flag && weave2 == null)
				{
					weave2 = weave3;
				}
			}
			if (obj is Sequence || obj is Conditional)
			{
				flag = true;
			}
			obj = obj.parent;
		}
		if (weave == null && weave2 == null)
		{
			return;
		}
		for (int num = looseEnds.Count - 1; num >= 0; num--)
		{
			IWeavePoint weavePoint = looseEnds[num];
			bool flag2 = false;
			if (flag)
			{
				if (weavePoint is Choice && weave != null)
				{
					weave.ReceiveLooseEnd(weavePoint);
					flag2 = true;
				}
				else if (!(weavePoint is Choice))
				{
					Weave weave4 = weave ?? weave2;
					if (weave4 != null)
					{
						weave4.ReceiveLooseEnd(weavePoint);
						flag2 = true;
					}
				}
			}
			else
			{
				weave.ReceiveLooseEnd(weavePoint);
				flag2 = true;
			}
			if (flag2)
			{
				looseEnds.RemoveAt(num);
			}
		}
	}

	private void ReceiveLooseEnd(IWeavePoint childWeaveLooseEnd)
	{
		looseEnds.Add(childWeaveLooseEnd);
	}

	public override void ResolveReferences(Story context)
	{
		base.ResolveReferences(context);
		if (looseEnds != null && looseEnds.Count > 0)
		{
			bool flag = false;
			Object obj = base.parent;
			while (obj != null)
			{
				if (obj is Sequence || obj is Conditional)
				{
					flag = true;
					break;
				}
				obj = obj.parent;
			}
			if (flag)
			{
				ValidateTermination(BadNestedTerminationHandler);
			}
		}
		foreach (GatherPointToResolve item in gatherPointsToResolve)
		{
			item.divert.targetPath = item.targetRuntimeObj.path;
		}
		CheckForWeavePointNamingCollisions();
	}

	public IWeavePoint WeavePointNamed(string name)
	{
		if (_namedWeavePoints == null)
		{
			return null;
		}
		IWeavePoint value = null;
		if (_namedWeavePoints.TryGetValue(name, out value))
		{
			return value;
		}
		return null;
	}

	private bool IsGlobalDeclaration(Object obj)
	{
		VariableAssignment variableAssignment = obj as VariableAssignment;
		if ((bool)variableAssignment && variableAssignment.isGlobalDeclaration && variableAssignment.isDeclaration)
		{
			return true;
		}
		if ((bool)(obj as ConstantDeclaration))
		{
			return true;
		}
		return false;
	}

	private IEnumerable<Object> ContentThatFollowsWeavePoint(IWeavePoint weavePoint)
	{
		Object obj = (Object)weavePoint;
		if (obj.content != null)
		{
			foreach (Object item in obj.content)
			{
				if (!IsGlobalDeclaration(item))
				{
					yield return item;
				}
			}
		}
		Weave parentWeave = obj.parent as Weave;
		if (parentWeave == null)
		{
			throw new Exception("Expected weave point parent to be weave?");
		}
		int num = parentWeave.content.IndexOf(obj);
		for (int i = num + 1; i < parentWeave.content.Count; i++)
		{
			Object obj2 = parentWeave.content[i];
			if (!IsGlobalDeclaration(obj2))
			{
				if (obj2 is IWeavePoint || obj2 is Weave)
				{
					break;
				}
				yield return obj2;
			}
		}
	}

	public void ValidateTermination(BadTerminationHandler badTerminationHandler)
	{
		if (lastParsedSignificantObject is AuthorWarning)
		{
			return;
		}
		if (looseEnds != null && looseEnds.Count > 0)
		{
			foreach (IWeavePoint looseEnd in looseEnds)
			{
				IEnumerable<Object> objFlow = ContentThatFollowsWeavePoint(looseEnd);
				ValidateFlowOfObjectsTerminates(objFlow, (Object)looseEnd, badTerminationHandler);
			}
			return;
		}
		foreach (Object item in base.content)
		{
			if (item is IWeavePoint)
			{
				return;
			}
		}
		ValidateFlowOfObjectsTerminates(base.content, this, badTerminationHandler);
	}

	private void BadNestedTerminationHandler(Object terminatingObj)
	{
		Conditional conditional = null;
		Object obj = terminatingObj.parent;
		while (obj != null)
		{
			if (obj is Sequence || obj is Conditional)
			{
				conditional = obj as Conditional;
				break;
			}
			obj = obj.parent;
		}
		string text = "Choices nested in conditionals or sequences need to explicitly divert afterwards.";
		if (conditional != null && conditional.FindAll<Choice>().Count == 1)
		{
			text = "Choices with conditions should be written: '* {condition} choice'. Otherwise, " + text.ToLower();
		}
		Error(text, terminatingObj);
	}

	private void ValidateFlowOfObjectsTerminates(IEnumerable<Object> objFlow, Object defaultObj, BadTerminationHandler badTerminationHandler)
	{
		bool flag = false;
		Object obj = defaultObj;
		foreach (Object item in objFlow)
		{
			if (item.Find((Divert d) => !d.isThread && !d.isTunnel && !d.isFunctionCall && !(d.parent is DivertTarget)) != null)
			{
				flag = true;
			}
			if (item.Find<TunnelOnwards>() != null)
			{
				flag = true;
				break;
			}
			obj = item;
		}
		if (!flag && !(obj is AuthorWarning))
		{
			badTerminationHandler(obj);
		}
	}

	private bool WeavePointHasLooseEnd(IWeavePoint weavePoint)
	{
		if (weavePoint.content == null)
		{
			return true;
		}
		for (int num = weavePoint.content.Count - 1; num >= 0; num--)
		{
			Divert divert = weavePoint.content[num] as Divert;
			if ((bool)divert && !divert.isThread && !divert.isTunnel && !divert.isFunctionCall)
			{
				return false;
			}
		}
		return true;
	}

	private void CheckForWeavePointNamingCollisions()
	{
		if (_namedWeavePoints == null)
		{
			return;
		}
		List<FlowBase> list = new List<FlowBase>();
		foreach (Object item in base.ancestry)
		{
			FlowBase flowBase = item as FlowBase;
			if ((bool)flowBase)
			{
				list.Add(flowBase);
				continue;
			}
			break;
		}
		foreach (KeyValuePair<string, IWeavePoint> namedWeavePoint in _namedWeavePoints)
		{
			string key = namedWeavePoint.Key;
			Object obj = (Object)namedWeavePoint.Value;
			foreach (FlowBase item2 in list)
			{
				Object obj2 = item2.ContentWithNameAtLevel(key);
				if ((bool)obj2 && obj2 != obj)
				{
					string message = $"{obj.GetType().Name} '{key}' has the same label name as a {obj2.GetType().Name} (on {obj2.debugMetadata})";
					Error(message, obj);
				}
			}
		}
	}
}
