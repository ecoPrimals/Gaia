using System.Collections.Generic;

namespace Ink.Parsed;

public class Stitch : FlowBase
{
	public override FlowLevel flowLevel => FlowLevel.Stitch;

	public Stitch(Identifier name, List<Object> topLevelObjects, List<Argument> arguments, bool isFunction)
		: base(name, topLevelObjects, arguments, isFunction)
	{
	}
}
