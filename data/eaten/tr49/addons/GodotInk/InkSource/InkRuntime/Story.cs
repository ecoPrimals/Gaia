using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;

namespace Ink.Runtime;

public class Story : Object
{
	private enum OutputStateChange
	{
		NoChange,
		ExtendedBeyondNewline,
		NewlineRemoved
	}

	public delegate object ExternalFunction(object[] args);

	public delegate void VariableObserver(string variableName, object newValue);

	private struct ExternalFunctionDef
	{
		public ExternalFunction function;

		public bool lookaheadSafe;
	}

	private enum LookaheadUnsafeFeatureSeen
	{
		None,
		ExternalFunction,
		ChoicePoint
	}

	public const int inkVersionCurrent = 21;

	private const int inkVersionMinimumCompatible = 18;

	private List<Container> _prevContainers = new List<Container>();

	private Container _mainContentContainer;

	private ListDefinitionsOrigin _listDefinitions;

	private Dictionary<string, ExternalFunctionDef> _externals;

	private Dictionary<string, VariableObserver> _variableObservers;

	private bool _hasValidatedExternals;

	private Container _temporaryEvaluationContainer;

	private StoryState _state;

	private bool _asyncContinueActive;

	private StoryState _stateSnapshotAtLastNewline;

	private LookaheadUnsafeFeatureSeen _sawLookaheadUnsafeFeatureAfterNewline;

	private int _recursiveContinueCount;

	private bool _asyncSaving;

	private Profiler _profiler;

	public List<Choice> currentChoices
	{
		get
		{
			List<Choice> list = new List<Choice>();
			foreach (Choice currentChoice in _state.currentChoices)
			{
				if (!currentChoice.isInvisibleDefault)
				{
					currentChoice.index = list.Count;
					list.Add(currentChoice);
				}
			}
			return list;
		}
	}

	public string currentText
	{
		get
		{
			IfAsyncWeCant("call currentText since it's a work in progress");
			return state.currentText;
		}
	}

	public List<string> currentTags
	{
		get
		{
			IfAsyncWeCant("call currentTags since it's a work in progress");
			return state.currentTags;
		}
	}

	public List<string> currentErrors => state.currentErrors;

	public List<string> currentWarnings => state.currentWarnings;

	public string currentFlowName => state.currentFlowName;

	public bool currentFlowIsDefaultFlow => state.currentFlowIsDefaultFlow;

	public List<string> aliveFlowNames => state.aliveFlowNames;

	public bool hasError => state.hasError;

	public bool hasWarning => state.hasWarning;

	public VariablesState variablesState => state.variablesState;

	public ListDefinitionsOrigin listDefinitions => _listDefinitions;

	public StoryState state => _state;

	public bool canContinue => state.canContinue;

	public bool asyncContinueComplete => !_asyncContinueActive;

	public bool allowExternalFunctionFallbacks { get; set; }

	public List<string> globalTags => TagsAtStartOfFlowContainerWithPathString("");

	private DebugMetadata currentDebugMetadata
	{
		get
		{
			Pointer currentPointer = state.currentPointer;
			if (!currentPointer.isNull)
			{
				DebugMetadata debugMetadata = currentPointer.Resolve().debugMetadata;
				if (debugMetadata != null)
				{
					return debugMetadata;
				}
			}
			for (int num = state.callStack.elements.Count - 1; num >= 0; num--)
			{
				currentPointer = state.callStack.elements[num].currentPointer;
				if (!currentPointer.isNull && currentPointer.Resolve() != null)
				{
					DebugMetadata debugMetadata = currentPointer.Resolve().debugMetadata;
					if (debugMetadata != null)
					{
						return debugMetadata;
					}
				}
			}
			for (int num2 = state.outputStream.Count - 1; num2 >= 0; num2--)
			{
				DebugMetadata debugMetadata = state.outputStream[num2].debugMetadata;
				if (debugMetadata != null)
				{
					return debugMetadata;
				}
			}
			return null;
		}
	}

	private int currentLineNumber => currentDebugMetadata?.startLineNumber ?? 0;

	public Container mainContentContainer
	{
		get
		{
			if ((bool)_temporaryEvaluationContainer)
			{
				return _temporaryEvaluationContainer;
			}
			return _mainContentContainer;
		}
	}

	public event ErrorHandler onError;

	public event Action onDidContinue;

	public event Action<Choice> onMakeChoice;

	public event Action<string, object[]> onEvaluateFunction;

	public event Action<string, object[], string, object> onCompleteEvaluateFunction;

	public event Action<string, object[]> onChoosePathString;

	public Profiler StartProfiling()
	{
		IfAsyncWeCant("start profiling");
		_profiler = new Profiler();
		return _profiler;
	}

	public void EndProfiling()
	{
		_profiler = null;
	}

	public Story(Container contentContainer, List<ListDefinition> lists = null)
	{
		_mainContentContainer = contentContainer;
		if (lists != null)
		{
			_listDefinitions = new ListDefinitionsOrigin(lists);
		}
		_externals = new Dictionary<string, ExternalFunctionDef>();
	}

	public Story(string jsonString)
		: this(null, null)
	{
		Dictionary<string, object> dictionary = SimpleJson.TextToDictionary(jsonString);
		int num = (int)(dictionary["inkVersion"] ?? throw new Exception("ink version number not found. Are you sure it's a valid .ink.json file?"));
		if (num > 21)
		{
			throw new Exception("Version of ink used to build story was newer than the current version of the engine");
		}
		if (num < 18)
		{
			throw new Exception("Version of ink used to build story is too old to be loaded by this version of the engine");
		}
		_ = 21;
		object obj = dictionary["root"];
		if (obj == null)
		{
			throw new Exception("Root node for ink not found. Are you sure it's a valid .ink.json file?");
		}
		if (dictionary.TryGetValue("listDefs", out var value))
		{
			_listDefinitions = Json.JTokenToListDefinitions(value);
		}
		_mainContentContainer = Json.JTokenToRuntimeObject(obj) as Container;
		ResetState();
	}

	public string ToJson()
	{
		SimpleJson.Writer writer = new SimpleJson.Writer();
		ToJson(writer);
		return writer.ToString();
	}

	public void ToJson(Stream stream)
	{
		SimpleJson.Writer writer = new SimpleJson.Writer(stream);
		ToJson(writer);
	}

	private void ToJson(SimpleJson.Writer writer)
	{
		writer.WriteObjectStart();
		writer.WriteProperty("inkVersion", 21);
		writer.WriteProperty("root", delegate(SimpleJson.Writer w)
		{
			Json.WriteRuntimeContainer(w, _mainContentContainer);
		});
		if (_listDefinitions != null)
		{
			writer.WritePropertyStart("listDefs");
			writer.WriteObjectStart();
			foreach (ListDefinition list in _listDefinitions.lists)
			{
				writer.WritePropertyStart(list.name);
				writer.WriteObjectStart();
				foreach (KeyValuePair<InkListItem, int> item in list.items)
				{
					InkListItem key = item.Key;
					int value = item.Value;
					writer.WriteProperty(key.itemName, value);
				}
				writer.WriteObjectEnd();
				writer.WritePropertyEnd();
			}
			writer.WriteObjectEnd();
			writer.WritePropertyEnd();
		}
		writer.WriteObjectEnd();
	}

	public void ResetState()
	{
		IfAsyncWeCant("ResetState");
		_state = new StoryState(this);
		_state.variablesState.variableChangedEvent += VariableStateDidChangeEvent;
		ResetGlobals();
	}

	private void ResetErrors()
	{
		_state.ResetErrors();
	}

	public void ResetCallstack()
	{
		IfAsyncWeCant("ResetCallstack");
		_state.ForceEnd();
	}

