using System.Globalization;

namespace Ink.Runtime;

public class StringValue : Value<string>
{
	public override ValueType valueType => ValueType.String;

	public override bool isTruthy => base.value.Length > 0;

	public bool isNewline { get; private set; }

	public bool isInlineWhitespace { get; private set; }

	public bool isNonWhitespace
	{
		get
		{
			if (!isNewline)
			{
				return !isInlineWhitespace;
			}
			return false;
		}
	}

	public StringValue(string str)
		: base(str)
	{
		isNewline = base.value == "\n";
		isInlineWhitespace = true;
		string text = base.value;
		foreach (char c in text)
		{
			if (c != ' ' && c != '\t')
			{
				isInlineWhitespace = false;
				break;
			}
		}
	}

	public StringValue()
		: this("")
	{
	}

	public override Value Cast(ValueType newType)
	{
		if (newType == valueType)
		{
			return this;
		}
		switch (newType)
		{
		case ValueType.Int:
		{
			if (int.TryParse(base.value, out var result2))
			{
				return new IntValue(result2);
			}
			return null;
		}
		case ValueType.Float:
		{
			if (float.TryParse(base.value, NumberStyles.Float, CultureInfo.InvariantCulture, out var result))
			{
				return new FloatValue(result);
			}
			return null;
		}
		default:
			throw BadCastException(newType);
		}
	}
}
