using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Godot;
using Ink.Runtime;

internal class InkRelationStore
{
	public Story story;

	private static readonly char[] _pairStoreStringDelimiter = new char[1] { ';' };

	private static readonly char[] _pairStoreElementDelimiter = new char[1] { '>' };

	private Dictionary<string, Dictionary<string, List<string>>> _cachedPairStore = new Dictionary<string, Dictionary<string, List<string>>>();

	private Dictionary<string, Dictionary<string, List<string>>> _reversedCachedPairStore = new Dictionary<string, Dictionary<string, List<string>>>();

	public void Clear()
	{
		_cachedPairStore.Clear();
		_reversedCachedPairStore.Clear();
	}

	public InkRelationStore(Story story)
	{
		InkRelationStore inkRelationStore = this;
		this.story = story;
		story.BindExternalFunction("reached_any_of", (InkList list) => list.HasIntersection((InkList)story.variablesState["allTrueStates"]), lookaheadSafe: true);
		story.BindExternalFunction("reached", (InkList list) => ((InkList)story.variablesState["allTrueStates"]).Contains(list), lookaheadSafe: true);
		story.BindExternalFunction("between", delegate(InkList minList, InkList maxList)
		{
			InkList inkList = (InkList)story.variablesState["allTrueStates"];
			return inkList.Contains(minList) && !inkList.HasIntersection(maxList);
		}, lookaheadSafe: true);
		story.BindExternalFunction("_relate", delegate(InkList list1, InkList list2, InkList relation)
		{
			string itemName = relation.singleItem.itemName;
			string text = "";
			foreach (KeyValuePair<InkListItem, int> item in list1)
			{
				foreach (KeyValuePair<InkListItem, int> item2 in list2)
				{
					if (!inkRelationStore.IsRelatedPairInPairStoreString(item.Key, item2.Key, itemName))
					{
						text += inkRelationStore.PairStoreString(item.Key.itemName, item2.Key.itemName, itemName);
						inkRelationStore.LinkInRelationCache(item.Key.itemName, itemName, item2.Key.itemName);
					}
				}
			}
			VariablesState variablesState = story.variablesState;
			variablesState["pairstore"] = variablesState["pairstore"]?.ToString() + text;
			return !string.IsNullOrWhiteSpace(text);
		});
		story.BindExternalFunction("_unrelate", delegate(InkList list1, InkList relation, InkList list2)
		{
			string itemName = relation.singleItem.itemName;
			List<string> removeKeys = new List<string>();
			foreach (KeyValuePair<InkListItem, int> item3 in list1)
			{
				foreach (KeyValuePair<InkListItem, int> item4 in list2)
				{
					if (inkRelationStore.IsRelatedPairInPairStoreString(item3.Key, item4.Key, itemName))
					{
						removeKeys.Add(inkRelationStore.PairStoreString(item3.Key.itemName, item4.Key.itemName, itemName, appendFinalDelimiter: false));
						inkRelationStore._cachedPairStore[itemName][item3.Key.itemName].Remove(item4.Key.itemName);
						inkRelationStore._reversedCachedPairStore[itemName][item4.Key.itemName].Remove(item3.Key.itemName);
					}
				}
			}
			if (removeKeys.Count == 0)
			{
				return false;
			}
			IEnumerable<string> enumerable = from t in ((string)story.variablesState["pairstore"]).Split(_pairStoreStringDelimiter, StringSplitOptions.RemoveEmptyEntries)
				where !removeKeys.Contains(t)
				select t;
			StringBuilder stringBuilder = new StringBuilder();
			foreach (string item5 in enumerable)
			{
				stringBuilder.Append(item5 + _pairStoreStringDelimiter[0]);
			}
			story.variablesState["pairstore"] = stringBuilder.ToString();
			return true;
		});
		story.BindExternalFunction("_isRelated", delegate(InkList list1, InkList list2, string relationName)
		{
			foreach (KeyValuePair<InkListItem, int> item6 in list1)
			{
				foreach (KeyValuePair<InkListItem, int> item7 in list2)
				{
					if (!inkRelationStore.IsRelatedPairInPairStoreString(item6.Key, item7.Key, relationName))
					{
						return false;
					}
				}
			}
			return true;
		}, lookaheadSafe: true);
		story.BindExternalFunction("_getRelatesTo", (InkList list1, InkList relation) => inkRelationStore.GetRelatedElementsInPairStoreString(list1, relation.First().Key.itemName, returnLHS: false), lookaheadSafe: true);
		story.BindExternalFunction("_getRelatedFrom", (InkList list2, InkList relation) => inkRelationStore.GetRelatedElementsInPairStoreString(list2, relation.First().Key.itemName, returnLHS: true), lookaheadSafe: true);
	}

