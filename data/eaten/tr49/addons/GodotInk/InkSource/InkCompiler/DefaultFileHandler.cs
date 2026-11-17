using System.IO;

namespace Ink;

public class DefaultFileHandler : IFileHandler
{
	public string ResolveInkFilename(string includeName)
	{
		return Path.Combine(Directory.GetCurrentDirectory(), includeName);
	}

	public string LoadInkFileContents(string fullFilename)
	{
		return File.ReadAllText(fullFilename);
	}
}
