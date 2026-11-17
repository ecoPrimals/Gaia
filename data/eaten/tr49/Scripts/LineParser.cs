using System;
using System.Collections.Generic;
using System.Text;
using Godot;

public class LineParser
{
	public struct Word
	{
		public string text;

		public Color? color;

		public bool isBold;

		public bool isItalic;

		public string link;

		public bool isWhitespace;

		public override string ToString()
		{
			if (isWhitespace)
			{
				return "' '";
			}
			StringBuilder stringBuilder = new StringBuilder();
			stringBuilder.Append(text);
			if (color.HasValue)
			{
				stringBuilder.Append(" - COLOR:");
				stringBuilder.Append(color.Value.ToString());
			}
			if (isBold)
			{
				stringBuilder.Append(" - BOLD");
			}
			if (isItalic)
			{
				stringBuilder.Append(" - ITALIC");
			}
			if (link != null)
			{
				stringBuilder.Append(" - LINK:");
				stringBuilder.Append(link);
			}
			return stringBuilder.ToString();
		}
	}

	private string text;

	private int index;

	private List<Word> words = new List<Word>();

	private Color? color;

	private bool isBold;

	private bool isItalic;

	private string link;

	public LineParser(string text)
	{
		this.text = text;
		index = 0;
	}

	public List<Word> Parse()
	{
		while (index < text.Length)
		{
			if (ParseCloseTag() || ParseOpenTag())
			{
				continue;
			}
			if (link != null)
			{
				if (ParseAnyTextBetweenTags())
				{
					continue;
				}
			}
			else if (ParseWord() || ParseWhitespace())
			{
				continue;
			}
			throw new Exception("Invalid content: " + RemainingString());
		}
		return words;
	}

	private bool ParseOpenTag()
	{
		if (!ParseString("["))
		{
			return false;
		}
		if (ParseString("color"))
		{
			Expect("=#");
			string text = ParseUntilCharacterFrom("]");
			if (text == null)
			{
				throw new Exception("Expected color hex");
			}
			color = new Color(text);
		}
		else if (ParseString("b"))
		{
			isBold = true;
		}
		else if (ParseString("i"))
		{
			isItalic = true;
		}
		else if (ParseString("url"))
		{
			Expect("=");
			link = ParseUntilCharacterFrom("]");
			if (link == null)
			{
				throw new Exception("Expected link");
			}
		}
		Expect("]");
		return true;
	}

	private bool ParseCloseTag()
	{
		if (!ParseString("[/"))
		{
			return false;
		}
		if (ParseString("color"))
		{
			color = null;
			Expect("]");
		}
		else if (ParseString("b"))
		{
			isBold = false;
			Expect("]");
		}
		else if (ParseString("i"))
		{
			isItalic = false;
			Expect("]");
		}
		else if (ParseString("url"))
		{
			link = null;
			Expect("]");
		}
		else
		{
			string text = ParseUntilCharacterFrom("]");
			GD.PushError("Unsupported close tag: [/" + text + "]");
		}
		return true;
	}

	private bool ParseWord()
	{
		string text = ParseUntilCharacterFrom("[] \t");
		if (text == null)
		{
			return false;
		}
		words.Add(new Word
		{
			text = text,
			color = color,
			isBold = isBold,
			isItalic = isItalic,
			link = link
		});
		return true;
	}

	private bool ParseWhitespace()
	{
		if (ParseCharactersFrom(" \t\n\r") == null)
		{
			return false;
		}
		words.Add(new Word
		{
			isWhitespace = true
		});
		return true;
	}

	private bool ParseAnyTextBetweenTags()
	{
		string text = ParseUntilCharacterFrom("[]");
		if (text == null)
		{
			return false;
		}
		words.Add(new Word
		{
			text = text,
			color = color,
			isBold = isBold,
			isItalic = isItalic,
			link = link
		});
		return true;
	}

	private bool ParseString(string s)
	{
		if (index + s.Length > text.Length)
		{
			return false;
		}
		for (int i = 0; i < s.Length; i++)
		{
			if (text[index + i] != s[i])
			{
				return false;
			}
		}
		index += s.Length;
		return true;
	}

	private string ParseUntilCharacterFrom(string chars)
	{
		int num = index;
		while (index < text.Length && !chars.Contains(text[index]))
		{
			index++;
		}
		if (index == num)
		{
			return null;
		}
		return text.Substring(num, index - num);
	}

	private string ParseCharactersFrom(string chars)
	{
		int num = index;
		while (index < text.Length && chars.Contains(text[index]))
		{
			index++;
		}
		if (index == num)
		{
			return null;
		}
		return text.Substring(num, index - num);
	}

	private void Expect(string s)
	{
		if (!ParseString(s))
		{
			throw new Exception("Expected: " + s + " but saw " + RemainingString());
		}
	}

	private string RemainingString()
	{
		return text.Substring(index);
	}
}