	private void ResetGlobals()
	{
		if (_mainContentContainer.namedContent.ContainsKey("global decl"))
		{
			Pointer currentPointer = state.currentPointer;
			ChoosePath(new Path("global decl"), incrementingTurnIndex: false);
			ContinueInternal();
			state.currentPointer = currentPointer;
		}
		state.variablesState.SnapshotDefaultGlobals();
	}

	public void SwitchFlow(string flowName)
	{
		IfAsyncWeCant("switch flow");
		if (_asyncSaving)
		{
			throw new Exception("Story is already in background saving mode, can't switch flow to " + flowName);
		}
		state.SwitchFlow_Internal(flowName);
	}

	public void RemoveFlow(string flowName)
	{
		state.RemoveFlow_Internal(flowName);
	}

	public void SwitchToDefaultFlow()
	{
		state.SwitchToDefaultFlow_Internal();
	}

	public string Continue()
	{
		ContinueAsync(0f);
		return currentText;
	}

	public void ContinueAsync(float millisecsLimitAsync)
	{
		if (!_hasValidatedExternals)
		{
			ValidateExternalBindings();
		}
		ContinueInternal(millisecsLimitAsync);
	}

	private void ContinueInternal(float millisecsLimitAsync = 0f)
	{
		if (_profiler != null)
		{
			_profiler.PreContinue();
		}
		bool flag = millisecsLimitAsync > 0f;
		_recursiveContinueCount++;
		if (!_asyncContinueActive)
		{
			_asyncContinueActive = flag;
			if (!canContinue)
			{
				throw new Exception("Can't continue - should check canContinue before calling Continue");
			}
			_state.didSafeExit = false;
			_state.ResetOutput();
			if (_recursiveContinueCount == 1)
			{
				_state.variablesState.StartVariableObservation();
			}
		}
		else if (_asyncContinueActive && !flag)
		{
			_asyncContinueActive = false;
		}
		Stopwatch stopwatch = new Stopwatch();
		stopwatch.Start();
		bool flag2 = false;
		_sawLookaheadUnsafeFeatureAfterNewline = LookaheadUnsafeFeatureSeen.None;
		do
		{
			try
			{
				flag2 = ContinueSingleStep();
			}
			catch (StoryException ex)
			{
				AddError(ex.Message, isWarning: false, ex.useEndLineNumber);
				break;
			}
		}
		while (!flag2 && (!_asyncContinueActive || !((float)stopwatch.ElapsedMilliseconds > millisecsLimitAsync)) && canContinue);
		stopwatch.Stop();
		Dictionary<string, Object> dictionary = null;
		if (flag2 || !canContinue)
		{
			if (_stateSnapshotAtLastNewline != null)
			{
				RestoreStateSnapshot();
			}
			if (!canContinue)
			{
				if (state.callStack.canPopThread)
				{
					AddError("Thread available to pop, threads should always be flat by the end of evaluation?");
				}
				if (state.generatedChoices.Count == 0 && !state.didSafeExit && _temporaryEvaluationContainer == null)
				{
					if (state.callStack.CanPop(PushPopType.Tunnel))
					{
						AddError("unexpectedly reached end of content. Do you need a '->->' to return from a tunnel?");
					}
					else if (state.callStack.CanPop(PushPopType.Function))
					{
						AddError("unexpectedly reached end of content. Do you need a '~ return'?");
					}
					else if (!state.callStack.canPop)
					{
						AddError("ran out of content. Do you need a '-> DONE' or '-> END'?");
					}
					else
					{
						AddError("unexpectedly reached end of content for unknown reason. Please debug compiler!");
					}
				}
			}
			state.didSafeExit = false;
			_sawLookaheadUnsafeFeatureAfterNewline = LookaheadUnsafeFeatureSeen.None;
			if (_recursiveContinueCount == 1)
			{
				dictionary = _state.variablesState.CompleteVariableObservation();
			}
			_asyncContinueActive = false;
			if (onDidContinue != null)
			{
				onDidContinue();
			}
		}
		_recursiveContinueCount--;
		if (_profiler != null)
		{
			_profiler.PostContinue();
		}
		if (state.hasError || state.hasWarning)
		{
			if (onError == null)
			{
				StringBuilder stringBuilder = new StringBuilder();
				stringBuilder.Append("Ink had ");
				if (state.hasError)
				{
					stringBuilder.Append(state.currentErrors.Count);
					stringBuilder.Append((state.currentErrors.Count == 1) ? " error" : " errors");
					if (state.hasWarning)
					{
						stringBuilder.Append(" and ");
					}
				}
				if (state.hasWarning)
				{
					stringBuilder.Append(state.currentWarnings.Count);
					stringBuilder.Append((state.currentWarnings.Count == 1) ? " warning" : " warnings");
				}
				stringBuilder.Append(". It is strongly suggested that you assign an error handler to story.onError. The first issue was: ");
				stringBuilder.Append(state.hasError ? state.currentErrors[0] : state.currentWarnings[0]);
				throw new StoryException(stringBuilder.ToString());
			}
			if (state.hasError)
			{
				foreach (string currentError in state.currentErrors)
				{
					onError(currentError, ErrorType.Error);
				}
			}
			if (state.hasWarning)
			{
				foreach (string currentWarning in state.currentWarnings)
				{
					onError(currentWarning, ErrorType.Warning);
				}
			}
			ResetErrors();
		}
		if (dictionary != null && dictionary.Count > 0)
		{
			_state.variablesState.NotifyObservers(dictionary);
		}
	}

	private bool ContinueSingleStep()
	{
		if (_profiler != null)
		{
			_profiler.PreStep();
		}
		Step();
		if (_profiler != null)
		{
			_profiler.PostStep();
		}
		if (!canContinue && !state.callStack.elementIsEvaluateFromGame)
		{
			TryFollowDefaultInvisibleChoice();
		}
		if (_profiler != null)
		{
			_profiler.PreSnapshot();
		}
		if (!state.inStringEvaluation)
		{
			if (_stateSnapshotAtLastNewline != null)
			{
				OutputStateChange outputStateChange = CalculateNewlineOutputStateChange(_stateSnapshotAtLastNewline.currentText, state.currentText, _stateSnapshotAtLastNewline.currentTags.Count, state.currentTags.Count);
				if (outputStateChange == OutputStateChange.ExtendedBeyondNewline || _sawLookaheadUnsafeFeatureAfterNewline != LookaheadUnsafeFeatureSeen.None)
				{
					RestoreStateSnapshot();
					return true;
				}
				if (outputStateChange == OutputStateChange.NewlineRemoved)
				{
					DiscardSnapshot();
				}
			}
			if (state.outputStreamEndsInNewline)
			{
				if (canContinue)
				{
					if (_stateSnapshotAtLastNewline == null)
					{
						StateSnapshot();
					}
				}
				else
				{
					DiscardSnapshot();
				}
			}
		}
		if (_profiler != null)
		{
			_profiler.PostSnapshot();
		}
		return false;
	}

	private OutputStateChange CalculateNewlineOutputStateChange(string prevText, string currText, int prevTagCount, int currTagCount)
	{
		bool flag = currText.Length >= prevText.Length && prevText.Length > 0 && currText[prevText.Length - 1] == '\n';
		if ((prevTagCount == currTagCount && prevText.Length == currText.Length) & flag)
		{
			return OutputStateChange.NoChange;
		}
		if (!flag)
		{
			return OutputStateChange.NewlineRemoved;
		}
		if (currTagCount > prevTagCount)
		{
			return OutputStateChange.ExtendedBeyondNewline;
		}
		for (int i = prevText.Length; i < currText.Length; i++)
		{
			char c = currText[i];
			if (c != ' ' && c != '\t')
			{
				return OutputStateChange.ExtendedBeyondNewline;
			}
		}
		return OutputStateChange.NoChange;
	}

