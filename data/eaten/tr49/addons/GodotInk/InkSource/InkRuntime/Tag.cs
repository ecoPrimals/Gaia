namespace Ink.Runtime;

public class Tag : Object
{
	public string text { get; private set; }

	public Tag(string tagText)
	{
		text = tagText;
	}

	public override string ToString()
	{
		return "# " + text;
	}
}
