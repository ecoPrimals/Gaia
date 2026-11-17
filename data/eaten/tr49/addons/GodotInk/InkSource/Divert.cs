using System.Collections.Generic;
using System.Linq;
using Ink.Runtime;

namespace Ink.Parsed;

public class Divert : Object
{
	public Path target { get; protected set; }

	public Object targetContent { get; protected set; }

	public List<Expression> arguments { get; protected set; }

	public Ink.Runtime.Divert runtimeDivert { get; protected set; }

	public bool isFunctionCall { get; set; }

	public bool isEmpty { get; set; }

	public bool isTunnel { get; set; }

	public bool isThread { get; set; }

	public bool isEnd
	{
		get
		{
			if (target != null)
			{
				return target.dotSeparatedComponents == "END";
			}
			return false;
		}
	}

	public bool isDone
	{
		get
		{
			if (target != null)
			{
				return target.dotSeparatedComponents == "DONE";
			}
			return false;
		}
	}

	public Divert(Path target, List<Expression> arguments = null)
	{
		this.target = target;
		this.arguments = arguments;
		if (arguments != null)
		{
			AddContent(arguments.Cast<Object>().ToList());
		}
	}

	public Divert(Object targetContent)
	{
		this.targetContent = targetContent;
	}

	public override Ink.Runtime.Object GenerateRuntimeObject()
	{
		if (isEnd)
		{
			return ControlCommand.End();
		}
		if (isDone)
		{
			return ControlCommand.Done();
		}
		runtimeDivert = new Ink.Runtime.Divert();
		ResolveTargetContent();
		CheckArgumentValidity();
		bool flag = arguments != null && arguments.Count > 0;
		if (flag || isFunctionCall || isTunnel || isThread)
		{
			Container container = new Container();
			if (flag)
			{
				if (!isFunctionCall)
				{
					container.AddContent(ControlCommand.EvalStart());
				}
				List<FlowBase.Argument> list = null;
				if ((bool)targetContent)
				{
					list = (targetContent as FlowBase).arguments;
				}
				for (int i = 0; i < arguments.Count; i++)
				{
					Expression expression = arguments[i];
					FlowBase.Argument argument = null;
					if (list != null && i < list.Count)
					{
						argument = list[i];
					}
					if (argument != null && argument.isByReference)
					{
						VariableReference variableReference = expression as VariableReference;
						if (variableReference == null)
						{
							Error("Expected variable name to pass by reference to 'ref " + argument.identifier?.ToString() + "' but saw " + expression.ToString());
							break;
						}
						Path path = new Path(variableReference.pathIdentifiers);
						if (path.ResolveFromContext(this) != null)
						{
							Error("can't pass a read count by reference. '" + path.dotSeparatedComponents + "' is a knot/stitch/label, but '" + target.dotSeparatedComponents + "' requires the name of a VAR to be passed.");
							break;
						}
						VariablePointerValue contentObj = new VariablePointerValue(variableReference.name);
						container.AddContent(contentObj);
					}
					else
					{
						expression.GenerateIntoContainer(container);
					}
				}
				if (!isFunctionCall)
				{
					container.AddContent(ControlCommand.EvalEnd());
				}
			}
			if (isThread)
			{
				container.AddContent(ControlCommand.StartThread());
			}
			else if (isFunctionCall || isTunnel)
			{
				runtimeDivert.pushesToStack = true;
				runtimeDivert.stackPushType = (isFunctionCall ? PushPopType.Function : PushPopType.Tunnel);
			}
			container.AddContent(runtimeDivert);
			return container;
		}
		return runtimeDivert;
	}

	public string PathAsVariableName()
	{
		return target.firstComponent;
	}

	private void ResolveTargetContent()
	{
		if (isEmpty || isEnd || !(targetContent == null))
		{
			return;
		}
		string variableTargetName = PathAsVariableName();
		if (variableTargetName != null)
		{
			FlowBase.VariableResolveResult variableResolveResult = ClosestFlowBase().ResolveVariableWithName(variableTargetName, this);
			if (variableResolveResult.found)
			{
				if (variableResolveResult.isArgument)
				{
					FlowBase.Argument argument = variableResolveResult.ownerFlow.arguments.Where((FlowBase.Argument a) => a.identifier.name == variableTargetName).First();
					if (!argument.isDivertTarget)
					{
						Error("Since '" + argument.identifier?.ToString() + "' is used as a variable divert target (on " + base.debugMetadata?.ToString() + "), it should be marked as: -> " + argument.identifier, variableResolveResult.ownerFlow);
					}
				}
				runtimeDivert.variableDivertName = variableTargetName;
				return;
			}
		}
		targetContent = target.ResolveFromContext(this);
	}

