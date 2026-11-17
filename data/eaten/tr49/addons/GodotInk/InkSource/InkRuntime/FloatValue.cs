using System.Globalization;

namespace Ink.Runtime;

public class FloatValue : Value<float>
{
	public override ValueType valueType => ValueType.Float;

	public override bool isTruthy => base.value != 0f;

	public FloatValue(float val)
		: base(val)
	{
	}

	public FloatValue()
		: this(0f)
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
			ValueType.Bool => new BoolValue(base.value != 0f), 
			ValueType.Int => new IntValue((int)base.value), 
			ValueType.String => new StringValue(base.value.ToString(CultureInfo.InvariantCulture) ?? ""), 
			_ => throw BadCastException(newType), 
		};
	}
}
