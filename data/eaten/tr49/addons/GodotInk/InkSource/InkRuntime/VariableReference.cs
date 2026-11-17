namespace Ink.Runtime;

public class VariableReference : Object
{
	public string name { get; set; }

	public Path pathForCount { get; set; }

	public Container containerForCount => ResolvePath(pathForCount).container;

	public string pathStringForCount
	{
		get
		{
			if (pathForCount == null)
			{
				return null;
			}
			return CompactPathString(pathForCount);
		}
		set
		{
			if (value == null)
			{
				pathForCount = null;
			}
			else
			{
				pathForCount = new Path(value);
			}
		}
	}

	public VariableReference(string name)
	{
		this.name = name;
	}

	public VariableReference()
	{
	}

	public override string ToString()
	{
		if (name != null)
		{
			return $"var({name})";
		}
		string arg = pathStringForCount;
		return $"read_count({arg})";
	}
}
