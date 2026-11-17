using System.Collections.Generic;
using System.Linq;
using Ink.Runtime;

namespace Ink.Parsed;

public class VariableReference : Expression
{
	private Identifier _singleIdentifier;

	public List<Identifier> pathIdentifiers;

	public bool isConstantReference;

	public bool isListItemReference;

	private Ink.Runtime.VariableReference _runtimeVarRef;

	public string name { get; private set; }

	public Identifier identifier
	{
		get
		{
			if (pathIdentifiers == null || pathIdentifiers.Count == 0)
			{
				return null;
			}
			if (_singleIdentifier == null)
			{
				string text = string.Join(".", path.ToArray());
				DebugMetadata seed = pathIdentifiers.First().debugMetadata;
				DebugMetadata debugMetadata = pathIdentifiers.Aggregate(seed, (DebugMetadata acc, Identifier id) => acc.Merge(id.debugMetadata));
				_singleIdentifier = new Identifier
				{
					name = text,
					debugMetadata = debugMetadata
				};
			}
			return _singleIdentifier;
		}
	}

	public List<string> path { get; private set; }

	public Ink.Runtime.VariableReference runtimeVarRef => _runtimeVarRef;

	public VariableReference(List<Identifier> pathIdentifiers)
	{
		this.pathIdentifiers = pathIdentifiers;
		path = pathIdentifiers.Select((Identifier id) => id?.name).ToList();
		name = string.Join(".", pathIdentifiers);
	}

	public override void GenerateIntoContainer(Container container)
	{
		Expression value = null;
		if (base.story.constants.TryGetValue(name, out value))
		{
			value.GenerateConstantIntoContainer(container);
			isConstantReference = true;
			return;
		}
		_runtimeVarRef = new Ink.Runtime.VariableReference(name);
		if (path.Count == 1 || path.Count == 2)
		{
			string text = null;
			string listName = null;
			if (path.Count == 1)
			{
				text = path[0];
			}
			else
			{
				listName = path[0];
				text = path[1];
			}
			if ((bool)base.story.ResolveListItem(listName, text, this))
			{
				isListItemReference = true;
			}
		}
		container.AddContent(_runtimeVarRef);
	}

	public override void ResolveReferences(Story context)
	{
		base.ResolveReferences(context);
		if (isConstantReference || isListItemReference)
		{
			return;
		}
		Path path = new Path(pathIdentifiers);
		Object obj = path.ResolveFromContext(this);
		if ((bool)obj)
		{
			obj.containerForCounting.visitsShouldBeCounted = true;
			if (!(_runtimeVarRef == null))
			{
				_runtimeVarRef.pathForCount = obj.runtimePath;
				_runtimeVarRef.name = null;
				FlowBase flowBase = obj as FlowBase;
				if ((bool)flowBase && flowBase.isFunction && (base.parent is Weave || base.parent is ContentList || base.parent is FlowBase))
				{
					Warning("'" + flowBase.identifier?.ToString() + "' being used as read count rather than being called as function. Perhaps you intended to write " + flowBase.name + "()");
				}
			}
		}
		else if (this.path.Count > 1)
		{
			string text = "Could not find target for read count: " + path;
			if (this.path.Count <= 2)
			{
				text = text + ", or couldn't find list item with the name " + string.Join(",", this.path.ToArray());
			}
			Error(text);
		}
		else if (!context.ResolveVariableWithName(name, this).found)
		{
			Error("Unresolved variable: " + ToString(), this);
		}
	}

	public override string ToString()
	{
		return string.Join(".", path.ToArray());
	}
}
