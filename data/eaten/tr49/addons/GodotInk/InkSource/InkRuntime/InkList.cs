using System;
using System.Collections.Generic;
using System.Text;

namespace Ink.Runtime;

public class InkList : Dictionary<InkListItem, int>
{
	public List<ListDefinition> origins;

	private List<string> _originNames;

	public ListDefinition originOfMaxItem
	{
		get
		{
			if (origins == null)
			{
				return null;
			}
			string originName = maxItem.Key.originName;
			foreach (ListDefinition origin in origins)
			{
				if (origin.name == originName)
				{
					return origin;
				}
			}
			return null;
		}
	}

	public List<string> originNames
	{
		get
		{
			if (base.Count > 0)
			{
				if (_originNames == null && base.Count > 0)
				{
					_originNames = new List<string>();
				}
				else
				{
					_originNames.Clear();
				}
				using Enumerator enumerator = GetEnumerator();
				while (enumerator.MoveNext())
				{
					KeyValuePair<InkListItem, int> current = enumerator.Current;
					_originNames.Add(current.Key.originName);
				}
			}
			return _originNames;
		}
	}

	public KeyValuePair<InkListItem, int> maxItem
	{
		get
		{
			KeyValuePair<InkListItem, int> result = default(KeyValuePair<InkListItem, int>);
			using Enumerator enumerator = GetEnumerator();
			while (enumerator.MoveNext())
			{
				KeyValuePair<InkListItem, int> current = enumerator.Current;
				if (result.Key.isNull || current.Value > result.Value)
				{
					result = current;
				}
			}
			return result;
		}
	}

	public KeyValuePair<InkListItem, int> minItem
	{
		get
		{
			KeyValuePair<InkListItem, int> result = default(KeyValuePair<InkListItem, int>);
			using Enumerator enumerator = GetEnumerator();
			while (enumerator.MoveNext())
			{
				KeyValuePair<InkListItem, int> current = enumerator.Current;
				if (result.Key.isNull || current.Value < result.Value)
				{
					result = current;
				}
			}
			return result;
		}
	}

	public InkList inverse
	{
		get
		{
			InkList inkList = new InkList();
			if (origins != null)
			{
				foreach (ListDefinition origin in origins)
				{
					foreach (KeyValuePair<InkListItem, int> item in origin.items)
					{
						if (!ContainsKey(item.Key))
						{
							inkList.Add(item.Key, item.Value);
						}
					}
				}
			}
			return inkList;
		}
	}

	public InkList all
	{
		get
		{
			InkList inkList = new InkList();
			if (origins != null)
			{
				foreach (ListDefinition origin in origins)
				{
					foreach (KeyValuePair<InkListItem, int> item in origin.items)
					{
						inkList[item.Key] = item.Value;
					}
				}
			}
			return inkList;
		}
	}

	private List<KeyValuePair<InkListItem, int>> orderedItems
	{
		get
		{
			List<KeyValuePair<InkListItem, int>> list = new List<KeyValuePair<InkListItem, int>>();
			list.AddRange(this);
			list.Sort((KeyValuePair<InkListItem, int> x, KeyValuePair<InkListItem, int> y) => (x.Value == y.Value) ? x.Key.originName.CompareTo(y.Key.originName) : x.Value.CompareTo(y.Value));
			return list;
		}
	}

	public InkListItem singleItem
	{
		get
		{
			using (Enumerator enumerator = GetEnumerator())
			{
				if (enumerator.MoveNext())
				{
					return enumerator.Current.Key;
				}
			}
			return default(InkListItem);
		}
	}

	public InkList()
	{
	}

	public InkList(InkList otherList)
		: base((IDictionary<InkListItem, int>)otherList)
	{
		List<string> list = otherList.originNames;
		if (list != null)
		{
			_originNames = new List<string>(list);
		}
		if (otherList.origins != null)
		{
			origins = new List<ListDefinition>(otherList.origins);
		}
	}

	public InkList(string singleOriginListName, Story originStory)
	{
		SetInitialOriginName(singleOriginListName);
		if (originStory.listDefinitions.TryListGetDefinition(singleOriginListName, out var def))
		{
			origins = new List<ListDefinition> { def };
			return;
		}
		throw new Exception("InkList origin could not be found in story when constructing new list: " + singleOriginListName);
	}

