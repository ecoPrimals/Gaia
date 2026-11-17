using System.Collections.Generic;

namespace Ink.Parsed;

public class Knot : FlowBase
{
	public override FlowLevel flowLevel => FlowLevel.Knot;

	public Knot(Identifier name, List<Object> topLevelObjects, List<Argument> arguments, bool isFunction)
		: base(name, topLevelObjects, arguments, isFunction)
	{
	}

	public override void ResolveReferences(Story context)
	{
		base.ResolveReferences(context);
		Story story = base.story;
		foreach (KeyValuePair<string, FlowBase> item in base.subFlowsByName)
		{
			string key = item.Key;
			Object obj = story.ContentWithNameAtLevel(key, FlowLevel.Knot);
			if ((bool)obj)
			{
				FlowBase value = item.Value;
				string message = $"Stitch '{value.identifier}' has the same name as a knot (on {obj.debugMetadata})";
				Error(message, value);
			}
		}
	}
}
