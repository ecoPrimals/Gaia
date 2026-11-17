using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Godot;

public static class InkStylingUtility
{
	private const string openItalics = "[i]";

	private const string closeItalics = "[/i]";

	private const string openBold = "[b]";

	private const string closeBold = "[/b]";

	private const string closeColor = "[/color]";

	private static char[] nonTerminatorsWhichThenRequireTerminators = new char[2] { '"', '”' };

	private static char[] nonTerminators = new char[6] { ')', '_', ' ', '\'', '’', '§' };

	private static char[] terminators = new char[3] { '?', '!', '.' };

	private static char[] acceptableTerminators = new char[2] { ':', ',' };

	private static char[] specialTerminators = new char[2] { '?', '!' };

	private static char[] punctuation = new char[6] { '?', '!', '.', ',', ';', ':' };

	private static StringBuilder sb = new StringBuilder();

	public const string defaultColor = "#FFE473";

	private static readonly string[] Tens = new string[10] { "zero", "ten", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety" };

	private static readonly string[] Units = new string[20]
	{
		"zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
		"ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"
	};

	private static string OpenColor(string hexColor)
	{
		return $"[color={hexColor}]";
	}

	public static bool StartsWithVowel(string s)
	{
		if (s.Length > 0 && "aeiou".IndexOf(s.Substring(0, 1).ToLower()) > -1)
		{
			return true;
		}
		return false;
	}

	public static string UppercaseFirstCharacterHandlingQuotesAndOtherMarkers(string s)
	{
		if (string.IsNullOrEmpty(s))
		{
			return string.Empty;
		}
		char[] array = s.ToCharArray();
		bool flag = true;
		for (int i = 0; i < array.Length; i++)
		{
			char c = array[i];
			if (c != '"' && c != '\'' && c != '_' && c != '‘' && c != '’' && c != '“' && c != '”' && c != '§' && c != ' ')
			{
				if (flag)
				{
					array[i] = char.ToUpperInvariant(c);
				}
				flag = c.isTerminator();
				if (flag && i < array.Length - 1 && (array[i] == '!' || array[i] == '?') && (array[i + 1] == '"' || array[i + 1] == '\'' || array[i + 1] == '’' || array[i + 1] == '”'))
				{
					flag = false;
				}
				if (i >= 2 && c == '.' && array[i - 1] == '.' && array[i - 2] == '.')
				{
					flag = false;
				}
			}
		}
		return new string(array);
	}

	public static string ProcessAndStyleText(string label, bool terminatingPunctuation = true, string hexColor = "#FFE473")
	{
		label = ProcessText(label, terminatingPunctuation, stripSquareBrackets: true);
		label = ParseStyling(label, colourise: true, hexColor);
		return label;
	}

	public static string ParseStyling(string dialogueText, bool colourise = true, string hexColor = "#FFE473")
	{
		sb.Clear();
		bool flag = false;
		bool flag2 = false;
		bool flag3 = false;
		for (int i = 0; i < dialogueText.Length; i++)
		{
			if (dialogueText[i] == '_')
			{
				flag = !flag;
				sb.Append(flag ? "[i]" : "[/i]");
				continue;
			}
			if (dialogueText[i] == '>')
			{
				flag2 = !flag2;
				sb.Append(flag2 ? "[b]" : "[/b]");
				continue;
			}
			if (dialogueText[i] == '§')
			{
				if (colourise)
				{
					flag3 = !flag3;
					sb.Append(flag3 ? OpenColor(hexColor) : "[/color]");
				}
				continue;
			}
			if (dialogueText[i] == ' ')
			{
				if (flag3)
				{
					sb.Append("[/color]");
				}
				if (flag)
				{
					sb.Append("[/i]");
				}
				if (flag2)
				{
					sb.Append("[/b]");
				}
			}
			sb.Append(dialogueText[i]);
			if (dialogueText[i] == ' ' && i != dialogueText.Length - 1)
			{
				if (flag3)
				{
					sb.Append(OpenColor(hexColor));
				}
				if (flag)
				{
					sb.Append("[i]");
				}
				if (flag2)
				{
					sb.Append("[b]");
				}
			}
		}
		if (flag3)
		{
			sb.Append("[/color]");
		}
		if (flag)
		{
			sb.Append("[/i]");
		}
		if (flag2)
		{
			sb.Append("[/b]");
		}
		return sb.ToString();
	}

	public static string ExhaustifyDialogueText(string dialogueLine, bool veryTired = false)
	{
		List<string> list = new List<string> { "i", "you", "i'm", "but", "if" };
		List<char> list2 = new List<char> { '.', ',', ';', ':', ')', '-', '\'', '"', '>' };
		bool flag = false;
		int num = GD.RandRange(2, 5);
		StringBuilder stringBuilder = new StringBuilder();
		string[] array = dialogueLine.Split(' ');
		foreach (string text in array)
		{
			if (!flag && list.Contains(text.ToLower()))
			{
				stringBuilder.Append(text + "... ");
				flag = true;
			}
			num--;
			stringBuilder.Append(text);
			if (text.Length > 0)
			{
				char item = text[text.Length - 1];
				if (num <= 0 && !list2.Contains(item))
				{
					stringBuilder.Append("...");
					num = GD.RandRange(2, 5) + ((!veryTired) ? 2 : 0);
				}
				stringBuilder.Append(" ");
			}
		}
		return stringBuilder.ToString();
	}

	public static string SentenceCaseWithoutArticles(string s)
	{
		if (s.IndexOf("a ", StringComparison.OrdinalIgnoreCase) == 0)
		{
			s = s.Remove(0, 2);
		}
		if (s.IndexOf("the ", StringComparison.OrdinalIgnoreCase) == 0)
		{
			s = s.Remove(0, 4);
		}
		return UppercaseFirstCharacterHandlingQuotesAndOtherMarkers(s);
	}

	public static string ResolveArticleAlteringMarkers(string s)
	{
		bool flag = false;
		StringBuilder stringBuilder = new StringBuilder(s.Length);
		for (int i = 0; i < s.Length - 1; i++)
		{
			if (!flag && (s[i] == 'n' || s[i] == 'N') && s[i + 1] == ' ')
			{
				if (i < 2 || s[i - 1] != ' ' || (s[i - 2] != 'a' && s[i - 2] != 'A'))
				{
					if (i >= 1)
					{
						stringBuilder.Append(s[i - 1]);
					}
					i += 2;
				}
			}
			else
			{
				flag = char.IsLetter(s[i]);
				if (i > 0)
				{
					stringBuilder.Append(s[i - 1]);
				}
			}
		}
		if (s.Length >= 2)
		{
			stringBuilder.Append(s[s.Length - 2]);
		}
		if (s.Length >= 1)
		{
			stringBuilder.Append(s[s.Length - 1]);
		}
		return stringBuilder.ToString();
	}

	public static string CorrectSpacingErrors(string s)
	{
		if (string.IsNullOrEmpty(s))
		{
			return string.Empty;
		}
		StringBuilder stringBuilder = new StringBuilder(s.Length * 2);
		bool flag = false;
		bool flag2 = false;
		bool flag3 = false;
		bool flag4 = false;
		char c = '^';
		int num = 0;
		bool flag5 = false;
		for (int i = 0; i < s.Length; i++)
		{
			char c2 = s[i];
			if (c2 == '\'')
			{
				if ((c == '^' || c == ' ' || (flag && !flag3)) && (!flag3 | flag4))
				{
					c2 = '‘';
					flag3 = true;
					flag4 = false;
				}
				else
				{
					if (flag3 && (c.isPunctuation() || (c == ' ' && stringBuilder[stringBuilder.Length - 2].isPunctuation())))
					{
						flag4 = true;
					}
					if (flag3 & flag)
					{
						flag3 = false;
					}
					c2 = '’';
				}
			}
			if (c2 == '"')
			{
				if (flag2)
				{
					flag2 = false;
					c2 = '”';
				}
				else
				{
					c2 = '“';
					flag2 = true;
				}
			}
			if ((c == '“' || c == '‘') && c2 == ' ')
			{
				continue;
			}
			if (flag5 && !c2.isPunctuation() && c2 != ' ')
			{
				flag5 = false;
				stringBuilder.Append('_');
			}
			if (c2 == '_')
			{
				flag5 = true;
				continue;
			}
			if (c2.isPunctuation() || c2.isQuoteMark() || c2 == ')')
			{
				if (c2 != '’')
				{
					flag = true;
					if (c == '’')
					{
						flag3 = false;
					}
				}
				if (c == ' ' && stringBuilder.Length > 0 && (!c2.isQuoteMark() | flag4))
				{
					stringBuilder.Remove(stringBuilder.Length - 1, 1);
					c = stringBuilder[stringBuilder.Length - 1];
					if (!flag5 && c == '_' && stringBuilder.Length > 0)
					{
						flag5 = true;
						stringBuilder.Remove(stringBuilder.Length - 1, 1);
						c = stringBuilder[stringBuilder.Length - 1];
					}
					if (flag4)
					{
						flag3 = false;
						if (c.isPunctuation())
						{
							flag = true;
						}
					}
				}
			}
			else
			{
				if (flag && c2 != ' ' && c2 != '_')
				{
					stringBuilder.Append(' ');
				}
				flag = false;
			}
			if ((c2 == c && (c2 == ' ' || c2 == ',' || c2 == ':' || c2 == ';' || c2 == ')' || c2 == '(')) || (stringBuilder.Length == 0 && (c2 == ' ' || c2 == ',' || c2 == ':' || c2 == ';' || c2 == ')')))
			{
				continue;
			}
			bool flag6 = false;
			if (c2.isTerminator())
			{
				if (c == '.')
				{
					num++;
					if ((i != s.Length - 1 && (s[i + 1] == '.' || s[i + 1] == '!' || s[i + 1] == '?')) || num < 3)
					{
						continue;
					}
					stringBuilder.Append('.');
					flag6 = true;
				}
				else
				{
					num = 1;
				}
			}
			if (!flag6 && c != c2 && c.isPunctuation() && c2.isPunctuation() && (!c.isSpecialTerminator() || !c2.isSpecialTerminator()))
			{
				if (c.isTerminator() == c2.isTerminator() || num > 1)
				{
					continue;
				}
				num = 0;
				stringBuilder.Remove(stringBuilder.Length - 1, 1);
				c = ((stringBuilder.Length < 2) ? '^' : stringBuilder[stringBuilder.Length - 1]);
			}
			if (flag5 && c2 == ' ')
			{
				flag5 = false;
				stringBuilder.Append('_');
			}
			stringBuilder.Append(c2);
			if (flag3 && c == '’')
			{
				if (c2 != ' ' && !flag)
				{
					flag4 = false;
				}
				else if (c2 == ' ')
				{
					flag4 = true;
				}
			}
			c = c2;
		}
		if (flag5)
		{
			stringBuilder.Append('_');
		}
		return stringBuilder.ToString().Trim();
	}

	public static bool isPunctuation(this char thisChar)
	{
		return punctuation.Contains(thisChar);
	}

	public static bool isTerminator(this char thisChar)
	{
		return terminators.Contains(thisChar);
	}

	public static bool isSpecialTerminator(this char thisChar)
	{
		return specialTerminators.Contains(thisChar);
	}

	public static bool isQuoteMark(this char thisChar)
	{
		if (thisChar != '”' && thisChar != '’' && thisChar != '\'')
		{
			return thisChar == '"';
		}
		return true;
	}

	public static string Possessive(this string txt)
	{
		if (!string.IsNullOrEmpty(txt))
		{
			if (txt[txt.Length - 1] == 's')
			{
				return txt + "'";
			}
			return txt + "'s";
		}
		return "";
	}

	public static string ProcessText(string text, bool terminatingPunctuation = true, bool stripSquareBrackets = false)
	{
		if (string.IsNullOrEmpty(text))
		{
			return string.Empty;
		}
		string s = text;
		if (stripSquareBrackets)
		{
			s = StripSquareBrackets(s).Trim();
		}
		s = CorrectSpacingErrors(s);
		s = ResolveArticleAlteringMarkers(s);
		s = UppercaseFirstCharacterHandlingQuotesAndOtherMarkers(s);
		return EnforceTerminatingPunctuation(s, terminatingPunctuation);
	}

	public static string StripSquareBrackets(string s)
	{
		StringBuilder stringBuilder = new StringBuilder(s.Length);
		bool flag = false;
		foreach (char c in s)
		{
			switch (c)
			{
			case '[':
				flag = true;
				break;
			case ']':
				flag = false;
				continue;
			}
			if (!flag)
			{
				stringBuilder.Append(c);
			}
		}
		return stringBuilder.ToString();
	}

	public static string AppendEllipsis(string text)
	{
		text = text.Trim();
		char c = text[text.Length - 1];
		if (c == '_')
		{
			return AppendEllipsis(text.Substring(0, text.Length - 1)) + "_";
		}
		if (text.Length == 0)
		{
			return text;
		}
		if (!c.isTerminator())
		{
			if (!c.isPunctuation())
			{
				return text + "...";
			}
			return text.Substring(0, text.Length - 1) + "...";
		}
		if (c.isTerminator() && text[text.Length - 2].isTerminator())
		{
			return text;
		}
		StringBuilder stringBuilder = new StringBuilder();
		char value = c;
		stringBuilder.Append(text.Substring(0, text.Length - 1));
		stringBuilder.Append("..");
		stringBuilder.Append(value);
		return stringBuilder.ToString();
	}

	public static string EnforceTerminatingPunctuation(string s, bool requireTerminatingPunctuation)
	{
		if (string.IsNullOrEmpty(s))
		{
			return string.Empty;
		}
		StringBuilder stringBuilder = new StringBuilder(s.Length + 1);
		int num;
		for (num = s.Length - 1; num >= 0; num--)
		{
			if (nonTerminatorsWhichThenRequireTerminators.Contains(s[num]))
			{
				requireTerminatingPunctuation = true;
			}
			else if (!nonTerminators.Contains(s[num]))
			{
				break;
			}
		}
		if (num < 0)
		{
			return s;
		}
		if (requireTerminatingPunctuation)
		{
			if (terminators.Contains(s[num]) || acceptableTerminators.Contains(s[num]))
			{
				return s;
			}
			stringBuilder.Append(s.Substring(0, num + 1));
			stringBuilder.Append('.');
		}
		else
		{
			if (s[num] != '.')
			{
				return s;
			}
			if (num >= 3 && s[num - 1] == '.' && s[num - 2] == '.')
			{
				return s;
			}
			stringBuilder.Append(s.Substring(0, num));
		}
		if (num < s.Length - 1)
		{
			stringBuilder.Append(s.Substring(num + 1));
		}
		return stringBuilder.ToString();
	}

	public static string NumberAsWords(int number, bool withLeadingConjunction = false)
	{
		StringBuilder stringBuilder = new StringBuilder();
		if (number > 0)
		{
			if (withLeadingConjunction)
			{
				if (number < 100)
				{
					stringBuilder.Append(" and ");
				}
				else
				{
					stringBuilder.Append(", ");
				}
			}
			if (number >= 1000000)
			{
				stringBuilder.Append(NumberAsWords((int)Mathf.Floor(number / 1000000)));
				stringBuilder.Append(" million");
				if (number % 1000 > 0)
				{
					stringBuilder.Append(NumberAsWords(number % 1000000, withLeadingConjunction: true));
				}
			}
			else if (number >= 1000)
			{
				stringBuilder.Append(NumberAsWords((int)Mathf.Floor(number / 1000)));
				stringBuilder.Append(" thousand");
				if (number % 1000 > 0)
				{
					stringBuilder.Append(NumberAsWords(number % 1000, withLeadingConjunction: true));
				}
			}
			else if (number >= 100)
			{
				stringBuilder.Append(NumberAsWords((int)Mathf.Floor(number / 100)));
				stringBuilder.Append(" hundred");
				if (number % 100 > 0)
				{
					stringBuilder.Append(NumberAsWords(number % 100, withLeadingConjunction: true));
				}
			}
			else
			{
				if (number >= 20)
				{
					stringBuilder.Append(Tens[Mathf.FloorToInt(number / 10)]);
					if (number % 10 > 0)
					{
						stringBuilder.Append("-");
					}
				}
				if (number >= 10 && number < 20)
				{
					stringBuilder.Append(Units[number]);
				}
				else if (number % 10 > 0)
				{
					stringBuilder.Append(Units[number % 10]);
				}
			}
		}
		else if (!withLeadingConjunction)
		{
			stringBuilder.Append("zero");
		}
		return stringBuilder.ToString();
	}

	public static string StringWithInsertedNewline(string str, int maxSingleLineCharacters)
	{
		if (str == null)
		{
			return null;
		}
		int length = str.Length;
		if (length <= maxSingleLineCharacters)
		{
			return str;
		}
		int num = length / 2;
		for (int i = 0; i < length - 2; i++)
		{
			int num2 = i / 2;
			if (i % 2 == 1)
			{
				num2 = -num2 - 1;
			}
			int num3 = num + num2;
			if (str[num3] == ' ')
			{
				return str.Substring(0, num3) + "\n" + str.Substring(num3 + 1);
			}
		}
		return str;
	}
}
