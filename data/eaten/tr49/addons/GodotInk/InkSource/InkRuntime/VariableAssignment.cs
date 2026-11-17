namespace Ink.Runtime;

public class VariableAssignment : Object
{
	public string variableName { get; protected set; }

	public bool isNewDeclaration { get; protected set; }

	public bool isGlobal { get; set; }

	public VariableAssignment(string variableName, bool isNewDeclaration)
	{
		this.variableName = variableName;
		this.isNewDeclaration = isNewDeclaration;
	}

	public VariableAssignment()
		: this(null, isNewDeclaration: false)
	{
	}

	public override string ToString()
	{
		return "VarAssign to " + variableName;
	}
}
