using System.Collections.Generic;

namespace Ink.Runtime;

public class ListValue : Value<InkList>
{
	public override ValueType valueType => ValueType.List;

	public override bool isTruthy => base.value.Count > 0;

	public override Value Cast(ValueType newType)
	{
		switch (newType)
		{
		case ValueType.Int:
		{
			KeyValuePair<InkListItem, int> maxItem2 = base.value.maxItem;
			if (maxItem2.Key.isNull)
			{
				return new IntValue(0);
			}
			return new IntValue(maxItem2.Value);
		}
		case ValueType.Float:
		{
			KeyValuePair<InkListItem, int> maxItem = base.value.maxItem;
			if (maxItem.Key.isNull)
			{
				return new FloatValue(0f);
			}
			return new FloatValue(maxItem.Value);
		}
		case ValueType.String:
		{
			KeyValuePair<InkListItem, int> maxItem3 = base.value.maxItem;
			if (maxItem3.Key.isNull)
			{
				return new StringValue("");
			}
			return new StringValue(maxItem3.Key.ToString());
		}
		default:
			if (newType == valueType)
			{
				return this;
			}
			throw BadCastException(newType);
		}
	}

	public ListValue()
		: base((InkList)null)
	{
		base.value = new InkList();
	}

	public ListValue(InkList list)
		: base((InkList)null)
	{
		base.value = new InkList(list);
	}

	public ListValue(InkListItem singleItem, int singleValue)
		: base((InkList)null)
	{
		base.value = new InkList { { singleItem, singleValue } };
	}

	public static void RetainListOriginsForAssignment(Object oldValue, Object newValue)
	{
		ListValue listValue = oldValue as ListValue;
		ListValue listValue2 = newValue as ListValue;
		if ((bool)listValue && (bool)listValue2 && listValue2.value.Count == 0)
		{
			listValue2.value.SetInitialOriginNames(listValue.value.originNames);
		}
	}
}
