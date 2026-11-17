using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using Godot;
using Godot.Collections;
using Ink.Runtime;

namespace GodotInk;

[Tool]
[GlobalClass]
[Icon("../GodotInk.svg")]
public partial class InkStory : Resource
{
	[Signal]
	public delegate void ContinuedEventHandler();

	[Signal]
	public delegate void MadeChoiceEventHandler(InkChoice choice);

	[Signal]
	public delegate void StoryLoadedEventHandler();

	private string rawStory = string.Empty;

	public Story runtimeStory;

	private readonly System.Collections.Generic.Dictionary<string, HashSet<Callable>> observers = new System.Collections.Generic.Dictionary<string, HashSet<Callable>>();

	private readonly System.Collections.Generic.Dictionary<string, Story.VariableObserver> internalObservers = new System.Collections.Generic.Dictionary<string, Story.VariableObserver>();

	protected virtual string RawStory
	{
		get
		{
			return rawStory;
		}
		set
		{
			rawStory = value;
			InitializeRuntimeStory();
		}
	}

	public string CurrentText => runtimeStory.currentText;

	public IReadOnlyList<InkChoice> CurrentChoices => MarshalUtils.ToVariants(runtimeStory.currentChoices);

	public IReadOnlyList<string> CurrentTags => runtimeStory.currentTags;

	public bool HasWarning => runtimeStory.hasWarning;

	public IReadOnlyList<string> CurrentWarnings => runtimeStory.currentWarnings;

	public bool HasError => runtimeStory.hasError;

	public IReadOnlyList<string> CurrentErrors => runtimeStory.currentErrors;

	public bool CanContinue => runtimeStory.canContinue;

	public IReadOnlyList<string> GlobalTags => runtimeStory.globalTags;

	public string CurrentFlowName => runtimeStory.currentFlowName;

	public bool CurrentFlowIsDefaultFlow => runtimeStory.currentFlowIsDefaultFlow;

	public IReadOnlyList<string> AliveFlowNames => runtimeStory.aliveFlowNames;

	public bool AllowExternalFunctionFallbacks => runtimeStory.allowExternalFunctionFallbacks;

	public static InkStory Create(string rawStory)
	{
		return new InkStory
		{
			rawStory = rawStory
		};
	}

	private void InitializeRuntimeStory()
	{
		if (runtimeStory != null)
		{
			runtimeStory.onDidContinue -= OnContinued;
			runtimeStory.onMakeChoice -= OnMadeChoice;
		}
		runtimeStory = new Story(rawStory);
		runtimeStory.onDidContinue += OnContinued;
		runtimeStory.onMakeChoice += OnMadeChoice;
		EmitSignal(SignalName.StoryLoaded);
	}

	public string Continue()
	{
		return runtimeStory.Continue();
	}

	public string ContinueMaximally()
	{
		return runtimeStory.ContinueMaximally();
	}

	public void ChooseChoiceIndex(int choiceIdx)
	{
		runtimeStory.ChooseChoiceIndex(choiceIdx);
	}

	public void ChoosePathString(string path, bool resetCallstack = true, params Variant[] arguments)
	{
		runtimeStory.ChoosePathString(path, resetCallstack, MarshalUtils.FromVariants(arguments));
	}

	public void ResetCallstack()
	{
		runtimeStory.ResetCallstack();
	}

	public new void ResetState()
	{
		runtimeStory.ResetState();
	}

	public IReadOnlyList<string> TagsForContentAtPath(string path)
	{
		return runtimeStory.TagsForContentAtPath(path);
	}

	public void RemoveFlow(string flowName)
	{
		runtimeStory.RemoveFlow(flowName);
	}

	public void SwitchFlow(string flowName)
	{
		runtimeStory.SwitchFlow(flowName);
	}

	public void SwitchToDefaultFlow()
	{
		runtimeStory.SwitchToDefaultFlow();
	}

	public int VisitCountAtPathString(string pathString)
	{
		return runtimeStory.state.VisitCountAtPathString(pathString);
	}

	public Variant FetchVariable(string variableName)
	{
		return MarshalUtils.ToVariant(runtimeStory.variablesState[variableName]);
	}

	public T FetchVariable<[MustBeVariant] T>(string variableName)
	{
		return FetchVariable(variableName).As<T>();
	}

	public void StoreVariable(string variableName, Variant value)
	{
		runtimeStory.variablesState[variableName] = MarshalUtils.FromVariant(value);
	}

	public void StoreVariable<[MustBeVariant] T>(string variableName, T value)
	{
		StoreVariable(variableName, Variant.From(in value));
	}

