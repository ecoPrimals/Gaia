using System;

namespace Ink.Runtime;

public class DivertTargetValue : Value<Path>
{
	public Path targetPath
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

	public override ValueType valueType => ValueType.DivertTarget;

	public override bool isTruthy
	{
		get
		{
			throw new Exception("Shouldn't be checking the truthiness of a divert target");
		}
	}

	public DivertTargetValue(Path targetPath)
		: base(targetPath)
	{
	}

	public DivertTargetValue()
		: base((Path)null)
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
		return "DivertTargetValue(" + targetPath?.ToString() + ")";
	}
}