	private bool IsRelatedPairInPairStoreString(InkListItem x1, InkListItem x2, string relationName)
	{
		RebuildCachedPairStore();
		if (!_cachedPairStore.ContainsKey(relationName))
		{
			return false;
		}
		if (!_cachedPairStore[relationName].ContainsKey(x1.itemName))
		{
			return false;
		}
		return _cachedPairStore[relationName][x1.itemName].Contains(x2.itemName);
	}

	private string PairStoreString(string x1, string x2, string relationName, bool appendFinalDelimiter = true)
	{
		StringBuilder stringBuilder = new StringBuilder();
		stringBuilder.Append(x1);
		stringBuilder.Append(_pairStoreElementDelimiter[0]);
		stringBuilder.Append(relationName);
		stringBuilder.Append(_pairStoreElementDelimiter[0]);
		stringBuilder.Append(x2);
		if (appendFinalDelimiter)
		{
			stringBuilder.Append(_pairStoreStringDelimiter[0]);
		}
		return stringBuilder.ToString();
	}

	private void LinkInRelationCache(string x1, string relationName, string x2)
	{
		if (!_cachedPairStore.ContainsKey(relationName))
		{
			_cachedPairStore[relationName] = new Dictionary<string, List<string>>();
			_reversedCachedPairStore[relationName] = new Dictionary<string, List<string>>();
		}
		if (!_cachedPairStore[relationName].ContainsKey(x1))
		{
			_cachedPairStore[relationName][x1] = new List<string>();
		}
		_cachedPairStore[relationName][x1].Add(x2);
		if (!_reversedCachedPairStore[relationName].ContainsKey(x2))
		{
			_reversedCachedPairStore[relationName][x2] = new List<string>();
		}
		_reversedCachedPairStore[relationName][x2].Add(x1);
	}

	private InkList GetRelatedElementsInPairStoreString(InkList keyList, string relationName, bool returnLHS)
	{
		new List<string>();
		InkList inkList = new InkList();
		RebuildCachedPairStore();
		Dictionary<string, Dictionary<string, List<string>>> dictionary = (returnLHS ? _reversedCachedPairStore : _cachedPairStore);
		if (dictionary.ContainsKey(relationName))
		{
			foreach (KeyValuePair<InkListItem, int> key in keyList)
			{
				if (!dictionary[relationName].ContainsKey(key.Key.itemName))
				{
					continue;
				}
				foreach (string item in dictionary[relationName][key.Key.itemName])
				{
					try
					{
						inkList.AddItem(item, story);
					}
					catch (Exception ex)
					{
						GD.PushError(ex.Message + " Old save data? This item will be skipped in GetRelatedElementsInPairStoreString");
					}
				}
			}
		}
		return inkList;
	}

	private void RebuildCachedPairStore(bool clearAndRebuild = false)
	{
		if (clearAndRebuild)
		{
			_cachedPairStore.Clear();
			_reversedCachedPairStore.Clear();
		}
		if (_cachedPairStore.Count == 0)
		{
			string[] array = ((string)story.variablesState["pairstore"]).Split(_pairStoreStringDelimiter, StringSplitOptions.RemoveEmptyEntries);
			for (int i = 0; i < array.Length; i++)
			{
				string[] array2 = array[i].Split(_pairStoreElementDelimiter, StringSplitOptions.RemoveEmptyEntries);
				LinkInRelationCache(array2[0], array2[1], array2[2]);
			}
		}
	}
}
