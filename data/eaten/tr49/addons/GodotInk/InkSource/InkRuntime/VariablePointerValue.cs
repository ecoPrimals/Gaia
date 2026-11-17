using System;

namespace Ink.Runtime;

public class VariablePointerValue : Value<string>
{
	public string variableName
	{
		get
		{
			return base.value;
		}
		set
		{
			base.value = value;
		}
	}

	public override ValueType valueType => ValueType.VariablePointer;

	public override bool isTruthy
	{
		get
		{
			throw new Exception("Shouldn't be checking the truthiness of a variable pointer");
		}
	}

	public int contextIndex { get; set; }

	public VariablePointerValue(string variableName, int contextIndex = -1)
		: base(variableName)
	{
		this.contextIndex = contextIndex;
	}

	public VariablePointerValue()
		: this(null)
	{
	}

	public override Value Cast(ValueType newType)
	{
		if (newType == valueType)
		{
			return this;
		}
		throw BadCastException(newType);
	}

	public override string ToString()
	{
		return "VariablePointerValue(" + variableName + ")";
	}

	public override Object Copy()
	{
		return new VariablePointerValue(variableName, contextIndex);
	}
}
