using Ink.Runtime;

namespace Ink.Parsed;

public class ConstantDeclaration : Object
{
	public string constantName => constantIdentifier?.name;

	public Identifier constantIdentifier { get; protected set; }

	public Expression expression { get; protected set; }

	public override string typeName => "Constant";

	public ConstantDeclaration(Identifier name, Expression assignedExpression)
	{
		constantIdentifier = name;
		if ((bool)assignedExpression)
		{
			expression = AddContent(assignedExpression);
		}
	}

	public override Ink.Runtime.Object GenerateRuntimeObject()
	{
		return null;
	}

	public override void ResolveReferences(Story context)
	{
		base.ResolveReferences(context);
		context.CheckForNamingCollisions(this, constantIdentifier, Story.SymbolType.Var);
	}
}
