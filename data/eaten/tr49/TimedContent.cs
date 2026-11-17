using System.Collections.Generic;
using GodotInk;

public struct TimedContent
{
	public string speaker;

	public TimedContentType type;

	public string content;

	public List<InkChoice> choices;

	public string audioFile;

	public bool subtitleCentre;

	public bool skippable;

	public bool cuttable;
}
