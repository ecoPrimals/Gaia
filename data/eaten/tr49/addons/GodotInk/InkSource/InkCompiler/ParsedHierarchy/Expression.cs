using Ink.Runtime;

namespace Ink.Parsed;

public abstract class Expression : Object
{
	private Container _prototypeRuntimeConstantExpression;

	public bool outputWhenComplete { get; set; }

	public override Ink.Runtime.Object GenerateRuntimeObject()
	{
		Container container = new Container();
		container.AddContent(ControlCommand.EvalStart());
		GenerateIntoContainer(container);
		if (outputWhenComplete)
		{
			container.AddContent(ControlCommand.EvalOutput());
		}
		container.AddContent(ControlCommand.EvalEnd());
		return container;
	}

	public void GenerateConstantIntoContainer(Container container)
	{
		if (_prototypeRuntimeConstantExpression == null)
		{
			_prototypeRuntimeConstantExpression = new Container();
			GenerateIntoContainer(_prototypeRuntimeConstantExpression);
		}
		foreach (Ink.Runtime.Object item in _prototypeRuntimeConstantExpression.content)
		{
			container.AddContent(item.Copy());
		}
	}

	public abstract void GenerateIntoContainer(Container container);
}
