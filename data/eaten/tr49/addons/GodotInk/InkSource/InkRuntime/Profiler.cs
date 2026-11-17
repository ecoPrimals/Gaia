using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;

namespace Ink.Runtime;

public class Profiler
{
	private struct StepDetails
	{
		public string type;

		public Object obj;

		public double time;
	}

	private Stopwatch _continueWatch = new Stopwatch();

	private Stopwatch _stepWatch = new Stopwatch();

	private Stopwatch _snapWatch = new Stopwatch();

	private double _continueTotal;

	private double _snapTotal;

	private double _stepTotal;

	private string[] _currStepStack;

	private StepDetails _currStepDetails;

	private ProfileNode _rootNode;

	private int _numContinues;

	private List<StepDetails> _stepDetails = new List<StepDetails>();

	private static double _millisecsPerTick = 1000.0 / (double)Stopwatch.Frequency;

	public ProfileNode rootNode => _rootNode;

	public Profiler()
	{
		_rootNode = new ProfileNode();
	}

	public string Report()
	{
		StringBuilder stringBuilder = new StringBuilder();
		stringBuilder.AppendFormat("{0} CONTINUES / LINES:\n", _numContinues);
		stringBuilder.AppendFormat("TOTAL TIME: {0}\n", FormatMillisecs(_continueTotal));
		stringBuilder.AppendFormat("SNAPSHOTTING: {0}\n", FormatMillisecs(_snapTotal));
		stringBuilder.AppendFormat("OTHER: {0}\n", FormatMillisecs(_continueTotal - (_stepTotal + _snapTotal)));
		stringBuilder.Append(_rootNode.ToString());
		return stringBuilder.ToString();
	}

	public void PreContinue()
	{
		_continueWatch.Reset();
		_continueWatch.Start();
	}

	public void PostContinue()
	{
		_continueWatch.Stop();
		_continueTotal += Millisecs(_continueWatch);
		_numContinues++;
	}

	public void PreStep()
	{
		_currStepStack = null;
		_stepWatch.Reset();
		_stepWatch.Start();
	}

	public void Step(CallStack callstack)
	{
		_stepWatch.Stop();
		string[] array = new string[callstack.elements.Count];
		for (int i = 0; i < array.Length; i++)
		{
			string text = "";
			if (!callstack.elements[i].currentPointer.isNull)
			{
				Path path = callstack.elements[i].currentPointer.path;
				for (int j = 0; j < path.length; j++)
				{
					Path.Component component = path.GetComponent(j);
					if (!component.isIndex)
					{
						text = component.name;
						break;
					}
				}
			}
			array[i] = text;
		}
		_currStepStack = array;
		Object obj = callstack.currentElement.currentPointer.Resolve();
		string text2 = null;
		ControlCommand controlCommand = obj as ControlCommand;
		text2 = ((!controlCommand) ? obj.GetType().Name : (controlCommand.commandType.ToString() + " CC"));
		_currStepDetails = new StepDetails
		{
			type = text2,
			obj = obj
		};
		_stepWatch.Start();
	}

	public void PostStep()
	{
		_stepWatch.Stop();
		double num = Millisecs(_stepWatch);
		_stepTotal += num;
		_rootNode.AddSample(_currStepStack, num);
		_currStepDetails.time = num;
		_stepDetails.Add(_currStepDetails);
	}

	public string StepLengthReport()
	{
		StringBuilder stringBuilder = new StringBuilder();
		stringBuilder.AppendLine("TOTAL: " + _rootNode.totalMillisecs + "ms");
		string[] value = (from s in _stepDetails
			group s by s.type into typeToDetails
			select new KeyValuePair<string, double>(typeToDetails.Key, typeToDetails.Average((StepDetails d) => d.time)) into stepTypeToAverage
			orderby stepTypeToAverage.Value descending
			select stepTypeToAverage.Key + ": " + stepTypeToAverage.Value + "ms").ToArray();
		stringBuilder.AppendLine("AVERAGE STEP TIMES: " + string.Join(", ", value));
		string[] value2 = (from s in _stepDetails
			group s by s.type into typeToDetails
			select new KeyValuePair<string, double>(typeToDetails.Key + " (x" + typeToDetails.Count() + ")", typeToDetails.Sum((StepDetails d) => d.time)) into stepTypeToAccum
			orderby stepTypeToAccum.Value descending
			select stepTypeToAccum.Key + ": " + stepTypeToAccum.Value).ToArray();
		stringBuilder.AppendLine("ACCUMULATED STEP TIMES: " + string.Join(", ", value2));
		return stringBuilder.ToString();
	}

	public string Megalog()
	{
		StringBuilder stringBuilder = new StringBuilder();
		stringBuilder.AppendLine("Step type\tDescription\tPath\tTime");
		foreach (StepDetails stepDetail in _stepDetails)
		{
			stringBuilder.Append(stepDetail.type);
			stringBuilder.Append("\t");
			stringBuilder.Append(stepDetail.obj.ToString());
			stringBuilder.Append("\t");
			stringBuilder.Append(stepDetail.obj.path);
			stringBuilder.Append("\t");
			stringBuilder.AppendLine(stepDetail.time.ToString("F8"));
		}
		return stringBuilder.ToString();
	}

	public void PreSnapshot()
	{
		_snapWatch.Reset();
		_snapWatch.Start();
	}

	public void PostSnapshot()
	{
		_snapWatch.Stop();
		_snapTotal += Millisecs(_snapWatch);
	}

	private double Millisecs(Stopwatch watch)
	{
		return (double)watch.ElapsedTicks * _millisecsPerTick;
	}

	public static string FormatMillisecs(double num)
	{
		if (num > 5000.0)
		{
			return $"{num / 1000.0:N1} secs";
		}
		if (num > 1000.0)
		{
			return $"{num / 1000.0:N2} secs";
		}
		if (num > 100.0)
		{
			return $"{num:N0} ms";
		}
		if (num > 1.0)
		{
			return $"{num:N1} ms";
		}
		if (num > 0.01)
		{
			return $"{num:N3} ms";
		}
		return $"{num:N} ms";
	}
}
