using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace Ink.Runtime;

public class StoryState
{
	public const int kInkSaveStateVersion = 10;

	private const int kMinCompatibleLoadVersion = 8;

	private string _currentText;

	private List<string> _currentTags;

	private List<string> _aliveFlowNames;

	private Dictionary<string, int> _visitCounts;

	private Dictionary<string, int> _turnIndices;

	private bool _outputStreamTextDirty = true;

	private bool _outputStreamTagsDirty = true;

	private StatePatch _patch;

	private Flow _currentFlow;

	private Dictionary<string, Flow> _namedFlows;

	private const string kDefaultFlowName = "DEFAULT_FLOW";

	private bool _aliveFlowNamesDirty = true;

	public int callstackDepth => callStack.depth;

	public List<Object> outputStream => _currentFlow.outputStream;

	public List<Choice> currentChoices
	{
		get
		{
			if (canContinue)
			{
				return new List<Choice>();
			}
			return _currentFlow.currentChoices;
		}
	}

	public List<Choice> generatedChoices => _currentFlow.currentChoices;

	public List<string> currentErrors { get; private set; }

	public List<string> currentWarnings { get; private set; }

	public VariablesState variablesState { get; private set; }

	public CallStack callStack => _currentFlow.callStack;

	public List<Object> evaluationStack { get; private set; }

	public Pointer divertedPointer { get; set; }

	public int currentTurnIndex { get; private set; }

	public int storySeed { get; set; }

	public int previousRandom { get; set; }

	public bool didSafeExit { get; set; }

	public Story story { get; set; }

	public string currentPathString
	{
		get
		{
			Pointer pointer = currentPointer;
			if (pointer.isNull)
			{
				return null;
			}
			return pointer.path.ToString();
		}
	}

	public string previousPathString
	{
		get
		{
			Pointer pointer = previousPointer;
			if (pointer.isNull)
			{
				return null;
			}
			return pointer.path.ToString();
		}
	}

	public Pointer currentPointer
	{
		get
		{
			return callStack.currentElement.currentPointer;
		}
		set
		{
			callStack.currentElement.currentPointer = value;
		}
	}

	public Pointer previousPointer
	{
		get
		{
			return callStack.currentThread.previousPointer;
		}
		set
		{
			callStack.currentThread.previousPointer = value;
		}
	}

	public bool canContinue
	{
		get
		{
			if (!currentPointer.isNull)
			{
				return !hasError;
			}
			return false;
		}
	}

	public bool hasError
	{
		get
		{
			if (currentErrors != null)
			{
				return currentErrors.Count > 0;
			}
			return false;
		}
	}

	public bool hasWarning
	{
		get
		{
			if (currentWarnings != null)
			{
				return currentWarnings.Count > 0;
			}
			return false;
		}
	}

	public string currentText
	{
		get
		{
			if (_outputStreamTextDirty)
			{
				StringBuilder stringBuilder = new StringBuilder();
				bool flag = false;
				foreach (Object item in outputStream)
				{
					StringValue stringValue = item as StringValue;
					if (!flag && stringValue != null)
					{
						stringBuilder.Append(stringValue.value);
						continue;
					}
					ControlCommand controlCommand = item as ControlCommand;
					if (controlCommand != null)
					{
						if (controlCommand.commandType == ControlCommand.CommandType.BeginTag)
						{
							flag = true;
						}
						else if (controlCommand.commandType == ControlCommand.CommandType.EndTag)
						{
							flag = false;
						}
					}
				}
				_currentText = CleanOutputWhitespace(stringBuilder.ToString());
				_outputStreamTextDirty = false;
			}
			return _currentText;
		}
	}

