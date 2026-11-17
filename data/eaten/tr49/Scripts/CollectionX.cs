using System.Collections.Generic;
using Godot;

public static class CollectionX
{
	public static T Random<T>(this IList<T> list)
	{
		if (list.Count == 0)
		{
			return default(T);
		}
		int index = GD.RandRange(0, list.Count - 1);
		return list[index];
	}
}