	public InkList(KeyValuePair<InkListItem, int> singleElement)
	{
		Add(singleElement.Key, singleElement.Value);
	}

	public static InkList FromString(string myListItem, Story originStory)
	{
		if (string.IsNullOrEmpty(myListItem))
		{
			return new InkList();
		}
		ListValue listValue = originStory.listDefinitions.FindSingleItemListWithName(myListItem);
		if ((bool)listValue)
		{
			return new InkList(listValue.value);
		}
		throw new Exception("Could not find the InkListItem from the string '" + myListItem + "' to create an InkList because it doesn't exist in the original list definition in ink.");
	}

	public void AddItem(InkListItem item)
	{
		if (item.originName == null)
		{
			AddItem(item.itemName);
			return;
		}
		foreach (ListDefinition origin in origins)
		{
			if (origin.name == item.originName)
			{
				if (origin.TryGetValueForItem(item, out var intVal))
				{
					base[item] = intVal;
					return;
				}
				InkListItem inkListItem = item;
				throw new Exception("Could not add the item " + inkListItem.ToString() + " to this list because it doesn't exist in the original list definition in ink.");
			}
		}
		throw new Exception("Failed to add item to list because the item was from a new list definition that wasn't previously known to this list. Only items from previously known lists can be used, so that the int value can be found.");
	}

	public void AddItem(string itemName, Story storyObject = null)
	{
		ListDefinition listDefinition = null;
		if (origins != null)
		{
			foreach (ListDefinition origin in origins)
			{
				if (origin.ContainsItemWithName(itemName))
				{
					if (listDefinition != null)
					{
						throw new Exception("Could not add the item " + itemName + " to this list because it could come from either " + origin.name + " or " + listDefinition.name);
					}
					listDefinition = origin;
				}
			}
		}
		if (listDefinition == null)
		{
			if (storyObject == null)
			{
				throw new Exception("Could not add the item " + itemName + " to this list because it isn't known to any list definitions previously associated with this list, and no ink Story object was provided to create it from.");
			}
			KeyValuePair<InkListItem, int> keyValuePair = FromString(itemName, storyObject).orderedItems[0];
			base[keyValuePair.Key] = keyValuePair.Value;
		}
		else
		{
			InkListItem inkListItem = new InkListItem(listDefinition.name, itemName);
			int value = listDefinition.ValueForItem(inkListItem);
			base[inkListItem] = value;
		}
	}

	public bool ContainsItemNamed(string itemName)
	{
		using (Enumerator enumerator = GetEnumerator())
		{
			while (enumerator.MoveNext())
			{
				if (enumerator.Current.Key.itemName == itemName)
				{
					return true;
				}
			}
		}
		return false;
	}

	public void SetInitialOriginName(string initialOriginName)
	{
		_originNames = new List<string> { initialOriginName };
	}

	public void SetInitialOriginNames(List<string> initialOriginNames)
	{
		if (initialOriginNames == null)
		{
			_originNames = null;
		}
		else
		{
			_originNames = new List<string>(initialOriginNames);
		}
	}

	public InkList Union(InkList otherList)
	{
		InkList inkList = new InkList(this);
		foreach (KeyValuePair<InkListItem, int> other in otherList)
		{
			inkList[other.Key] = other.Value;
		}
		return inkList;
	}

	public InkList Intersect(InkList otherList)
	{
		InkList inkList = new InkList();
		using Enumerator enumerator = GetEnumerator();
		while (enumerator.MoveNext())
		{
			KeyValuePair<InkListItem, int> current = enumerator.Current;
			if (otherList.ContainsKey(current.Key))
			{
				inkList.Add(current.Key, current.Value);
			}
		}
		return inkList;
	}

	public bool HasIntersection(InkList otherList)
	{
		using (Enumerator enumerator = GetEnumerator())
		{
			while (enumerator.MoveNext())
			{
				if (otherList.ContainsKey(enumerator.Current.Key))
				{
					return true;
				}
			}
		}
		return false;
	}

	public InkList Without(InkList listToRemove)
	{
		InkList inkList = new InkList(this);
		foreach (KeyValuePair<InkListItem, int> item in listToRemove)
		{
			inkList.Remove(item.Key);
		}
		return inkList;
	}

