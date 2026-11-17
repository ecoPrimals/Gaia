using Ink.Runtime;

namespace Ink.Parsed;

public class BinaryExpression : Expression
{
	public Expression leftExpression;

	public Expression rightExpression;

	public string opName;

	public BinaryExpression(Expression left, Expression right, string opName)
	{
		leftExpression = AddContent(left);
		rightExpression = AddContent(right);
		this.opName = opName;
	}

	public override void GenerateIntoContainer(Container container)
	{
		leftExpression.GenerateIntoContainer(container);
		rightExpression.GenerateIntoContainer(container);
		opName = NativeNameForOp(opName);
		container.AddContent(NativeFunctionCall.CallWithName(opName));
	}

	public override void ResolveReferences(Story context)
	{
		base.ResolveReferences(context);
		if (NativeNameForOp(opName) == "?")
		{
			UnaryExpression unaryExpression = leftExpression as UnaryExpression;
			if (unaryExpression != null && (unaryExpression.op == "not" || unaryExpression.op == "!"))
			{
				Error("Using 'not' or '!' here negates '" + unaryExpression.innerExpression?.ToString() + "' rather than the result of the '?' or 'has' operator. You need to add parentheses around the (A ? B) expression.");
			}
		}
	}

	private string NativeNameForOp(string opName)
	{
		return opName switch
		{
			"and" => "&&", 
			"or" => "||", 
			"mod" => "%", 
			"has" => "?", 
			"hasnt" => "!?", 
			_ => opName, 
		};
	}

	public override string ToString()
	{
		return $"({leftExpression} {opName} {rightExpression})";
	}
}