	public List<string> currentTags
	{
		get
		{
			if (_outputStreamTagsDirty)
			{
				_currentTags = new List<string>();
				bool flag = false;
				StringBuilder stringBuilder = new StringBuilder();
				foreach (Object item4 in outputStream)
				{
					ControlCommand controlCommand = item4 as ControlCommand;
					if (controlCommand != null)
					{
						if (controlCommand.commandType == ControlCommand.CommandType.BeginTag)
						{
							if (flag && stringBuilder.Length > 0)
							{
								string item = CleanOutputWhitespace(stringBuilder.ToString());
								_currentTags.Add(item);
								stringBuilder.Clear();
							}
							flag = true;
						}
						else if (controlCommand.commandType == ControlCommand.CommandType.EndTag)
						{
							if (stringBuilder.Length > 0)
							{
								string item2 = CleanOutputWhitespace(stringBuilder.ToString());
								_currentTags.Add(item2);
								stringBuilder.Clear();
							}
							flag = false;
						}
					}
					else if (flag)
					{
						StringValue stringValue = item4 as StringValue;
						if (stringValue != null)
						{
							stringBuilder.Append(stringValue.value);
						}
					}
					else
					{
						Tag tag = item4 as Tag;
						if (tag != null && tag.text != null && tag.text.Length > 0)
						{
							_currentTags.Add(tag.text);
						}
					}
				}
				if (stringBuilder.Length > 0)
				{
					string item3 = CleanOutputWhitespace(stringBuilder.ToString());
					_currentTags.Add(item3);
					stringBuilder.Clear();
				}
				_outputStreamTagsDirty = false;
			}
			return _currentTags;
		}
	}

	public string currentFlowName => _currentFlow.name;

	public bool currentFlowIsDefaultFlow => _currentFlow.name == "DEFAULT_FLOW";

	public List<string> aliveFlowNames
	{
		get
		{
			if (_aliveFlowNamesDirty)
			{
				_aliveFlowNames = new List<string>();
				if (_namedFlows != null)
				{
					foreach (string key in _namedFlows.Keys)
					{
						if (key != "DEFAULT_FLOW")
						{
							_aliveFlowNames.Add(key);
						}
					}
				}
				_aliveFlowNamesDirty = false;
			}
			return _aliveFlowNames;
		}
	}

	public bool inExpressionEvaluation
	{
		get
		{
			return callStack.currentElement.inExpressionEvaluation;
		}
		set
		{
			callStack.currentElement.inExpressionEvaluation = value;
		}
	}

	public bool outputStreamEndsInNewline
	{
		get
		{
			if (outputStream.Count > 0)
			{
				int num = outputStream.Count - 1;
				while (num >= 0 && !(outputStream[num] is ControlCommand))
				{
					StringValue stringValue = outputStream[num] as StringValue;
					if ((bool)stringValue)
					{
						if (stringValue.isNewline)
						{
							return true;
						}
						if (stringValue.isNonWhitespace)
						{
							break;
						}
					}
					num--;
				}
			}
			return false;
		}
	}

	public bool outputStreamContainsContent
	{
		get
		{
			foreach (Object item in outputStream)
			{
				if (item is StringValue)
				{
					return true;
				}
			}
			return false;
		}
	}

	public bool inStringEvaluation
	{
		get
		{
			for (int num = outputStream.Count - 1; num >= 0; num--)
			{
				ControlCommand controlCommand = outputStream[num] as ControlCommand;
				if ((bool)controlCommand && controlCommand.commandType == ControlCommand.CommandType.BeginString)
				{
					return true;
				}
			}
			return false;
		}
	}

	public event Action onDidLoadState;

	public string ToJson()
	{
		SimpleJson.Writer writer = new SimpleJson.Writer();
		WriteJson(writer);
		return writer.ToString();
	}

	public void ToJson(Stream stream)
	{
		SimpleJson.Writer writer = new SimpleJson.Writer(stream);
		WriteJson(writer);
	}

	public void LoadJson(string json)
	{
		Dictionary<string, object> jObject = SimpleJson.TextToDictionary(json);
		LoadJsonObj(jObject);
		if (onDidLoadState != null)
		{
			onDidLoadState();
		}
	}

	public int VisitCountAtPathString(string pathString)
	{
		int count;
		if (_patch != null)
		{
			Container container = story.ContentAtPath(new Path(pathString)).container;
			if (container == null)
			{
				throw new Exception("Content at path not found: " + pathString);
			}
			if (_patch.TryGetVisitCount(container, out count))
			{
				return count;
			}
		}
		if (_visitCounts.TryGetValue(pathString, out count))
		{
			return count;
		}
		return 0;
	}

