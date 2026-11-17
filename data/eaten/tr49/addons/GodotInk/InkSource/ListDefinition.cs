using System.Collections.Generic;
using Ink.Runtime;

namespace Ink.Parsed;

public class ListDefinition : Object
{
	public Identifier identifier;

	public List<ListElementDefinition> itemDefinitions;

	public VariableAssignment variableAssignment;

	private Dictionary<string, ListElementDefinition> _elementsByName;

	public Ink.Runtime.ListDefinition runtimeListDefinition
	{
		get
		{
			Dictionary<string, int> dictionary = new Dictionary<string, int>();
			foreach (ListElementDefinition itemDefinition in itemDefinitions)
			{
				if (!dictionary.ContainsKey(itemDefinition.name))
				{
					dictionary.Add(itemDefinition.name, itemDefinition.seriesValue);
					continue;
				}
				Error("List '" + identifier?.ToString() + "' contains dupicate items called '" + itemDefinition.name + "'");
			}
			return new Ink.Runtime.ListDefinition(identifier?.name, dictionary);
		}
	}

	public override string typeName => "List definition";

	public ListElementDefinition ItemNamed(string itemName)
	{
		if (_elementsByName == null)
		{
			_elementsByName = new Dictionary<string, ListElementDefinition>();
			foreach (ListElementDefinition itemDefinition in itemDefinitions)
			{
				_elementsByName[itemDefinition.name] = itemDefinition;
			}
		}
		if (_elementsByName.TryGetValue(itemName, out var value))
		{
			return value;
		}
		return null;
	}

	public ListDefinition(List<ListElementDefinition> elements)
	{
		itemDefinitions = elements;
		int num = 1;
		foreach (ListElementDefinition itemDefinition in itemDefinitions)
		{
			if (itemDefinition.explicitValue.HasValue)
			{
				num = itemDefinition.explicitValue.Value;
			}
			itemDefinition.seriesValue = num;
			num++;
		}
		AddContent(elements);
	}

	public override Ink.Runtime.Object GenerateRuntimeObject()
	{
		InkList inkList = new InkList();
		foreach (ListElementDefinition itemDefinition in itemDefinitions)
		{
			if (itemDefinition.inInitialList)
			{
				InkListItem key = new InkListItem(identifier?.name, itemDefinition.name);
				inkList[key] = itemDefinition.seriesValue;
			}
		}
		inkList.SetInitialOriginName(identifier?.name);
		return new ListValue(inkList);
	}

	public override void ResolveReferences(Story context)
	{
		base.ResolveReferences(context);
		context.CheckForNamingCollisions(this, identifier, Story.SymbolType.List);
	}
}
