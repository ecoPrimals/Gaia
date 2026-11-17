namespace Ink.Runtime;

public struct Pointer(Container container, int index)
{
	public Container container = container;

	public int index = index;

	public static Pointer Null = new Pointer
	{
		container = null,
		index = -1
	};

	public bool isNull => container == null;

	public Path path
	{
		get
		{
			if (isNull)
			{
				return null;
			}
			if (index >= 0)
			{
				return container.path.PathByAppendingComponent(new Path.Component(index));
			}
			return container.path;
		}
	}

	public Object Resolve()
	{
		if (index < 0)
		{
			return container;
		}
		if (container == null)
		{
			return null;
		}
		if (container.content.Count == 0)
		{
			return container;
		}
		if (index >= container.content.Count)
		{
			return null;
		}
		return container.content[index];
	}

	public override string ToString()
	{
		if (container == null)
		{
			return "Ink Pointer (null)";
		}
		return "Ink Pointer -> " + container.path.ToString() + " -- index " + index;
	}

	public static Pointer StartOf(Container container)
	{
		return new Pointer
		{
			container = container,
			index = 0
		};
	}
}