	public int VisitCountForContainer(Container container)
	{
		if (!container.visitsShouldBeCounted)
		{
			story.Error("Read count for target (" + container.name + " - on " + container.debugMetadata?.ToString() + ") unknown.");
			return 0;
		}
		int count = 0;
		if (_patch != null && _patch.TryGetVisitCount(container, out count))
		{
			return count;
		}
		string key = container.path.ToString();
		_visitCounts.TryGetValue(key, out count);
		return count;
	}

	public void IncrementVisitCountForContainer(Container container)
	{
		if (_patch != null)
		{
			int num = VisitCountForContainer(container);
			num++;
			_patch.SetVisitCount(container, num);
		}
		else
		{
			int value = 0;
			string key = container.path.ToString();
			_visitCounts.TryGetValue(key, out value);
			value++;
			_visitCounts[key] = value;
		}
	}

	public void RecordTurnIndexVisitToContainer(Container container)
	{
		if (_patch != null)
		{
			_patch.SetTurnIndex(container, currentTurnIndex);
			return;
		}
		string key = container.path.ToString();
		_turnIndices[key] = currentTurnIndex;
	}

	public int TurnsSinceForContainer(Container container)
	{
		if (!container.turnIndexShouldBeCounted)
		{
			story.Error("TURNS_SINCE() for target (" + container.name + " - on " + container.debugMetadata?.ToString() + ") unknown.");
		}
		int index = 0;
		if (_patch != null && _patch.TryGetTurnIndex(container, out index))
		{
			return currentTurnIndex - index;
		}
		string key = container.path.ToString();
		if (_turnIndices.TryGetValue(key, out index))
		{
			return currentTurnIndex - index;
		}
		return -1;
	}

	public string CleanOutputWhitespace(string str)
	{
		StringBuilder stringBuilder = new StringBuilder(str.Length);
		int num = -1;
		int num2 = 0;
		for (int num3 = 0; num3 < str.Length; num3++)
		{
			char c = str[num3];
			int num4;
			if (c != ' ')
			{
				num4 = ((c == '\t') ? 1 : 0);
				if (num4 == 0)
				{
					goto IL_0035;
				}
			}
			else
			{
				num4 = 1;
			}
			if (num == -1)
			{
				num = num3;
			}
			goto IL_0035;
			IL_0035:
			if (num4 == 0)
			{
				if (c != '\n' && num > 0 && num != num2)
				{
					stringBuilder.Append(' ');
				}
				num = -1;
			}
			if (c == '\n')
			{
				num2 = num3 + 1;
			}
			if (num4 == 0)
			{
				stringBuilder.Append(c);
			}
		}
		return stringBuilder.ToString();
	}

	public StoryState(Story story)
	{
		this.story = story;
		_currentFlow = new Flow("DEFAULT_FLOW", story);
		OutputStreamDirty();
		_aliveFlowNamesDirty = true;
		evaluationStack = new List<Object>();
		variablesState = new VariablesState(callStack, story.listDefinitions);
		_visitCounts = new Dictionary<string, int>();
		_turnIndices = new Dictionary<string, int>();
		currentTurnIndex = -1;
		int millisecond = DateTime.UtcNow.Millisecond;
		storySeed = new Random(millisecond).Next() % 100;
		previousRandom = 0;
		GoToStart();
	}

	public void GoToStart()
	{
		callStack.currentElement.currentPointer = Pointer.StartOf(story.mainContentContainer);
	}

	internal void SwitchFlow_Internal(string flowName)
	{
		if (flowName == null)
		{
			throw new Exception("Must pass a non-null string to Story.SwitchFlow");
		}
		if (_namedFlows == null)
		{
			_namedFlows = new Dictionary<string, Flow>();
			_namedFlows["DEFAULT_FLOW"] = _currentFlow;
		}
		if (!(flowName == _currentFlow.name))
		{
			if (!_namedFlows.TryGetValue(flowName, out var value))
			{
				value = new Flow(flowName, story);
				_namedFlows[flowName] = value;
				_aliveFlowNamesDirty = true;
			}
			_currentFlow = value;
			variablesState.callStack = _currentFlow.callStack;
			OutputStreamDirty();
		}
	}

