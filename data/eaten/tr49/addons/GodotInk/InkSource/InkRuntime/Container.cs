using System;
using System.Collections.Generic;
using System.Text;

namespace Ink.Runtime;

public class Container : Object, INamedContent
{
	[Flags]
	public enum CountFlags
	{
		Visits = 1,
		Turns = 2,
		CountStartOnly = 4
	}

	private List<Object> _content;

	private Path _pathToFirstLeafContent;

	public string name { get; set; }

	public List<Object> content
	{
		get
		{
			return _content;
		}
		set
		{
			AddContent(value);
		}
	}

	public Dictionary<string, INamedContent> namedContent { get; set; }

	public Dictionary<string, Object> namedOnlyContent
	{
		get
		{
			Dictionary<string, Object> dictionary = new Dictionary<string, Object>();
			foreach (KeyValuePair<string, INamedContent> item in this.namedContent)
			{
				dictionary[item.Key] = (Object)item.Value;
			}
			foreach (Object item2 in content)
			{
				if (item2 is INamedContent { hasValidName: not false } namedContent)
				{
					dictionary.Remove(namedContent.name);
				}
			}
			if (dictionary.Count == 0)
			{
				dictionary = null;
			}
			return dictionary;
		}
		set
		{
			Dictionary<string, Object> dictionary = namedOnlyContent;
			if (dictionary != null)
			{
				foreach (KeyValuePair<string, Object> item in dictionary)
				{
					namedContent.Remove(item.Key);
				}
			}
			if (value == null)
			{
				return;
			}
			foreach (KeyValuePair<string, Object> item2 in value)
			{
				if (item2.Value is INamedContent namedContentObj)
				{
					AddToNamedContentOnly(namedContentObj);
				}
			}
		}
	}

	public bool visitsShouldBeCounted { get; set; }

	public bool turnIndexShouldBeCounted { get; set; }

	public bool countingAtStartOnly { get; set; }

	public int countFlags
	{
		get
		{
			CountFlags countFlags = (CountFlags)0;
			if (visitsShouldBeCounted)
			{
				countFlags |= CountFlags.Visits;
			}
			if (turnIndexShouldBeCounted)
			{
				countFlags |= CountFlags.Turns;
			}
			if (countingAtStartOnly)
			{
				countFlags |= CountFlags.CountStartOnly;
			}
			if (countFlags == CountFlags.CountStartOnly)
			{
				countFlags = (CountFlags)0;
			}
			return (int)countFlags;
		}
		set
		{
			if ((value & 1) > 0)
			{
				visitsShouldBeCounted = true;
			}
			if ((value & 2) > 0)
			{
				turnIndexShouldBeCounted = true;
			}
			if ((value & 4) > 0)
			{
				countingAtStartOnly = true;
			}
		}
	}

	public bool hasValidName
	{
		get
		{
			if (name != null)
			{
				return name.Length > 0;
			}
			return false;
		}
	}

	public Path pathToFirstLeafContent
	{
		get
		{
			if (_pathToFirstLeafContent == null)
			{
				_pathToFirstLeafContent = base.path.PathByAppendingPath(internalPathToFirstLeafContent);
			}
			return _pathToFirstLeafContent;
		}
	}

	private Path internalPathToFirstLeafContent
	{
		get
		{
			List<Path.Component> list = new List<Path.Component>();
			Container container = this;
			while (container != null)
			{
				if (container.content.Count > 0)
				{
					list.Add(new Path.Component(0));
					container = container.content[0] as Container;
				}
			}
			return new Path(list);
		}
	}

	public Container()
	{
		_content = new List<Object>();
		namedContent = new Dictionary<string, INamedContent>();
	}

	public void AddContent(Object contentObj)
	{
		content.Add(contentObj);
		if ((bool)contentObj.parent)
		{
			throw new Exception("content is already in " + contentObj.parent);
		}
		contentObj.parent = this;
		TryAddNamedContent(contentObj);
	}

	public void AddContent(IList<Object> contentList)
	{
		foreach (Object content in contentList)
		{
			AddContent(content);
		}
	}