	public string ContinueMaximally()
	{
		IfAsyncWeCant("ContinueMaximally");
		StringBuilder stringBuilder = new StringBuilder();
		while (canContinue)
		{
			stringBuilder.Append(Continue());
		}
		return stringBuilder.ToString();
	}

	public SearchResult ContentAtPath(Path path)
	{
		return mainContentContainer.ContentAtPath(path);
	}

	public Container KnotContainerWithName(string name)
	{
		if (mainContentContainer.namedContent.TryGetValue(name, out var value))
		{
			return value as Container;
		}
		return null;
	}

	public Pointer PointerAtPath(Path path)
	{
		if (path.length == 0)
		{
			return Pointer.Null;
		}
		Pointer result = default(Pointer);
		int num = path.length;
		SearchResult searchResult;
		if (path.lastComponent.isIndex)
		{
			num = path.length - 1;
			searchResult = mainContentContainer.ContentAtPath(path, 0, num);
			result.container = searchResult.container;
			result.index = path.lastComponent.index;
		}
		else
		{
			searchResult = mainContentContainer.ContentAtPath(path);
			result.container = searchResult.container;
			result.index = -1;
		}
		if (searchResult.obj == null || (searchResult.obj == mainContentContainer && num > 0))
		{
			Error("Failed to find content at path '" + path?.ToString() + "', and no approximation of it was possible.");
		}
		else if (searchResult.approximate)
		{
			Warning("Failed to find content at path '" + path?.ToString() + "', so it was approximated to: '" + searchResult.obj.path?.ToString() + "'.");
		}
		return result;
	}

	private void StateSnapshot()
	{
		_stateSnapshotAtLastNewline = _state;
		_state = _state.CopyAndStartPatching(forBackgroundSave: false);
	}

	private void RestoreStateSnapshot()
	{
		_stateSnapshotAtLastNewline.RestoreAfterPatch();
		_state = _stateSnapshotAtLastNewline;
		_stateSnapshotAtLastNewline = null;
		if (!_asyncSaving)
		{
			_state.ApplyAnyPatch();
		}
	}

	private void DiscardSnapshot()
	{
		if (!_asyncSaving)
		{
			_state.ApplyAnyPatch();
		}
		_stateSnapshotAtLastNewline = null;
	}

	public StoryState CopyStateForBackgroundThreadSave()
	{
		IfAsyncWeCant("start saving on a background thread");
		if (_asyncSaving)
		{
			throw new Exception("Story is already in background saving mode, can't call CopyStateForBackgroundThreadSave again!");
		}
		StoryState result = _state;
		_state = _state.CopyAndStartPatching(forBackgroundSave: true);
		_asyncSaving = true;
		return result;
	}

	public void BackgroundSaveComplete()
	{
		if (_stateSnapshotAtLastNewline == null)
		{
			_state.ApplyAnyPatch();
		}
		_asyncSaving = false;
	}

	private void Step()
	{
		bool flag = true;
		Pointer currentPointer = state.currentPointer;
		if (currentPointer.isNull)
		{
			return;
		}
		Container container = currentPointer.Resolve() as Container;
		while ((bool)container)
		{
			VisitContainer(container, atStart: true);
			if (container.content.Count == 0)
			{
				break;
			}
			currentPointer = Pointer.StartOf(container);
			container = currentPointer.Resolve() as Container;
		}
		state.currentPointer = currentPointer;
		if (_profiler != null)
		{
			_profiler.Step(state.callStack);
		}
		Object obj = currentPointer.Resolve();
		bool flag2 = PerformLogicAndFlowControl(obj);
		if (state.currentPointer.isNull)
		{
			return;
		}
		if (flag2)
		{
			flag = false;
		}
		ChoicePoint choicePoint = obj as ChoicePoint;
		if ((bool)choicePoint)
		{
			if (_stateSnapshotAtLastNewline != null)
			{
				_sawLookaheadUnsafeFeatureAfterNewline = LookaheadUnsafeFeatureSeen.ChoicePoint;
			}
			else
			{
				Choice choice = ProcessChoice(choicePoint);
				if ((bool)choice)
				{
					state.generatedChoices.Add(choice);
				}
			}
			obj = null;
			flag = false;
		}
		if (obj is Container)
		{
			flag = false;
		}
		if (flag)
		{
			VariablePointerValue variablePointerValue = obj as VariablePointerValue;
			if ((bool)variablePointerValue && variablePointerValue.contextIndex == -1)
			{
				int contextIndex = state.callStack.ContextForVariableNamed(variablePointerValue.variableName);
				obj = new VariablePointerValue(variablePointerValue.variableName, contextIndex);
			}
			if (state.inExpressionEvaluation)
			{
				state.PushEvaluationStack(obj);
			}
			else
			{
				state.PushToOutputStream(obj);
			}
		}
		NextContent();
		ControlCommand controlCommand = obj as ControlCommand;
		if ((bool)controlCommand && controlCommand.commandType == ControlCommand.CommandType.StartThread)
		{
			state.callStack.PushThread();
		}
	}

	private void VisitContainer(Container container, bool atStart)
	{
		if (!container.countingAtStartOnly | atStart)
		{
			if (container.visitsShouldBeCounted)
			{
				state.IncrementVisitCountForContainer(container);
			}
			if (container.turnIndexShouldBeCounted)
			{
				state.RecordTurnIndexVisitToContainer(container);
			}
		}
	}

	private void VisitChangedContainersDueToDivert()
	{
		Pointer previousPointer = state.previousPointer;
		Pointer currentPointer = state.currentPointer;
		if (currentPointer.isNull || currentPointer.index == -1)
		{
			return;
		}
		_prevContainers.Clear();
		if (!previousPointer.isNull)
		{
			Container container = (previousPointer.Resolve() as Container) ?? previousPointer.container;
			while ((bool)container)
			{
				_prevContainers.Add(container);
				container = container.parent as Container;
			}
		}
		Object obj = currentPointer.Resolve();
		if (obj == null)
		{
			return;
		}
		Container container2 = obj.parent as Container;
		bool flag = true;
		while ((bool)container2 && (!_prevContainers.Contains(container2) || container2.countingAtStartOnly))
		{
			bool flag2 = (container2.content.Count > 0 && obj == container2.content[0]) & flag;
			if (!flag2)
			{
				flag = false;
			}
			VisitContainer(container2, flag2);
			obj = container2;
			container2 = container2.parent as Container;
		}
	}

	private string PopChoiceStringAndTags(ref List<string> tags)
	{
		StringValue stringValue = (StringValue)state.PopEvaluationStack();
		while (state.evaluationStack.Count > 0 && state.PeekEvaluationStack() is Tag)
		{
			if (tags == null)
			{
				tags = new List<string>();
			}
			Tag tag = (Tag)state.PopEvaluationStack();
			tags.Insert(0, tag.text);
		}
		return stringValue.value;
	}

	private Choice ProcessChoice(ChoicePoint choicePoint)
	{
		bool flag = true;
		if (choicePoint.hasCondition)
		{
			Object obj = state.PopEvaluationStack();
			if (!IsTruthy(obj))
			{
				flag = false;
			}
		}
		string text = "";
		string text2 = "";
		List<string> tags = null;
		if (choicePoint.hasChoiceOnlyContent)
		{
			text2 = PopChoiceStringAndTags(ref tags);
		}
		if (choicePoint.hasStartContent)
		{
			text = PopChoiceStringAndTags(ref tags);
		}
		if (choicePoint.onceOnly && state.VisitCountForContainer(choicePoint.choiceTarget) > 0)
		{
			flag = false;
		}
		if (!flag)
		{
			return null;
		}
		Choice choice = new Choice();
		choice.targetPath = choicePoint.pathOnChoice;
		choice.sourcePath = choicePoint.path.ToString();
		choice.isInvisibleDefault = choicePoint.isInvisibleDefault;
		choice.tags = tags;
		choice.threadAtGeneration = state.callStack.ForkThread();
		choice.text = (text + text2).Trim(' ', '\t');
		return choice;
	}

