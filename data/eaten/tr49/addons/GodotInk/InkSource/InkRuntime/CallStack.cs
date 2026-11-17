using System;
using System.Collections.Generic;
using System.Text;

namespace Ink.Runtime;

public class CallStack
{
	public class Element
	{
		public Pointer currentPointer;

		public bool inExpressionEvaluation;

		public Dictionary<string, Object> temporaryVariables;

		public PushPopType type;

		public int evaluationStackHeightWhenPushed;

		public int functionStartInOuputStream;

		public Element(PushPopType type, Pointer pointer, bool inExpressionEvaluation = false)
		{
			currentPointer = pointer;
			this.inExpressionEvaluation = inExpressionEvaluation;
			temporaryVariables = new Dictionary<string, Object>();
			this.type = type;
		}

		public Element Copy()
		{
			return new Element(type, currentPointer, inExpressionEvaluation)
			{
				temporaryVariables = new Dictionary<string, Object>(temporaryVariables),
				evaluationStackHeightWhenPushed = evaluationStackHeightWhenPushed,
				functionStartInOuputStream = functionStartInOuputStream
			};
		}
	}

	public class Thread
	{
		public List<Element> callstack;

		public int threadIndex;

		public Pointer previousPointer;

		public Thread()
		{
			callstack = new List<Element>();
		}

		public Thread(Dictionary<string, object> jThreadObj, Story storyContext)
			: this()
		{
			threadIndex = (int)jThreadObj["threadIndex"];
			foreach (Dictionary<string, object> item in (List<object>)jThreadObj["callstack"])
			{
				PushPopType type = (PushPopType)(int)item["type"];
				Pointer pointer = Pointer.Null;
				string text = null;
				if (item.TryGetValue("cPath", out var value))
				{
					text = value.ToString();
					SearchResult searchResult = storyContext.ContentAtPath(new Path(text));
					pointer.container = searchResult.container;
					pointer.index = (int)item["idx"];
					if (searchResult.obj == null)
					{
						throw new Exception("When loading state, internal story location couldn't be found: " + text + ". Has the story changed since this save data was created?");
					}
					if (searchResult.approximate)
					{
						if (pointer.container != null)
						{
							storyContext.Warning("When loading state, exact internal story location couldn't be found: '" + text + "', so it was approximated to '" + pointer.container.path.ToString() + "' to recover. Has the story changed since this save data was created?");
						}
						else
						{
							storyContext.Warning("When loading state, exact internal story location couldn't be found: '" + text + "' and it may not be recoverable. Has the story changed since this save data was created?");
						}
					}
				}
				bool inExpressionEvaluation = (bool)item["exp"];
				Element element = new Element(type, pointer, inExpressionEvaluation);
				if (item.TryGetValue("temp", out var value2))
				{
					element.temporaryVariables = Json.JObjectToDictionaryRuntimeObjs((Dictionary<string, object>)value2);
				}
				else
				{
					element.temporaryVariables.Clear();
				}
				callstack.Add(element);
			}
			if (jThreadObj.TryGetValue("previousContentObject", out var value3))
			{
				Path path = new Path((string)value3);
				previousPointer = storyContext.PointerAtPath(path);
			}
		}

		public Thread Copy()
		{
			Thread thread = new Thread();
			thread.threadIndex = threadIndex;
			foreach (Element item in callstack)
			{
				thread.callstack.Add(item.Copy());
			}
			thread.previousPointer = previousPointer;
			return thread;
		}

		public void WriteJson(SimpleJson.Writer writer)
		{
			writer.WriteObjectStart();
			writer.WritePropertyStart("callstack");
			writer.WriteArrayStart();
			foreach (Element item in callstack)
			{
				writer.WriteObjectStart();
				if (!item.currentPointer.isNull)
				{
					writer.WriteProperty("cPath", item.currentPointer.container.path.componentsString);
					writer.WriteProperty("idx", item.currentPointer.index);
				}
				writer.WriteProperty("exp", item.inExpressionEvaluation);
				writer.WriteProperty("type", (int)item.type);
				if (item.temporaryVariables.Count > 0)
				{
					writer.WritePropertyStart("temp");
					Json.WriteDictionaryRuntimeObjs(writer, item.temporaryVariables);
					writer.WritePropertyEnd();
				}
				writer.WriteObjectEnd();
			}
			writer.WriteArrayEnd();
			writer.WritePropertyEnd();
			writer.WriteProperty("threadIndex", threadIndex);
			if (!previousPointer.isNull)
			{
				writer.WriteProperty("previousContentObject", previousPointer.Resolve().path.ToString());
			}
			writer.WriteObjectEnd();
		}
	}

	private List<Thread> _threads;

	private int _threadCounter;

	private Pointer _startOfRoot;

	public List<Element> elements => callStack;

	public int depth => elements.Count;

	public Element currentElement
	{
		get
		{
			List<Element> callstack = _threads[_threads.Count - 1].callstack;
			return callstack[callstack.Count - 1];
		}
	}

	public int currentElementIndex => callStack.Count - 1;

	public Thread currentThread
	{
		get
		{
			return _threads[_threads.Count - 1];
		}
		set
		{
			_threads.Clear();
			_threads.Add(value);
		}
	}

	public bool canPop => callStack.Count > 1;

	public bool canPopThread
	{
		get
		{
			if (_threads.Count > 1)
			{
				return !elementIsEvaluateFromGame;
			}
			return false;
		}
	}