	public bool Contains(InkList otherList)
	{
		if (otherList.Count == 0 || base.Count == 0)
		{
			return false;
		}
		foreach (KeyValuePair<InkListItem, int> other in otherList)
		{
			if (!ContainsKey(other.Key))
			{
				return false;
			}
		}
		return true;
	}

	public bool Contains(string listItemName)
	{
		using (Enumerator enumerator = GetEnumerator())
		{
			while (enumerator.MoveNext())
			{
				if (enumerator.Current.Key.itemName == listItemName)
				{
					return true;
				}
			}
		}
		return false;
	}

	public bool GreaterThan(InkList otherList)
	{
		if (base.Count == 0)
		{
			return false;
		}
		if (otherList.Count == 0)
		{
			return true;
		}
		return minItem.Value > otherList.maxItem.Value;
	}

	public bool GreaterThanOrEquals(InkList otherList)
	{
		if (base.Count == 0)
		{
			return false;
		}
		if (otherList.Count == 0)
		{
			return true;
		}
		if (minItem.Value >= otherList.minItem.Value)
		{
			return maxItem.Value >= otherList.maxItem.Value;
		}
		return false;
	}

	public bool LessThan(InkList otherList)
	{
		if (otherList.Count == 0)
		{
			return false;
		}
		if (base.Count == 0)
		{
			return true;
		}
		return maxItem.Value < otherList.minItem.Value;
	}

	public bool LessThanOrEquals(InkList otherList)
	{
		if (otherList.Count == 0)
		{
			return false;
		}
		if (base.Count == 0)
		{
			return true;
		}
		if (maxItem.Value <= otherList.maxItem.Value)
		{
			return minItem.Value <= otherList.minItem.Value;
		}
		return false;
	}

	public InkList MaxAsList()
	{
		if (base.Count > 0)
		{
			return new InkList(maxItem);
		}
		return new InkList();
	}

	public InkList MinAsList()
	{
		if (base.Count > 0)
		{
			return new InkList(minItem);
		}
		return new InkList();
	}

	public InkList ListWithSubRange(object minBound, object maxBound)
	{
		if (base.Count == 0)
		{
			return new InkList();
		}
		List<KeyValuePair<InkListItem, int>> list = orderedItems;
		int num = 0;
		int num2 = int.MaxValue;
		if (minBound is int)
		{
			num = (int)minBound;
		}
		else if (minBound is InkList && ((InkList)minBound).Count > 0)
		{
			num = ((InkList)minBound).minItem.Value;
		}
		if (maxBound is int)
		{
			num2 = (int)maxBound;
		}
		else if (maxBound is InkList && ((InkList)maxBound).Count > 0)
		{
			num2 = ((InkList)maxBound).maxItem.Value;
		}
		InkList inkList = new InkList();
		inkList.SetInitialOriginNames(originNames);
		foreach (KeyValuePair<InkListItem, int> item in list)
		{
			if (item.Value >= num && item.Value <= num2)
			{
				inkList.Add(item.Key, item.Value);
			}
		}
		return inkList;
	}

	public override bool Equals(object other)
	{
		if (!(other is InkList inkList))
		{
			return false;
		}
		if (inkList.Count != base.Count)
		{
			return false;
		}
		using (Enumerator enumerator = GetEnumerator())
		{
			while (enumerator.MoveNext())
			{
				if (!inkList.ContainsKey(enumerator.Current.Key))
				{
					return false;
				}
			}
		}
		return true;
	}

	public override int GetHashCode()
	{
		int num = 0;
		using Enumerator enumerator = GetEnumerator();
		while (enumerator.MoveNext())
		{
			num += enumerator.Current.Key.GetHashCode();
		}
		return num;
	}

	public override string ToString()
	{
		List<KeyValuePair<InkListItem, int>> list = orderedItems;
		StringBuilder stringBuilder = new StringBuilder();
		for (int i = 0; i < list.Count; i++)
		{
			if (i > 0)
			{
				stringBuilder.Append(", ");
			}
			stringBuilder.Append(list[i].Key.itemName);
		}
		return stringBuilder.ToString();
	}
}