	private bool IsTruthy(Object obj)
	{
		bool result = false;
		if (obj is Value)
		{
			Value value = (Value)obj;
			if (value is DivertTargetValue)
			{
				DivertTargetValue divertTargetValue = (DivertTargetValue)value;
				Error("Shouldn't use a divert target (to " + divertTargetValue.targetPath?.ToString() + ") as a conditional value. Did you intend a function call 'likeThis()' or a read count check 'likeThis'? (no arrows)");
				return false;
			}
			return value.isTruthy;
		}
		return result;
	}

	private bool PerformLogicAndFlowControl(Object contentObj)
	{
		if (contentObj == null)
		{
			return false;
		}
		if (contentObj is Divert)
		{
			Divert divert = (Divert)contentObj;
			if (divert.isConditional)
			{
				Object obj = state.PopEvaluationStack();
				if (!IsTruthy(obj))
				{
					return true;
				}
			}
			if (divert.hasVariableTarget)
			{
				string variableDivertName = divert.variableDivertName;
				Object variableWithName = state.variablesState.GetVariableWithName(variableDivertName);
				if (variableWithName == null)
				{
					Error("Tried to divert using a target from a variable that could not be found (" + variableDivertName + ")");
				}
				else if (!(variableWithName is DivertTargetValue))
				{
					IntValue intValue = variableWithName as IntValue;
					string text = "Tried to divert to a target from a variable, but the variable (" + variableDivertName + ") didn't contain a divert target, it ";
					text = ((!intValue || intValue.value != 0) ? (text + "contained '" + variableWithName?.ToString() + "'.") : (text + "was empty/null (the value 0)."));
					Error(text);
				}
				DivertTargetValue divertTargetValue = (DivertTargetValue)variableWithName;
				state.divertedPointer = PointerAtPath(divertTargetValue.targetPath);
			}
			else
			{
				if (divert.isExternal)
				{
					CallExternalFunction(divert.targetPathString, divert.externalArgs);
					return true;
				}
				state.divertedPointer = divert.targetPointer;
			}
			if (divert.pushesToStack)
			{
				state.callStack.Push(divert.stackPushType, 0, state.outputStream.Count);
			}
			if (state.divertedPointer.isNull && !divert.isExternal)
			{
				if ((bool)divert && divert.debugMetadata.sourceName != null)
				{
					Error("Divert target doesn't exist: " + divert.debugMetadata.sourceName);
				}
				else
				{
					Error("Divert resolution failed: " + divert);
				}
			}
			return true;
		}
		if (contentObj is ControlCommand)
		{
			ControlCommand controlCommand = (ControlCommand)contentObj;
			switch (controlCommand.commandType)
			{
			case ControlCommand.CommandType.EvalStart:
				Assert(!state.inExpressionEvaluation, "Already in expression evaluation?");
				state.inExpressionEvaluation = true;
				break;
			case ControlCommand.CommandType.EvalEnd:
				Assert(state.inExpressionEvaluation, "Not in expression evaluation mode");
				state.inExpressionEvaluation = false;
				break;
			case ControlCommand.CommandType.EvalOutput:
				if (state.evaluationStack.Count > 0)
				{
					Object obj9 = state.PopEvaluationStack();
					if (!(obj9 is Void))
					{
						StringValue obj10 = new StringValue(obj9.ToString());
						state.PushToOutputStream(obj10);
					}
				}
				break;
			case ControlCommand.CommandType.Duplicate:
				state.PushEvaluationStack(state.PeekEvaluationStack());
				break;
			case ControlCommand.CommandType.PopEvaluatedValue:
				state.PopEvaluationStack();
				break;
			case ControlCommand.CommandType.PopFunction:
			case ControlCommand.CommandType.PopTunnel:
			{
				PushPopType pushPopType = ((controlCommand.commandType == ControlCommand.CommandType.PopFunction) ? PushPopType.Function : PushPopType.Tunnel);
				DivertTargetValue divertTargetValue3 = null;
				if (pushPopType == PushPopType.Tunnel)
				{
					Object obj8 = state.PopEvaluationStack();
					divertTargetValue3 = obj8 as DivertTargetValue;
					if (divertTargetValue3 == null)
					{
						Assert(obj8 is Void, "Expected void if ->-> doesn't override target");
					}
				}
				if (state.TryExitFunctionEvaluationFromGame())
				{
					break;
				}
				if (state.callStack.currentElement.type != pushPopType || !state.callStack.canPop)
				{
					Dictionary<PushPopType, string> dictionary = new Dictionary<PushPopType, string>();
					dictionary[PushPopType.Function] = "function return statement (~ return)";
					dictionary[PushPopType.Tunnel] = "tunnel onwards statement (->->)";
					string arg = dictionary[state.callStack.currentElement.type];
					if (!state.callStack.canPop)
					{
						arg = "end of flow (-> END or choice)";
					}
					string message = $"Found {dictionary[pushPopType]}, when expected {arg}";
					Error(message);
				}
				else
				{
					state.PopCallstack();
					if ((bool)divertTargetValue3)
					{
						state.divertedPointer = PointerAtPath(divertTargetValue3.targetPath);
					}
				}
				break;
			}
			case ControlCommand.CommandType.BeginString:
				state.PushToOutputStream(controlCommand);
				Assert(state.inExpressionEvaluation, "Expected to be in an expression when evaluating a string");
				state.inExpressionEvaluation = false;
				break;
			case ControlCommand.CommandType.BeginTag:
				state.PushToOutputStream(controlCommand);
				break;
			case ControlCommand.CommandType.EndTag:
				if (state.inStringEvaluation)
				{
					Stack<Object> stack3 = new Stack<Object>();
					int num7 = 0;
					for (int num8 = state.outputStream.Count - 1; num8 >= 0; num8--)
					{
						Object obj6 = state.outputStream[num8];
						num7++;
						ControlCommand controlCommand3 = obj6 as ControlCommand;
						if (controlCommand3 != null)
						{
							if (controlCommand3.commandType != ControlCommand.CommandType.BeginTag)
							{
								Error("Unexpected ControlCommand while extracting tag from choice");
							}
							break;
						}
						if (obj6 is StringValue)
						{
							stack3.Push(obj6);
						}
					}
					state.PopFromOutputStream(num7);
					StringBuilder stringBuilder2 = new StringBuilder();
					foreach (StringValue item2 in stack3)
					{
						stringBuilder2.Append(item2.value);
					}
					Tag obj7 = new Tag(state.CleanOutputWhitespace(stringBuilder2.ToString()));
					state.PushEvaluationStack(obj7);
				}
				else
				{
					state.PushToOutputStream(controlCommand);
				}
				break;
			case ControlCommand.CommandType.EndString:
			{
				Stack<Object> stack = new Stack<Object>();
				Stack<Object> stack2 = new Stack<Object>();
				int num3 = 0;
				for (int num4 = state.outputStream.Count - 1; num4 >= 0; num4--)
				{
					Object obj5 = state.outputStream[num4];
					num3++;
					ControlCommand controlCommand2 = obj5 as ControlCommand;
					if (controlCommand2 != null && controlCommand2.commandType == ControlCommand.CommandType.BeginString)
					{
						break;
					}
					if (obj5 is Tag)
					{
						stack2.Push(obj5);
					}
					if (obj5 is StringValue)
					{
						stack.Push(obj5);
					}
				}
				state.PopFromOutputStream(num3);
				foreach (Object item3 in stack2)
				{
					state.PushToOutputStream(item3);
				}
				StringBuilder stringBuilder = new StringBuilder();
				foreach (Object item4 in stack)
				{
					stringBuilder.Append(item4.ToString());
				}
				state.inExpressionEvaluation = true;
				state.PushEvaluationStack(new StringValue(stringBuilder.ToString()));
				break;
			}
			case ControlCommand.CommandType.ChoiceCount:
			{
				int count = state.generatedChoices.Count;
				state.PushEvaluationStack(new IntValue(count));
				break;
			}
			case ControlCommand.CommandType.Turns:
				state.PushEvaluationStack(new IntValue(state.currentTurnIndex + 1));
				break;
			case ControlCommand.CommandType.TurnsSince:
			case ControlCommand.CommandType.ReadCount:
			{
				Object obj2 = state.PopEvaluationStack();
				if (!(obj2 is DivertTargetValue))
				{
					string text2 = "";
					if (obj2 is IntValue)
					{
						text2 = ". Did you accidentally pass a read count ('knot_name') instead of a target ('-> knot_name')?";
					}
					Error("TURNS_SINCE expected a divert target (knot, stitch, label name), but saw " + obj2?.ToString() + text2);
					break;
				}
				DivertTargetValue divertTargetValue2 = obj2 as DivertTargetValue;
				Container container = ContentAtPath(divertTargetValue2.targetPath).correctObj as Container;
				int intVal;
				if (container != null)
				{
					intVal = ((controlCommand.commandType != ControlCommand.CommandType.TurnsSince) ? state.VisitCountForContainer(container) : state.TurnsSinceForContainer(container));
				}
				else
				{
					intVal = ((controlCommand.commandType == ControlCommand.CommandType.TurnsSince) ? (-1) : 0);
					Warning("Failed to find container for " + controlCommand.ToString() + " lookup at " + divertTargetValue2.targetPath.ToString());
				}
				state.PushEvaluationStack(new IntValue(intVal));
				break;
			}
			case ControlCommand.CommandType.Random:
			{
				IntValue intValue3 = state.PopEvaluationStack() as IntValue;
				IntValue intValue4 = state.PopEvaluationStack() as IntValue;
				if (intValue4 == null)
				{
					Error("Invalid value for minimum parameter of RANDOM(min, max)");
				}
				if (intValue3 == null)
				{
					Error("Invalid value for maximum parameter of RANDOM(min, max)");
				}
				int num5;
				try
				{
					num5 = checked(intValue3.value - intValue4.value + 1);
				}
				catch (OverflowException)
				{
					num5 = int.MaxValue;
					Error("RANDOM was called with a range that exceeds the size that ink numbers can use.");
				}
				if (num5 <= 0)
				{
					Error("RANDOM was called with minimum as " + intValue4.value + " and maximum as " + intValue3.value + ". The maximum must be larger");
				}
				int num6 = new Random(state.storySeed + state.previousRandom).Next();
				int intVal4 = num6 % num5 + intValue4.value;
				state.PushEvaluationStack(new IntValue(intVal4));
				state.previousRandom = num6;
				break;
			}
			case ControlCommand.CommandType.SeedRandom:
			{
				IntValue intValue2 = state.PopEvaluationStack() as IntValue;
				if (intValue2 == null)
				{
					Error("Invalid value passed to SEED_RANDOM");
				}
				state.storySeed = intValue2.value;
				state.previousRandom = 0;
				state.PushEvaluationStack(new Void());
				break;
			}
			case ControlCommand.CommandType.VisitIndex:
			{
				int intVal3 = state.VisitCountForContainer(state.currentPointer.container) - 1;
				state.PushEvaluationStack(new IntValue(intVal3));
				break;
			}
			case ControlCommand.CommandType.SequenceShuffleIndex:
			{
				int intVal2 = NextSequenceShuffleIndex();
				state.PushEvaluationStack(new IntValue(intVal2));
				break;
			}
			case ControlCommand.CommandType.Done:
				if (state.callStack.canPopThread)
				{
					state.callStack.PopThread();
					break;
				}
				state.didSafeExit = true;
				state.currentPointer = Pointer.Null;
				break;
			case ControlCommand.CommandType.End:
				state.ForceEnd();
				break;
			case ControlCommand.CommandType.ListFromInt:
			{
				IntValue intValue5 = state.PopEvaluationStack() as IntValue;
				StringValue stringValue = state.PopEvaluationStack() as StringValue;
				if (intValue5 == null)
				{
					throw new StoryException("Passed non-integer when creating a list element from a numerical value.");
				}
				ListValue listValue = null;
				if (listDefinitions.TryListGetDefinition(stringValue.value, out var def))
				{
					if (def.TryGetItemWithValue(intValue5.value, out var item))
					{
						listValue = new ListValue(item, intValue5.value);
					}
					if (listValue == null)
					{
						listValue = new ListValue();
					}
					state.PushEvaluationStack(listValue);
					break;
				}
				throw new StoryException("Failed to find LIST called " + stringValue.value);
			}
			case ControlCommand.CommandType.ListRange:
			{
				Value value2 = state.PopEvaluationStack() as Value;
				Value value3 = state.PopEvaluationStack() as Value;
				ListValue obj4 = state.PopEvaluationStack() as ListValue;
				if (obj4 == null || value3 == null || value2 == null)
				{
					throw new StoryException("Expected list, minimum and maximum for LIST_RANGE");
				}
				InkList list = obj4.value.ListWithSubRange(value3.valueObject, value2.valueObject);
				state.PushEvaluationStack(new ListValue(list));
				break;
			}
			case ControlCommand.CommandType.ListRandom:
			{
				ListValue obj3 = state.PopEvaluationStack() as ListValue;
				if (obj3 == null)
				{
					throw new StoryException("Expected list for LIST_RANDOM");
				}
				InkList value = obj3.value;
				InkList inkList = null;
				if (value.Count == 0)
				{
					inkList = new InkList();
				}
				else
				{
					int num = new Random(state.storySeed + state.previousRandom).Next();
					int num2 = num % value.Count;
					Dictionary<InkListItem, int>.Enumerator enumerator = value.GetEnumerator();
					for (int i = 0; i <= num2; i++)
					{
						enumerator.MoveNext();
					}
					KeyValuePair<InkListItem, int> current = enumerator.Current;
					inkList = new InkList(current.Key.originName, this);
					inkList.Add(current.Key, current.Value);
					state.previousRandom = num;
				}
				state.PushEvaluationStack(new ListValue(inkList));
				break;
			}
			default:
				Error("unhandled ControlCommand: " + controlCommand);
				break;
			case ControlCommand.CommandType.NoOp:
			case ControlCommand.CommandType.StartThread:
				break;
			}
			return true;
		}
		if (contentObj is VariableAssignment)
		{
			VariableAssignment varAss = (VariableAssignment)contentObj;
			Object value4 = state.PopEvaluationStack();
			state.variablesState.Assign(varAss, value4);
			return true;
		}
		if (contentObj is VariableReference)
		{
			VariableReference variableReference = (VariableReference)contentObj;
			Object obj11 = null;
			if (variableReference.pathForCount != null)
			{
				Container containerForCount = variableReference.containerForCount;
				obj11 = new IntValue(state.VisitCountForContainer(containerForCount));
			}
			else
			{
				obj11 = state.variablesState.GetVariableWithName(variableReference.name);
				if (obj11 == null)
				{
					Warning("Variable not found: '" + variableReference.name + "'. Using default value of 0 (false). This can happen with temporary variables if the declaration hasn't yet been hit. Globals are always given a default value on load if a value doesn't exist in the save state.");
					obj11 = new IntValue(0);
				}
			}
			state.PushEvaluationStack(obj11);
			return true;
		}
		if (contentObj is NativeFunctionCall)
		{
			NativeFunctionCall nativeFunctionCall = (NativeFunctionCall)contentObj;
			List<Object> parameters = state.PopEvaluationStack(nativeFunctionCall.numberOfParameters);
			Object obj12 = nativeFunctionCall.Call(parameters);
			state.PushEvaluationStack(obj12);
			return true;
		}
		return false;
	}

