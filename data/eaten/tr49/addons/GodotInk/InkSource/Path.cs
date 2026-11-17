using System.Collections.Generic;
using System.Linq;

namespace Ink.Parsed;

public class Path
{
	private string _dotSeparatedComponents;

	private FlowLevel? _baseTargetLevel;

	public FlowLevel baseTargetLevel
	{
		get
		{
			if (baseLevelIsAmbiguous)
			{
				return FlowLevel.Story;
			}
			return _baseTargetLevel.Value;
		}
	}

	public bool baseLevelIsAmbiguous => !_baseTargetLevel.HasValue;

	public string firstComponent
	{
		get
		{
			if (components == null || components.Count == 0)
			{
				return null;
			}
			return components[0].name;
		}
	}

	public int numberOfComponents => components.Count;

	public string dotSeparatedComponents
	{
		get
		{
			if (_dotSeparatedComponents == null)
			{
				_dotSeparatedComponents = string.Join(".", components.Select((Identifier c) => c?.name));
			}
			return _dotSeparatedComponents;
		}
	}

	public List<Identifier> components { get; }

	public Path(FlowLevel baseFlowLevel, List<Identifier> components)
	{
		_baseTargetLevel = baseFlowLevel;
		this.components = components;
	}

	public Path(List<Identifier> components)
	{
		_baseTargetLevel = null;
		this.components = components;
	}

	public Path(Identifier ambiguousName)
	{
		_baseTargetLevel = null;
		components = new List<Identifier>();
		components.Add(ambiguousName);
	}

	public override string ToString()
	{
		if (components == null || components.Count == 0)
		{
			if (baseTargetLevel == FlowLevel.WeavePoint)
			{
				return "-> <next gather point>";
			}
			return "<invalid Path>";
		}
		return "-> " + dotSeparatedComponents;
	}

	public Object ResolveFromContext(Object context)
	{
		if (components == null || components.Count == 0)
		{
			return null;
		}
		Object obj = ResolveBaseTarget(context);
		if (obj == null)
		{
			return null;
		}
		if (components.Count > 1)
		{
			return ResolveTailComponents(obj);
		}
		return obj;
	}

	private Object ResolveBaseTarget(Object originalContext)
	{
		string childName = firstComponent;
		Object obj = originalContext;
		while (obj != null)
		{
			bool forceDeepSearch = obj == originalContext;
			Object obj2 = TryGetChildFromContext(obj, childName, null, forceDeepSearch);
			if (obj2 != null)
			{
				return obj2;
			}
			obj = obj.parent;
		}
		return null;
	}

	private Object ResolveTailComponents(Object rootTarget)
	{
		Object obj = rootTarget;
		for (int i = 1; i < components.Count; i++)
		{
			string name = components[i].name;
			FlowBase flowBase = obj as FlowBase;
			FlowLevel value = ((!(flowBase != null)) ? FlowLevel.WeavePoint : (flowBase.flowLevel + 1));
			obj = TryGetChildFromContext(obj, name, value);
			if (obj == null)
			{
				break;
			}
		}
		return obj;
	}

	private Object TryGetChildFromContext(Object context, string childName, FlowLevel? minimumLevel, bool forceDeepSearch = false)
	{
		bool flag = !minimumLevel.HasValue;
		Weave weave = context as Weave;
		if (weave != null && (flag || minimumLevel == FlowLevel.WeavePoint))
		{
			return (Object)weave.WeavePointNamed(childName);
		}
		FlowBase flowBase = context as FlowBase;
		if (flowBase != null)
		{
			bool deepSearch = forceDeepSearch || flowBase.flowLevel == FlowLevel.Knot;
			return flowBase.ContentWithNameAtLevel(childName, minimumLevel, deepSearch);
		}
		return null;
	}
}
