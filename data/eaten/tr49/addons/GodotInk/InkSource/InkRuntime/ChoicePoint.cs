namespace Ink.Runtime;

public class ChoicePoint : Object
{
	private Path _pathOnChoice;

	public Path pathOnChoice
	{
		get
		{
			if (_pathOnChoice != null && _pathOnChoice.isRelative)
			{
				Container container = choiceTarget;
				if ((bool)container)
				{
					_pathOnChoice = container.path;
				}
			}
			return _pathOnChoice;
		}
		set
		{
			_pathOnChoice = value;
		}
	}

	public Container choiceTarget => ResolvePath(_pathOnChoice).container;

	public string pathStringOnChoice
	{
		get
		{
			return CompactPathString(pathOnChoice);
		}
		set
		{
			pathOnChoice = new Path(value);
		}
	}

	public bool hasCondition { get; set; }

	public bool hasStartContent { get; set; }

	public bool hasChoiceOnlyContent { get; set; }

	public bool onceOnly { get; set; }

	public bool isInvisibleDefault { get; set; }

	public int flags
	{
		get
		{
			int num = 0;
			if (hasCondition)
			{
				num |= 1;
			}
			if (hasStartContent)
			{
				num |= 2;
			}
			if (hasChoiceOnlyContent)
			{
				num |= 4;
			}
			if (isInvisibleDefault)
			{
				num |= 8;
			}
			if (onceOnly)
			{
				num |= 0x10;
			}
			return num;
		}
		set
		{
			hasCondition = (value & 1) > 0;
			hasStartContent = (value & 2) > 0;
			hasChoiceOnlyContent = (value & 4) > 0;
			isInvisibleDefault = (value & 8) > 0;
			onceOnly = (value & 0x10) > 0;
		}
	}

	public ChoicePoint(bool onceOnly)
	{
		this.onceOnly = onceOnly;
	}

	public ChoicePoint()
		: this(onceOnly: true)
	{
	}

	public override string ToString()
	{
		int? num = DebugLineNumberOfPath(pathOnChoice);
		string text = pathOnChoice.ToString();
		if (num.HasValue)
		{
			string[] obj = new string[5] { " line ", null, null, null, null };
			int? num2 = num;
			obj[1] = num2.ToString();
			obj[2] = "(";
			obj[3] = text;
			obj[4] = ")";
			text = string.Concat(obj);
		}
		return "Choice: -> " + text;
	}
}