	public void ChoosePathString(string path, bool resetCallstack = true, params object[] arguments)
	{
		IfAsyncWeCant("call ChoosePathString right now");
		if (onChoosePathString != null)
		{
			onChoosePathString(path, arguments);
		}
		if (resetCallstack)
		{
			ResetCallstack();
		}
		else if (state.callStack.currentElement.type == PushPopType.Function)
		{
			string text = "";
			Container container = state.callStack.currentElement.currentPointer.container;
			if (container != null)
			{
				text = "(" + container.path.ToString() + ") ";
			}
			throw new Exception("Story was running a function " + text + "when you called ChoosePathString(" + path + ") - this is almost certainly not not what you want! Full stack trace: \n" + state.callStack.callStackTrace);
		}
		state.PassArgumentsToEvaluationStack(arguments);
		ChoosePath(new Path(path));
	}

	private void IfAsyncWeCant(string activityStr)
	{
		if (_asyncContinueActive)
		{
			throw new Exception("Can't " + activityStr + ". Story is in the middle of a ContinueAsync(). Make more ContinueAsync() calls or a single Continue() call beforehand.");
		}
	}

	public void ChoosePath(Path p, bool incrementingTurnIndex = true)
	{
		state.SetChosenPath(p, incrementingTurnIndex);
		VisitChangedContainersDueToDivert();
	}

