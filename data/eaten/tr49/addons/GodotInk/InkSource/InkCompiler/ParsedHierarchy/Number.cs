using System;
using System.Globalization;
using Ink.Runtime;

namespace Ink.Parsed;

public class Number : Expression
{
	public object value;

	public Number(object value)
	{
		if (value is int || value is float || value is bool)
		{
			this.value = value;
			return;
		}
		throw new Exception("Unexpected object type in Number");
	}

	public override void GenerateIntoContainer(Container container)
	{
		if (value is int)
		{
			container.AddContent(new IntValue((int)value));
		}
		else if (value is float)
		{
			container.AddContent(new FloatValue((float)value));
		}
		else if (value is bool)
		{
			container.AddContent(new BoolValue((bool)value));
		}
	}

	public override string ToString()
	{
		if (value is float)
		{
			return ((float)value).ToString(CultureInfo.InvariantCulture);
		}
		return value.ToString();
	}

	public override bool Equals(object obj)
	{
		Number number = obj as Number;
		if (number == null)
		{
			return false;
		}
		return value.Equals(number.value);
	}

	public override int GetHashCode()
	{
		return value.GetHashCode();
	}
}
