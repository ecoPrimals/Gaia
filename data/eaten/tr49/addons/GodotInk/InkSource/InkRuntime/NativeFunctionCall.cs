using System;
using System.Collections.Generic;

namespace Ink.Runtime;

public class NativeFunctionCall : Object
{
	private delegate object BinaryOp<T>(T left, T right);

	private delegate object UnaryOp<T>(T val);

	public const string Add = "+";

	public const string Subtract = "-";

	public const string Divide = "/";

	public const string Multiply = "*";

	public const string Mod = "%";

	public const string Negate = "_";

	public const string Equal = "==";

	public const string Greater = ">";

	public const string Less = "<";

	public const string GreaterThanOrEquals = ">=";

	public const string LessThanOrEquals = "<=";

	public const string NotEquals = "!=";

	public const string Not = "!";

	public const string And = "&&";

	public const string Or = "||";

	public const string Min = "MIN";

	public const string Max = "MAX";

	public const string Pow = "POW";

	public const string Floor = "FLOOR";

	public const string Ceiling = "CEILING";

	public const string Int = "INT";

	public const string Float = "FLOAT";

	public const string Has = "?";

	public const string Hasnt = "!?";

	public const string Intersect = "^";

	public const string ListMin = "LIST_MIN";

	public const string ListMax = "LIST_MAX";

	public const string All = "LIST_ALL";

	public const string Count = "LIST_COUNT";

	public const string ValueOfList = "LIST_VALUE";

	public const string Invert = "LIST_INVERT";

	private string _name;

	private int _numberOfParameters;

	private NativeFunctionCall _prototype;

	private bool _isPrototype;

	private Dictionary<ValueType, object> _operationFuncs;

	private static Dictionary<string, NativeFunctionCall> _nativeFunctions;

	public string name
	{
		get
		{
			return _name;
		}
		protected set
		{
			_name = value;
			if (!_isPrototype)
			{
				_prototype = _nativeFunctions[_name];
			}
		}
	}

	public int numberOfParameters
	{
		get
		{
			if ((bool)_prototype)
			{
				return _prototype.numberOfParameters;
			}
			return _numberOfParameters;
		}
		protected set
		{
			_numberOfParameters = value;
		}
	}

	public static NativeFunctionCall CallWithName(string functionName)
	{
		return new NativeFunctionCall(functionName);
	}

	public static bool CallExistsWithName(string functionName)
	{
		GenerateNativeFunctionsIfNecessary();
		return _nativeFunctions.ContainsKey(functionName);
	}

	public Object Call(List<Object> parameters)
	{
		if ((bool)_prototype)
		{
			return _prototype.Call(parameters);
		}
		if (numberOfParameters != parameters.Count)
		{
			throw new Exception("Unexpected number of parameters");
		}
		bool flag = false;
		foreach (Object parameter in parameters)
		{
			if (parameter is Void)
			{
				throw new StoryException("Attempting to perform " + name + " on a void value. Did you forget to 'return' a value from a function you called here?");
			}
			if (parameter is ListValue)
			{
				flag = true;
			}
		}
		if ((parameters.Count == 2) & flag)
		{
			return CallBinaryListOperation(parameters);
		}
		List<Value> list = CoerceValuesToSingleType(parameters);
		return list[0].valueType switch
		{
			ValueType.Int => Call<int>(list), 
			ValueType.Float => Call<float>(list), 
			ValueType.String => Call<string>(list), 
			ValueType.DivertTarget => Call<Path>(list), 
			ValueType.List => Call<InkList>(list), 
			_ => null, 
		};
	}

