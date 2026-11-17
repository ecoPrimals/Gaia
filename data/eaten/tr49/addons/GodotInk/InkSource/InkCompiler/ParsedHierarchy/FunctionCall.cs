using System.Collections.Generic;
using Ink.Runtime;

namespace Ink.Parsed;

public class FunctionCall : Expression
{
	public bool shouldPopReturnedValue;

	private Divert _proxyDivert;

	private DivertTarget _divertTargetToCount;

	private VariableReference _variableReferenceToCount;

	public string name => _proxyDivert.target.firstComponent;

	public Divert proxyDivert => _proxyDivert;

	public List<Expression> arguments => _proxyDivert.arguments;

	public Ink.Runtime.Divert runtimeDivert => _proxyDivert.runtimeDivert;

	public bool isChoiceCount => name == "CHOICE_COUNT";

	public bool isTurns => name == "TURNS";

	public bool isTurnsSince => name == "TURNS_SINCE";

	public bool isRandom => name == "RANDOM";

	public bool isSeedRandom => name == "SEED_RANDOM";

	public bool isListRange => name == "LIST_RANGE";

	public bool isListRandom => name == "LIST_RANDOM";

	public bool isReadCount => name == "READ_COUNT";

	public FunctionCall(Identifier functionName, List<Expression> arguments)
	{
		_proxyDivert = new Divert(new Path(functionName), arguments);
		_proxyDivert.isFunctionCall = true;
		AddContent(_proxyDivert);
	}

	public override void GenerateIntoContainer(Container container)
	{
		ListDefinition listDefinition = base.story.ResolveList(name);
		bool flag = false;
		if (isChoiceCount)
		{
			if (arguments.Count > 0)
			{
				Error("The CHOICE_COUNT() function shouldn't take any arguments");
			}
			container.AddContent(ControlCommand.ChoiceCount());
		}
		else if (isTurns)
		{
			if (arguments.Count > 0)
			{
				Error("The TURNS() function shouldn't take any arguments");
			}
			container.AddContent(ControlCommand.Turns());
		}
		else if (isTurnsSince || isReadCount)
		{
			DivertTarget divertTarget = arguments[0] as DivertTarget;
			VariableReference variableReference = arguments[0] as VariableReference;
			if (arguments.Count != 1 || (divertTarget == null && variableReference == null))
			{
				Error("The " + name + "() function should take one argument: a divert target to the target knot, stitch, gather or choice you want to check. e.g. TURNS_SINCE(-> myKnot)");
				return;
			}
			if ((bool)divertTarget)
			{
				_divertTargetToCount = divertTarget;
				AddContent(_divertTargetToCount);
				_divertTargetToCount.GenerateIntoContainer(container);
			}
			else
			{
				_variableReferenceToCount = variableReference;
				AddContent(_variableReferenceToCount);
				_variableReferenceToCount.GenerateIntoContainer(container);
			}
			if (isTurnsSince)
			{
				container.AddContent(ControlCommand.TurnsSince());
			}
			else
			{
				container.AddContent(ControlCommand.ReadCount());
			}
		}
		else if (isRandom)
		{
			if (arguments.Count != 2)
			{
				Error("RANDOM should take 2 parameters: a minimum and a maximum integer");
			}
			for (int i = 0; i < arguments.Count; i++)
			{
				if (arguments[i] is Number && !((arguments[i] as Number).value is int))
				{
					string text = ((i == 0) ? "minimum" : "maximum");
					Error("RANDOM's " + text + " parameter should be an integer");
				}
				arguments[i].GenerateIntoContainer(container);
			}
			container.AddContent(ControlCommand.Random());
		}
		else if (isSeedRandom)
		{
			if (arguments.Count != 1)
			{
				Error("SEED_RANDOM should take 1 parameter - an integer seed");
			}
			Number number = arguments[0] as Number;
			if ((bool)number && !(number.value is int))
			{
				Error("SEED_RANDOM's parameter should be an integer seed");
			}
			arguments[0].GenerateIntoContainer(container);
			container.AddContent(ControlCommand.SeedRandom());
		}
		else if (isListRange)
		{
			if (arguments.Count != 3)
			{
				Error("LIST_RANGE should take 3 parameters - a list, a min and a max");
			}
			for (int j = 0; j < arguments.Count; j++)
			{
				arguments[j].GenerateIntoContainer(container);
			}
			container.AddContent(ControlCommand.ListRange());
		}
		else if (isListRandom)
		{
			if (arguments.Count != 1)
			{
				Error("LIST_RANDOM should take 1 parameter - a list");
			}
			arguments[0].GenerateIntoContainer(container);
			container.AddContent(ControlCommand.ListRandom());
		}
		else if (NativeFunctionCall.CallExistsWithName(name))
		{
			NativeFunctionCall nativeFunctionCall = NativeFunctionCall.CallWithName(name);
			if (nativeFunctionCall.numberOfParameters != arguments.Count)
			{
				string text2 = name + " should take " + nativeFunctionCall.numberOfParameters + " parameter";
				if (nativeFunctionCall.numberOfParameters > 1)
				{
					text2 += "s";
				}
				Error(text2);
			}
			for (int k = 0; k < arguments.Count; k++)
			{
				arguments[k].GenerateIntoContainer(container);
			}
			container.AddContent(NativeFunctionCall.CallWithName(name));
		}
		else if (listDefinition != null)
		{
			if (arguments.Count > 1)
			{
				Error("Can currently only construct a list from one integer (or an empty list from a given list definition)");
			}
			if (arguments.Count == 1)
			{
				container.AddContent(new StringValue(name));
				arguments[0].GenerateIntoContainer(container);
				container.AddContent(ControlCommand.ListFromInt());
			}
			else
			{
				InkList inkList = new InkList();
				inkList.SetInitialOriginName(name);
				container.AddContent(new ListValue(inkList));
			}
		}
		else
		{
			container.AddContent(_proxyDivert.runtimeObject);
			flag = true;
		}
		if (!flag)
		{
			base.content.Remove(_proxyDivert);
		}
		if (shouldPopReturnedValue)
		{
			container.AddContent(ControlCommand.PopEvaluatedValue());
		}
	}

