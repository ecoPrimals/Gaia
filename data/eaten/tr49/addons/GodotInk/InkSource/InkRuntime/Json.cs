using System;
using System.Collections.Generic;
using System.Linq;

namespace Ink.Runtime;

public static class Json
{
	private static string[] _controlCommandNames = new string[26];

	public static List<T> JArrayToRuntimeObjList<T>(List<object> jArray, bool skipLast = false) where T : Object
	{
		int num = jArray.Count;
		if (skipLast)
		{
			num--;
		}
		List<T> list = new List<T>(jArray.Count);
		for (int i = 0; i < num; i++)
		{
			T item = JTokenToRuntimeObject(jArray[i]) as T;
			list.Add(item);
		}
		return list;
	}

	public static List<Object> JArrayToRuntimeObjList(List<object> jArray, bool skipLast = false)
	{
		return JArrayToRuntimeObjList<Object>(jArray, skipLast);
	}

	public static void WriteDictionaryRuntimeObjs(SimpleJson.Writer writer, Dictionary<string, Object> dictionary)
	{
		writer.WriteObjectStart();
		foreach (KeyValuePair<string, Object> item in dictionary)
		{
			writer.WritePropertyStart(item.Key);
			WriteRuntimeObject(writer, item.Value);
			writer.WritePropertyEnd();
		}
		writer.WriteObjectEnd();
	}

	public static void WriteListRuntimeObjs(SimpleJson.Writer writer, List<Object> list)
	{
		writer.WriteArrayStart();
		foreach (Object item in list)
		{
			WriteRuntimeObject(writer, item);
		}
		writer.WriteArrayEnd();
	}

	public static void WriteIntDictionary(SimpleJson.Writer writer, Dictionary<string, int> dict)
	{
		writer.WriteObjectStart();
		foreach (KeyValuePair<string, int> item in dict)
		{
			writer.WriteProperty(item.Key, item.Value);
		}
		writer.WriteObjectEnd();
	}

