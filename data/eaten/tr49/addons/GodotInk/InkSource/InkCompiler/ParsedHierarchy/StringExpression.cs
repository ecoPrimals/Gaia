using System.Collections.Generic;
using System.Text;
using Ink.Runtime;

namespace Ink.Parsed;

public class StringExpression : Expression
{
	public bool isSingleString
	{
		get
		{
			if (base.content.Count != 1)
			{
				return false;
			}
			if (!(base.content[0] is Text))
			{
				return false;
			}
			return true;
		}
	}

	public StringExpression(List<Object> content)
	{
		AddContent(content);
	}

	public override void GenerateIntoContainer(Container container)
	{
		container.AddContent(ControlCommand.BeginString());
		foreach (Object item in base.content)
		{
			container.AddContent(item.runtimeObject);
		}
		container.AddContent(ControlCommand.EndString());
	}

	public override string ToString()
	{
		StringBuilder stringBuilder = new StringBuilder();
		foreach (Object item in base.content)
		{
			stringBuilder.Append(item.ToString());
		}
		return stringBuilder.ToString();
	}

	public override bool Equals(object obj)
	{
		StringExpression stringExpression = obj as StringExpression;
		if (stringExpression == null)
		{
			return false;
		}
		if (!isSingleString || !stringExpression.isSingleString)
		{
			return false;
		}
		string text = ToString();
		string value = stringExpression.ToString();
		return text.Equals(value);
	}

	public override int GetHashCode()
	{
		return ToString().GetHashCode();
	}
}
