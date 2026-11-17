using Ink.Runtime;

namespace Ink.Parsed;

public class Return : Object
{
	public Expression returnedExpression { get; protected set; }

	public Return(Expression returnedExpression = null)
	{
		if ((bool)returnedExpression)
		{
			this.returnedExpression = AddContent(returnedExpression);
		}
	}

	public override Ink.Runtime.Object GenerateRuntimeObject()
	{
		Container container = new Container();
		if ((bool)returnedExpression)
		{
			container.AddContent(returnedExpression.runtimeObject);
		}
		else
		{
			container.AddContent(ControlCommand.EvalStart());
			container.AddContent(new Void());
			container.AddContent(ControlCommand.EvalEnd());
		}
		container.AddContent(ControlCommand.PopFunction());
		return container;
	}
}
