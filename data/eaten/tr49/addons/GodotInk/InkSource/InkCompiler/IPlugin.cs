using Ink.Parsed;
using Ink.Runtime;

namespace Ink;

public interface IPlugin
{
	void PreParse(ref string storyContent);

	void PostParse(ref Ink.Parsed.Story parsedStory);

	void PostExport(Ink.Parsed.Story parsedStory, ref Ink.Runtime.Story runtimeStory);
}
