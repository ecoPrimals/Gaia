using Ink.Runtime;

namespace Ink.Parsed;

public class VariableAssignment : Object
{
	private Ink.Runtime.VariableAssignment _runtimeAssignment;

	public string variableName => variableIdentifier.name;

	public Identifier variableIdentifier { get; protected set; }

	public Expression expression { get; protected set; }

	public ListDefinition listDefinition { get; protected set; }

	public bool isGlobalDeclaration { get; set; }

	public bool isNewTemporaryDeclaration { get; set; }

	public bool isDeclaration
	{
		get
		{
			if (!isGlobalDeclaration)
			{
				return isNewTemporaryDeclaration;
			}
			return true;
		}
	}

	public override string typeName
	{
		get
		{
			if (isNewTemporaryDeclaration)
			{
				return "temp";
			}
			if (isGlobalDeclaration)
			{
				return "VAR";
			}
			return "variable assignment";
		}
	}

	public VariableAssignment(Identifier identifier, Expression assignedExpression)
	{
		variableIdentifier = identifier;
		if ((bool)assignedExpression)
		{
			expression = AddContent(assignedExpression);
		}
	}

	public VariableAssignment(Identifier identifier, ListDefinition listDef)
	{
		variableIdentifier = identifier;
		if ((bool)listDef)
		{
			listDefinition = AddContent(listDef);
			listDefinition.variableAssignment = this;
		}
		isGlobalDeclaration = true;
	}

	public override Ink.Runtime.Object GenerateRuntimeObject()
	{
		FlowBase flowBase = null;
		if (isGlobalDeclaration)
		{
			flowBase = base.story;
		}
		else if (isNewTemporaryDeclaration)
		{
			flowBase = ClosestFlowBase();
		}
		if ((bool)flowBase)
		{
			flowBase.TryAddNewVariableDeclaration(this);
		}
		if (isGlobalDeclaration)
		{
			return null;
		}
		Container container = new Container();
		if (expression != null)
		{
			container.AddContent(expression.runtimeObject);
		}
		else if (listDefinition != null)
		{
			container.AddContent(listDefinition.runtimeObject);
		}
		_runtimeAssignment = new Ink.Runtime.VariableAssignment(variableName, isNewTemporaryDeclaration);
		container.AddContent(_runtimeAssignment);
		return container;
	}

	public override void ResolveReferences(Story context)
	{
		base.ResolveReferences(context);
		if (isDeclaration && listDefinition == null)
		{
			context.CheckForNamingCollisions(this, variableIdentifier, isGlobalDeclaration ? Story.SymbolType.Var : Story.SymbolType.Temp);
		}
		if (isGlobalDeclaration)
		{
			VariableReference variableReference = expression as VariableReference;
			if ((bool)variableReference && !variableReference.isConstantReference && !variableReference.isListItemReference)
			{
				Error("global variable assignments cannot refer to other variables, only literal values, constants and list items");
			}
		}
		if (isNewTemporaryDeclaration)
		{
			return;
		}
		FlowBase.VariableResolveResult variableResolveResult = context.ResolveVariableWithName(variableName, this);
		if (!variableResolveResult.found)
		{
			if (base.story.constants.ContainsKey(variableName))
			{
				Error("Can't re-assign to a constant (do you need to use VAR when declaring '" + variableName + "'?)", this);
			}
			else
			{
				Error("Variable could not be found to assign to: '" + variableName + "'", this);
			}
		}
		if (_runtimeAssignment != null)
		{
			_runtimeAssignment.isGlobal = variableResolveResult.isGlobal;
		}
	}
}
