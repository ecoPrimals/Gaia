using System.Collections.Generic;
using Ink.Runtime;

namespace Ink.Parsed;

public class ExternalDeclaration : Object, INamedContent
{
	public string name => identifier?.name;

	public Identifier identifier { get; set; }

	public List<string> argumentNames { get; set; }

	public ExternalDeclaration(Identifier identifier, List<string> argumentNames)
	{
		this.identifier = identifier;
		this.argumentNames = argumentNames;
	}

	public override Ink.Runtime.Object GenerateRuntimeObject()
	{
		base.story.AddExternal(this);
		return null;
	}
}
