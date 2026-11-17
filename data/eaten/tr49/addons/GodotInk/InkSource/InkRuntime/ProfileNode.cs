using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Ink.Runtime;

public class ProfileNode
{
	public readonly string key;

	public bool openInUI;

	private Dictionary<string, ProfileNode> _nodes;

	private double _selfMillisecs;

	private double _totalMillisecs;

	private int _selfSampleCount;

	private int _totalSampleCount;

	public bool hasChildren
	{
		get
		{
			if (_nodes != null)
			{
				return _nodes.Count > 0;
			}
			return false;
		}
	}

	public int totalMillisecs => (int)_totalMillisecs;

	public IEnumerable<KeyValuePair<string, ProfileNode>> descendingOrderedNodes
	{
		get
		{
			if (_nodes == null)
			{
				return null;
			}
			return _nodes.OrderByDescending((KeyValuePair<string, ProfileNode> keyNode) => keyNode.Value._totalMillisecs);
		}
	}

	public string ownReport
	{
		get
		{
			StringBuilder stringBuilder = new StringBuilder();
			stringBuilder.Append("total ");
			stringBuilder.Append(Profiler.FormatMillisecs(_totalMillisecs));
			stringBuilder.Append(", self ");
			stringBuilder.Append(Profiler.FormatMillisecs(_selfMillisecs));
			stringBuilder.Append(" (");
			stringBuilder.Append(_selfSampleCount);
			stringBuilder.Append(" self samples, ");
			stringBuilder.Append(_totalSampleCount);
			stringBuilder.Append(" total)");
			return stringBuilder.ToString();
		}
	}

	public ProfileNode()
	{
	}

	public ProfileNode(string key)
	{
		this.key = key;
	}

	public void AddSample(string[] stack, double duration)
	{
		AddSample(stack, -1, duration);
	}

	private void AddSample(string[] stack, int stackIdx, double duration)
	{
		_totalSampleCount++;
		_totalMillisecs += duration;
		if (stackIdx == stack.Length - 1)
		{
			_selfSampleCount++;
			_selfMillisecs += duration;
		}
		if (stackIdx + 1 < stack.Length)
		{
			AddSampleToNode(stack, stackIdx + 1, duration);
		}
	}

	private void AddSampleToNode(string[] stack, int stackIdx, double duration)
	{
		string text = stack[stackIdx];
		if (_nodes == null)
		{
			_nodes = new Dictionary<string, ProfileNode>();
		}
		if (!_nodes.TryGetValue(text, out var value))
		{
			value = new ProfileNode(text);
			_nodes[text] = value;
		}
		value.AddSample(stack, stackIdx, duration);
	}

	private void PrintHierarchy(StringBuilder sb, int indent)
	{
		Pad(sb, indent);
		sb.Append(key);
		sb.Append(": ");
		sb.AppendLine(ownReport);
		if (_nodes == null)
		{
			return;
		}
		foreach (KeyValuePair<string, ProfileNode> descendingOrderedNode in descendingOrderedNodes)
		{
			descendingOrderedNode.Value.PrintHierarchy(sb, indent + 1);
		}
	}

	private void Pad(StringBuilder sb, int spaces)
	{
		for (int i = 0; i < spaces; i++)
		{
			sb.Append("   ");
		}
	}

	public override string ToString()
	{
		StringBuilder stringBuilder = new StringBuilder();
		PrintHierarchy(stringBuilder, 0);
		return stringBuilder.ToString();
	}
}