	private Value Call<T>(List<Value> parametersOfSingleType)
	{
		Value value = parametersOfSingleType[0];
		ValueType valueType = value.valueType;
		Value<T> value2 = (Value<T>)value;
		int count = parametersOfSingleType.Count;
		if (count == 2 || count == 1)
		{
			object value3 = null;
			if (!_operationFuncs.TryGetValue(valueType, out value3))
			{
				throw new StoryException("Cannot perform operation '" + name + "' on " + valueType);
			}
			if (count == 2)
			{
				Value<T> value4 = (Value<T>)parametersOfSingleType[1];
				return Value.Create(((BinaryOp<T>)value3)(value2.value, value4.value));
			}
			return Value.Create(((UnaryOp<T>)value3)(value2.value));
		}
		throw new Exception("Unexpected number of parameters to NativeFunctionCall: " + parametersOfSingleType.Count);
	}

	private Value CallBinaryListOperation(List<Object> parameters)
	{
		if ((name == "+" || name == "-") && parameters[0] is ListValue && parameters[1] is IntValue)
		{
			return CallListIncrementOperation(parameters);
		}
		Value value = parameters[0] as Value;
		Value value2 = parameters[1] as Value;
		if ((name == "&&" || name == "||") && (value.valueType != ValueType.List || value2.valueType != ValueType.List))
		{
			return new BoolValue((bool)(_operationFuncs[ValueType.Int] as BinaryOp<int>)(value.isTruthy ? 1 : 0, value2.isTruthy ? 1 : 0));
		}
		if (value.valueType == ValueType.List && value2.valueType == ValueType.List)
		{
			return Call<InkList>(new List<Value> { value, value2 });
		}
		throw new StoryException("Can not call use '" + name + "' operation on " + value.valueType.ToString() + " and " + value2.valueType);
	}

	private Value CallListIncrementOperation(List<Object> listIntParams)
	{
		ListValue listValue = (ListValue)listIntParams[0];
		IntValue intValue = (IntValue)listIntParams[1];
		InkList inkList = new InkList();
		foreach (KeyValuePair<InkListItem, int> item2 in listValue.value)
		{
			InkListItem key = item2.Key;
			int value = item2.Value;
			int num = (int)((BinaryOp<int>)_operationFuncs[ValueType.Int])(value, intValue.value);
			ListDefinition listDefinition = null;
			foreach (ListDefinition origin in listValue.value.origins)
			{
				if (origin.name == key.originName)
				{
					listDefinition = origin;
					break;
				}
			}
			if (listDefinition != null && listDefinition.TryGetItemWithValue(num, out var item))
			{
				inkList.Add(item, num);
			}
		}
		return new ListValue(inkList);
	}

	private List<Value> CoerceValuesToSingleType(List<Object> parametersIn)
	{
		ValueType valueType = ValueType.Int;
		ListValue listValue = null;
		foreach (Value item4 in parametersIn)
		{
			if (item4.valueType > valueType)
			{
				valueType = item4.valueType;
			}
			if (item4.valueType == ValueType.List)
			{
				listValue = item4 as ListValue;
			}
		}
		List<Value> list = new List<Value>();
		if (valueType == ValueType.List)
		{
			foreach (Value item5 in parametersIn)
			{
				if (item5.valueType == ValueType.List)
				{
					list.Add(item5);
					continue;
				}
				if (item5.valueType == ValueType.Int)
				{
					int num = (int)item5.valueObject;
					ListDefinition originOfMaxItem = listValue.value.originOfMaxItem;
					if (originOfMaxItem.TryGetItemWithValue(num, out var item))
					{
						ListValue item2 = new ListValue(item, num);
						list.Add(item2);
						continue;
					}
					throw new StoryException("Could not find List item with the value " + num + " in " + originOfMaxItem.name);
				}
				throw new StoryException("Cannot mix Lists and " + item5.valueType.ToString() + " values in this operation");
			}
		}
		else
		{
			foreach (Value item6 in parametersIn)
			{
				Value item3 = item6.Cast(valueType);
				list.Add(item3);
			}
		}
		return list;
	}

	public NativeFunctionCall(string name)
	{
		GenerateNativeFunctionsIfNecessary();
		this.name = name;
	}

	public NativeFunctionCall()
	{
		GenerateNativeFunctionsIfNecessary();
	}

	private NativeFunctionCall(string name, int numberOfParameters)
	{
		_isPrototype = true;
		this.name = name;
		this.numberOfParameters = numberOfParameters;
	}

