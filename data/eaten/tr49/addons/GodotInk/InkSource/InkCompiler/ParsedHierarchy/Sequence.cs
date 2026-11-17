using System.Collections.Generic;
using Ink.Runtime;

namespace Ink.Parsed;

public class Sequence : Object
{
	private class SequenceDivertToResolve
	{
		public Ink.Runtime.Divert divert;

		public Ink.Runtime.Object targetContent;
	}

	public List<Object> sequenceElements;

	public SequenceType sequenceType;

	private List<SequenceDivertToResolve> _sequenceDivertsToResove;

	public Sequence(List<ContentList> elementContentLists, SequenceType sequenceType)
	{
		this.sequenceType = sequenceType;
		sequenceElements = new List<Object>();
		foreach (ContentList elementContentList in elementContentLists)
		{
			List<Object> list = elementContentList.content;
			Object obj = null;
			obj = ((list != null && list.Count != 0) ? ((Object)new Weave(list)) : ((Object)elementContentList));
			sequenceElements.Add(obj);
			AddContent(obj);
		}
	}

	public override Ink.Runtime.Object GenerateRuntimeObject()
	{
		Container container = new Container();
		container.visitsShouldBeCounted = true;
		container.countingAtStartOnly = true;
		_sequenceDivertsToResove = new List<SequenceDivertToResolve>();
		container.AddContent(ControlCommand.EvalStart());
		container.AddContent(ControlCommand.VisitIndex());
		bool flag = (sequenceType & SequenceType.Once) > (SequenceType)0;
		bool flag2 = (sequenceType & SequenceType.Cycle) > (SequenceType)0;
		bool flag3 = (sequenceType & SequenceType.Stopping) > (SequenceType)0;
		bool num = (sequenceType & SequenceType.Shuffle) > (SequenceType)0;
		int num2 = sequenceElements.Count;
		if (flag)
		{
			num2++;
		}
		if (flag3 | flag)
		{
			container.AddContent(new IntValue(num2 - 1));
			container.AddContent(NativeFunctionCall.CallWithName("MIN"));
		}
		else if (flag2)
		{
			container.AddContent(new IntValue(sequenceElements.Count));
			container.AddContent(NativeFunctionCall.CallWithName("%"));
		}
		if (num)
		{
			ControlCommand controlCommand = ControlCommand.NoOp();
			if (flag | flag3)
			{
				int intVal = (flag3 ? (sequenceElements.Count - 1) : sequenceElements.Count);
				container.AddContent(ControlCommand.Duplicate());
				container.AddContent(new IntValue(intVal));
				container.AddContent(NativeFunctionCall.CallWithName("=="));
				Ink.Runtime.Divert divert = new Ink.Runtime.Divert();
				divert.isConditional = true;
				container.AddContent(divert);
				AddDivertToResolve(divert, controlCommand);
			}
			int num3 = sequenceElements.Count;
			if (flag3)
			{
				num3--;
			}
			container.AddContent(new IntValue(num3));
			container.AddContent(ControlCommand.SequenceShuffleIndex());
			if (flag | flag3)
			{
				container.AddContent(controlCommand);
			}
		}
		container.AddContent(ControlCommand.EvalEnd());
		ControlCommand controlCommand2 = ControlCommand.NoOp();
		for (int i = 0; i < num2; i++)
		{
			container.AddContent(ControlCommand.EvalStart());
			container.AddContent(ControlCommand.Duplicate());
			container.AddContent(new IntValue(i));
			container.AddContent(NativeFunctionCall.CallWithName("=="));
			container.AddContent(ControlCommand.EvalEnd());
			Ink.Runtime.Divert divert2 = new Ink.Runtime.Divert();
			divert2.isConditional = true;
			container.AddContent(divert2);
			Container container2 = ((i >= sequenceElements.Count) ? new Container() : ((Container)sequenceElements[i].runtimeObject));
			container2.name = "s" + i;
			container2.InsertContent(ControlCommand.PopEvaluatedValue(), 0);
			Ink.Runtime.Divert divert3 = new Ink.Runtime.Divert();
			container2.AddContent(divert3);
			container.AddToNamedContentOnly(container2);
			AddDivertToResolve(divert2, container2);
			AddDivertToResolve(divert3, controlCommand2);
		}
		container.AddContent(controlCommand2);
		return container;
	}

	private void AddDivertToResolve(Ink.Runtime.Divert divert, Ink.Runtime.Object targetContent)
	{
		_sequenceDivertsToResove.Add(new SequenceDivertToResolve
		{
			divert = divert,
			targetContent = targetContent
		});
	}

	public override void ResolveReferences(Story context)
	{
		base.ResolveReferences(context);
		foreach (SequenceDivertToResolve item in _sequenceDivertsToResove)
		{
			item.divert.targetPath = item.targetContent.path;
		}
	}
}