	internal void SwitchToDefaultFlow_Internal()
	{
		if (_namedFlows != null)
		{
			SwitchFlow_Internal("DEFAULT_FLOW");
		}
	}

	internal void RemoveFlow_Internal(string flowName)
	{
		if (flowName == null)
		{
			throw new Exception("Must pass a non-null string to Story.DestroyFlow");
		}
		if (flowName == "DEFAULT_FLOW")
		{
			throw new Exception("Cannot destroy default flow");
		}
		if (_currentFlow.name == flowName)
		{
			SwitchToDefaultFlow_Internal();
		}
		_namedFlows.Remove(flowName);
		_aliveFlowNamesDirty = true;
	}

	public StoryState CopyAndStartPatching(bool forBackgroundSave)
	{
		StoryState storyState = new StoryState(story);
		storyState._patch = new StatePatch(_patch);
		storyState._currentFlow.name = _currentFlow.name;
		storyState._currentFlow.callStack = new CallStack(_currentFlow.callStack);
		storyState._currentFlow.outputStream.AddRange(_currentFlow.outputStream);
		storyState.OutputStreamDirty();
		if (forBackgroundSave)
		{
			foreach (Choice currentChoice in _currentFlow.currentChoices)
			{
				storyState._currentFlow.currentChoices.Add(currentChoice.Clone());
			}
		}
		else
		{
			storyState._currentFlow.currentChoices.AddRange(_currentFlow.currentChoices);
		}
		if (_namedFlows != null)
		{
			storyState._namedFlows = new Dictionary<string, Flow>();
			foreach (KeyValuePair<string, Flow> namedFlow in _namedFlows)
			{
				storyState._namedFlows[namedFlow.Key] = namedFlow.Value;
			}
			storyState._namedFlows[_currentFlow.name] = storyState._currentFlow;
			storyState._aliveFlowNamesDirty = true;
		}
		if (hasError)
		{
			storyState.currentErrors = new List<string>();
			storyState.currentErrors.AddRange(currentErrors);
		}
		if (hasWarning)
		{
			storyState.currentWarnings = new List<string>();
			storyState.currentWarnings.AddRange(currentWarnings);
		}
		storyState.variablesState = variablesState;
		storyState.variablesState.callStack = storyState.callStack;
		storyState.variablesState.patch = storyState._patch;
		storyState.evaluationStack.AddRange(evaluationStack);
		if (!divertedPointer.isNull)
		{
			storyState.divertedPointer = divertedPointer;
		}
		storyState.previousPointer = previousPointer;
		storyState._visitCounts = _visitCounts;
		storyState._turnIndices = _turnIndices;
		storyState.currentTurnIndex = currentTurnIndex;
		storyState.storySeed = storySeed;
		storyState.previousRandom = previousRandom;
		storyState.didSafeExit = didSafeExit;
		return storyState;
	}

	public void RestoreAfterPatch()
	{
		variablesState.callStack = callStack;
		variablesState.patch = _patch;
	}

	public void ApplyAnyPatch()
	{
		if (_patch == null)
		{
			return;
		}
		variablesState.ApplyPatch();
		foreach (KeyValuePair<Container, int> visitCount in _patch.visitCounts)
		{
			ApplyCountChanges(visitCount.Key, visitCount.Value, isVisit: true);
		}
		foreach (KeyValuePair<Container, int> turnIndex in _patch.turnIndices)
		{
			ApplyCountChanges(turnIndex.Key, turnIndex.Value, isVisit: false);
		}
		_patch = null;
	}

	private void ApplyCountChanges(Container container, int newCount, bool isVisit)
	{
		(isVisit ? _visitCounts : _turnIndices)[container.path.ToString()] = newCount;
	}

