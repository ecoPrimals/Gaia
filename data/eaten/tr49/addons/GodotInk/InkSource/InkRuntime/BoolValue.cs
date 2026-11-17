namespace Ink.Runtime;

public class BoolValue : Value<bool>
{
	public override ValueType valueType => ValueType.Bool;

	public override bool isTruthy => base.value;

	public BoolValue(bool boolVal)
		: base(boolVal)
	{
	}

	public BoolValue()
		: this(boolVal: false)
	{
	}

	public override Value Cast(ValueType newType)
	{
		if (newType == valueType)
		{
			return this;
		}
		return newType switch
		{
			ValueType.Int => new IntValue(base.value ? 1 : 0), 
			ValueType.Float => new FloatValue(base.value ? 1f : 0f), 
			ValueType.String => new StringValue(base.value ? "true" : "false"), 
			_ => throw BadCastException(newType), 
		};
	}

	public override string ToString()
	{
		if (!base.value)
		{
			return "false";
		}
		return "true";
	}
}
