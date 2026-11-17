namespace Ink.Runtime;

public class IntValue : Value<int>
{
	public override ValueType valueType => ValueType.Int;

	public override bool isTruthy => base.value != 0;

	public IntValue(int intVal)
		: base(intVal)
	{
	}

	public IntValue()
		: this(0)
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
			ValueType.Bool => new BoolValue(base.value != 0), 
			ValueType.Float => new FloatValue(base.value), 
			ValueType.String => new StringValue(base.value.ToString() ?? ""), 
			_ => throw BadCastException(newType), 
		};
	}
}
