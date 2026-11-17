using System;

namespace Ink;

public class StringParserState
{
	public class Element
	{
		public int characterIndex;

		public int characterInLineIndex;

		public int lineIndex;

		public bool reportedErrorInScope;

		public int uniqueId;

		public uint customFlags;

		private static int _uniqueIdCounter;

		public void CopyFrom(Element fromElement)
		{
			_uniqueIdCounter++;
			uniqueId = _uniqueIdCounter;
			characterIndex = fromElement.characterIndex;
			characterInLineIndex = fromElement.characterInLineIndex;
			lineIndex = fromElement.lineIndex;
			customFlags = fromElement.customFlags;
			reportedErrorInScope = false;
		}

		public void SquashFrom(Element fromElement)
		{
			characterIndex = fromElement.characterIndex;
			characterInLineIndex = fromElement.characterInLineIndex;
			lineIndex = fromElement.lineIndex;
			reportedErrorInScope = fromElement.reportedErrorInScope;
			customFlags = fromElement.customFlags;
		}
	}

	private Element[] _stack;

	private int _numElements;

	public int lineIndex
	{
		get
		{
			return currentElement.lineIndex;
		}
		set
		{
			currentElement.lineIndex = value;
		}
	}

	public int characterIndex
	{
		get
		{
			return currentElement.characterIndex;
		}
		set
		{
			currentElement.characterIndex = value;
		}
	}

	public int characterInLineIndex
	{
		get
		{
			return currentElement.characterInLineIndex;
		}
		set
		{
			currentElement.characterInLineIndex = value;
		}
	}

	public uint customFlags
	{
		get
		{
			return currentElement.customFlags;
		}
		set
		{
			currentElement.customFlags = value;
		}
	}

	public bool errorReportedAlreadyInScope => currentElement.reportedErrorInScope;

	public int stackHeight => _numElements;

	protected Element currentElement => _stack[_numElements - 1];

	public StringParserState()
	{
		_stack = new Element[200];
		for (int i = 0; i < 200; i++)
		{
			_stack[i] = new Element();
		}
		_numElements = 1;
	}

	public int Push()
	{
		if (_numElements >= _stack.Length)
		{
			throw new Exception("Stack overflow in parser state");
		}
		Element fromElement = _stack[_numElements - 1];
		Element obj = _stack[_numElements];
		_numElements++;
		obj.CopyFrom(fromElement);
		return obj.uniqueId;
	}

	public void Pop(int expectedRuleId)
	{
		if (_numElements == 1)
		{
			throw new Exception("Attempting to remove final stack element is illegal! Mismatched Begin/Succceed/Fail?");
		}
		if (currentElement.uniqueId != expectedRuleId)
		{
			throw new Exception("Mismatched rule IDs - do you have mismatched Begin/Succeed/Fail?");
		}
		_numElements--;
	}

	public Element Peek(int expectedRuleId)
	{
		if (currentElement.uniqueId != expectedRuleId)
		{
			throw new Exception("Mismatched rule IDs - do you have mismatched Begin/Succeed/Fail?");
		}
		return _stack[_numElements - 1];
	}

	public Element PeekPenultimate()
	{
		if (_numElements >= 2)
		{
			return _stack[_numElements - 2];
		}
		return null;
	}

	public void Squash()
	{
		if (_numElements < 2)
		{
			throw new Exception("Attempting to remove final stack element is illegal! Mismatched Begin/Succceed/Fail?");
		}
		Element obj = _stack[_numElements - 2];
		Element fromElement = _stack[_numElements - 1];
		obj.SquashFrom(fromElement);
		_numElements--;
	}

	public void NoteErrorReported()
	{
		Element[] stack = _stack;
		for (int i = 0; i < stack.Length; i++)
		{
			stack[i].reportedErrorInScope = true;
		}
	}
}