	public static void WriteRuntimeObject(SimpleJson.Writer writer, Object obj)
	{
		Container container = obj as Container;
		if ((bool)container)
		{
			WriteRuntimeContainer(writer, container);
			return;
		}
		Divert divert = obj as Divert;
		if ((bool)divert)
		{
			string name = "->";
			if (divert.isExternal)
			{
				name = "x()";
			}
			else if (divert.pushesToStack)
			{
				if (divert.stackPushType == PushPopType.Function)
				{
					name = "f()";
				}
				else if (divert.stackPushType == PushPopType.Tunnel)
				{
					name = "->t->";
				}
			}
			string content = ((!divert.hasVariableTarget) ? divert.targetPathString : divert.variableDivertName);
			writer.WriteObjectStart();
			writer.WriteProperty(name, content);
			if (divert.hasVariableTarget)
			{
				writer.WriteProperty("var", content: true);
			}
			if (divert.isConditional)
			{
				writer.WriteProperty("c", content: true);
			}
			if (divert.externalArgs > 0)
			{
				writer.WriteProperty("exArgs", divert.externalArgs);
			}
			writer.WriteObjectEnd();
			return;
		}
		ChoicePoint choicePoint = obj as ChoicePoint;
		if ((bool)choicePoint)
		{
			writer.WriteObjectStart();
			writer.WriteProperty("*", choicePoint.pathStringOnChoice);
			writer.WriteProperty("flg", choicePoint.flags);
			writer.WriteObjectEnd();
			return;
		}
		BoolValue boolValue = obj as BoolValue;
		if ((bool)boolValue)
		{
			writer.Write(boolValue.value);
			return;
		}
		IntValue intValue = obj as IntValue;
		if ((bool)intValue)
		{
			writer.Write(intValue.value);
			return;
		}
		FloatValue floatValue = obj as FloatValue;
		if ((bool)floatValue)
		{
			writer.Write(floatValue.value);
			return;
		}
		StringValue stringValue = obj as StringValue;
		if ((bool)stringValue)
		{
			if (stringValue.isNewline)
			{
				writer.Write("\\n", escape: false);
				return;
			}
			writer.WriteStringStart();
			writer.WriteStringInner("^");
			writer.WriteStringInner(stringValue.value);
			writer.WriteStringEnd();
			return;
		}
		ListValue listValue = obj as ListValue;
		if ((bool)listValue)
		{
			WriteInkList(writer, listValue);
			return;
		}
		DivertTargetValue divertTargetValue = obj as DivertTargetValue;
		if ((bool)divertTargetValue)
		{
			writer.WriteObjectStart();
			writer.WriteProperty("^->", divertTargetValue.value.componentsString);
			writer.WriteObjectEnd();
			return;
		}
		VariablePointerValue variablePointerValue = obj as VariablePointerValue;
		if ((bool)variablePointerValue)
		{
			writer.WriteObjectStart();
			writer.WriteProperty("^var", variablePointerValue.value);
			writer.WriteProperty("ci", variablePointerValue.contextIndex);
			writer.WriteObjectEnd();
			return;
		}
		if ((bool)(obj as Glue))
		{
			writer.Write("<>");
			return;
		}
		ControlCommand controlCommand = obj as ControlCommand;
		if ((bool)controlCommand)
		{
			writer.Write(_controlCommandNames[(int)controlCommand.commandType]);
			return;
		}
		NativeFunctionCall nativeFunctionCall = obj as NativeFunctionCall;
		if ((bool)nativeFunctionCall)
		{
			string text = nativeFunctionCall.name;
			if (text == "^")
			{
				text = "L^";
			}
			writer.Write(text);
			return;
		}
		VariableReference variableReference = obj as VariableReference;
		if ((bool)variableReference)
		{
			writer.WriteObjectStart();
			string pathStringForCount = variableReference.pathStringForCount;
			if (pathStringForCount != null)
			{
				writer.WriteProperty("CNT?", pathStringForCount);
			}
			else
			{
				writer.WriteProperty("VAR?", variableReference.name);
			}
			writer.WriteObjectEnd();
			return;
		}
		VariableAssignment variableAssignment = obj as VariableAssignment;
		if ((bool)variableAssignment)
		{
			writer.WriteObjectStart();
			string name2 = (variableAssignment.isGlobal ? "VAR=" : "temp=");
			writer.WriteProperty(name2, variableAssignment.variableName);
			if (!variableAssignment.isNewDeclaration)
			{
				writer.WriteProperty("re", content: true);
			}
			writer.WriteObjectEnd();
			return;
		}
		if ((bool)(obj as Void))
		{
			writer.Write("void");
			return;
		}
		Tag tag = obj as Tag;
		if ((bool)tag)
		{
			writer.WriteObjectStart();
			writer.WriteProperty("#", tag.text);
			writer.WriteObjectEnd();
			return;
		}
		Choice choice = obj as Choice;
		if ((bool)choice)
		{
			WriteChoice(writer, choice);
			return;
		}
		throw new Exception("Failed to write runtime object to JSON: " + obj);
	}

	public static Dictionary<string, Object> JObjectToDictionaryRuntimeObjs(Dictionary<string, object> jObject)
	{
		Dictionary<string, Object> dictionary = new Dictionary<string, Object>(jObject.Count);
		foreach (KeyValuePair<string, object> item in jObject)
		{
			dictionary[item.Key] = JTokenToRuntimeObject(item.Value);
		}
		return dictionary;
	}

	public static Dictionary<string, int> JObjectToIntDictionary(Dictionary<string, object> jObject)
	{
		Dictionary<string, int> dictionary = new Dictionary<string, int>(jObject.Count);
		foreach (KeyValuePair<string, object> item in jObject)
		{
			dictionary[item.Key] = (int)item.Value;
		}
		return dictionary;
	}

