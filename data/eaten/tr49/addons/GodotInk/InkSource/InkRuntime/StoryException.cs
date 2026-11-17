using System;

namespace Ink.Runtime;

public class StoryException : Exception
{
	public bool useEndLineNumber;

	public StoryException()
	{
	}

	public StoryException(string message)
		: base(message)
	{
	}
}
