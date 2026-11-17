using System;

namespace Ink.Runtime;

public class DebugMetadata
{
	public int startLineNumber;

	public int endLineNumber;

	public int startCharacterNumber;

	public int endCharacterNumber;

	public string fileName;

	public string sourceName;

	public DebugMetadata Merge(DebugMetadata dm)
	{
		DebugMetadata debugMetadata = new DebugMetadata();
		debugMetadata.fileName = fileName;
		debugMetadata.sourceName = sourceName;
		if (startLineNumber < dm.startLineNumber)
		{
			debugMetadata.startLineNumber = startLineNumber;
			debugMetadata.startCharacterNumber = startCharacterNumber;
		}
		else if (startLineNumber > dm.startLineNumber)
		{
			debugMetadata.startLineNumber = dm.startLineNumber;
			debugMetadata.startCharacterNumber = dm.startCharacterNumber;
		}
		else
		{
			debugMetadata.startLineNumber = startLineNumber;
			debugMetadata.startCharacterNumber = Math.Min(startCharacterNumber, dm.startCharacterNumber);
		}
		if (endLineNumber > dm.endLineNumber)
		{
			debugMetadata.endLineNumber = endLineNumber;
			debugMetadata.endCharacterNumber = endCharacterNumber;
		}
		else if (endLineNumber < dm.endLineNumber)
		{
			debugMetadata.endLineNumber = dm.endLineNumber;
			debugMetadata.endCharacterNumber = dm.endCharacterNumber;
		}
		else
		{
			debugMetadata.endLineNumber = endLineNumber;
			debugMetadata.endCharacterNumber = Math.Max(endCharacterNumber, dm.endCharacterNumber);
		}
		return debugMetadata;
	}

	public override string ToString()
	{
		if (fileName != null)
		{
			return $"line {startLineNumber} of {fileName}";
		}
		return "line " + startLineNumber;
	}
}
