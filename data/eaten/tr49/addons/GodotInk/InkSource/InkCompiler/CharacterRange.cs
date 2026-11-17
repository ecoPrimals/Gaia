using System.Collections.Generic;

namespace Ink;

public sealed class CharacterRange
{
	private char _start;

	private char _end;

	private ICollection<char> _excludes;

	private CharacterSet _correspondingCharSet = new CharacterSet();

	public char start => _start;

	public char end => _end;

	public static CharacterRange Define(char start, char end, IEnumerable<char> excludes = null)
	{
		return new CharacterRange(start, end, excludes);
	}

	public CharacterSet ToCharacterSet()
	{
		if (_correspondingCharSet.Count == 0)
		{
			for (char c = _start; c <= _end; c = (char)(c + 1))
			{
				if (!_excludes.Contains(c))
				{
					_correspondingCharSet.Add(c);
				}
			}
		}
		return _correspondingCharSet;
	}

	private CharacterRange(char start, char end, IEnumerable<char> excludes)
	{
		_start = start;
		_end = end;
		_excludes = ((excludes == null) ? new HashSet<char>() : new HashSet<char>(excludes));
	}
}
