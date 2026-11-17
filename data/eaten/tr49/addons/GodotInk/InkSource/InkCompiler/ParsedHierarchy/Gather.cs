using Ink.Runtime;

namespace Ink.Parsed;

public class Gather : Object, IWeavePoint, INamedContent
{
	public string name => identifier?.name;

	public Identifier identifier { get; set; }

	public int indentationDepth { get; protected set; }

	public Container runtimeContainer => (Container)base.runtimeObject;

	public Gather(Identifier identifier, int indentationDepth)
	{
		this.identifier = identifier;
		this.indentationDepth = indentationDepth;
	}

	public override Ink.Runtime.Object GenerateRuntimeObject()
	{
		Container container = new Container();
		container.name = name;
		if (base.story.countAllVisits)
		{
			container.visitsShouldBeCounted = true;
		}
		container.countingAtStartOnly = true;
		if (base.content != null)
		{
			foreach (Object item in base.content)
			{
				container.AddContent(item.runtimeObject);
			}
		}
		return container;
	}

	public override void ResolveReferences(Story context)
	{
		base.ResolveReferences(context);
		if (identifier != null && identifier.name.Length > 0)
		{
			context.CheckForNamingCollisions(this, identifier, Story.SymbolType.SubFlowAndWeave);
		}
	}
}
