using System.Collections.Generic;

namespace Ink.Runtime;

public class ListDefinitionsOrigin
{
	private Dictionary<string, ListDefinition> _lists;

	private Dictionary<string, ListValue> _allUnambiguousListValueCache;

	public List<ListDefinition> lists
	{
		get
		{
			List<ListDefinition> list = new List<ListDefinition>();
			foreach (KeyValuePair<string, ListDefinition> list2 in _lists)
			{
				list.Add(list2.Value);
			}
			return list;
		}
	}

	public ListDefinitionsOrigin(List<ListDefinition> lists)
	{
		_lists = new Dictionary<string, ListDefinition>();
		_allUnambiguousListValueCache = new Dictionary<string, ListValue>();
		foreach (ListDefinition list in lists)
		{
			_lists[list.name] = list;
			foreach (KeyValuePair<InkListItem, int> item in list.items)
			{
				InkListItem key = item.Key;
				int value = item.Value;
				ListValue value2 = new ListValue(key, value);
				_allUnambiguousListValueCache[key.itemName] = value2;
				_allUnambiguousListValueCache[key.fullName] = value2;
			}
		}
	}

	public bool TryListGetDefinition(string name, out ListDefinition def)
	{
		return _lists.TryGetValue(name, out def);
	}

	public ListValue FindSingleItemListWithName(string name)
	{
		ListValue value = null;
		if (!string.IsNullOrWhiteSpace(name))
		{
			_allUnambiguousListValueCache.TryGetValue(name, out value);
		}
		return value;
	}
}