	private void WriteJson(SimpleJson.Writer writer)
	{
		writer.WriteObjectStart();
		writer.WritePropertyStart("flows");
		writer.WriteObjectStart();
		if (_namedFlows != null)
		{
			foreach (KeyValuePair<string, Flow> namedFlow in _namedFlows)
			{
				writer.WriteProperty(namedFlow.Key, namedFlow.Value.WriteJson);
			}
		}
		else
		{
			writer.WriteProperty(_currentFlow.name, _currentFlow.WriteJson);
		}
		writer.WriteObjectEnd();
		writer.WritePropertyEnd();
		writer.WriteProperty("currentFlowName", _currentFlow.name);
		writer.WriteProperty("variablesState", variablesState.WriteJson);
		writer.WriteProperty("evalStack", delegate(SimpleJson.Writer w)
		{
			Json.WriteListRuntimeObjs(w, evaluationStack);
		});
		if (!divertedPointer.isNull)
		{
			writer.WriteProperty("currentDivertTarget", divertedPointer.path.componentsString);
		}
		writer.WriteProperty("visitCounts", delegate(SimpleJson.Writer w)
		{
			Json.WriteIntDictionary(w, _visitCounts);
		});
		writer.WriteProperty("turnIndices", delegate(SimpleJson.Writer w)
		{
			Json.WriteIntDictionary(w, _turnIndices);
		});
		writer.WriteProperty("turnIdx", currentTurnIndex);
		writer.WriteProperty("storySeed", storySeed);
		writer.WriteProperty("previousRandom", previousRandom);
		writer.WriteProperty("inkSaveVersion", 10);
		writer.WriteProperty("inkFormatVersion", 21);
		writer.WriteObjectEnd();
	}

	private void LoadJsonObj(Dictionary<string, object> jObject)
	{
		object value = null;
		if (!jObject.TryGetValue("inkSaveVersion", out value))
		{
			throw new Exception("ink save format incorrect, can't load.");
		}
		if ((int)value < 8)
		{
			throw new Exception("Ink save format isn't compatible with the current version (saw '" + value?.ToString() + "', but minimum is " + 8 + "), so can't load.");
		}
		object value2 = null;
		if (jObject.TryGetValue("flows", out value2))
		{
			Dictionary<string, object> dictionary = (Dictionary<string, object>)value2;
			if (dictionary.Count == 1)
			{
				_namedFlows = null;
			}
			else if (_namedFlows == null)
			{
				_namedFlows = new Dictionary<string, Flow>();
			}
			else
			{
				_namedFlows.Clear();
			}
			foreach (KeyValuePair<string, object> item in dictionary)
			{
				string key = item.Key;
				Dictionary<string, object> jObject2 = (Dictionary<string, object>)item.Value;
				Flow value3 = new Flow(key, story, jObject2);
				if (dictionary.Count == 1)
				{
					_currentFlow = new Flow(key, story, jObject2);
				}
				else
				{
					_namedFlows[key] = value3;
				}
			}
			if (_namedFlows != null && _namedFlows.Count > 1)
			{
				string key2 = (string)jObject["currentFlowName"];
				_currentFlow = _namedFlows[key2];
			}
		}
		else
		{
			_namedFlows = null;
			_currentFlow.name = "DEFAULT_FLOW";
			_currentFlow.callStack.SetJsonToken((Dictionary<string, object>)jObject["callstackThreads"], story);
			_currentFlow.outputStream = Json.JArrayToRuntimeObjList((List<object>)jObject["outputStream"]);
			_currentFlow.currentChoices = Json.JArrayToRuntimeObjList<Choice>((List<object>)jObject["currentChoices"]);
			object value4 = null;
			jObject.TryGetValue("choiceThreads", out value4);
			_currentFlow.LoadFlowChoiceThreads((Dictionary<string, object>)value4, story);
		}
		OutputStreamDirty();
		_aliveFlowNamesDirty = true;
		variablesState.SetJsonToken((Dictionary<string, object>)jObject["variablesState"]);
		variablesState.callStack = _currentFlow.callStack;
		evaluationStack = Json.JArrayToRuntimeObjList((List<object>)jObject["evalStack"]);
		if (jObject.TryGetValue("currentDivertTarget", out var value5))
		{
			Path path = new Path(value5.ToString());
			divertedPointer = story.PointerAtPath(path);
		}
		_visitCounts = Json.JObjectToIntDictionary((Dictionary<string, object>)jObject["visitCounts"]);
		_turnIndices = Json.JObjectToIntDictionary((Dictionary<string, object>)jObject["turnIndices"]);
		currentTurnIndex = (int)jObject["turnIdx"];
		storySeed = (int)jObject["storySeed"];
		object value6 = null;
		if (jObject.TryGetValue("previousRandom", out value6))
		{
			previousRandom = (int)value6;
		}
		else
		{
			previousRandom = 0;
		}
	}