	public void ChooseChoiceIndex(int choiceIdx)
	{
		List<Choice> list = currentChoices;
		Assert(choiceIdx >= 0 && choiceIdx < list.Count, "choice out of range");
		Choice choice = list[choiceIdx];
		if (onMakeChoice != null)
		{
			onMakeChoice(choice);
		}
		state.callStack.currentThread = choice.threadAtGeneration;
		ChoosePath(choice.targetPath);
	}

	public bool HasFunction(string functionName)
	{
		try
		{
			return KnotContainerWithName(functionName) != null;
		}
		catch
		{
			return false;
		}
	}

	public object EvaluateFunction(string functionName, params object[] arguments)
	{
		string textOutput;
		return EvaluateFunction(functionName, out textOutput, arguments);
	}

	public object EvaluateFunction(string functionName, out string textOutput, params object[] arguments)
	{
		if (onEvaluateFunction != null)
		{
			onEvaluateFunction(functionName, arguments);
		}
		IfAsyncWeCant("evaluate a function");
		if (functionName == null)
		{
			throw new Exception("Function is null");
		}
		if (functionName == string.Empty || functionName.Trim() == string.Empty)
		{
			throw new Exception("Function is empty or white space.");
		}
		Container container = KnotContainerWithName(functionName);
		if (container == null)
		{
			throw new Exception("Function doesn't exist: '" + functionName + "'");
		}
		List<Object> objs = new List<Object>(state.outputStream);
		_state.ResetOutput();
		state.StartFunctionEvaluationFromGame(container, arguments);
		StringBuilder stringBuilder = new StringBuilder();
		while (canContinue)
		{
			stringBuilder.Append(Continue());
		}
		textOutput = stringBuilder.ToString();
		_state.ResetOutput(objs);
		object obj = state.CompleteFunctionEvaluationFromGame();
		if (onCompleteEvaluateFunction != null)
		{
			onCompleteEvaluateFunction(functionName, arguments, textOutput, obj);
		}
		return obj;
	}

	public Object EvaluateExpression(Container exprContainer)
	{
		int count = state.callStack.elements.Count;
		state.callStack.Push(PushPopType.Tunnel);
		_temporaryEvaluationContainer = exprContainer;
		state.GoToStart();
		int count2 = state.evaluationStack.Count;
		Continue();
		_temporaryEvaluationContainer = null;
		if (state.callStack.elements.Count > count)
		{
			state.PopCallstack();
		}
		if (state.evaluationStack.Count > count2)
		{
			return state.PopEvaluationStack();
		}
		return null;
	}

	public bool TryGetExternalFunction(string functionName, out ExternalFunction externalFunction)
	{
		if (_externals.TryGetValue(functionName, out var value))
		{
			externalFunction = value.function;
			return true;
		}
		externalFunction = null;
		return false;
	}

	public void CallExternalFunction(string funcName, int numberOfArguments)
	{
		Container container = null;
		bool flag = _externals.TryGetValue(funcName, out var value);
		if (flag && !value.lookaheadSafe && state.inStringEvaluation)
		{
			Error("External function " + funcName + " could not be called because 1) it wasn't marked as lookaheadSafe when BindExternalFunction was called and 2) the story is in the middle of string generation, either because choice text is being generated, or because you have ink like \"hello {func()}\". You can work around this by generating the result of your function into a temporary variable before the string or choice gets generated: ~ temp x = " + funcName + "()");
			return;
		}
		if (flag && !value.lookaheadSafe && _stateSnapshotAtLastNewline != null)
		{
			_sawLookaheadUnsafeFeatureAfterNewline = LookaheadUnsafeFeatureSeen.ExternalFunction;
			return;
		}
		if (!flag)
		{
			if (allowExternalFunctionFallbacks)
			{
				container = KnotContainerWithName(funcName);
				Assert(container != null, "Trying to call EXTERNAL function '" + funcName + "' which has not been bound, and fallback ink function could not be found.");
				state.callStack.Push(PushPopType.Function, 0, state.outputStream.Count);
				state.divertedPointer = Pointer.StartOf(container);
				return;
			}
			Assert(false, "Trying to call EXTERNAL function '" + funcName + "' which has not been bound (and ink fallbacks disabled).");
		}
		List<object> list = new List<object>();
		for (int i = 0; i < numberOfArguments; i++)
		{
			object valueObject = (state.PopEvaluationStack() as Value).valueObject;
			list.Add(valueObject);
		}
		list.Reverse();
		object obj = value.function(list.ToArray());
		Object obj2 = null;
		if (obj != null)
		{
			obj2 = Value.Create(obj);
			Assert(obj2 != null, "Could not create ink value from returned object of type " + obj.GetType());
		}
		else
		{
			obj2 = new Void();
		}
		state.PushEvaluationStack(obj2);
	}

	public void BindExternalFunctionGeneral(string funcName, ExternalFunction func, bool lookaheadSafe = true)
	{
		IfAsyncWeCant("bind an external function");
		Assert(!_externals.ContainsKey(funcName), "Function '" + funcName + "' has already been bound.");
		_externals[funcName] = new ExternalFunctionDef
		{
			function = func,
			lookaheadSafe = lookaheadSafe
		};
	}

	private object TryCoerce<T>(object value)
	{
		if (value == null)
		{
			return null;
		}
		if (value is T)
		{
			return (T)value;
		}
		if (value is float && typeof(T) == typeof(int))
		{
			return (int)Math.Round((float)value);
		}
		if (value is int && typeof(T) == typeof(float))
		{
			return (float)(int)value;
		}
		if (value is int && typeof(T) == typeof(bool))
		{
			return (int)value != 0;
		}
		if (value is bool && typeof(T) == typeof(int))
		{
			return ((bool)value) ? 1 : 0;
		}
		if (typeof(T) == typeof(string))
		{
			return value.ToString();
		}
		Assert(false, "Failed to cast " + value.GetType().Name + " to " + typeof(T).Name);
		return null;
	}