	public static Object JTokenToRuntimeObject(object token)
	{
		if (token is int || token is float || token is bool)
		{
			return Value.Create(token);
		}
		if (token is string)
		{
			string text = (string)token;
			switch (text[0])
			{
			case '^':
				return new StringValue(text.Substring(1));
			case '\n':
				if (text.Length == 1)
				{
					return new StringValue("\n");
				}
				break;
			}
			if (text == "<>")
			{
				return new Glue();
			}
			for (int i = 0; i < _controlCommandNames.Length; i++)
			{
				string text2 = _controlCommandNames[i];
				if (text == text2)
				{
					return new ControlCommand((ControlCommand.CommandType)i);
				}
			}
			if (text == "L^")
			{
				text = "^";
			}
			if (NativeFunctionCall.CallExistsWithName(text))
			{
				return NativeFunctionCall.CallWithName(text);
			}
			switch (text)
			{
			case "->->":
				return ControlCommand.PopTunnel();
			case "~ret":
				return ControlCommand.PopFunction();
			case "void":
				return new Void();
			}
		}
		if (token is Dictionary<string, object>)
		{
			Dictionary<string, object> dictionary = (Dictionary<string, object>)token;
			if (dictionary.TryGetValue("^->", out var value))
			{
				return new DivertTargetValue(new Path((string)value));
			}
			if (dictionary.TryGetValue("^var", out value))
			{
				VariablePointerValue variablePointerValue = new VariablePointerValue((string)value);
				if (dictionary.TryGetValue("ci", out value))
				{
					variablePointerValue.contextIndex = (int)value;
				}
				return variablePointerValue;
			}
			bool flag = false;
			bool pushesToStack = false;
			PushPopType stackPushType = PushPopType.Function;
			bool flag2 = false;
			if (dictionary.TryGetValue("->", out value))
			{
				flag = true;
			}
			else if (dictionary.TryGetValue("f()", out value))
			{
				flag = true;
				pushesToStack = true;
				stackPushType = PushPopType.Function;
			}
			else if (dictionary.TryGetValue("->t->", out value))
			{
				flag = true;
				pushesToStack = true;
				stackPushType = PushPopType.Tunnel;
			}
			else if (dictionary.TryGetValue("x()", out value))
			{
				flag = true;
				flag2 = true;
				pushesToStack = false;
				stackPushType = PushPopType.Function;
			}
			if (flag)
			{
				Divert divert = new Divert();
				divert.pushesToStack = pushesToStack;
				divert.stackPushType = stackPushType;
				divert.isExternal = flag2;
				string text3 = value.ToString();
				if (dictionary.TryGetValue("var", out value))
				{
					divert.variableDivertName = text3;
				}
				else
				{
					divert.targetPathString = text3;
				}
				divert.isConditional = dictionary.TryGetValue("c", out value);
				if (flag2 && dictionary.TryGetValue("exArgs", out value))
				{
					divert.externalArgs = (int)value;
				}
				return divert;
			}
			if (dictionary.TryGetValue("*", out value))
			{
				ChoicePoint choicePoint = new ChoicePoint();
				choicePoint.pathStringOnChoice = value.ToString();
				if (dictionary.TryGetValue("flg", out value))
				{
					choicePoint.flags = (int)value;
				}
				return choicePoint;
			}
			if (dictionary.TryGetValue("VAR?", out value))
			{
				return new VariableReference(value.ToString());
			}
			if (dictionary.TryGetValue("CNT?", out value))
			{
				return new VariableReference
				{
					pathStringForCount = value.ToString()
				};
			}
			bool flag3 = false;
			bool isGlobal = false;
			if (dictionary.TryGetValue("VAR=", out value))
			{
				flag3 = true;
				isGlobal = true;
			}
			else if (dictionary.TryGetValue("temp=", out value))
			{
				flag3 = true;
				isGlobal = false;
			}
			if (flag3)
			{
				string? variableName = value.ToString();
				bool isNewDeclaration = !dictionary.TryGetValue("re", out value);
				return new VariableAssignment(variableName, isNewDeclaration)
				{
					isGlobal = isGlobal
				};
			}
			if (dictionary.TryGetValue("#", out value))
			{
				return new Tag((string)value);
			}
			if (dictionary.TryGetValue("list", out value))
			{
				Dictionary<string, object> obj = (Dictionary<string, object>)value;
				InkList inkList = new InkList();
				if (dictionary.TryGetValue("origins", out value))
				{
					List<object> source = (List<object>)value;
					inkList.SetInitialOriginNames(source.Cast<string>().ToList());
				}
				foreach (KeyValuePair<string, object> item in obj)
				{
					InkListItem key = new InkListItem(item.Key);
					int value2 = (int)item.Value;
					inkList.Add(key, value2);
				}
				return new ListValue(inkList);
			}
			if (dictionary["originalChoicePath"] != null)
			{
				return JObjectToChoice(dictionary);
			}
		}
		if (token is List<object>)
		{
			return JArrayToContainer((List<object>)token);
		}
		if (token == null)
		{
			return null;
		}
		throw new Exception("Failed to convert token to runtime object: " + token);
	}

