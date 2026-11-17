using System;
using System.Collections.Generic;

namespace Ink.Runtime;

public class Object
{
	private DebugMetadata _debugMetadata;

	private Path _path;

	public Object parent { get; set; }

	public DebugMetadata debugMetadata
	{
		get
		{
			if (_debugMetadata == null && (bool)parent)
			{
				return parent.debugMetadata;
			}
			return _debugMetadata;
		}
		set
		{
			_debugMetadata = value;
		}
	}

	public DebugMetadata ownDebugMetadata => _debugMetadata;

	public Path path
	{
		get
		{
			if (_path == null)
			{
				if (parent == null)
				{
					_path = new Path();
				}
				else
				{
					Stack<Path.Component> stack = new Stack<Path.Component>();
					Object obj = this;
					Container container = obj.parent as Container;
					while ((bool)container)
					{
						if (obj is INamedContent { hasValidName: not false } namedContent)
						{
							stack.Push(new Path.Component(namedContent.name));
						}
						else
						{
							stack.Push(new Path.Component(container.content.IndexOf(obj)));
						}
						obj = container;
						container = container.parent as Container;
					}
					_path = new Path(stack);
				}
			}
			return _path;
		}
	}

	public Container rootContentContainer
	{
		get
		{
			Object obj = this;
			while ((bool)obj.parent)
			{
				obj = obj.parent;
			}
			return obj as Container;
		}
	}

	public int? DebugLineNumberOfPath(Path path)
	{
		if (path == null)
		{
			return null;
		}
		Container container = rootContentContainer;
		if ((bool)container)
		{
			Object obj = container.ContentAtPath(path).obj;
			if ((bool)obj)
			{
				DebugMetadata debugMetadata = obj.debugMetadata;
				if (debugMetadata != null)
				{
					return debugMetadata.startLineNumber;
				}
			}
		}
		return null;
	}

	public SearchResult ResolvePath(Path path)
	{
		if (path.isRelative)
		{
			Container container = this as Container;
			if (!container)
			{
				container = parent as Container;
				path = path.tail;
			}
			return container.ContentAtPath(path);
		}
		return rootContentContainer.ContentAtPath(path);
	}

	public Path ConvertPathToRelative(Path globalPath)
	{
		Path path = this.path;
		int num = Math.Min(globalPath.length, path.length);
		int num2 = -1;
		for (int i = 0; i < num; i++)
		{
			Path.Component component = path.GetComponent(i);
			Path.Component component2 = globalPath.GetComponent(i);
			if (!component.Equals(component2))
			{
				break;
			}
			num2 = i;
		}
		if (num2 == -1)
		{
			return globalPath;
		}
		int num3 = path.length - 1 - num2;
		List<Path.Component> list = new List<Path.Component>();
		for (int j = 0; j < num3; j++)
		{
			list.Add(Path.Component.ToParent());
		}
		for (int k = num2 + 1; k < globalPath.length; k++)
		{
			list.Add(globalPath.GetComponent(k));
		}
		return new Path(list, relative: true);
	}

	public string CompactPathString(Path otherPath)
	{
		string text = null;
		string text2 = null;
		if (otherPath.isRelative)
		{
			text2 = otherPath.componentsString;
			text = path.PathByAppendingPath(otherPath).componentsString;
		}
		else
		{
			text2 = ConvertPathToRelative(otherPath).componentsString;
			text = otherPath.componentsString;
		}
		if (text2.Length < text.Length)
		{
			return text2;
		}
		return text;
	}

	public virtual Object Copy()
	{
		throw new NotImplementedException(GetType().Name + " doesn't support copying");
	}

	public void SetChild<T>(ref T obj, T value) where T : Object
	{
		if ((bool)obj)
		{
			obj.parent = null;
		}
		obj = value;
		if ((bool)obj)
		{
			obj.parent = this;
		}
	}

	public static implicit operator bool(Object obj)
	{
		return (object)obj != null;
	}

	public static bool operator ==(Object a, Object b)
	{
		return (object)a == b;
	}

	public static bool operator !=(Object a, Object b)
	{
		return !(a == b);
	}

	public override bool Equals(object obj)
	{
		return obj == this;
	}

	public override int GetHashCode()
	{
		return base.GetHashCode();
	}
}