	public void ResetErrors()
	{
		currentErrors = null;
		currentWarnings = null;
	}

	public void ResetOutput(List<Object> objs = null)
	{
		outputStream.Clear();
		if (objs != null)
		{
			outputStream.AddRange(objs);
		}
		OutputStreamDirty();
	}

	public void PushToOutputStream(Object obj)
	{
		StringValue stringValue = obj as StringValue;
		if ((bool)stringValue)
		{
			List<StringValue> list = TrySplittingHeadTailWhitespace(stringValue);
			if (list != null)
			{
				foreach (StringValue item in list)
				{
					PushToOutputStreamIndividual(item);
				}
				OutputStreamDirty();
				return;
			}
		}
		PushToOutputStreamIndividual(obj);
		OutputStreamDirty();
	}

	public void PopFromOutputStream(int count)
	{
		outputStream.RemoveRange(outputStream.Count - count, count);
		OutputStreamDirty();
	}

	private List<StringValue> TrySplittingHeadTailWhitespace(StringValue single)
	{
		string value = single.value;
		int num = -1;
		int num2 = -1;
		for (int i = 0; i < value.Length; i++)
		{
			switch (value[i])
			{
			case '\n':
				if (num == -1)
				{
					num = i;
				}
				num2 = i;
				continue;
			case '\t':
			case ' ':
				continue;
			}
			break;
		}
		int num3 = -1;
		int num4 = -1;
		for (int num5 = value.Length - 1; num5 >= 0; num5--)
		{
			switch (value[num5])
			{
			case '\n':
				if (num3 == -1)
				{
					num3 = num5;
				}
				num4 = num5;
				continue;
			case '\t':
			case ' ':
				continue;
			}
			break;
		}
		if (num == -1 && num3 == -1)
		{
			return null;
		}
		List<StringValue> list = new List<StringValue>();
		int num6 = 0;
		int num7 = value.Length;
		if (num != -1)
		{
			if (num > 0)
			{
				StringValue item = new StringValue(value.Substring(0, num));
				list.Add(item);
			}
			list.Add(new StringValue("\n"));
			num6 = num2 + 1;
		}
		if (num3 != -1)
		{
			num7 = num4;
		}
		if (num7 > num6)
		{
			string str = value.Substring(num6, num7 - num6);
			list.Add(new StringValue(str));
		}
		if (num3 != -1 && num4 > num2)
		{
			list.Add(new StringValue("\n"));
			if (num3 < value.Length - 1)
			{
				int length = value.Length - num3 - 1;
				StringValue item2 = new StringValue(value.Substring(num3 + 1, length));
				list.Add(item2);
			}
		}
		return list;
	}

