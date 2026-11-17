using System.Collections.Generic;

namespace Ink.Runtime;

public class Flow
{
	public string name;

	public CallStack callStack;

	public List<Object> outputStream;

	public List<Choice> currentChoices;

	public Flow(string name, Story story)
	{
		this.name = name;
		callStack = new CallStack(story);
		outputStream = new List<Object>();
		currentChoices = new List<Choice>();
	}

	public Flow(string name, Story story, Dictionary<string, object> jObject)
	{
		this.name = name;
		callStack = new CallStack(story);
		callStack.SetJsonToken((Dictionary<string, object>)jObject["callstack"], story);
		outputStream = Json.JArrayToRuntimeObjList((List<object>)jObject["outputStream"]);
		currentChoices = Json.JArrayToRuntimeObjList<Choice>((List<object>)jObject["currentChoices"]);
		jObject.TryGetValue("choiceThreads", out var value);
		LoadFlowChoiceThreads((Dictionary<string, object>)value, story);
	}

	public void WriteJson(SimpleJson.Writer writer)
	{
		writer.WriteObjectStart();
		writer.WriteProperty("callstack", callStack.WriteJson);
		writer.WriteProperty("outputStream", delegate(SimpleJson.Writer w)
		{
			Json.WriteListRuntimeObjs(w, outputStream);
		});
		bool flag = false;
		foreach (Choice currentChoice in currentChoices)
		{
			currentChoice.originalThreadIndex = currentChoice.threadAtGeneration.threadIndex;
			if (callStack.ThreadWithIndex(currentChoice.originalThreadIndex) == null)
			{
				if (!flag)
				{
					flag = true;
					writer.WritePropertyStart("choiceThreads");
					writer.WriteObjectStart();
				}
				writer.WritePropertyStart(currentChoice.originalThreadIndex);
				currentChoice.threadAtGeneration.WriteJson(writer);
				writer.WritePropertyEnd();
			}
		}
		if (flag)
		{
			writer.WriteObjectEnd();
			writer.WritePropertyEnd();
		}
		writer.WriteProperty("currentChoices", delegate(SimpleJson.Writer w)
		{
			w.WriteArrayStart();
			foreach (Choice currentChoice2 in currentChoices)
			{
				Json.WriteChoice(w, currentChoice2);
			}
			w.WriteArrayEnd();
		});
		writer.WriteObjectEnd();
	}

	public void LoadFlowChoiceThreads(Dictionary<string, object> jChoiceThreads, Story story)
	{
		foreach (Choice currentChoice in currentChoices)
		{
			CallStack.Thread thread = callStack.ThreadWithIndex(currentChoice.originalThreadIndex);
			if (thread != null)
			{
				currentChoice.threadAtGeneration = thread.Copy();
				continue;
			}
			Dictionary<string, object> jThreadObj = (Dictionary<string, object>)jChoiceThreads[currentChoice.originalThreadIndex.ToString()];
			currentChoice.threadAtGeneration = new CallStack.Thread(jThreadObj, story);
		}
	}
}
