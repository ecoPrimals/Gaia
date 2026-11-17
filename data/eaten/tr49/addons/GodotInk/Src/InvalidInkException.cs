using System;

namespace GodotInk;

public class InvalidInkException : Exception
{
	public InvalidInkException()
	{
	}

	public InvalidInkException(string message)
		: base(message)
	{
	}
}
