using Ink.Runtime;

namespace Ink.Parsed;

public class IncludedFile : Object
{
	public Story includedStory { get; private set; }

	public IncludedFile(Story includedStory)
	{
		this.includedStory = includedStory;
	}

	public override Ink.Runtime.Object GenerateRuntimeObject()
	{
		return null;
	}
}
