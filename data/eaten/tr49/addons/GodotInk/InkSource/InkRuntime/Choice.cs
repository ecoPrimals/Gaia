using System.Collections.Generic;

namespace Ink.Runtime;

public class Choice : Object
{
	public string sourcePath;

	public Path targetPath;

	public int originalThreadIndex;

	public bool isInvisibleDefault;

	public List<string> tags;

	public string text { get; set; }

	public string pathStringOnChoice
	{
		get
		{
			return targetPath.ToString();
		}
		set
		{
			targetPath = new Path(value);
		}
	}

	public int index { get; set; }

	public CallStack.Thread threadAtGeneration { get; set; }

	public Choice Clone()
	{
		Choice choice = new Choice();
		choice.text = text;
		choice.sourcePath = sourcePath;
		choice.index = index;
		choice.targetPath = targetPath;
		choice.originalThreadIndex = originalThreadIndex;
		choice.isInvisibleDefault = isInvisibleDefault;
		if (threadAtGeneration != null)
		{
			choice.threadAtGeneration = threadAtGeneration.Copy();
		}
		return choice;
	}
}
