using System;
using Ink.Runtime;

namespace Ink.Parsed;

public class ListElementDefinition : Object
{
	public Identifier identifier;

	public int? explicitValue;

	public int seriesValue;

	public bool inInitialList;

	public string name => identifier?.name;

	public string fullName
	{
		get
		{
			ListDefinition obj = base.parent as ListDefinition;
			if (obj == null)
			{
				throw new Exception("Can't get full name without a parent list");
			}
			return obj.identifier?.ToString() + "." + name;
		}
	}

	public override string typeName => "List element";

	public ListElementDefinition(Identifier identifier, bool inInitialList, int? explicitValue = null)
	{
		this.identifier = identifier;
		this.inInitialList = inInitialList;
		this.explicitValue = explicitValue;
	}

	public override Ink.Runtime.Object GenerateRuntimeObject()
	{
		throw new NotImplementedException();
	}

	public override void ResolveReferences(Story context)
	{
		base.ResolveReferences(context);
		context.CheckForNamingCollisions(this, identifier, Story.SymbolType.ListItem);
	}
}