	private static object Identity<T>(T t)
	{
		return t;
	}

	private static void GenerateNativeFunctionsIfNecessary()
	{
		if (_nativeFunctions == null)
		{
			_nativeFunctions = new Dictionary<string, NativeFunctionCall>();
			AddIntBinaryOp("+", (int x, int y) => x + y);
			AddIntBinaryOp("-", (int x, int y) => x - y);
			AddIntBinaryOp("*", (int x, int y) => x * y);
			AddIntBinaryOp("/", (int x, int y) => x / y);
			AddIntBinaryOp("%", (int x, int y) => x % y);
			AddIntUnaryOp("_", (int x) => -x);
			AddIntBinaryOp("==", (int x, int y) => x == y);
			AddIntBinaryOp(">", (int x, int y) => x > y);
			AddIntBinaryOp("<", (int x, int y) => x < y);
			AddIntBinaryOp(">=", (int x, int y) => x >= y);
			AddIntBinaryOp("<=", (int x, int y) => x <= y);
			AddIntBinaryOp("!=", (int x, int y) => x != y);
			AddIntUnaryOp("!", (int x) => x == 0);
			AddIntBinaryOp("&&", (int x, int y) => x != 0 && y != 0);
			AddIntBinaryOp("||", (int x, int y) => x != 0 || y != 0);
			AddIntBinaryOp("MAX", (int x, int y) => Math.Max(x, y));
			AddIntBinaryOp("MIN", (int x, int y) => Math.Min(x, y));
			AddIntBinaryOp("POW", (int x, int y) => (float)Math.Pow(x, y));
			AddIntUnaryOp("FLOOR", Identity);
			AddIntUnaryOp("CEILING", Identity);
			AddIntUnaryOp("INT", Identity);
			AddIntUnaryOp("FLOAT", (int x) => (float)x);
			AddFloatBinaryOp("+", (float x, float y) => x + y);
			AddFloatBinaryOp("-", (float x, float y) => x - y);
			AddFloatBinaryOp("*", (float x, float y) => x * y);
			AddFloatBinaryOp("/", (float x, float y) => x / y);
			AddFloatBinaryOp("%", (float x, float y) => x % y);
			AddFloatUnaryOp("_", (float x) => 0f - x);
			AddFloatBinaryOp("==", (float x, float y) => x == y);
			AddFloatBinaryOp(">", (float x, float y) => x > y);
			AddFloatBinaryOp("<", (float x, float y) => x < y);
			AddFloatBinaryOp(">=", (float x, float y) => x >= y);
			AddFloatBinaryOp("<=", (float x, float y) => x <= y);
			AddFloatBinaryOp("!=", (float x, float y) => x != y);
			AddFloatUnaryOp("!", (float x) => x == 0f);
			AddFloatBinaryOp("&&", (float x, float y) => x != 0f && y != 0f);
			AddFloatBinaryOp("||", (float x, float y) => x != 0f || y != 0f);
			AddFloatBinaryOp("MAX", (float x, float y) => Math.Max(x, y));
			AddFloatBinaryOp("MIN", (float x, float y) => Math.Min(x, y));
			AddFloatBinaryOp("POW", (float x, float y) => (float)Math.Pow(x, y));
			AddFloatUnaryOp("FLOOR", (float x) => (float)Math.Floor(x));
			AddFloatUnaryOp("CEILING", (float x) => (float)Math.Ceiling(x));
			AddFloatUnaryOp("INT", (float x) => (int)x);
			AddFloatUnaryOp("FLOAT", Identity);
			AddStringBinaryOp("+", (string x, string y) => x + y);
			AddStringBinaryOp("==", (string x, string y) => x.Equals(y));
			AddStringBinaryOp("!=", (string x, string y) => !x.Equals(y));
			AddStringBinaryOp("?", (string x, string y) => x.Contains(y));
			AddStringBinaryOp("!?", (string x, string y) => !x.Contains(y));
			AddListBinaryOp("+", (InkList x, InkList y) => x.Union(y));
			AddListBinaryOp("-", (InkList x, InkList y) => x.Without(y));
			AddListBinaryOp("?", (InkList x, InkList y) => x.Contains(y));
			AddListBinaryOp("!?", (InkList x, InkList y) => !x.Contains(y));
			AddListBinaryOp("^", (InkList x, InkList y) => x.Intersect(y));
			AddListBinaryOp("==", (InkList x, InkList y) => x.Equals(y));
			AddListBinaryOp(">", (InkList x, InkList y) => x.GreaterThan(y));
			AddListBinaryOp("<", (InkList x, InkList y) => x.LessThan(y));
			AddListBinaryOp(">=", (InkList x, InkList y) => x.GreaterThanOrEquals(y));
			AddListBinaryOp("<=", (InkList x, InkList y) => x.LessThanOrEquals(y));
			AddListBinaryOp("!=", (InkList x, InkList y) => !x.Equals(y));
			AddListBinaryOp("&&", (InkList x, InkList y) => x.Count > 0 && y.Count > 0);
			AddListBinaryOp("||", (InkList x, InkList y) => x.Count > 0 || y.Count > 0);
			AddListUnaryOp("!", (InkList x) => (x.Count == 0) ? 1 : 0);
			AddListUnaryOp("LIST_INVERT", (InkList x) => x.inverse);
			AddListUnaryOp("LIST_ALL", (InkList x) => x.all);
			AddListUnaryOp("LIST_MIN", (InkList x) => x.MinAsList());
			AddListUnaryOp("LIST_MAX", (InkList x) => x.MaxAsList());
			AddListUnaryOp("LIST_COUNT", (InkList x) => x.Count);
			AddListUnaryOp("LIST_VALUE", (InkList x) => x.maxItem.Value);
			BinaryOp<Path> op = (Path d1, Path d2) => d1.Equals(d2);
			BinaryOp<Path> op2 = (Path d1, Path d2) => !d1.Equals(d2);
			AddOpToNativeFunc("==", 2, ValueType.DivertTarget, op);
			AddOpToNativeFunc("!=", 2, ValueType.DivertTarget, op2);
		}
	}