	public override void ResolveReferences(Story context)
	{
		base.ResolveReferences(context);
		if (!base.content.Contains(_proxyDivert) && arguments != null)
		{
			foreach (Expression argument in arguments)
			{
				argument.ResolveReferences(context);
			}
		}
		if ((bool)_divertTargetToCount)
		{
			Divert divert = _divertTargetToCount.divert;
			bool flag = divert.runtimeDivert.variableDivertName != null;
			if (flag)
			{
				Error("When getting the TURNS_SINCE() of a variable target, remove the '->' - i.e. it should just be TURNS_SINCE(" + divert.runtimeDivert.variableDivertName + ")");
				return;
			}
			Object targetContent = divert.targetContent;
			if (targetContent == null)
			{
				if (!flag)
				{
					Error("Failed to find target for TURNS_SINCE: '" + divert.target?.ToString() + "'");
				}
			}
			else
			{
				targetContent.containerForCounting.turnIndexShouldBeCounted = true;
			}
		}
		else if ((bool)_variableReferenceToCount && _variableReferenceToCount.runtimeVarRef.pathForCount != null)
		{
			Error("Should be " + name + "(-> " + _variableReferenceToCount.name + "). Usage without the '->' only makes sense for variable targets.");
		}
	}

	public static bool IsBuiltIn(string name)
	{
		if (NativeFunctionCall.CallExistsWithName(name))
		{
			return true;
		}
		switch (name)
		{
		default:
			return name == "READ_COUNT";
		case "CHOICE_COUNT":
		case "TURNS_SINCE":
		case "TURNS":
		case "RANDOM":
		case "SEED_RANDOM":
		case "LIST_VALUE":
		case "LIST_RANDOM":
			return true;
		}
	}

	public override string ToString()
	{
		string arg = string.Join(", ", arguments.ToStringsArray());
		return $"{name}({arg})";
	}
}