	public void ObserveVariable(string variableName, Callable observer)
	{
		if (!internalObservers.ContainsKey(variableName))
		{
			Story.VariableObserver variableObserver = BuildObserver();
			runtimeStory.ObserveVariable(variableName, variableObserver);
			internalObservers[variableName] = variableObserver;
		}
		if (observers.ContainsKey(variableName))
		{
			observers[variableName].Add(observer);
			return;
		}
		observers[variableName] = new HashSet<Callable> { observer };
	}

	public void ObserveVariable(string[] variableNames, Callable observer)
	{
		foreach (string variableName in variableNames)
		{
			ObserveVariable(variableName, observer);
		}
	}

	private Story.VariableObserver BuildObserver()
	{
		return delegate(string name, object? value)
		{
			if (!observers.TryGetValue(name, out HashSet<Callable> value2))
			{
				return;
			}
			Variant variant = MarshalUtils.ToVariant(value);
			foreach (Callable item in value2)
			{
				item.Call(name, variant);
			}
		};
	}

	public void RemoveVariableObserver(Callable callable)
	{
		foreach (string key in observers.Keys)
		{
			RemoveVariableObserver(callable, key);
		}
	}

	public void RemoveVariableObserver(string specificVariableName)
	{
		runtimeStory.RemoveVariableObserver(null, specificVariableName);
		internalObservers.Remove(specificVariableName);
		observers.Remove(specificVariableName);
	}

	public void RemoveVariableObserver(Callable callable, string specificVariableName)
	{
		HashSet<Callable> hashSet = observers[specificVariableName];
		if (hashSet.Contains(callable))
		{
			hashSet.Remove(callable);
			if (hashSet.Count <= 0)
			{
				runtimeStory.RemoveVariableObserver(null, specificVariableName);
				internalObservers.Remove(specificVariableName);
			}
		}
	}

	public bool HasFunction(string functionName)
	{
		return runtimeStory.HasFunction(functionName);
	}

	public Variant EvaluateFunction(string functionName, params Variant[] arguments)
	{
		return MarshalUtils.ToVariant(runtimeStory.EvaluateFunction(functionName, MarshalUtils.FromVariants(arguments)));
	}

	public Variant EvaluateFunction(string functionName, Array<Variant> arguments)
	{
		return MarshalUtils.ToVariant(runtimeStory.EvaluateFunction(functionName, MarshalUtils.FromVariants(arguments)));
	}

	public Variant EvaluateFunction(string functionName, out string textOutput, params Variant[] arguments)
	{
		return MarshalUtils.ToVariant(runtimeStory.EvaluateFunction(functionName, out textOutput, MarshalUtils.FromVariants(arguments)));
	}

	public void BindExternalFunction(string funcName, Callable callable, bool lookaheadSafe = false)
	{
		runtimeStory.BindExternalFunctionGeneral(funcName, trampoline, lookaheadSafe);
		object? trampoline(object?[] arguments)
		{
			return MarshalUtils.FromVariant(callable.Call(MarshalUtils.ToVariants(arguments)));
		}
	}

	public void BindExternalFunction(string funcName, Func<Variant> func, bool lookaheadSafe = false)
	{
		runtimeStory.BindExternalFunction(funcName, (Func<object>)trampoline, lookaheadSafe);
		object? trampoline()
		{
			return MarshalUtils.FromVariant(func());
		}
	}

	public void BindExternalFunction<T>(string funcName, Func<T, Variant> func, bool lookaheadSafe = false)
	{
		runtimeStory.BindExternalFunction(funcName, (Func<T, object>)trampoline, lookaheadSafe);
		object? trampoline(T a)
		{
			return MarshalUtils.FromVariant(func(a));
		}
	}

	public void BindExternalFunction<T1, T2>(string funcName, Func<T1, T2, Variant> func, bool lookaheadSafe = false)
	{
		runtimeStory.BindExternalFunction(funcName, (Func<T1, T2, object>)trampoline, lookaheadSafe);
		object? trampoline(T1 a, T2 b)
		{
			return MarshalUtils.FromVariant(func(a, b));
		}
	}

	public void BindExternalFunction<T1, T2, T3>(string funcName, Func<T1, T2, T3, Variant> func, bool lookaheadSafe = false)
	{
		runtimeStory.BindExternalFunction(funcName, (Func<T1, T2, T3, object>)trampoline, lookaheadSafe);
		object? trampoline(T1 a, T2 b, T3 c)
		{
			return MarshalUtils.FromVariant(func(a, b, c));
		}
	}

	public void BindExternalFunction<T1, T2, T3, T4>(string funcName, Func<T1, T2, T3, T4, Variant> func, bool lookaheadSafe = false)
	{
		runtimeStory.BindExternalFunction(funcName, (Func<T1, T2, T3, T4, object>)trampoline, lookaheadSafe);
		object? trampoline(T1 a, T2 b, T3 c, T4 d)
		{
			return MarshalUtils.FromVariant(func(a, b, c, d));
		}
	}

