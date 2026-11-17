namespace Ink.Runtime;

public abstract class Value : Object
{
	public abstract ValueType valueType { get; }

	public abstract bool isTruthy { get; }

	public abstract object valueObject { get; }

	public abstract Value Cast(ValueType newType);

	public static Value Create(object val)
	{
		if (val is double)
		{
			val = (float)(double)val;
		}
		if (val is bool)
		{
			return new BoolValue((bool)val);
		}
		if (val is int)
		{
			return new IntValue((int)val);
		}
		if (val is long)
		{
			return new IntValue((int)(long)val);
		}
		if (val is float)
		{
			return new FloatValue((float)val);
		}
		if (val is double)
		{
			return new FloatValue((float)(double)val);
		}
		if (val is string)
		{
			return new StringValue((string)val);
		}
		if (val is Path)
		{
			return new DivertTargetValue((Path)val);
		}
		if (val is InkList)
		{
			return new ListValue((InkList)val);
		}
		return null;
	}

	public override Object Copy()
	{
		return Create(valueObject);
	}

	protected StoryException BadCastException(ValueType targetType)
	{
		return new StoryException("Can't cast " + valueObject?.ToString() + " from " + valueType.ToString() + " to " + targetType);
	}
}
public abstract class Value<T> : Value
{
	public T value { get; set; }

	public override object valueObject => value;

	public Value(T val)
	{
		value = val;
	}

	public override string ToString()
	{
		return value.ToString();
	}
}
