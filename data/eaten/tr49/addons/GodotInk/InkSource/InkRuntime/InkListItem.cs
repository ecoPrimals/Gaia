namespace Ink.Runtime;

public struct InkListItem
{
	public readonly string originName;

	public readonly string itemName;

	public static InkListItem Null => new InkListItem(null, null);

	public bool isNull
	{
		get
		{
			if (originName == null)
			{
				return itemName == null;
			}
			return false;
		}
	}

	public string fullName => (originName ?? "?") + "." + itemName;

	public InkListItem(string originName, string itemName)
	{
		this.originName = originName;
		this.itemName = itemName;
	}

	public InkListItem(string fullName)
	{
		string[] array = fullName.Split('.');
		originName = array[0];
		itemName = array[1];
	}

	public override string ToString()
	{
		return fullName;
	}

	public override bool Equals(object obj)
	{
		if (obj is InkListItem)
		{
			return Equals((InkListItem)obj);
		}
		return false;
	}

	public bool Equals(InkListItem otherItem)
	{
		if (otherItem.itemName == itemName)
		{
			return otherItem.originName == originName;
		}
		return false;
	}

	public static bool operator ==(InkListItem left, InkListItem right)
	{
		return left.Equals(right);
	}

	public static bool operator !=(InkListItem left, InkListItem right)
	{
		return !(left == right);
	}

	public override int GetHashCode()
	{
		int num = 0;
		int hashCode = itemName.GetHashCode();
		if (originName != null)
		{
			num = originName.GetHashCode();
		}
		return num + hashCode;
	}
}
