using System;
using System.Collections.Generic;
using System.ComponentModel;
using Godot;
using Godot.Collections;
using Ink.Runtime;

namespace GodotInk;

[Tool]
[GlobalClass]
public partial class InkChoice : RefCounted
{
	public readonly Choice inner;

	public string Text => inner.text;

	public string PathStringOnChoice => inner.pathStringOnChoice;

	public string SourcePath => inner.sourcePath;

	public int Index => inner.index;

	public IReadOnlyList<string> Tags
	{
		get
		{
			IReadOnlyList<string> tags = inner.tags;
			return tags ?? System.Array.Empty<string>();
		}
	}

	private InkChoice()
	{
		inner = new Choice();
	}

	public InkChoice(Choice inner)
	{
		this.inner = inner;
	}

	[EditorBrowsable(EditorBrowsableState.Never)]
	public string GetText()
	{
		return Text;
	}

	[EditorBrowsable(EditorBrowsableState.Never)]
	public string GetPathStringOnChoice()
	{
		return PathStringOnChoice;
	}

	[EditorBrowsable(EditorBrowsableState.Never)]
	public string GetSourcePath()
	{
		return SourcePath;
	}

	[EditorBrowsable(EditorBrowsableState.Never)]
	public int GetIndex()
	{
		return Index;
	}

	[EditorBrowsable(EditorBrowsableState.Never)]
	public Array<string> GetTags()
	{
		return new Array<string>(Tags);
	}
}