	private void PushToOutputStreamIndividual(Object obj)
	{
		Glue obj2 = obj as Glue;
		StringValue stringValue = obj as StringValue;
		bool flag = true;
		if ((bool)obj2)
		{
			TrimNewlinesFromOutputStream();
			flag = true;
		}
		else if ((bool)stringValue)
		{
			int num = -1;
			CallStack.Element currentElement = callStack.currentElement;
			if (currentElement.type == PushPopType.Function)
			{
				num = currentElement.functionStartInOuputStream;
			}
			int num2 = -1;
			for (int num3 = outputStream.Count - 1; num3 >= 0; num3--)
			{
				Object obj3 = outputStream[num3];
				ControlCommand controlCommand = obj3 as ControlCommand;
				if ((bool)(obj3 as Glue))
				{
					num2 = num3;
					break;
				}
				if ((bool)controlCommand && controlCommand.commandType == ControlCommand.CommandType.BeginString)
				{
					if (num3 >= num)
					{
						num = -1;
					}
					break;
				}
			}
			int num4 = -1;
			num4 = ((num2 != -1 && num != -1) ? Math.Min(num, num2) : ((num2 == -1) ? num : num2));
			if (num4 != -1)
			{
				if (stringValue.isNewline)
				{
					flag = false;
				}
				else if (stringValue.isNonWhitespace)
				{
					if (num2 > -1)
					{
						RemoveExistingGlue();
					}
					if (num > -1)
					{
						List<CallStack.Element> elements = callStack.elements;
						for (int num5 = elements.Count - 1; num5 >= 0; num5--)
						{
							CallStack.Element element = elements[num5];
							if (element.type != PushPopType.Function)
							{
								break;
							}
							element.functionStartInOuputStream = -1;
						}
					}
				}
			}
			else if (stringValue.isNewline && (outputStreamEndsInNewline || !outputStreamContainsContent))
			{
				flag = false;
			}
		}
		if (flag)
		{
			outputStream.Add(obj);
			OutputStreamDirty();
		}
	}

	private void TrimNewlinesFromOutputStream()
	{
		int num = -1;
		for (int num2 = outputStream.Count - 1; num2 >= 0; num2--)
		{
			Object obj = outputStream[num2];
			ControlCommand controlCommand = obj as ControlCommand;
			StringValue stringValue = obj as StringValue;
			if ((bool)controlCommand || ((bool)stringValue && stringValue.isNonWhitespace))
			{
				break;
			}
			if ((bool)stringValue && stringValue.isNewline)
			{
				num = num2;
			}
		}
		if (num >= 0)
		{
			int num2 = num;
			while (num2 < outputStream.Count)
			{
				if ((bool)(outputStream[num2] as StringValue))
				{
					outputStream.RemoveAt(num2);
				}
				else
				{
					num2++;
				}
			}
		}
		OutputStreamDirty();
	}

	private void RemoveExistingGlue()
	{
		for (int num = outputStream.Count - 1; num >= 0; num--)
		{
			Object obj = outputStream[num];
			if (obj is Glue)
			{
				outputStream.RemoveAt(num);
			}
			else if (obj is ControlCommand)
			{
				break;
			}
		}
		OutputStreamDirty();
	}

	public void PushEvaluationStack(Object obj)
	{
		ListValue listValue = obj as ListValue;
		if ((bool)listValue)
		{
			InkList value = listValue.value;
			if (value.originNames != null)
			{
				if (value.origins == null)
				{
					value.origins = new List<ListDefinition>();
				}
				value.origins.Clear();
				foreach (string originName in value.originNames)
				{
					ListDefinition def = null;
					story.listDefinitions.TryListGetDefinition(originName, out def);
					if (!value.origins.Contains(def))
					{
						value.origins.Add(def);
					}
				}
			}
		}
		evaluationStack.Add(obj);
	}

	public Object PopEvaluationStack()
	{
		Object result = evaluationStack[evaluationStack.Count - 1];
		evaluationStack.RemoveAt(evaluationStack.Count - 1);
		return result;
	}

	public Object PeekEvaluationStack()
	{
		return evaluationStack[evaluationStack.Count - 1];
	}

	public List<Object> PopEvaluationStack(int numberOfObjects)
	{
		if (numberOfObjects > evaluationStack.Count)
		{
			throw new Exception("trying to pop too many objects");
		}
		List<Object> range = evaluationStack.GetRange(evaluationStack.Count - numberOfObjects, numberOfObjects);
		evaluationStack.RemoveRange(evaluationStack.Count - numberOfObjects, numberOfObjects);
		return range;
	}

	public void ForceEnd()
	{
		callStack.Reset();
		_currentFlow.currentChoices.Clear();
		currentPointer = Pointer.Null;
		previousPointer = Pointer.Null;
		didSafeExit = true;
	}