	public void BindExternalFunction(string funcName, Func<object> func, bool lookaheadSafe = false)
	{
		Assert(func != null, "Can't bind a null function");
		BindExternalFunctionGeneral(funcName, delegate(object[] args)
		{
			Assert(args.Length == 0, "External function expected no arguments");
			return func();
		}, lookaheadSafe);
	}

	public void BindExternalFunction(string funcName, Action act, bool lookaheadSafe = false)
	{
		Assert(act != null, "Can't bind a null function");
		BindExternalFunctionGeneral(funcName, delegate(object[] args)
		{
			Assert(args.Length == 0, "External function expected no arguments");
			act();
			return (object)null;
		}, lookaheadSafe);
	}

	public void BindExternalFunction<T>(string funcName, Func<T, object> func, bool lookaheadSafe = false)
	{
		Assert(func != null, "Can't bind a null function");
		BindExternalFunctionGeneral(funcName, delegate(object[] args)
		{
			Assert(args.Length == 1, "External function expected one argument");
			return func((T)TryCoerce<T>(args[0]));
		}, lookaheadSafe);
	}

	public void BindExternalFunction<T>(string funcName, Action<T> act, bool lookaheadSafe = false)
	{
		Assert(act != null, "Can't bind a null function");
		BindExternalFunctionGeneral(funcName, delegate(object[] args)
		{
			Assert(args.Length == 1, "External function expected one argument");
			act((T)TryCoerce<T>(args[0]));
			return (object)null;
		}, lookaheadSafe);
	}

	public void BindExternalFunction<T1, T2>(string funcName, Func<T1, T2, object> func, bool lookaheadSafe = false)
	{
		Assert(func != null, "Can't bind a null function");
		BindExternalFunctionGeneral(funcName, delegate(object[] args)
		{
			Assert(args.Length == 2, "External function expected two arguments");
			return func((T1)TryCoerce<T1>(args[0]), (T2)TryCoerce<T2>(args[1]));
		}, lookaheadSafe);
	}

	public void BindExternalFunction<T1, T2>(string funcName, Action<T1, T2> act, bool lookaheadSafe = false)
	{
		Assert(act != null, "Can't bind a null function");
		BindExternalFunctionGeneral(funcName, delegate(object[] args)
		{
			Assert(args.Length == 2, "External function expected two arguments");
			act((T1)TryCoerce<T1>(args[0]), (T2)TryCoerce<T2>(args[1]));
			return (object)null;
		}, lookaheadSafe);
	}

	public void BindExternalFunction<T1, T2, T3>(string funcName, Func<T1, T2, T3, object> func, bool lookaheadSafe = false)
	{
		Assert(func != null, "Can't bind a null function");
		BindExternalFunctionGeneral(funcName, delegate(object[] args)
		{
			Assert(args.Length == 3, "External function expected three arguments");
			return func((T1)TryCoerce<T1>(args[0]), (T2)TryCoerce<T2>(args[1]), (T3)TryCoerce<T3>(args[2]));
		}, lookaheadSafe);
	}

	public void BindExternalFunction<T1, T2, T3>(string funcName, Action<T1, T2, T3> act, bool lookaheadSafe = false)
	{
		Assert(act != null, "Can't bind a null function");
		BindExternalFunctionGeneral(funcName, delegate(object[] args)
		{
			Assert(args.Length == 3, "External function expected three arguments");
			act((T1)TryCoerce<T1>(args[0]), (T2)TryCoerce<T2>(args[1]), (T3)TryCoerce<T3>(args[2]));
			return (object)null;
		}, lookaheadSafe);
	}

	public void BindExternalFunction<T1, T2, T3, T4>(string funcName, Func<T1, T2, T3, T4, object> func, bool lookaheadSafe = false)
	{
		Assert(func != null, "Can't bind a null function");
		BindExternalFunctionGeneral(funcName, delegate(object[] args)
		{
			Assert(args.Length == 4, "External function expected four arguments");
			return func((T1)TryCoerce<T1>(args[0]), (T2)TryCoerce<T2>(args[1]), (T3)TryCoerce<T3>(args[2]), (T4)TryCoerce<T4>(args[3]));
		}, lookaheadSafe);
	}

	public void BindExternalFunction<T1, T2, T3, T4>(string funcName, Action<T1, T2, T3, T4> act, bool lookaheadSafe = false)
	{
		Assert(act != null, "Can't bind a null function");
		BindExternalFunctionGeneral(funcName, delegate(object[] args)
		{
			Assert(args.Length == 4, "External function expected four arguments");
			act((T1)TryCoerce<T1>(args[0]), (T2)TryCoerce<T2>(args[1]), (T3)TryCoerce<T3>(args[2]), (T4)TryCoerce<T4>(args[3]));
			return (object)null;
		}, lookaheadSafe);
	}

	public void UnbindExternalFunction(string funcName)
	{
		IfAsyncWeCant("unbind an external a function");
		Assert(_externals.ContainsKey(funcName), "Function '" + funcName + "' has not been bound.");
		_externals.Remove(funcName);
	}

	public void ValidateExternalBindings()
	{
		HashSet<string> hashSet = new HashSet<string>();
		ValidateExternalBindings(_mainContentContainer, hashSet);
		_hasValidatedExternals = true;
		if (hashSet.Count == 0)
		{
			_hasValidatedExternals = true;
			return;
		}
		string message = string.Format("ERROR: Missing function binding for external{0}: '{1}' {2}", (hashSet.Count > 1) ? "s" : string.Empty, string.Join("', '", hashSet.ToArray()), allowExternalFunctionFallbacks ? ", and no fallback ink function found." : " (ink fallbacks disabled)");
		Error(message);
	}

	private void ValidateExternalBindings(Container c, HashSet<string> missingExternals)
	{
		foreach (Object item in c.content)
		{
			Container container = item as Container;
			if (container == null || !container.hasValidName)
			{
				ValidateExternalBindings(item, missingExternals);
			}
		}
		foreach (KeyValuePair<string, INamedContent> item2 in c.namedContent)
		{
			ValidateExternalBindings(item2.Value as Object, missingExternals);
		}
	}

	private void ValidateExternalBindings(Object o, HashSet<string> missingExternals)
	{
		Container container = o as Container;
		if ((bool)container)
		{
			ValidateExternalBindings(container, missingExternals);
			return;
		}
		Divert divert = o as Divert;
		if (!divert || !divert.isExternal)
		{
			return;
		}
		string targetPathString = divert.targetPathString;
		if (_externals.ContainsKey(targetPathString))
		{
			return;
		}
		if (allowExternalFunctionFallbacks)
		{
			if (!mainContentContainer.namedContent.ContainsKey(targetPathString))
			{
				missingExternals.Add(targetPathString);
			}
		}
		else
		{
			missingExternals.Add(targetPathString);
		}
	}

	public void ObserveVariable(string variableName, VariableObserver observer)
	{
		IfAsyncWeCant("observe a new variable");
		if (_variableObservers == null)
		{
			_variableObservers = new Dictionary<string, VariableObserver>();
		}
		if (!state.variablesState.GlobalVariableExistsWithName(variableName))
		{
			throw new Exception("Cannot observe variable '" + variableName + "' because it wasn't declared in the ink story.");
		}
		if (_variableObservers.ContainsKey(variableName))
		{
			Dictionary<string, VariableObserver> variableObservers = _variableObservers;
			variableObservers[variableName] = (VariableObserver)Delegate.Combine(variableObservers[variableName], observer);
		}
		else
		{
			_variableObservers[variableName] = observer;
		}
	}

	public void ObserveVariables(IList<string> variableNames, VariableObserver observer)
	{
		foreach (string variableName in variableNames)
		{
			ObserveVariable(variableName, observer);
		}
	}

