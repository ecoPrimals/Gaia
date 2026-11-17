using System.Collections.Generic;
using Ink.Parsed;

namespace Ink;

public struct Stats
{
	public int words;

	public int knots;

	public int stitches;

	public int functions;

	public int choices;

	public int gathers;

	public int diverts;

	public static Stats Generate(Story story)
	{
		Stats result = default(Stats);
		List<Text> list = story.FindAll<Text>();
		result.words = 0;
		foreach (Text item in list)
		{
			int num = 0;
			bool flag = true;
			string text = item.text;
			foreach (char c in text)
			{
				if (c == ' ' || c == '\t' || c == '\n' || c == '\r')
				{
					flag = true;
				}
				else if (flag)
				{
					num++;
					flag = false;
				}
			}
			result.words += num;
		}
		List<Knot> list2 = story.FindAll<Knot>();
		result.knots = list2.Count;
		result.functions = 0;
		foreach (Knot item2 in list2)
		{
			if (item2.isFunction)
			{
				result.functions++;
			}
		}
		List<Stitch> list3 = story.FindAll<Stitch>();
		result.stitches = list3.Count;
		List<Choice> list4 = story.FindAll<Choice>();
		result.choices = list4.Count;
		List<Gather> list5 = story.FindAll((Gather g) => g.debugMetadata != null);
		result.gathers = list5.Count;
		List<Divert> list6 = story.FindAll<Divert>();
		result.diverts = list6.Count - 1;
		return result;
	}
}