	private void AddOpFuncForType(ValueType valType, object op)
	{
		if (_operationFuncs == null)
		{
			_operationFuncs = new Dictionary<ValueType, object>();
		}
		_operationFuncs[valType] = op;
	}

	private static void AddOpToNativeFunc(string name, int args, ValueType valType, object op)
	{
		NativeFunctionCall value = null;
		if (!_nativeFunctions.TryGetValue(name, out value))
		{
			value = new NativeFunctionCall(name, args);
			_nativeFunctions[name] = value;
		}
		value.AddOpFuncForType(valType, op);
	}

	private static void AddIntBinaryOp(string name, BinaryOp<int> op)
	{
		AddOpToNativeFunc(name, 2, ValueType.Int, op);
	}

	private static void AddIntUnaryOp(string name, UnaryOp<int> op)
	{
		AddOpToNativeFunc(name, 1, ValueType.Int, op);
	}

	private static void AddFloatBinaryOp(string name, BinaryOp<float> op)
	{
		AddOpToNativeFunc(name, 2, ValueType.Float, op);
	}

	private static void AddStringBinaryOp(string name, BinaryOp<string> op)
	{
		AddOpToNativeFunc(name, 2, ValueType.String, op);
	}

	private static void AddListBinaryOp(string name, BinaryOp<InkList> op)
	{
		AddOpToNativeFunc(name, 2, ValueType.List, op);
	}

	private static void AddListUnaryOp(string name, UnaryOp<InkList> op)
	{
		AddOpToNativeFunc(name, 1, ValueType.List, op);
	}

	private static void AddFloatUnaryOp(string name, UnaryOp<float> op)
	{
		AddOpToNativeFunc(name, 1, ValueType.Float, op);
	}

	public override string ToString()
	{
		return "Native '" + name + "'";
	}
}