	public void InsertContent(Object contentObj, int index)
	{
		content.Insert(index, contentObj);
		if ((bool)contentObj.parent)
		{
			throw new Exception("content is already in " + contentObj.parent);
		}
		contentObj.parent = this;
		TryAddNamedContent(contentObj);
	}

	public void TryAddNamedContent(Object contentObj)
	{
		if (contentObj is INamedContent { hasValidName: not false } namedContent)
		{
			AddToNamedContentOnly(namedContent);
		}
	}

	public void AddToNamedContentOnly(INamedContent namedContentObj)
	{
		((Object)namedContentObj).parent = this;
		namedContent[namedContentObj.name] = namedContentObj;
	}

	public void AddContentsOfContainer(Container otherContainer)
	{
		content.AddRange(otherContainer.content);
		foreach (Object item in otherContainer.content)
		{
			item.parent = this;
			TryAddNamedContent(item);
		}
	}

	protected Object ContentWithPathComponent(Path.Component component)
	{
		if (component.isIndex)
		{
			if (component.index >= 0 && component.index < content.Count)
			{
				return content[component.index];
			}
			return null;
		}
		if (component.isParent)
		{
			return base.parent;
		}
		INamedContent value = null;
		if (namedContent.TryGetValue(component.name, out value))
		{
			return (Object)value;
		}
		return null;
	}

	public SearchResult ContentAtPath(Path path, int partialPathStart = 0, int partialPathLength = -1)
	{
		if (partialPathLength == -1)
		{
			partialPathLength = path.length;
		}
		SearchResult result = new SearchResult
		{
			approximate = false
		};
		Container container = this;
		Object obj = this;
		for (int i = partialPathStart; i < partialPathLength; i++)
		{
			Path.Component component = path.GetComponent(i);
			if (container == null)
			{
				result.approximate = true;
				break;
			}
			Object obj2 = container.ContentWithPathComponent(component);
			if (obj2 == null)
			{
				result.approximate = true;
				break;
			}
			Container container2 = obj2 as Container;
			if (i < partialPathLength - 1 && container2 == null)
			{
				result.approximate = true;
				break;
			}
			obj = obj2;
			container = container2;
		}
		result.obj = obj;
		return result;
	}

	public void BuildStringOfHierarchy(StringBuilder sb, int indentation, Object pointedObj)
	{
		Action action = delegate
		{
			for (int i = 0; i < 4 * indentation; i++)
			{
				sb.Append(" ");
			}
		};
		action();
		sb.Append("[");
		if (hasValidName)
		{
			sb.AppendFormat(" ({0})", name);
		}
		if (this == pointedObj)
		{
			sb.Append("  <---");
		}
		sb.AppendLine();
		indentation++;
		for (int num = 0; num < content.Count; num++)
		{
			Object obj = content[num];
			if (obj is Container)
			{
				((Container)obj).BuildStringOfHierarchy(sb, indentation, pointedObj);
			}
			else
			{
				action();
				if (obj is StringValue)
				{
					sb.Append("\"");
					sb.Append(obj.ToString().Replace("\n", "\\n"));
					sb.Append("\"");
				}
				else
				{
					sb.Append(obj.ToString());
				}
			}
			if (num != content.Count - 1)
			{
				sb.Append(",");
			}
			if (!(obj is Container) && obj == pointedObj)
			{
				sb.Append("  <---");
			}
			sb.AppendLine();
		}
		Dictionary<string, INamedContent> dictionary = new Dictionary<string, INamedContent>();
		foreach (KeyValuePair<string, INamedContent> item in namedContent)
		{
			if (!content.Contains((Object)item.Value))
			{
				dictionary.Add(item.Key, item.Value);
			}
		}
		if (dictionary.Count > 0)
		{
			action();
			sb.AppendLine("-- named: --");
			foreach (KeyValuePair<string, INamedContent> item2 in dictionary)
			{
				((Container)item2.Value).BuildStringOfHierarchy(sb, indentation, pointedObj);
				sb.AppendLine();
			}
		}
		indentation--;
		action();
		sb.Append("]");
	}

	public virtual string BuildStringOfHierarchy()
	{
		StringBuilder stringBuilder = new StringBuilder();
		BuildStringOfHierarchy(stringBuilder, 0, null);
		return stringBuilder.ToString();
	}
}
