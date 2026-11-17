using System.Collections.Generic;
using Godot;
using Ink.Runtime;

namespace GodotInk;

[GlobalClass]
public partial class InkList : RefCounted
{
	public readonly Ink.Runtime.InkList inner;

	public InkList Inverse => new InkList(inner.inverse);

	public InkList All => new InkList(inner.all);

	public InkList(Ink.Runtime.InkList inner)
	{
		this.inner = inner;
	}

	public InkList(InkList otherList)
		: this(new Ink.Runtime.InkList(otherList.inner))
	{
	}

	public void AddItem(string itemName)
	{
		inner.AddItem(itemName);
	}

	public bool Contains(string listItemName)
	{
		return inner.Contains(listItemName);
	}

	public bool Contains(InkList otherList)
	{
		return inner.Contains(otherList.inner);
	}

	public bool ContainsItemNamed(string itemName)
	{
		return inner.ContainsItemNamed(itemName);
	}

	public override bool Equals(object? other)
	{
		return inner.Equals(other);
	}

	public override int GetHashCode()
	{
		return inner.GetHashCode();
	}

	public override string ToString()
	{
		return inner.ToString();
	}

	public bool GreaterThan(InkList otherList)
	{
		return inner.GreaterThan(otherList.inner);
	}

	public bool GreaterThanOrEquals(InkList otherList)
	{
		return inner.GreaterThanOrEquals(otherList.inner);
	}

	public bool LessThan(InkList otherList)
	{
		return inner.LessThan(otherList.inner);
	}

	public bool LessThanOrEquals(InkList otherList)
	{
		return inner.LessThanOrEquals(otherList.inner);
	}

	public bool HashIntersection(InkList otherList)
	{
		return inner.HasIntersection(otherList.inner);
	}

	public InkList Intersect(InkList otherList)
	{
		return new InkList(inner.Intersect(otherList.inner));
	}

	public InkList Union(InkList otherList)
	{
		return new InkList(inner.Union(otherList.inner));
	}

	public InkList Without(InkList listToRemove)
	{
		return new InkList(inner.Without(listToRemove.inner));
	}

	public InkList MaxAsList()
	{
		return new InkList(inner.MaxAsList());
	}

	public InkList MinAsList()
	{
		return new InkList(inner.MinAsList());
	}

	public static InkList FromString(string stringName, InkStory originStory)
	{
		return new InkList(Ink.Runtime.InkList.FromString(stringName, originStory.runtimeStory));
	}

	public void SetInitialOriginName(string initialOriginName)
	{
		inner.SetInitialOriginName(initialOriginName);
	}

	public void SetInitialOriginNames(string[] initialOriginNames)
	{
		inner.SetInitialOriginNames(new List<string>(initialOriginNames));
	}
}
