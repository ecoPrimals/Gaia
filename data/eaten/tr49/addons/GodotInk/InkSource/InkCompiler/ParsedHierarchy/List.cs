using System.Collections.Generic;
using Ink.Runtime;

namespace Ink.Parsed;

public class List : Expression
{
	public List<Identifier> itemIdentifierList;

	public List(List<Identifier> itemIdentifierList)
	{
		this.itemIdentifierList = itemIdentifierList;
	}

	public override void GenerateIntoContainer(Container container)
	{
		InkList inkList = new InkList();
		if (itemIdentifierList != null)
		{
			foreach (Identifier itemIdentifier in itemIdentifierList)
			{
				string[] array = itemIdentifier?.name.Split('.');
				string text = null;
				string text2 = null;
				if (array.Length > 1)
				{
					text = array[0];
					text2 = array[1];
				}
				else
				{
					text2 = array[0];
				}
				ListElementDefinition listElementDefinition = base.story.ResolveListItem(text, text2, this);
				if (listElementDefinition == null)
				{
					if (text == null)
					{
						Error("Could not find list definition that contains item '" + itemIdentifier?.ToString() + "'");
					}
					else
					{
						Error("Could not find list item " + itemIdentifier);
					}
					continue;
				}
				if (text == null)
				{
					text = ((ListDefinition)listElementDefinition.parent).identifier?.name;
				}
				InkListItem key = new InkListItem(text, listElementDefinition.name);
				if (inkList.ContainsKey(key))
				{
					Warning("Duplicate of item '" + itemIdentifier?.ToString() + "' in list.");
				}
				else
				{
					inkList[key] = listElementDefinition.seriesValue;
				}
			}
		}
		container.AddContent(new ListValue(inkList));
	}
}
