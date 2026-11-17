using System.Collections.Generic;
using Ink.Runtime;

namespace Ink.Parsed;

public class TunnelOnwards : Object
{
	private Divert _divertAfter;

	private DivertTargetValue _overrideDivertTarget;

	public Divert divertAfter
	{
		get
		{
			return _divertAfter;
		}
		set
		{
			_divertAfter = value;
			if ((bool)_divertAfter)
			{
				AddContent(_divertAfter);
			}
		}
	}

	public override Ink.Runtime.Object GenerateRuntimeObject()
	{
		Container container = new Container();
		container.AddContent(ControlCommand.EvalStart());
		if ((bool)divertAfter)
		{
			Ink.Runtime.Object obj = divertAfter.GenerateRuntimeObject();
			Container container2 = obj as Container;
			if ((bool)container2)
			{
				List<Expression> arguments = divertAfter.arguments;
				if (arguments != null && arguments.Count > 0)
				{
					int num = -1;
					int num2 = -1;
					for (int i = 0; i < container2.content.Count; i++)
					{
						ControlCommand controlCommand = container2.content[i] as ControlCommand;
						if ((bool)controlCommand)
						{
							if (num == -1 && controlCommand.commandType == ControlCommand.CommandType.EvalStart)
							{
								num = i;
							}
							else if (controlCommand.commandType == ControlCommand.CommandType.EvalEnd)
							{
								num2 = i;
							}
						}
					}
					for (int j = num + 1; j < num2; j++)
					{
						container2.content[j].parent = null;
						container.AddContent(container2.content[j]);
					}
				}
			}
			Ink.Runtime.Divert divert = obj as Ink.Runtime.Divert;
			if (divert != null && divert.hasVariableTarget)
			{
				Ink.Runtime.VariableReference contentObj = new Ink.Runtime.VariableReference(divert.variableDivertName);
				container.AddContent(contentObj);
			}
			else
			{
				_overrideDivertTarget = new DivertTargetValue();
				container.AddContent(_overrideDivertTarget);
			}
		}
		else
		{
			container.AddContent(new Void());
		}
		container.AddContent(ControlCommand.EvalEnd());
		container.AddContent(ControlCommand.PopTunnel());
		return container;
	}

	public override void ResolveReferences(Story context)
	{
		base.ResolveReferences(context);
		if ((bool)divertAfter && (bool)divertAfter.targetContent)
		{
			_overrideDivertTarget.targetPath = divertAfter.targetContent.runtimePath;
		}
	}
}
