using Ink.Runtime;

namespace Ink.Parsed;

public class LegacyTag : Wrap<Ink.Runtime.Tag>
{
	public LegacyTag(Ink.Runtime.Tag tag)
		: base(tag)
	{
	}
}