	public override void ResolveReferences(Story context)
	{
		if (isEmpty || isEnd || isDone)
		{
			return;
		}
		if ((bool)targetContent)
		{
			runtimeDivert.targetPath = targetContent.runtimePath;
		}
		base.ResolveReferences(context);
		FlowBase flowBase = targetContent as FlowBase;
		if ((bool)flowBase)
		{
			if (!flowBase.isFunction && isFunctionCall)
			{
				base.Error(flowBase.identifier?.ToString() + " hasn't been marked as a function, but it's being called as one. Do you need to delcare the knot as '== function " + flowBase.identifier?.ToString() + " =='?");
			}
			else if (flowBase.isFunction && !isFunctionCall && !(base.parent is DivertTarget))
			{
				base.Error(flowBase.identifier?.ToString() + " can't be diverted to. It can only be called as a function since it's been marked as such: '" + flowBase.identifier?.ToString() + "(...)'");
			}
		}
		bool flag = targetContent != null;
		bool flag2 = false;
		bool flag3 = false;
		if (target.numberOfComponents == 1)
		{
			flag2 = FunctionCall.IsBuiltIn(target.firstComponent);
			flag3 = context.IsExternal(target.firstComponent);
			if (flag2 | flag3)
			{
				if (!isFunctionCall)
				{
					base.Error(target.firstComponent + " must be called as a function: ~ " + target.firstComponent + "()");
				}
				if (flag3)
				{
					runtimeDivert.isExternal = true;
					if (arguments != null)
					{
						runtimeDivert.externalArgs = arguments.Count;
					}
					runtimeDivert.pushesToStack = false;
					runtimeDivert.targetPath = new Ink.Runtime.Path(target.firstComponent);
					CheckExternalArgumentValidity(context);
				}
				return;
			}
		}
		if (runtimeDivert.variableDivertName == null && !flag && !flag2 && !flag3)
		{
			Error("target not found: '" + target?.ToString() + "'");
		}
	}

	private void CheckArgumentValidity()
	{
		if (isEmpty)
		{
			return;
		}
		int num = 0;
		if (arguments != null && arguments.Count > 0)
		{
			num = arguments.Count;
		}
		if (targetContent == null)
		{
			return;
		}
		FlowBase flowBase = targetContent as FlowBase;
		if (num == 0 && (flowBase == null || !flowBase.hasParameters))
		{
			return;
		}
		if (flowBase == null && num > 0)
		{
			Error("target needs to be a knot or stitch in order to pass arguments");
			return;
		}
		if (flowBase.arguments == null && num > 0)
		{
			Error("target (" + flowBase.name + ") doesn't take parameters");
			return;
		}
		if (base.parent is DivertTarget)
		{
			if (num > 0)
			{
				Error("can't store arguments in a divert target variable");
			}
			return;
		}
		int count = flowBase.arguments.Count;
		if (count != num)
		{
			string text = ((num == 0) ? "but there weren't any passed to it" : ((num >= count) ? ("but got " + num) : ("but only got " + num)));
			Error("to '" + flowBase.identifier?.ToString() + "' requires " + count + " arguments, " + text);
			return;
		}
		for (int i = 0; i < count; i++)
		{
			FlowBase.Argument argument = flowBase.arguments[i];
			Expression expression = arguments[i];
			if (!argument.isDivertTarget)
			{
				continue;
			}
			VariableReference variableReference = expression as VariableReference;
			if (!(expression is DivertTarget) && variableReference == null)
			{
				Error("Target '" + flowBase.identifier?.ToString() + "' expects a divert target for the parameter named -> " + argument.identifier?.ToString() + " but saw " + expression, expression);
			}
			else if (variableReference != null)
			{
				Path path = new Path(variableReference.pathIdentifiers);
				if (path.ResolveFromContext(variableReference) != null)
				{
					Error("Passing read count of '" + path.dotSeparatedComponents + "' instead of a divert target. You probably meant '" + path?.ToString() + "'");
				}
			}
		}
		if (flowBase == null)
		{
			Error("Can't call as a function or with arguments unless it's a knot or stitch");
		}
	}

	private void CheckExternalArgumentValidity(Story context)
	{
		string firstComponent = target.firstComponent;
		ExternalDeclaration value = null;
		context.externals.TryGetValue(firstComponent, out value);
		int count = value.argumentNames.Count;
		int num = 0;
		if (arguments != null)
		{
			num = arguments.Count;
		}
		if (num != count)
		{
			Error("incorrect number of arguments sent to external function '" + firstComponent + "'. Expected " + count + " but got " + num);
		}
	}

	public override void Error(string message, Object source = null, bool isWarning = false)
	{
		if (source != this && (bool)source)
		{
			base.Error(message, source);
		}
		else if (isFunctionCall)
		{
			base.Error("Function call " + message, source, isWarning);
		}
		else
		{
			base.Error("Divert " + message, source, isWarning);
		}
	}

	public override string ToString()
	{
		if (target != null)
		{
			return target.ToString();
		}
		return "-> <empty divert>";
	}
}
