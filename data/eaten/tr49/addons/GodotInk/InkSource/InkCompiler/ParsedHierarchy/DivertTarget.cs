using Ink.Runtime;

namespace Ink.Parsed;

public class DivertTarget : Expression
{
	public Divert divert;

	private DivertTargetValue _runtimeDivertTargetValue;

	private Ink.Runtime.Divert _runtimeDivert;

	public DivertTarget(Divert divert)
	{
		this.divert = AddContent(divert);
	}

	public override void GenerateIntoContainer(Container container)
	{
		divert.GenerateRuntimeObject();
		_runtimeDivert = divert.runtimeDivert;
		_runtimeDivertTargetValue = new DivertTargetValue();
		container.AddContent(_runtimeDivertTargetValue);
	}

	public override void ResolveReferences(Story context)
	{
		base.ResolveReferences(context);
		if (divert.isDone || divert.isEnd)
		{
			Error("Can't Can't use -> DONE or -> END as variable divert targets", this);
			return;
		}
		Object obj = this;
		while ((bool)obj && obj is Expression)
		{
			bool flag = false;
			bool flag2 = false;
			Object obj2 = obj.parent;
			if (obj2 is BinaryExpression)
			{
				BinaryExpression binaryExpression = obj2 as BinaryExpression;
				if (binaryExpression.opName != "==" && binaryExpression.opName != "!=")
				{
					flag = true;
				}
				else
				{
					if (!(binaryExpression.leftExpression is DivertTarget) && !(binaryExpression.leftExpression is VariableReference))
					{
						flag = true;
					}
					if (!(binaryExpression.rightExpression is DivertTarget) && !(binaryExpression.rightExpression is VariableReference))
					{
						flag = true;
					}
				}
				flag2 = true;
			}
			else if (obj2 is FunctionCall)
			{
				FunctionCall functionCall = obj2 as FunctionCall;
				if (!functionCall.isTurnsSince && !functionCall.isReadCount)
				{
					flag = true;
				}
				flag2 = true;
			}
			else if (obj2 is Expression)
			{
				flag = true;
				flag2 = true;
			}
			else if (obj2 is MultipleConditionExpression)
			{
				flag = true;
				flag2 = true;
			}
			else if (obj2 is Choice && ((Choice)obj2).condition == obj)
			{
				flag = true;
				flag2 = true;
			}
			else if (obj2 is Conditional || obj2 is ConditionalSingleBranch)
			{
				flag = true;
				flag2 = true;
			}
			if (flag)
			{
				Error("Can't use a divert target like that. Did you intend to call '" + divert.target?.ToString() + "' as a function: likeThis(), or check the read count: likeThis, with no arrows?", this);
			}
			if (flag2)
			{
				break;
			}
			obj = obj2;
		}
		if (_runtimeDivert.hasVariableTarget)
		{
			Error("Since '" + divert.target.dotSeparatedComponents + "' is a variable, it shouldn't be preceded by '->' here.");
		}
		_runtimeDivertTargetValue.targetPath = _runtimeDivert.targetPath;
		Object targetContent = divert.targetContent;
		if (!(targetContent != null))
		{
			return;
		}
		Container container = targetContent.containerForCounting;
		if (container != null)
		{
			FunctionCall functionCall2 = base.parent as FunctionCall;
			if ((bool)functionCall2 && functionCall2.isTurnsSince)
			{
				container.turnIndexShouldBeCounted = true;
			}
			else
			{
				container.visitsShouldBeCounted = true;
				container.turnIndexShouldBeCounted = true;
			}
		}
		FlowBase flowBase = targetContent as FlowBase;
		if (!(flowBase != null) || flowBase.arguments == null)
		{
			return;
		}
		foreach (FlowBase.Argument argument in flowBase.arguments)
		{
			if (argument.isByReference)
			{
				Error("Can't store a divert target to a knot or function that has by-reference arguments ('" + flowBase.identifier?.ToString() + "' has 'ref " + argument.identifier?.ToString() + "').");
			}
		}
	}

	public override bool Equals(object obj)
	{
		DivertTarget divertTarget = obj as DivertTarget;
		if (divertTarget == null)
		{
			return false;
		}
		string dotSeparatedComponents = divert.target.dotSeparatedComponents;
		string dotSeparatedComponents2 = divertTarget.divert.target.dotSeparatedComponents;
		return dotSeparatedComponents.Equals(dotSeparatedComponents2);
	}

	public override int GetHashCode()
	{
		return divert.target.dotSeparatedComponents.GetHashCode();
	}
}