	public static void WriteRuntimeContainer(SimpleJson.Writer writer, Container container, bool withoutName = false)
	{
		writer.WriteArrayStart();
		foreach (Object item in container.content)
		{
			WriteRuntimeObject(writer, item);
		}
		Dictionary<string, Object> namedOnlyContent = container.namedOnlyContent;
		int countFlags = container.countFlags;
		bool flag = container.name != null && !withoutName;
		bool flag2 = (namedOnlyContent != null || countFlags > 0) | flag;
		if (flag2)
		{
			writer.WriteObjectStart();
		}
		if (namedOnlyContent != null)
		{
			foreach (KeyValuePair<string, Object> item2 in namedOnlyContent)
			{
				string key = item2.Key;
				Container container2 = item2.Value as Container;
				writer.WritePropertyStart(key);
				WriteRuntimeContainer(writer, container2, withoutName: true);
				writer.WritePropertyEnd();
			}
		}
		if (countFlags > 0)
		{
			writer.WriteProperty("#f", countFlags);
		}
		if (flag)
		{
			writer.WriteProperty("#n", container.name);
		}
		if (flag2)
		{
			writer.WriteObjectEnd();
		}
		else
		{
			writer.WriteNull();
		}
		writer.WriteArrayEnd();
	}

	private static Container JArrayToContainer(List<object> jArray)
	{
		Container container = new Container();
		container.content = JArrayToRuntimeObjList(jArray, skipLast: true);
		if (jArray[jArray.Count - 1] is Dictionary<string, object> dictionary)
		{
			Dictionary<string, Object> dictionary2 = new Dictionary<string, Object>(dictionary.Count);
			foreach (KeyValuePair<string, object> item in dictionary)
			{
				if (item.Key == "#f")
				{
					container.countFlags = (int)item.Value;
					continue;
				}
				if (item.Key == "#n")
				{
					container.name = item.Value.ToString();
					continue;
				}
				Object obj = JTokenToRuntimeObject(item.Value);
				Container container2 = obj as Container;
				if ((bool)container2)
				{
					container2.name = item.Key;
				}
				dictionary2[item.Key] = obj;
			}
			container.namedOnlyContent = dictionary2;
		}
		return container;
	}

	private static Choice JObjectToChoice(Dictionary<string, object> jObj)
	{
		Choice choice = new Choice();
		choice.text = jObj["text"].ToString();
		choice.index = (int)jObj["index"];
		choice.sourcePath = jObj["originalChoicePath"].ToString();
		choice.originalThreadIndex = (int)jObj["originalThreadIndex"];
		choice.pathStringOnChoice = jObj["targetPath"].ToString();
		choice.tags = JArrayToTags(jObj, choice);
		return choice;
	}

	private static List<string> JArrayToTags(Dictionary<string, object> jObj, Choice choice)
	{
		if (!jObj.TryGetValue("tags", out var value))
		{
			return null;
		}
		List<string> list = new List<string>();
		foreach (object item in (List<object>)value)
		{
			list.Add(item.ToString());
		}
		return list;
	}

