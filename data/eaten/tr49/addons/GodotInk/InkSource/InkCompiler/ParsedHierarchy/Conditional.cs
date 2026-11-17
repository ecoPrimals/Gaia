using System.Collections.Generic;
using System.Linq;
using Ink.Runtime;

namespace Ink.Parsed;

public class Conditional : Object
{
	private ControlCommand _reJoinTarget;

	public Expression initialCondition { get; private set; }

	public List<ConditionalSingleBranch> branches { get; private set; }

	public Conditional(Expression condition, List<ConditionalSingleBranch> branches)
	{
		initialCondition = condition;
		if ((bool)initialCondition)
		{
			AddContent(condition);
		}
		this.branches = branches;
		if (this.branches != null)
		{
			AddContent(this.branches.Cast<Object>().ToList());
		}
	}

	public override Ink.Runtime.Object GenerateRuntimeObject()
	{
		Container container = new Container();
		if ((bool)initialCondition)
		{
			container.AddContent(initialCondition.runtimeObject);
		}
		foreach (ConditionalSingleBranch branch in branches)
		{
			Container contentObj = (Container)branch.runtimeObject;
			container.AddContent(contentObj);
		}
		if (initialCondition != null && branches[0].ownExpression != null && !branches[branches.Count - 1].isElse)
		{
			container.AddContent(ControlCommand.PopEvaluatedValue());
		}
		_reJoinTarget = ControlCommand.NoOp();
		container.AddContent(_reJoinTarget);
		return container;
	}

	public override void ResolveReferences(Story context)
	{
		Ink.Runtime.Path path = _reJoinTarget.path;
		foreach (ConditionalSingleBranch branch in branches)
		{
			branch.returnDivert.targetPath = path;
		}
		base.ResolveReferences(context);
	}
}
