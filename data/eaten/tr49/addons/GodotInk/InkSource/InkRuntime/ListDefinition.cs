using System.Collections.Generic;

namespace Ink.Runtime;

public class ListDefinition
{
	private Dictionary<InkListItem, int> _items;

	private string _name;

	private Dictionary<string, int> _itemNameToValues;

	public string name => _name;

	public Dictionary<InkListItem, int> items
	{
		get
		{
			if (_items == null)
			{
				_items = new Dictionary<InkListItem, int>();
				foreach (KeyValuePair<string, int> itemNameToValue in _itemNameToValues)
				{
					InkListItem key = new InkListItem(name, itemNameToValue.Key);
					_items[key] = itemNameToValue.Value;
				}
			}
			return _items;
		}
	}

	public int ValueForItem(InkListItem item)
	{
		if (_itemNameToValues.TryGetValue(item.itemName, out var value))
		{
			return value;
		}
		return 0;
	}

	public bool ContainsItem(InkListItem item)
	{
		if (item.originName != name)
		{
			return false;
		}
		return _itemNameToValues.ContainsKey(item.itemName);
	}

	public bool ContainsItemWithName(string itemName)
	{
		return _itemNameToValues.ContainsKey(itemName);
	}

	public bool TryGetItemWithValue(int val, out InkListItem item)
	{
		foreach (KeyValuePair<string, int> itemNameToValue in _itemNameToValues)
		{
			if (itemNameToValue.Value == val)
			{
				item = new InkListItem(name, itemNameToValue.Key);
				return true;
			}
		}
		item = InkListItem.Null;
		return false;
	}

	public bool TryGetValueForItem(InkListItem item, out int intVal)
	{
		return _itemNameToValues.TryGetValue(item.itemName, out intVal);
	}

	public ListDefinition(string name, Dictionary<string, int> items)
	{
		_name = name;
		_itemNameToValues = items;
	}
}
