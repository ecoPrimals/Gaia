using System.Text;
using System.Text.RegularExpressions;

public static class CardLinks
{
	private static Regex cardCodeRegex = new Regex("^[a-zA-Z]{2}(-?)\\d{2}\\.?$");

	private static Regex initialsOrDateRegex = new Regex("^[a-zA-Z0-9]{2}\\.?$");

	public static string ConvertToBBCode(string text, bool allowTitleLinks)
	{
		if (string.IsNullOrEmpty(text))
		{
			return text;
		}
		StringBuilder stringBuilder = new StringBuilder();
		int num = 0;
		while (num < text.Length)
		{
			int num2 = text.IndexOf('(', num);
			if (num2 == -1)
			{
				stringBuilder.Append(text.Substring(num));
				break;
			}
			int num3 = text.IndexOf(')', num2);
			int num4 = text.IndexOf('(', num2 + 1);
			if (num4 > 0 && num4 < num3)
			{
				num2 = num4;
			}
			stringBuilder.Append(text.Substring(num, num2 - num));
			if (num3 == -1)
			{
				stringBuilder.Append(text.Substring(num2));
				break;
			}
			string text2 = text.Substring(num2 + 1, num3 - num2 - 1);
			if (cardCodeRegex.IsMatch(text2))
			{
				stringBuilder.Append(ClickableCode(text2));
			}
			else if (initialsOrDateRegex.IsMatch(text2))
			{
				stringBuilder.Append(ClickableCode(text2));
			}
			else if (text2.StartsWith("%") && (text2.EndsWith("%") || text2.EndsWith("%.")))
			{
				text2 = StoryController.DepunctuateCode(text2);
				string value = "Book Title";
				if (StoryController.instance != null)
				{
					value = StoryController.instance.GetTitleForBook(text2);
				}
				StringBuilder stringBuilder2 = stringBuilder;
				StringBuilder stringBuilder3 = stringBuilder2;
				StringBuilder.AppendInterpolatedStringHandler handler = new StringBuilder.AppendInterpolatedStringHandler(20, 2, stringBuilder2);
				handler.AppendLiteral("[url=TITLE:");
				handler.AppendFormatted(text2);
				handler.AppendLiteral("]\"");
				handler.AppendFormatted(value);
				handler.AppendLiteral("\"[/url]");
				stringBuilder3.Append(ref handler);
			}
			else
			{
				StringBuilder stringBuilder2 = stringBuilder;
				StringBuilder stringBuilder4 = stringBuilder2;
				StringBuilder.AppendInterpolatedStringHandler handler = new StringBuilder.AppendInterpolatedStringHandler(2, 1, stringBuilder2);
				handler.AppendLiteral("(");
				handler.AppendFormatted(text2);
				handler.AppendLiteral(")");
				stringBuilder4.Append(ref handler);
			}
			num = num3 + 1;
		}
		return stringBuilder.ToString();
	}

	public static string ClickableCode(string linkText)
	{
		linkText = StoryController.DepunctuateCode(linkText);
		if (string.IsNullOrWhiteSpace(linkText))
		{
			return "";
		}
		string value = StoryController.HyphenateCode(linkText);
		return $"[url={linkText}]{value}[/url]";
	}
}
