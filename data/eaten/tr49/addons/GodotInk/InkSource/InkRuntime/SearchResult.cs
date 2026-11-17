namespace Ink.Runtime;

public struct SearchResult
{
	public Object obj;

	public bool approximate;

	public Object correctObj
	{
		get
		{
			if (!approximate)
			{
				return obj;
			}
			return null;
		}
	}

	public Container container => obj as Container;
}
