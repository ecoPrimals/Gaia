using Ink.Runtime;

namespace Ink.Parsed;

public class Wrap<T> : Object where T : Ink.Runtime.Object
{
	private T _objToWrap;

	public Wrap(T objToWrap)
	{
		_objToWrap = objToWrap;
	}

	public override Ink.Runtime.Object GenerateRuntimeObject()
	{
		return _objToWrap;
	}
}
