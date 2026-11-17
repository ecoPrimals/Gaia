using System.Collections.Generic;

namespace Ink;

public class CommentEliminator(string input) : StringParser(input)
{
	private CharacterSet _commentOrNewlineStartCharacter = new CharacterSet("/\r\n");

	private CharacterSet _commentBlockEndCharacter = new CharacterSet("*");

	private CharacterSet _newlineCharacters = new CharacterSet("\n\r");

	public string Process()
	{
		List<string> list = Interleave<string>(Optional(CommentsAndNewlines), Optional(MainInk));
		if (list != null)
		{
			return string.Join("", list.ToArray());
		}
		return null;
	}

	private string MainInk()
	{
		return ParseUntil(CommentsAndNewlines, _commentOrNewlineStartCharacter);
	}

	private string CommentsAndNewlines()
	{
		List<string> list = Interleave<string>(Optional(base.ParseNewline), Optional(ParseSingleComment));
		if (list != null)
		{
			return string.Join("", list.ToArray());
		}
		return null;
	}

	private string ParseSingleComment()
	{
		return (string)OneOf(EndOfLineComment, BlockComment);
	}

	private string EndOfLineComment()
	{
		if (ParseString("//") == null)
		{
			return null;
		}
		ParseUntilCharactersFromCharSet(_newlineCharacters);
		return "";
	}

	private string BlockComment()
	{
		if (ParseString("/*") == null)
		{
			return null;
		}
		int num = base.lineIndex;
		string text = ParseUntil(String("*/"), _commentBlockEndCharacter);
		if (!base.endOfInput)
		{
			ParseString("*/");
		}
		if (text != null)
		{
			return new string('\n', base.lineIndex - num);
		}
		return null;
	}
}
