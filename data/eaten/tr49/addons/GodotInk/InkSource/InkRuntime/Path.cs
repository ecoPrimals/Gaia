using System;
using System.Collections.Generic;
using System.Linq;

namespace Ink.Runtime;

public class Path : IEquatable<Path>
{
	public class Component : IEquatable<Component>
	{
		public int index { get; private set; }

		public string name { get; private set; }

		public bool isIndex => index >= 0;

		public bool isParent => name == parentId;

		public Component(int index)
		{
			this.index = index;
			name = null;
		}

		public Component(string name)
		{
			this.name = name;
			index = -1;
		}

		public static Component ToParent()
		{
			return new Component(parentId);
		}

		public override string ToString()
		{
			if (isIndex)
			{
				return index.ToString();
			}
			return name;
		}

		public override bool Equals(object obj)
		{
			return Equals(obj as Component);
		}

		public bool Equals(Component otherComp)
		{
			if (otherComp != null && otherComp.isIndex == isIndex)
			{
				if (isIndex)
				{
					return index == otherComp.index;
				}
				return name == otherComp.name;
			}
			return false;
		}

		public override int GetHashCode()
		{
			if (isIndex)
			{
				return index;
			}
			return name.GetHashCode();
		}
	}

	private static string parentId = "^";

	private string _componentsString;

	private List<Component> _components;

	public bool isRelative { get; private set; }

	public Component head
	{
		get
		{
			if (_components.Count > 0)
			{
				return _components.First();
			}
			return null;
		}
	}

	public Path tail
	{
		get
		{
			if (_components.Count >= 2)
			{
				return new Path(_components.GetRange(1, _components.Count - 1));
			}
			return self;
		}
	}

	public int length => _components.Count;

	public Component lastComponent
	{
		get
		{
			int num = _components.Count - 1;
			if (num >= 0)
			{
				return _components[num];
			}
			return null;
		}
	}

	public bool containsNamedComponent
	{
		get
		{
			foreach (Component component in _components)
			{
				if (!component.isIndex)
				{
					return true;
				}
			}
			return false;
		}
	}

	public static Path self => new Path
	{
		isRelative = true
	};

	public string componentsString
	{
		get
		{
			if (_componentsString == null)
			{
				_componentsString = StringExt.Join(".", _components);
				if (isRelative)
				{
					_componentsString = "." + _componentsString;
				}
			}
			return _componentsString;
		}
		private set
		{
			_components.Clear();
			_componentsString = value;
			if (string.IsNullOrEmpty(_componentsString))
			{
				return;
			}
			if (_componentsString[0] == '.')
			{
				isRelative = true;
				_componentsString = _componentsString.Substring(1);
			}
			else
			{
				isRelative = false;
			}
			string[] array = _componentsString.Split('.');
			foreach (string text in array)
			{
				if (int.TryParse(text, out var result))
				{
					_components.Add(new Component(result));
				}
				else
				{
					_components.Add(new Component(text));
				}
			}
		}
	}

	public Component GetComponent(int index)
	{
		return _components[index];
	}

	public Path()
	{
		_components = new List<Component>();
	}

	public Path(Component head, Path tail)
		: this()
	{
		_components.Add(head);
		_components.AddRange(tail._components);
	}

	public Path(IEnumerable<Component> components, bool relative = false)
		: this()
	{
		_components.AddRange(components);
		isRelative = relative;
	}

	public Path(string componentsString)
		: this()
	{
		this.componentsString = componentsString;
	}

	public Path PathByAppendingPath(Path pathToAppend)
	{
		Path path = new Path();
		int num = 0;
		for (int i = 0; i < pathToAppend._components.Count && pathToAppend._components[i].isParent; i++)
		{
			num++;
		}
		for (int j = 0; j < _components.Count - num; j++)
		{
			path._components.Add(_components[j]);
		}
		for (int k = num; k < pathToAppend._components.Count; k++)
		{
			path._components.Add(pathToAppend._components[k]);
		}
		return path;
	}

	public Path PathByAppendingComponent(Component c)
	{
		Path path = new Path();
		path._components.AddRange(_components);
		path._components.Add(c);
		return path;
	}

	public override string ToString()
	{
		return componentsString;
	}

	public override bool Equals(object obj)
	{
		return Equals(obj as Path);
	}

	public bool Equals(Path otherPath)
	{
		if (otherPath == null)
		{
			return false;
		}
		if (otherPath._components.Count != _components.Count)
		{
			return false;
		}
		if (otherPath.isRelative != isRelative)
		{
			return false;
		}
		return otherPath._components.SequenceEqual(_components);
	}

	public override int GetHashCode()
	{
		return ToString().GetHashCode();
	}
}