	private void TrimWhitespaceFromFunctionEnd()
	{
		int num = callStack.currentElement.functionStartInOuputStream;
		if (num == -1)
		{
			num = 0;
		}
		for (int num2 = outputStream.Count - 1; num2 >= num; num2--)
		{
			Object obj = outputStream[num2];
			StringValue stringValue = obj as StringValue;
			ControlCommand controlCommand = obj as ControlCommand;
			if ((bool)stringValue)
			{
				if ((bool)controlCommand || (!stringValue.isNewline && !stringValue.isInlineWhitespace))
				{
					break;
				}
				outputStream.RemoveAt(num2);
				OutputStreamDirty();
			}
		}
	}

	public void PopCallstack(PushPopType? popType = null)
	{
		if (callStack.currentElement.type == PushPopType.Function)
		{
			TrimWhitespaceFromFunctionEnd();
		}
		callStack.Pop(popType);
	}

	public void SetChosenPath(Path path, bool incrementingTurnIndex)
	{
		_currentFlow.currentChoices.Clear();
		Pointer pointer = story.PointerAtPath(path);
		if (!pointer.isNull && pointer.index == -1)
		{
			pointer.index = 0;
		}
		currentPointer = pointer;
		if (incrementingTurnIndex)
		{
			currentTurnIndex++;
		}
	}

	public void StartFunctionEvaluationFromGame(Container funcContainer, params object[] arguments)
	{
		callStack.Push(PushPopType.FunctionEvaluationFromGame, evaluationStack.Count);
		callStack.currentElement.currentPointer = Pointer.StartOf(funcContainer);
		PassArgumentsToEvaluationStack(arguments);
	}

	public void PassArgumentsToEvaluationStack(params object[] arguments)
	{
		if (arguments == null)
		{
			return;
		}
		for (int i = 0; i < arguments.Length; i++)
		{
			if (!(arguments[i] is int) && !(arguments[i] is float) && !(arguments[i] is string) && !(arguments[i] is bool) && !(arguments[i] is InkList))
			{
				throw new ArgumentException("ink arguments when calling EvaluateFunction / ChoosePathStringWithParameters must be int, float, string, bool or InkList. Argument was " + ((arguments[i] == null) ? "null" : arguments[i].GetType().Name));
			}
			PushEvaluationStack(Value.Create(arguments[i]));
		}
	}

	public bool TryExitFunctionEvaluationFromGame()
	{
		if (callStack.currentElement.type == PushPopType.FunctionEvaluationFromGame)
		{
			currentPointer = Pointer.Null;
			didSafeExit = true;
			return true;
		}
		return false;
	}

	public object CompleteFunctionEvaluationFromGame()
	{
		if (callStack.currentElement.type != PushPopType.FunctionEvaluationFromGame)
		{
			throw new Exception("Expected external function evaluation to be complete. Stack trace: " + callStack.callStackTrace);
		}
		int evaluationStackHeightWhenPushed = callStack.currentElement.evaluationStackHeightWhenPushed;
		Object obj = null;
		while (evaluationStack.Count > evaluationStackHeightWhenPushed)
		{
			Object obj2 = PopEvaluationStack();
			if (obj == null)
			{
				obj = obj2;
			}
		}
		PopCallstack(PushPopType.FunctionEvaluationFromGame);
		if ((bool)obj)
		{
			if (obj is Void)
			{
				return null;
			}
			Value value = obj as Value;
			if (value.valueType == ValueType.DivertTarget)
			{
				return value.valueObject.ToString();
			}
			return value.valueObject;
		}
		return null;
	}

	public void AddError(string message, bool isWarning)
	{
		if (!isWarning)
		{
			if (currentErrors == null)
			{
				currentErrors = new List<string>();
			}
			currentErrors.Add(message);
		}
		else
		{
			if (currentWarnings == null)
			{
				currentWarnings = new List<string>();
			}
			currentWarnings.Add(message);
		}
	}

	private void OutputStreamDirty()
	{
		_outputStreamTextDirty = true;
		_outputStreamTagsDirty = true;
	}
}
