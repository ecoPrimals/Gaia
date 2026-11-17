using System.Collections.Generic;

namespace Ink;

public class CharacterSet : HashSet<char>
{
	public static CharacterSet FromRange(char start, char end)
	{
		return new CharacterSet().AddRange(start, end);
	}

	public CharacterSet()
	{
	}

	public CharacterSet(string str)
	{
		AddCharacters(str);
	}

	public CharacterSet(CharacterSet charSetToCopy)
	{
		AddCharacters(charSetToCopy);
	}

	public CharacterSet AddRange(char start, char end)
	{
		for (char c = start; c <= end; c = (char)(c + 1))
		{
			Add(c);
		}
		return this;
	}

	public CharacterSet AddCharacters(IEnumerable<char> chars)
	{
		foreach (char @char in chars)
		{
			Add(@char);
		}
		return this;
	}

	public CharacterSet AddCharacters(string chars)
	{
		foreach (char item in chars)
		{
			Add(item);
		}
		return this;
	}
}
