using Ink.Runtime;

namespace Ink.Parsed;

public class Identifier
{
	public string name;

	public DebugMetadata debugMetadata;

	public static Identifier Done = new Identifier
	{
		name = "DONE",
		debugMetadata = null
	};

	public override string ToString()
	{
		return name;
	}
}
