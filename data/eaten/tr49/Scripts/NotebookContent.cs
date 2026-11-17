using System.Collections.Generic;
using System.Linq;
using Godot;

public struct NotebookContent
{
	public string objectivesText;

	public string sourcesText;

	public string titlesText;

	public List<NotebookCodeEntry> systemCodes;

	public List<NotebookCodeEntry> mainCodes;

	public List<NotebookCodeEntry> otherCodes;

	public List<NotebookAuthorPage> authorPages;

	private static string ProcessText(string text)
	{
		return CardLinks.ConvertToBBCode(InkStylingUtility.ProcessAndStyleText(text, terminatingPunctuation: false), allowTitleLinks: false);
	}

	public static NotebookContent Parse(List<string> notebookContentLines)
	{
		NotebookContent result = default(NotebookContent);
		int parseLineIdx = 0;
		while (parseLineIdx < notebookContentLines.Count)
		{
			string text = notebookContentLines[parseLineIdx];
			switch (text)
			{
			case "§Objective§":
				parseLineIdx++;
				result.objectivesText = ProcessText(notebookContentLines[parseLineIdx]);
				parseLineIdx++;
				if (parseLineIdx < notebookContentLines.Count && notebookContentLines[parseLineIdx].StartsWith("Sources:"))
				{
					result.sourcesText = ProcessText(notebookContentLines[parseLineIdx].Substring("Sources:".Length).Trim());
					result.sourcesText = result.sourcesText.Replace("PSICHARRED", "[img width=24]res://Glyphs/psi_small_red.png[/img]");
					parseLineIdx++;
				}
				else
				{
					result.sourcesText = "";
				}
				if (parseLineIdx < notebookContentLines.Count && notebookContentLines[parseLineIdx].StartsWith("Titles:"))
				{
					result.titlesText = ProcessText(notebookContentLines[parseLineIdx].Substring("Titles:".Length).Trim());
					parseLineIdx++;
				}
				else
				{
					result.titlesText = "";
				}
				break;
			case "§System Codes§":
				parseLineIdx++;
				result.systemCodes = ParseCodeList(ref parseLineIdx, notebookContentLines);
				break;
			case "§Main Codes§":
				parseLineIdx++;
				result.mainCodes = ParseCodeList(ref parseLineIdx, notebookContentLines);
				break;
			case "§Other Codes§":
				parseLineIdx++;
				result.otherCodes = ParseCodeList(ref parseLineIdx, notebookContentLines);
				break;
			case "§Journals§":
			case "§People§":
				parseLineIdx++;
				if (result.authorPages == null)
				{
					result.authorPages = new List<NotebookAuthorPage>();
				}
				result.authorPages.AddRange(ParseAuthorPages(ref parseLineIdx, notebookContentLines));
				break;
			default:
				GD.PushError("Unknown notebook line: " + text);
				parseLineIdx++;
				break;
			}
		}
		if (result.objectivesText == null)
		{
			result.objectivesText = "";
		}
		if (result.systemCodes == null)
		{
			result.systemCodes = new List<NotebookCodeEntry>();
		}
		if (result.mainCodes == null)
		{
			result.mainCodes = new List<NotebookCodeEntry>();
		}
		if (result.otherCodes == null)
		{
			result.otherCodes = new List<NotebookCodeEntry>();
		}
		return result;
	}

	private static List<NotebookCodeEntry> ParseCodeList(ref int parseLineIdx, List<string> notebookContentLines)
	{
		List<NotebookCodeEntry> list = new List<NotebookCodeEntry>();
		while (parseLineIdx < notebookContentLines.Count)
		{
			string text = notebookContentLines[parseLineIdx];
			if (text.StartsWith("§"))
			{
				break;
			}
			NotebookCodeEntry item = default(NotebookCodeEntry);
			List<string> list2 = SplitLineParts(text);
			item.code = list2[0];
			item.text = list2[1];
			for (int i = 2; i < list2.Count; i++)
			{
				string text2 = list2[i];
				if (string.IsNullOrWhiteSpace(text2))
				{
					continue;
				}
				string[] array = text2.Split('=');
				if (array.Length != 2)
				{
					GD.PushError("Notebook code ink optional line should've had a KEY=value, but saw: " + text);
					continue;
				}
				string text3 = array[0];
				string text4 = array[1];
				switch (text3)
				{
				case "REALCODE":
					item.realCode = text4;
					break;
				case "CONFIRMED":
					item.isConfirmed = text4 == "true";
					break;
				case "REFCOUNT":
				{
					string[] array2 = text4.Split('/');
					if (array2.Length != 2)
					{
						GD.PushError("Notebook code ink refcount line should've had a count/max count separated by /, but saw: " + text4);
						break;
					}
					item.refCount = int.Parse(array2[0]);
					item.refCountMax = int.Parse(array2[1]);
					break;
				}
				default:
					GD.PushError("Notebook code ink optional key '" + text3 + "' wasn't recognized in " + text);
					break;
				}
			}
			list.Add(item);
			parseLineIdx++;
		}
		return list;
	}

	private static List<string> SplitLineParts(string line)
	{
		return (from x in line.Split("--")
			select x.Trim()).ToList();
	}

	private static List<NotebookAuthorPage> ParseAuthorPages(ref int parseLineIdx, List<string> notebookContentLines)
	{
		List<NotebookAuthorPage> list = new List<NotebookAuthorPage>();
		while (parseLineIdx < notebookContentLines.Count)
		{
			string text = notebookContentLines[parseLineIdx];
			if (text.StartsWith("§"))
			{
				break;
			}
			List<string> list2 = SplitLineParts(text);
			if (list2.Count != 2 && list2.Count != 3)
			{
				GD.PushError("Notebook author header line expected something like 'Literary Review  -- LR -- Some/Image/Path.png' but saw: " + text);
				continue;
			}
			NotebookAuthorPage item = new NotebookAuthorPage
			{
				name = list2[0],
				prefixLetters = list2[1]
			};
			if (list2.Count > 2)
			{
				item.imagePath = list2[2];
			}
			item.publications = new List<NotebookAuthorPublication>();
			parseLineIdx++;
			if (notebookContentLines[parseLineIdx].StartsWith("BLURB"))
			{
				parseLineIdx++;
				while (parseLineIdx < notebookContentLines.Count && !notebookContentLines[parseLineIdx].StartsWith("END_BLURB"))
				{
					string text2 = ProcessText(notebookContentLines[parseLineIdx]);
					item.blurb = ((item.blurb == null) ? text2 : (item.blurb + "\n" + text2));
					parseLineIdx++;
				}
				parseLineIdx++;
			}
			while (parseLineIdx < notebookContentLines.Count)
			{
				string text3 = notebookContentLines[parseLineIdx];
				if (text3.StartsWith("§"))
				{
					break;
				}
				List<string> list3 = SplitLineParts(text3);
				if (list3.Count < 1 || list3[0] != "PUBLICATION")
				{
					break;
				}
				if (list3.Count < 2 || list3.Count > 4)
				{
					GD.PushError("Notebook author work line expected something like 'PUBLICATION -- 99 -- The Assigned Title -- ?' but saw: " + text3);
					parseLineIdx++;
					continue;
				}
				NotebookAuthorPublication item2 = new NotebookAuthorPublication
				{
					code = list3[1]
				};
				if (list3.Count >= 3)
				{
					item2.titleApplied = list3[2];
					item2.isDefinitive = !list3[3].Contains('?');
					item2.isNotFullyLinked = list3[3].Contains('*');
				}
				item.publications.Add(item2);
				parseLineIdx++;
			}
			list.Add(item);
		}
		return list;
	}
}
