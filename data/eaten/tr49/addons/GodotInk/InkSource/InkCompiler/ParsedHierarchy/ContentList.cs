using System.Collections.Generic;
using System.Text;
using Ink.Runtime;

namespace Ink.Parsed;

public class ContentList : Object
{
	public bool dontFlatten { get; set; }

	public Container runtimeContainer => (Container)base.runtimeObject;

	public ContentList(List<Object> objects)
	{
		if (objects != null)
		{
			AddContent(objects);
		}
	}

	public ContentList(params Object[] objects)
	{
		if (objects != null)
		{
			List<Object> listContent = new List<Object>(objects);
			AddContent(listContent);
		}
	}

	public ContentList()
	{
	}

	public void TrimTrailingWhitespace()
	{
		int num = base.content.Count - 1;
		while (num >= 0)
		{
			Text text = base.content[num] as Text;
			if (!(text == null))
			{
				text.text = text.text.TrimEnd(' ', '\t');
				if (text.text.Length == 0)
				{
					base.content.RemoveAt(num);
					num--;
					continue;
				}
				break;
			}
			break;
		}
	}

	public override Ink.Runtime.Object GenerateRuntimeObject()
	{
		Container container = new Container();
		if (base.content != null)
		{
			foreach (Object item in base.content)
			{
				Ink.Runtime.Object obj = item.runtimeObject;
				if ((bool)obj)
				{
					container.AddContent(obj);
				}
			}
		}
		if (dontFlatten)
		{
			base.story.DontFlattenContainer(container);
		}
		return container;
	}

	public override string ToString()
	{
		StringBuilder stringBuilder = new StringBuilder();
		stringBuilder.Append("ContentList(");
		stringBuilder.Append(string.Join(", ", base.content.ToStringsArray()));
		stringBuilder.Append(")");
		return stringBuilder.ToString();
	}
}
