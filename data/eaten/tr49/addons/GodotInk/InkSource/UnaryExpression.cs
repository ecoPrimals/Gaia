using System;
using Ink.Runtime;

namespace Ink.Parsed;

public class UnaryExpression : Expression
{
	public Expression innerExpression;

	public string op;

	private string nativeNameForOp
	{
		get
		{
			if (op == "-")
			{
				return "_";
			}
			if (op == "not")
			{
				return "!";
			}
			return op;
		}
	}

	public static Expression WithInner(Expression inner, string op)
	{
		Number number = inner as Number;
		if ((bool)number)
		{
			switch (op)
			{
			case "-":
				if (number.value is int)
				{
					return new Number(-(int)number.value);
				}
				if (number.value is float)
				{
					return new Number(0f - (float)number.value);
				}
				break;
			case "!":
			case "not":
				if (number.value is int)
				{
					return new Number((int)number.value == 0);
				}
				if (number.value is float)
				{
					return new Number((float)number.value == 0f);
				}
				if (number.value is bool)
				{
					return new Number(!(bool)number.value);
				}
				break;
			}
			throw new Exception("Unexpected operation or number type");
		}
		return new UnaryExpression(inner, op);
	}

	public UnaryExpression(Expression inner, string op)
	{
		innerExpression = AddContent(inner);
		this.op = op;
	}

	public override void GenerateIntoContainer(Container container)
	{
		innerExpression.GenerateIntoContainer(container);
		container.AddContent(NativeFunctionCall.CallWithName(nativeNameForOp));
	}

	public override string ToString()
	{
		return nativeNameForOp + innerExpression;
	}
}
