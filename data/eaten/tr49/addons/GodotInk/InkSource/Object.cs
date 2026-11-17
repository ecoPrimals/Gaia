using System;
using System.Collections.Generic;
using System.Text;
using Ink.Runtime;

namespace Ink.Parsed;

public abstract class Object
{
	public delegate bool FindQueryFunc<T>(T obj);

	private DebugMetadata _debugMetadata;

	private Ink.Runtime.Object _runtimeObject;

	private bool _alreadyHadError;

	private bool _alreadyHadWarning;

	public DebugMetadata debugMetadata
	{
		get
		{
			if (_debugMetadata == null && (bool)parent)
			{
				return parent.debugMetadata;
			}
			return _debugMetadata;
		}
		set
		{
			_debugMetadata = value;
		}
	}

	public bool hasOwnDebugMetadata => _debugMetadata != null;

	public virtual string typeName => GetType().Name;

	public Object parent { get; set; }

	public List<Object> content { get; protected set; }

	public Story story
	{
		get
		{
			Object obj = this;
			while ((bool)obj.parent)
			{
				obj = obj.parent;
			}
			return obj as Story;
		}
	}

	public Ink.Runtime.Object runtimeObject
	{
		get
		{
			if (_runtimeObject == null)
			{
				_runtimeObject = GenerateRuntimeObject();
				if ((bool)_runtimeObject)
				{
					_runtimeObject.debugMetadata = debugMetadata;
				}
			}
			return _runtimeObject;
		}
		set
		{
			_runtimeObject = value;
		}
	}

	public virtual Ink.Runtime.Path runtimePath => runtimeObject.path;

	public virtual Container containerForCounting => runtimeObject as Container;

	public List<Object> ancestry
	{
		get
		{
			List<Object> list = new List<Object>();
			Object obj = parent;
			while ((bool)obj)
			{
				list.Add(obj);
				obj = obj.parent;
			}
			list.Reverse();
			return list;
		}
	}

	public string descriptionOfScope
	{
		get
		{
			List<string> list = new List<string>();
			Object obj = this;
			while ((bool)obj)
			{
				FlowBase flowBase = obj as FlowBase;
				if ((bool)flowBase && flowBase.identifier != null)
				{
					list.Add("'" + flowBase.identifier?.ToString() + "'");
				}
				obj = obj.parent;
			}
			StringBuilder stringBuilder = new StringBuilder();
			if (list.Count > 0)
			{
				string value = string.Join(", ", list.ToArray());
				stringBuilder.Append(value);
				stringBuilder.Append(" and ");
			}
			stringBuilder.Append("at top scope");
			return stringBuilder.ToString();
		}
	}

	public Path PathRelativeTo(Object otherObj)
	{
		List<Object> list = ancestry;
		List<Object> list2 = otherObj.ancestry;
		Object obj = null;
		int num = Math.Min(list.Count, list2.Count);
		for (int i = 0; i < num; i++)
		{
			Object obj2 = ancestry[i];
			Object obj3 = list2[i];
			if (!(obj2 == obj3))
			{
				break;
			}
			obj = obj2;
		}
		FlowBase flowBase = obj as FlowBase;
		if (flowBase == null)
		{
			flowBase = obj.ClosestFlowBase();
		}
		List<Identifier> list3 = new List<Identifier>();
		bool flag = false;
		FlowLevel baseFlowLevel = FlowLevel.WeavePoint;
		Object obj4 = this;
		while ((bool)obj4 && obj4 != flowBase && !(obj4 is Story) && !(obj4 == flowBase))
		{
			if (!flag && obj4 is IWeavePoint { identifier: not null } weavePoint)
			{
				list3.Add(weavePoint.identifier);
				flag = true;
				continue;
			}
			FlowBase flowBase2 = obj4 as FlowBase;
			if ((bool)flowBase2)
			{
				list3.Add(flowBase2.identifier);
				baseFlowLevel = flowBase2.flowLevel;
			}
			obj4 = obj4.parent;
		}
		list3.Reverse();
		if (list3.Count > 0)
		{
			return new Path(baseFlowLevel, list3);
		}
		return null;
	}

	public T AddContent<T>(T subContent) where T : Object
	{
		if (content == null)
		{
			content = new List<Object>();
		}
		if ((bool)subContent)
		{
			subContent.parent = this;
			content.Add(subContent);
		}
		return subContent;
	}

	public void AddContent<T>(List<T> listContent) where T : Object
	{
		foreach (T item in listContent)
		{
			AddContent(item);
		}
	}

	public T InsertContent<T>(int index, T subContent) where T : Object
	{
		if (content == null)
		{
			content = new List<Object>();
		}
		subContent.parent = this;
		content.Insert(index, subContent);
		return subContent;
	}

	public T Find<T>(FindQueryFunc<T> queryFunc = null) where T : class
	{
		if (this is T val && (queryFunc == null || queryFunc(val)))
		{
			return val;
		}
		if (content == null)
		{
			return null;
		}
		foreach (Object item in content)
		{
			T val2 = item.Find(queryFunc);
			if (val2 != null)
			{
				return val2;
			}
		}
		return null;
	}

	public List<T> FindAll<T>(FindQueryFunc<T> queryFunc = null) where T : class
	{
		List<T> list = new List<T>();
		FindAll(queryFunc, list);
		return list;
	}

	private void FindAll<T>(FindQueryFunc<T> queryFunc, List<T> foundSoFar) where T : class
	{
		if (this is T val && (queryFunc == null || queryFunc(val)))
		{
			foundSoFar.Add(val);
		}
		if (content == null)
		{
			return;
		}
		foreach (Object item in content)
		{
			item.FindAll(queryFunc, foundSoFar);
		}
	}

	public abstract Ink.Runtime.Object GenerateRuntimeObject();

	public virtual void ResolveReferences(Story context)
	{
		if (content == null)
		{
			return;
		}
		foreach (Object item in content)
		{
			item.ResolveReferences(context);
		}
	}

	public FlowBase ClosestFlowBase()
	{
		Object obj = parent;
		while ((bool)obj)
		{
			if (obj is FlowBase)
			{
				return (FlowBase)obj;
			}
			obj = obj.parent;
		}
		return null;
	}

	public virtual void Error(string message, Object source = null, bool isWarning = false)
	{
		if (source == null)
		{
			source = this;
		}
		if ((!source._alreadyHadError || isWarning) && !(source._alreadyHadWarning & isWarning))
		{
			if (!parent)
			{
				throw new Exception("No parent object to send error to: " + message);
			}
			parent.Error(message, source, isWarning);
			if (isWarning)
			{
				source._alreadyHadWarning = true;
			}
			else
			{
				source._alreadyHadError = true;
			}
		}
	}

	public void Warning(string message, Object source = null)
	{
		Error(message, source, isWarning: true);
	}

	public static implicit operator bool(Object obj)
	{
		return (object)obj != null;
	}

	public static bool operator ==(Object a, Object b)
	{
		return (object)a == b;
	}

	public static bool operator !=(Object a, Object b)
	{
		return !(a == b);
	}

	public override bool Equals(object obj)
	{
		return obj == this;
	}

	public override int GetHashCode()
	{
		return base.GetHashCode();
	}
}