	public bool elementIsEvaluateFromGame => currentElement.type == PushPopType.FunctionEvaluationFromGame;

	private List<Element> callStack => currentThread.callstack;

	public string callStackTrace
	{
		get
		{
			StringBuilder stringBuilder = new StringBuilder();
			for (int i = 0; i < _threads.Count; i++)
			{
				Thread thread = _threads[i];
				bool flag = i == _threads.Count - 1;
				stringBuilder.AppendFormat("=== THREAD {0}/{1} {2}===\n", i + 1, _threads.Count, flag ? "(current) " : "");
				for (int j = 0; j < thread.callstack.Count; j++)
				{
					if (thread.callstack[j].type == PushPopType.Function)
					{
						stringBuilder.Append("  [FUNCTION] ");
					}
					else
					{
						stringBuilder.Append("  [TUNNEL] ");
					}
					Pointer currentPointer = thread.callstack[j].currentPointer;
					if (!currentPointer.isNull)
					{
						stringBuilder.Append("<SOMEWHERE IN ");
						stringBuilder.Append(currentPointer.container.path.ToString());
						stringBuilder.AppendLine(">");
					}
				}
			}
			return stringBuilder.ToString();
		}
	}

	public CallStack(Story storyContext)
	{
		_startOfRoot = Pointer.StartOf(storyContext.rootContentContainer);
		Reset();
	}

	public CallStack(CallStack toCopy)
	{
		_threads = new List<Thread>();
		foreach (Thread thread in toCopy._threads)
		{
			_threads.Add(thread.Copy());
		}
		_threadCounter = toCopy._threadCounter;
		_startOfRoot = toCopy._startOfRoot;
	}

	public void Reset()
	{
		_threads = new List<Thread>();
		_threads.Add(new Thread());
		_threads[0].callstack.Add(new Element(PushPopType.Tunnel, _startOfRoot));
	}

	public void SetJsonToken(Dictionary<string, object> jObject, Story storyContext)
	{
		_threads.Clear();
		foreach (Dictionary<string, object> item2 in (List<object>)jObject["threads"])
		{
			Thread item = new Thread(item2, storyContext);
			_threads.Add(item);
		}
		_threadCounter = (int)jObject["threadCounter"];
		_startOfRoot = Pointer.StartOf(storyContext.rootContentContainer);
	}

	public void WriteJson(SimpleJson.Writer w)
	{
		w.WriteObject(delegate(SimpleJson.Writer writer)
		{
			writer.WritePropertyStart("threads");
			writer.WriteArrayStart();
			foreach (Thread thread in _threads)
			{
				thread.WriteJson(writer);
			}
			writer.WriteArrayEnd();
			writer.WritePropertyEnd();
			writer.WritePropertyStart("threadCounter");
			writer.Write(_threadCounter);
			writer.WritePropertyEnd();
		});
	}

	public void PushThread()
	{
		Thread thread = currentThread.Copy();
		_threadCounter++;
		thread.threadIndex = _threadCounter;
		_threads.Add(thread);
	}

	public Thread ForkThread()
	{
		Thread thread = currentThread.Copy();
		_threadCounter++;
		thread.threadIndex = _threadCounter;
		return thread;
	}

	public void PopThread()
	{
		if (canPopThread)
		{
			_threads.Remove(currentThread);
			return;
		}
		throw new Exception("Can't pop thread");
	}

	public void Push(PushPopType type, int externalEvaluationStackHeight = 0, int outputStreamLengthWithPushed = 0)
	{
		Element element = new Element(type, currentElement.currentPointer);
		element.evaluationStackHeightWhenPushed = externalEvaluationStackHeight;
		element.functionStartInOuputStream = outputStreamLengthWithPushed;
		callStack.Add(element);
	}

	public bool CanPop(PushPopType? type = null)
	{
		if (!canPop)
		{
			return false;
		}
		if (!type.HasValue)
		{
			return true;
		}
		return currentElement.type == type;
	}

	public void Pop(PushPopType? type = null)
	{
		if (CanPop(type))
		{
			callStack.RemoveAt(callStack.Count - 1);
			return;
		}
		throw new Exception("Mismatched push/pop in Callstack");
	}

	public Object GetTemporaryVariableWithName(string name, int contextIndex = -1)
	{
		if (contextIndex == -1)
		{
			contextIndex = currentElementIndex + 1;
		}
		Object value = null;
		if (callStack[contextIndex - 1].temporaryVariables.TryGetValue(name, out value))
		{
			return value;
		}
		return null;
	}

	public void SetTemporaryVariable(string name, Object value, bool declareNew, int contextIndex = -1)
	{
		if (contextIndex == -1)
		{
			contextIndex = currentElementIndex + 1;
		}
		Element element = callStack[contextIndex - 1];
		if (!declareNew && !element.temporaryVariables.ContainsKey(name))
		{
			throw new Exception("Could not find temporary variable to set: " + name);
		}
		if (element.temporaryVariables.TryGetValue(name, out var value2))
		{
			ListValue.RetainListOriginsForAssignment(value2, value);
		}
		element.temporaryVariables[name] = value;
	}

	public int ContextForVariableNamed(string name)
	{
		if (currentElement.temporaryVariables.ContainsKey(name))
		{
			return currentElementIndex + 1;
		}
		return 0;
	}

	public Thread ThreadWithIndex(int index)
	{
		return _threads.Find((Thread t) => t.threadIndex == index);
	}
}