	public void BindExternalFunction(string funcName, Action action, bool lookaheadSafe = false)
	{
		runtimeStory.BindExternalFunction(funcName, action, lookaheadSafe);
	}

	public void BindExternalFunction<T>(string funcName, Action<T> action, bool lookaheadSafe = false)
	{
		runtimeStory.BindExternalFunction(funcName, action, lookaheadSafe);
	}

	public void BindExternalFunction<T1, T2>(string funcName, Action<T1, T2> action, bool lookaheadSafe = false)
	{
		runtimeStory.BindExternalFunction(funcName, action, lookaheadSafe);
	}

	public void BindExternalFunction<T1, T2, T3>(string funcName, Action<T1, T2, T3> action, bool lookaheadSafe = false)
	{
		runtimeStory.BindExternalFunction(funcName, action, lookaheadSafe);
	}

	public void BindExternalFunction<T1, T2, T3, T4>(string funcName, Action<T1, T2, T3, T4> action, bool lookaheadSafe = false)
	{
		runtimeStory.BindExternalFunction(funcName, action, lookaheadSafe);
	}

	public void UnbindExternalFunction(string funcName)
	{
		runtimeStory.UnbindExternalFunction(funcName);
	}

	public void Error(string message)
	{
		runtimeStory.Error(message);
	}

	public void Error(string message, bool useEndLineNumber)
	{
		runtimeStory.Error(message, useEndLineNumber);
	}

	public void Warning(string message)
	{
		runtimeStory.Warning(message);
	}

	public string SaveState()
	{
		return runtimeStory.state.ToJson();
	}

	public void SaveStateFile(string filePath)
	{
		using FileAccess fileAccess = FileAccess.Open(filePath, FileAccess.ModeFlags.Write);
		fileAccess.StoreString(SaveState());
	}

	public void LoadState(string jsonState)
	{
		runtimeStory.state.LoadJson(jsonState);
	}

	public void LoadStateFile(string filePath)
	{
		using FileAccess fileAccess = FileAccess.Open(filePath, FileAccess.ModeFlags.Read);
		LoadState(fileAccess.GetAsText());
	}

	private void OnContinued()
	{
		EmitSignal(SignalName.Continued);
	}

	private void OnMadeChoice(Choice choice)
	{
		EmitSignal(SignalName.MadeChoice, new InkChoice(choice));
	}

	public override Array<Dictionary> _GetPropertyList()
	{
		Array<Dictionary> obj = base._GetPropertyList() ?? new Array<Dictionary>();
		obj.Add(new Dictionary
		{
			{
				"name",
				PropertyName.RawStory
			},
			{
				"type",
				Variant.From<Variant.Type>(Variant.Type.Object)
			},
			{
				"usage",
				Variant.From<PropertyUsageFlags>(PropertyUsageFlags.Storage)
			}
		});
		return obj;
	}

	[EditorBrowsable(EditorBrowsableState.Never)]
	public bool GetCanContinue()
	{
		return CanContinue;
	}

	[EditorBrowsable(EditorBrowsableState.Never)]
	public Array<InkChoice> GetCurrentChoices()
	{
		return new Array<InkChoice>(CurrentChoices);
	}

	[EditorBrowsable(EditorBrowsableState.Never)]
	public Array<string> GetCurrentTags()
	{
		return new Array<string>(CurrentTags);
	}

	[EditorBrowsable(EditorBrowsableState.Never)]
	public string GetCurrentText()
	{
		return CurrentText;
	}

	[EditorBrowsable(EditorBrowsableState.Never)]
	public void ChoosePathString(string path)
	{
		ChoosePathString(path, resetCallstack: true, System.Array.Empty<Variant>());
	}

	[EditorBrowsable(EditorBrowsableState.Never)]
	public void ChoosePathString(string path, bool resetCallstack)
	{
		ChoosePathString(path, resetCallstack, System.Array.Empty<Variant>());
	}

	[EditorBrowsable(EditorBrowsableState.Never)]
	public void ChoosePathString(string path, Array<Variant> arguments)
	{
		ChoosePathString(path, resetCallstack: true, arguments.ToArray());
	}

	[EditorBrowsable(EditorBrowsableState.Never)]
	public void ChoosePathString(string path, bool resetCallstack, Array<Variant> arguments)
	{
		ChoosePathString(path, resetCallstack, arguments.ToArray());
	}

	[EditorBrowsable(EditorBrowsableState.Never)]
	public Variant EvaluateFunction(string functionName)
	{
		return EvaluateFunction(functionName, System.Array.Empty<Variant>());
	}

	[EditorBrowsable(EditorBrowsableState.Never)]
	public void BindExternalFunction(string funcName, Callable callable)
	{
		BindExternalFunction(funcName, callable, false);
	}
}
