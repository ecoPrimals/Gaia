using System.Text;

namespace Ink.Runtime;

public class Divert : Object
{
	private Path _targetPath;

	private Pointer _targetPointer;

	public PushPopType stackPushType;

	public Path targetPath
	{
		get
		{
			if (_targetPath != null && _targetPath.isRelative)
			{
				Object obj = targetPointer.Resolve();
				if ((bool)obj)
				{
					_targetPath = obj.path;
				}
			}
			return _targetPath;
		}
		set
		{
			_targetPath = value;
			_targetPointer = Pointer.Null;
		}
	}

	public Pointer targetPointer
	{
		get
		{
			if (_targetPointer.isNull)
			{
				Object obj = ResolvePath(_targetPath).obj;
				if (_targetPath.lastComponent.isIndex)
				{
					_targetPointer.container = obj.parent as Container;
					_targetPointer.index = _targetPath.lastComponent.index;
				}
				else
				{
					_targetPointer = Pointer.StartOf(obj as Container);
				}
			}
			return _targetPointer;
		}
	}

	public string targetPathString
	{
		get
		{
			if (targetPath == null)
			{
				return null;
			}
			return CompactPathString(targetPath);
		}
		set
		{
			if (value == null)
			{
				targetPath = null;
			}
			else
			{
				targetPath = new Path(value);
			}
		}
	}

	public string variableDivertName { get; set; }

	public bool hasVariableTarget => variableDivertName != null;

	public bool pushesToStack { get; set; }

	public bool isExternal { get; set; }

	public int externalArgs { get; set; }

	public bool isConditional { get; set; }

	public Divert()
	{
		pushesToStack = false;
	}

	public Divert(PushPopType stackPushType)
	{
		pushesToStack = true;
		this.stackPushType = stackPushType;
	}

	public override bool Equals(object obj)
	{
		Divert divert = obj as Divert;
		if ((bool)divert && hasVariableTarget == divert.hasVariableTarget)
		{
			if (hasVariableTarget)
			{
				return variableDivertName == divert.variableDivertName;
			}
			return targetPath.Equals(divert.targetPath);
		}
		return false;
	}

	public override int GetHashCode()
	{
		if (hasVariableTarget)
		{
			return variableDivertName.GetHashCode() + 12345;
		}
		return targetPath.GetHashCode() + 54321;
	}

	public override string ToString()
	{
		if (hasVariableTarget)
		{
			return "Divert(variable: " + variableDivertName + ")";
		}
		if (targetPath == null)
		{
			return "Divert(null)";
		}
		StringBuilder stringBuilder = new StringBuilder();
		string value = targetPath.ToString();
		int? num = DebugLineNumberOfPath(targetPath);
		if (num.HasValue)
		{
			int? num2 = num;
			value = "line " + num2;
		}
		stringBuilder.Append("Divert");
		if (isConditional)
		{
			stringBuilder.Append("?");
		}
		if (pushesToStack)
		{
			if (stackPushType == PushPopType.Function)
			{
				stringBuilder.Append(" function");
			}
			else
			{
				stringBuilder.Append(" tunnel");
			}
		}
		stringBuilder.Append(" -> ");
		stringBuilder.Append(targetPathString);
		stringBuilder.Append(" (");
		stringBuilder.Append(value);
		stringBuilder.Append(")");
		return stringBuilder.ToString();
	}
}
