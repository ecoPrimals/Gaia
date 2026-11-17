using Ink.Runtime;

namespace Ink.Parsed;

public class IncDecExpression : Expression
{
	public Identifier varIdentifier;

	public bool isInc;

	public Expression expression;

	private Ink.Runtime.VariableAssignment _runtimeAssignment;

	private string incrementDecrementWord
	{
		get
		{
			if (isInc)
			{
				return "increment";
			}
			return "decrement";
		}
	}

	public IncDecExpression(Identifier varIdentifier, bool isInc)
	{
		this.varIdentifier = varIdentifier;
		this.isInc = isInc;
	}

	public IncDecExpression(Identifier varIdentifier, Expression expression, bool isInc)
		: this(varIdentifier, isInc)
	{
		this.expression = expression;
		AddContent(expression);
	}

	public override void GenerateIntoContainer(Container container)
	{
		container.AddContent(new Ink.Runtime.VariableReference(varIdentifier?.name));
		if ((bool)expression)
		{
			expression.GenerateIntoContainer(container);
		}
		else
		{
			container.AddContent(new IntValue(1));
		}
		container.AddContent(NativeFunctionCall.CallWithName(isInc ? "+" : "-"));
		_runtimeAssignment = new Ink.Runtime.VariableAssignment(varIdentifier?.name, isNewDeclaration: false);
		container.AddContent(_runtimeAssignment);
	}

	public override void ResolveReferences(Story context)
	{
		base.ResolveReferences(context);
		FlowBase.VariableResolveResult variableResolveResult = context.ResolveVariableWithName(varIdentifier?.name, this);
		if (!variableResolveResult.found)
		{
			Error("variable for " + incrementDecrementWord + " could not be found: '" + varIdentifier?.ToString() + "' after searching: " + base.descriptionOfScope);
		}
		_runtimeAssignment.isGlobal = variableResolveResult.isGlobal;
		if (!(base.parent is Weave) && !(base.parent is FlowBase) && !(base.parent is ContentList))
		{
			Error("Can't use " + incrementDecrementWord + " as sub-expression");
		}
	}

	public override string ToString()
	{
		if ((bool)expression)
		{
			return varIdentifier?.ToString() + (isInc ? " += " : " -= ") + expression.ToString();
		}
		return varIdentifier?.ToString() + (isInc ? "++" : "--");
	}
}