	public static void WriteChoice(SimpleJson.Writer writer, Choice choice)
	{
		writer.WriteObjectStart();
		writer.WriteProperty("text", choice.text);
		writer.WriteProperty("index", choice.index);
		writer.WriteProperty("originalChoicePath", choice.sourcePath);
		writer.WriteProperty("originalThreadIndex", choice.originalThreadIndex);
		writer.WriteProperty("targetPath", choice.pathStringOnChoice);
		WriteChoiceTags(writer, choice);
		writer.WriteObjectEnd();
	}

	private static void WriteChoiceTags(SimpleJson.Writer writer, Choice choice)
	{
		if (choice.tags == null || choice.tags.Count == 0)
		{
			return;
		}
		writer.WritePropertyStart("tags");
		writer.WriteArrayStart();
		foreach (string tag in choice.tags)
		{
			writer.Write(tag);
		}
		writer.WriteArrayEnd();
		writer.WritePropertyEnd();
	}

	private static void WriteInkList(SimpleJson.Writer writer, ListValue listVal)
	{
		InkList value = listVal.value;
		writer.WriteObjectStart();
		writer.WritePropertyStart("list");
		writer.WriteObjectStart();
		foreach (KeyValuePair<InkListItem, int> item in value)
		{
			InkListItem key = item.Key;
			int value2 = item.Value;
			writer.WritePropertyNameStart();
			writer.WritePropertyNameInner(key.originName ?? "?");
			writer.WritePropertyNameInner(".");
			writer.WritePropertyNameInner(key.itemName);
			writer.WritePropertyNameEnd();
			writer.Write(value2);
			writer.WritePropertyEnd();
		}
		writer.WriteObjectEnd();
		writer.WritePropertyEnd();
		if (value.Count == 0 && value.originNames != null && value.originNames.Count > 0)
		{
			writer.WritePropertyStart("origins");
			writer.WriteArrayStart();
			foreach (string originName in value.originNames)
			{
				writer.Write(originName);
			}
			writer.WriteArrayEnd();
			writer.WritePropertyEnd();
		}
		writer.WriteObjectEnd();
	}

	public static ListDefinitionsOrigin JTokenToListDefinitions(object obj)
	{
		Dictionary<string, object> obj2 = (Dictionary<string, object>)obj;
		List<ListDefinition> list = new List<ListDefinition>();
		foreach (KeyValuePair<string, object> item2 in obj2)
		{
			string key = item2.Key;
			Dictionary<string, object> obj3 = (Dictionary<string, object>)item2.Value;
			Dictionary<string, int> dictionary = new Dictionary<string, int>();
			foreach (KeyValuePair<string, object> item3 in obj3)
			{
				dictionary.Add(item3.Key, (int)item3.Value);
			}
			ListDefinition item = new ListDefinition(key, dictionary);
			list.Add(item);
		}
		return new ListDefinitionsOrigin(list);
	}

	static Json()
	{
		_controlCommandNames[0] = "ev";
		_controlCommandNames[1] = "out";
		_controlCommandNames[2] = "/ev";
		_controlCommandNames[3] = "du";
		_controlCommandNames[4] = "pop";
		_controlCommandNames[5] = "~ret";
		_controlCommandNames[6] = "->->";
		_controlCommandNames[7] = "str";
		_controlCommandNames[8] = "/str";
		_controlCommandNames[9] = "nop";
		_controlCommandNames[10] = "choiceCnt";
		_controlCommandNames[11] = "turn";
		_controlCommandNames[12] = "turns";
		_controlCommandNames[13] = "readc";
		_controlCommandNames[14] = "rnd";
		_controlCommandNames[15] = "srnd";
		_controlCommandNames[16] = "visit";
		_controlCommandNames[17] = "seq";
		_controlCommandNames[18] = "thread";
		_controlCommandNames[19] = "done";
		_controlCommandNames[20] = "end";
		_controlCommandNames[21] = "listInt";
		_controlCommandNames[22] = "range";
		_controlCommandNames[23] = "lrnd";
		_controlCommandNames[24] = "#";
		_controlCommandNames[25] = "/#";
		for (int i = 0; i < 26; i++)
		{
			if (_controlCommandNames[i] == null)
			{
				throw new Exception("Control command not accounted for in serialisation");
			}
		}
	}
}