	public void RemoveVariableObserver(VariableObserver observer = null, string specificVariableName = null)
	{
		IfAsyncWeCant("remove a variable observer");
		if (_variableObservers == null)
		{
			return;
		}
		if (specificVariableName != null)
		{
			if (!_variableObservers.ContainsKey(specificVariableName))
			{
				return;
			}
			if (observer != null)
			{
				Dictionary<string, VariableObserver> variableObservers = _variableObservers;
				string key = specificVariableName;
				variableObservers[key] = (VariableObserver)Delegate.Remove(variableObservers[key], observer);
				if (_variableObservers[specificVariableName] == null)
				{
					_variableObservers.Remove(specificVariableName);
				}
			}
			else
			{
				_variableObservers.Remove(specificVariableName);
			}
		}
		else
		{
			if (observer == null)
			{
				return;
			}
			foreach (string item in new List<string>(_variableObservers.Keys))
			{
				Dictionary<string, VariableObserver> variableObservers = _variableObservers;
				string key = item;
				variableObservers[key] = (VariableObserver)Delegate.Remove(variableObservers[key], observer);
				if (_variableObservers[item] == null)
				{
					_variableObservers.Remove(item);
				}
			}
		}
	}

	private void VariableStateDidChangeEvent(string variableName, Object newValueObj)
	{
		if (_variableObservers == null)
		{
			return;
		}
		VariableObserver value = null;
		if (_variableObservers.TryGetValue(variableName, out value))
		{
			if (!(newValueObj is Value))
			{
				throw new Exception("Tried to get the value of a variable that isn't a standard type");
			}
			Value value2 = newValueObj as Value;
			value(variableName, value2.valueObject);
		}
	}

	public List<string> TagsForContentAtPath(string path)
	{
		return TagsAtStartOfFlowContainerWithPathString(path);
	}

	private List<string> TagsAtStartOfFlowContainerWithPathString(string pathString)
	{
		Path path = new Path(pathString);
		Container container = ContentAtPath(path).container;
		while (true)
		{
			Object obj = container.content[0];
			if (!(obj is Container))
			{
				break;
			}
			container = (Container)obj;
		}
		bool flag = false;
		List<string> list = null;
		foreach (Object item in container.content)
		{
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
				continue;
			}
			if (!flag)
			{
				break;
			}
			StringValue stringValue = item as StringValue;
			if (stringValue != null)
			{
				if (list == null)
				{
					list = new List<string>();
				}
				list.Add(stringValue.value);
			}
			else
			{
				Error("Tag contained non-text content. Only plain text is allowed when using globalTags or TagsAtContentPath. If you want to evaluate dynamic content, you need to use story.Continue().");
			}
		}
		return list;
	}

	public virtual string BuildStringOfHierarchy()
	{
		StringBuilder stringBuilder = new StringBuilder();
		mainContentContainer.BuildStringOfHierarchy(stringBuilder, 0, state.currentPointer.Resolve());
		return stringBuilder.ToString();
	}

	private string BuildStringOfContainer(Container container)
	{
		StringBuilder stringBuilder = new StringBuilder();
		container.BuildStringOfHierarchy(stringBuilder, 0, state.currentPointer.Resolve());
		return stringBuilder.ToString();
	}

	private void NextContent()
	{
		state.previousPointer = state.currentPointer;
		if (!state.divertedPointer.isNull)
		{
			state.currentPointer = state.divertedPointer;
			state.divertedPointer = Pointer.Null;
			VisitChangedContainersDueToDivert();
			if (!state.currentPointer.isNull)
			{
				return;
			}
		}
		if (IncrementContentPointer())
		{
			return;
		}
		bool flag = false;
		if (state.callStack.CanPop(PushPopType.Function))
		{
			state.PopCallstack(PushPopType.Function);
			if (state.inExpressionEvaluation)
			{
				state.PushEvaluationStack(new Void());
			}
			flag = true;
		}
		else if (state.callStack.canPopThread)
		{
			state.callStack.PopThread();
			flag = true;
		}
		else
		{
			state.TryExitFunctionEvaluationFromGame();
		}
		if (flag && !state.currentPointer.isNull)
		{
			NextContent();
		}
	}

	private bool IncrementContentPointer()
	{
		bool flag = true;
		Pointer currentPointer = state.callStack.currentElement.currentPointer;
		currentPointer.index++;
		while (currentPointer.index >= currentPointer.container.content.Count)
		{
			flag = false;
			Container container = currentPointer.container.parent as Container;
			if (!container)
			{
				break;
			}
			int num = container.content.IndexOf(currentPointer.container);
			if (num == -1)
			{
				break;
			}
			currentPointer = new Pointer(container, num);
			currentPointer.index++;
			flag = true;
		}
		if (!flag)
		{
			currentPointer = Pointer.Null;
		}
		state.callStack.currentElement.currentPointer = currentPointer;
		return flag;
	}

	private bool TryFollowDefaultInvisibleChoice()
	{
		List<Choice> list = _state.currentChoices;
		List<Choice> list2 = list.Where((Choice c) => c.isInvisibleDefault).ToList();
		if (list2.Count == 0 || list.Count > list2.Count)
		{
			return false;
		}
		Choice choice = list2[0];
		state.callStack.currentThread = choice.threadAtGeneration;
		if (_stateSnapshotAtLastNewline != null)
		{
			state.callStack.currentThread = state.callStack.ForkThread();
		}
		ChoosePath(choice.targetPath, incrementingTurnIndex: false);
		return true;
	}

	private int NextSequenceShuffleIndex()
	{
		IntValue intValue = state.PopEvaluationStack() as IntValue;
		if (intValue == null)
		{
			Error("expected number of elements in sequence for shuffle index");
			return 0;
		}
		Container container = state.currentPointer.container;
		int value = intValue.value;
		int value2 = (state.PopEvaluationStack() as IntValue).value;
		int num = value2 / value;
		int num2 = value2 % value;
		string text = container.path.ToString();
		int num3 = 0;
		string text2 = text;
		foreach (char c in text2)
		{
			num3 += c;
		}
		Random random = new Random(num3 + num + state.storySeed);
		List<int> list = new List<int>();
		for (int j = 0; j < value; j++)
		{
			list.Add(j);
		}
		for (int k = 0; k <= num2; k++)
		{
			int index = random.Next() % list.Count;
			int result = list[index];
			list.RemoveAt(index);
			if (k == num2)
			{
				return result;
			}
		}
		throw new Exception("Should never reach here");
	}

	public void Error(string message, bool useEndLineNumber = false)
	{
		throw new StoryException(message)
		{
			useEndLineNumber = useEndLineNumber
		};
	}

	public void Warning(string message)
	{
		AddError(message, isWarning: true);
	}

	private void AddError(string message, bool isWarning = false, bool useEndLineNumber = false)
	{
		DebugMetadata debugMetadata = currentDebugMetadata;
		string text = (isWarning ? "WARNING" : "ERROR");
		if (debugMetadata == null)
		{
			message = (state.currentPointer.isNull ? ("RUNTIME " + text + ": " + message) : $"RUNTIME {text}: ({state.currentPointer.path}): {message}");
		}
		else
		{
			int num = (useEndLineNumber ? debugMetadata.endLineNumber : debugMetadata.startLineNumber);
			message = $"RUNTIME {text}: '{debugMetadata.fileName}' line {num}: {message}";
		}
		state.AddError(message, isWarning);
		if (!isWarning)
		{
			state.ForceEnd();
		}
	}

	private void Assert(bool condition, string message = null, params object[] formatParams)
	{
		if (!condition)
		{
			if (message == null)
			{
				message = "Story assert";
			}
			if (formatParams != null && formatParams.Count() > 0)
			{
				message = string.Format(message, formatParams);
			}
			throw new Exception(message + " " + currentDebugMetadata);
		}
	}
}
