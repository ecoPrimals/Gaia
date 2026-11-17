using Ink.Runtime;

namespace Ink.Parsed;

public class AuthorWarning : Object
{
	public string warningMessage;

	public AuthorWarning(string message)
	{
		warningMessage = message;
	}

	public override Ink.Runtime.Object GenerateRuntimeObject()
	{
		Warning(warningMessage);
		return null;
	}
}
