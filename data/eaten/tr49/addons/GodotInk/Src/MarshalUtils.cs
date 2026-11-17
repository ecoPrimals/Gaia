using System;
using System.Collections.Generic;
using Godot;
using Ink.Runtime;

namespace GodotInk;

public static class MarshalUtils
{
	public static Variant ToVariant(object? obj)
	{
		if (!(obj is bool flag))
		{
			if (!(obj is int num))
			{
				if (!(obj is float num2))
				{
					if (!(obj is string text))
					{
						if (!(obj is Choice inner))
						{
							if (!(obj is Ink.Runtime.InkList inner2))
							{
								if (obj == null)
								{
									return default(Variant);
								}
								throw new ArgumentException($"Argument of type {obj.GetType()} is not valid.");
							}
							return new InkList(inner2);
						}
						return new InkChoice(inner);
					}
					return Variant.CreateFrom(text);
				}
				return Variant.CreateFrom(num2);
			}
			return Variant.CreateFrom(num);
		}
		return Variant.CreateFrom(flag);
	}

	public static object? FromVariant(Variant variant)
	{
		Variant.Type variantType = variant.VariantType;
		if ((ulong)variantType <= 4uL)
		{
			switch ((int)variantType)
			{
			case 1:
				return variant.AsBool();
			case 2:
				return variant.AsInt32();
			case 3:
				return variant.AsSingle();
			case 4:
				return variant.AsString();
			case 0:
				return null;
			}
		}
		throw new ArgumentException($"Argument of type {variant.Obj?.GetType()} is not valid.");
	}

	public static Variant[] ToVariants(IReadOnlyList<object?> objects)
	{
		if (objects.Count <= 0)
		{
			return Array.Empty<Variant>();
		}
		Variant[] array = new Variant[objects.Count];
		for (int i = 0; i < objects.Count; i++)
		{
			array[i] = ToVariant(objects[i]);
		}
		return array;
	}

	public static object?[] FromVariants(IReadOnlyList<Variant> variants)
	{
		if (variants.Count <= 0)
		{
			return Array.Empty<object>();
		}
		object[] array = new object[variants.Count];
		for (int i = 0; i < variants.Count; i++)
		{
			array[i] = FromVariant(variants[i]);
		}
		return array;
	}

	public static List<InkChoice> ToVariants(IReadOnlyList<Choice> choices)
	{
		List<InkChoice> list = new List<InkChoice>();
		foreach (Choice choice in choices)
		{
			list.Add((InkChoice)(GodotObject)ToVariant(choice));
		}
		return list;
	}
}
