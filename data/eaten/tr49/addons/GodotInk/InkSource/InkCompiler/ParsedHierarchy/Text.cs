using Ink.Runtime;

namespace Ink.Parsed;

public class Text : Object
{
	public string text { get; set; }

	public Text(string str)
	{
		text = str;
	}

	public override Ink.Runtime.Object GenerateRuntimeObject()
	{
		return new StringValue(text);
	}

	public override string ToString()
	{
		return text;
	}
}
