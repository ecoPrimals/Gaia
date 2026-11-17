using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
using Ink.Parsed;

namespace Ink;

public class StringParser
{
	public delegate object ParseRule();

	public delegate T SpecificParseRule<T>() where T : class;

	public delegate void ErrorHandler(string message, int index, int lineIndex, bool isWarning);

	public class ParseSuccessStruct
	{
	}

	public static ParseSuccessStruct ParseSuccess = new ParseSuccessStruct();

	public static CharacterSet numbersCharacterSet = new CharacterSet("0123456789");

	private char[] _chars;

	protected ErrorHandler errorHandler { get; set; }

	public char currentCharacter
	{
		get
		{
			if (index >= 0 && remainingLength > 0)
			{
				return _chars[index];
			}
			return '\0';
		}
	}

	public StringParserState state { get; private set; }

	public bool hadError { get; protected set; }

	public bool endOfInput => index >= _chars.Length;

	public string remainingString => new string(_chars, index, remainingLength);

	public int remainingLength => _chars.Length - index;

	public string inputString { get; private set; }

	public int lineIndex
	{
		get
		{
			return state.lineIndex;
		}
		set
		{
			state.lineIndex = value;
		}
	}

	public int characterInLineIndex
	{
		get
		{
			return state.characterInLineIndex;
		}
		set
		{
			state.characterInLineIndex = value;
		}
	}

	public int index
	{
		get
		{
			return state.characterIndex;
		}
		private set
		{
			state.characterIndex = value;
		}
	}

	public StringParser(string str)
	{
		str = PreProcessInputString(str);
		state = new StringParserState();
		if (str != null)
		{
			_chars = str.ToCharArray();
		}
		else
		{
			_chars = new char[0];
		}
		inputString = str;
	}

	protected virtual string PreProcessInputString(string str)
	{
		return str;
	}

	protected int BeginRule()
	{
		return state.Push();
	}

	protected object FailRule(int expectedRuleId)
	{
		state.Pop(expectedRuleId);
		return null;
	}

	protected void CancelRule(int expectedRuleId)
	{
		state.Pop(expectedRuleId);
	}

	protected object SucceedRule(int expectedRuleId, object result = null)
	{
		StringParserState.Element endState = state.Peek(expectedRuleId);
		StringParserState.Element startState = state.PeekPenultimate();
		RuleDidSucceed(result, startState, endState);
		state.Squash();
		if (result == null)
		{
			result = ParseSuccess;
		}
		return result;
	}

	protected virtual void RuleDidSucceed(object result, StringParserState.Element startState, StringParserState.Element endState)
	{
	}

	protected object Expect(ParseRule rule, string message = null, ParseRule recoveryRule = null)
	{
		object obj = ParseObject(rule);
		if (obj == null)
		{
			if (message == null)
			{
				message = rule.Method.Name;
			}
			string text = LineRemainder();
			string text2 = ((text != null && text.Length != 0) ? ("'" + text + "'") : "end of line");
			Error("Expected " + message + " but saw " + text2);
			if (recoveryRule != null)
			{
				obj = recoveryRule();
			}
		}
		return obj;
	}

	protected void Error(string message, bool isWarning = false)
	{
		ErrorOnLine(message, lineIndex + 1, isWarning);
	}

	protected void ErrorWithParsedObject(string message, Ink.Parsed.Object result, bool isWarning = false)
	{
		ErrorOnLine(message, result.debugMetadata.startLineNumber, isWarning);
	}

	protected void ErrorOnLine(string message, int lineNumber, bool isWarning)
	{
		if (!state.errorReportedAlreadyInScope)
		{
			string text = (isWarning ? "Warning" : "Error");
			if (errorHandler == null)
			{
				throw new Exception(text + " on line " + lineNumber + ": " + message);
			}
			errorHandler(message, index, lineNumber - 1, isWarning);
			state.NoteErrorReported();
		}
		if (!isWarning)
		{
			hadError = true;
		}
	}

	protected void Warning(string message)
	{
		Error(message, isWarning: true);
	}

	public string LineRemainder()
	{
		return (string)Peek(() => ParseUntilCharactersFromString("\n\r"));
	}

	public void SetFlag(uint flag, bool trueOrFalse)
	{
		if (trueOrFalse)
		{
			state.customFlags |= flag;
		}
		else
		{
			state.customFlags &= ~flag;
		}
	}

	public bool GetFlag(uint flag)
	{
		return (state.customFlags & flag) != 0;
	}

	public object ParseObject(ParseRule rule)
	{
		int expectedRuleId = BeginRule();
		int stackHeight = state.stackHeight;
		object obj = rule();
		if (stackHeight != state.stackHeight)
		{
			throw new Exception("Mismatched Begin/Fail/Succeed rules");
		}
		if (obj == null)
		{
			return FailRule(expectedRuleId);
		}
		SucceedRule(expectedRuleId, obj);
		return obj;
	}

	public T Parse<T>(SpecificParseRule<T> rule) where T : class
	{
		int expectedRuleId = BeginRule();
		T val = rule();
		if (val == null)
		{
			FailRule(expectedRuleId);
			return null;
		}
		SucceedRule(expectedRuleId, val);
		return val;
	}

	public object OneOf(params ParseRule[] array)
	{
		foreach (ParseRule rule in array)
		{
			object obj = ParseObject(rule);
			if (obj != null)
			{
				return obj;
			}
		}
		return null;
	}

	public List<object> OneOrMore(ParseRule rule)
	{
		List<object> list = new List<object>();
		object obj = null;
		do
		{
			obj = ParseObject(rule);
			if (obj != null)
			{
				list.Add(obj);
			}
		}
		while (obj != null);
		if (list.Count > 0)
		{
			return list;
		}
		return null;
	}

	public ParseRule Optional(ParseRule rule)
	{
		return delegate
		{
			object obj = ParseObject(rule);
			if (obj == null)
			{
				obj = ParseSuccess;
			}
			return obj;
		};
	}

	public ParseRule Exclude(ParseRule rule)
	{
		return () => (ParseObject(rule) == null) ? null : ParseSuccess;
	}

	public ParseRule OptionalExclude(ParseRule rule)
	{
		return delegate
		{
			ParseObject(rule);
			return ParseSuccess;
		};
	}

	protected ParseRule String(string str)
	{
		return () => ParseString(str);
	}

	private void TryAddResultToList<T>(object result, List<T> list, bool flatten = true)
	{
		if (result == ParseSuccess)
		{
			return;
		}
		if (flatten && result is ICollection collection)
		{
			{
				foreach (object item in collection)
				{
					list.Add((T)item);
				}
				return;
			}
		}
		list.Add((T)result);
	}

	public List<T> Interleave<T>(ParseRule ruleA, ParseRule ruleB, ParseRule untilTerminator = null, bool flatten = true)
	{
		int expectedRuleId = BeginRule();
		List<T> list = new List<T>();
		object obj = ParseObject(ruleA);
		if (obj == null)
		{
			return (List<T>)FailRule(expectedRuleId);
		}
		TryAddResultToList(obj, list, flatten);
		object obj2 = null;
		object obj3 = null;
		while (untilTerminator == null || Peek(untilTerminator) == null)
		{
			obj2 = ParseObject(ruleB);
			if (obj2 == null)
			{
				break;
			}
			TryAddResultToList(obj2, list, flatten);
			obj3 = null;
			if (obj2 != null)
			{
				obj3 = ParseObject(ruleA);
				if (obj3 == null)
				{
					break;
				}
				TryAddResultToList(obj3, list, flatten);
			}
			if ((obj2 == null && obj3 == null) || (obj2 == ParseSuccess && obj3 == ParseSuccess) || remainingLength <= 0)
			{
				break;
			}
		}
		if (list.Count == 0)
		{
			return (List<T>)FailRule(expectedRuleId);
		}
		return (List<T>)SucceedRule(expectedRuleId, list);
	}

	public string ParseString(string str)
	{
		if (str.Length > remainingLength)
		{
			return null;
		}
		int expectedRuleId = BeginRule();
		int num = index;
		int num2 = characterInLineIndex;
		int num3 = lineIndex;
		bool flag = true;
		foreach (char c in str)
		{
			if (_chars[num] != c)
			{
				flag = false;
				break;
			}
			if (c == '\n')
			{
				num3++;
				num2 = -1;
			}
			num++;
			num2++;
		}
		index = num;
		characterInLineIndex = num2;
		lineIndex = num3;
		if (flag)
		{
			return (string)SucceedRule(expectedRuleId, str);
		}
		return (string)FailRule(expectedRuleId);
	}

	public char ParseSingleCharacter()
	{
		if (remainingLength > 0)
		{
			char num = _chars[index];
			if (num == '\n')
			{
				lineIndex++;
				characterInLineIndex = -1;
			}
			index++;
			characterInLineIndex++;
			return num;
		}
		return '\0';
	}

	public string ParseUntilCharactersFromString(string str, int maxCount = -1)
	{
		return ParseCharactersFromString(str, shouldIncludeStrChars: false, maxCount);
	}

	public string ParseUntilCharactersFromCharSet(CharacterSet charSet, int maxCount = -1)
	{
		return ParseCharactersFromCharSet(charSet, shouldIncludeChars: false, maxCount);
	}

	public string ParseCharactersFromString(string str, int maxCount = -1)
	{
		return ParseCharactersFromString(str, shouldIncludeStrChars: true, maxCount);
	}

	public string ParseCharactersFromString(string str, bool shouldIncludeStrChars, int maxCount = -1)
	{
		return ParseCharactersFromCharSet(new CharacterSet(str), shouldIncludeStrChars);
	}

	public string ParseCharactersFromCharSet(CharacterSet charSet, bool shouldIncludeChars = true, int maxCount = -1)
	{
		if (maxCount == -1)
		{
			maxCount = int.MaxValue;
		}
		int num = index;
		int num2 = index;
		int num3 = characterInLineIndex;
		int num4 = lineIndex;
		int num5 = 0;
		while (num2 < _chars.Length && charSet.Contains(_chars[num2]) == shouldIncludeChars && num5 < maxCount)
		{
			if (_chars[num2] == '\n')
			{
				num4++;
				num3 = -1;
			}
			num2++;
			num3++;
			num5++;
		}
		index = num2;
		characterInLineIndex = num3;
		lineIndex = num4;
		if (index > num)
		{
			return new string(_chars, num, index - num);
		}
		return null;
	}

	public object Peek(ParseRule rule)
	{
		int expectedRuleId = BeginRule();
		object result = rule();
		CancelRule(expectedRuleId);
		return result;
	}

	public string ParseUntil(ParseRule stopRule, CharacterSet pauseCharacters = null, CharacterSet endCharacters = null)
	{
		int expectedRuleId = BeginRule();
		CharacterSet characterSet = new CharacterSet();
		if (pauseCharacters != null)
		{
			characterSet.UnionWith(pauseCharacters);
		}
		if (endCharacters != null)
		{
			characterSet.UnionWith(endCharacters);
		}
		StringBuilder stringBuilder = new StringBuilder();
		while (true)
		{
			string text = ParseUntilCharactersFromCharSet(characterSet);
			if (text != null)
			{
				stringBuilder.Append(text);
			}
			if (Peek(stopRule) != null || endOfInput)
			{
				break;
			}
			char c = currentCharacter;
			if (pauseCharacters == null || !pauseCharacters.Contains(c))
			{
				break;
			}
			stringBuilder.Append(c);
			if (c == '\n')
			{
				lineIndex++;
				characterInLineIndex = -1;
			}
			index++;
			characterInLineIndex++;
		}
		if (stringBuilder.Length > 0)
		{
			return (string)SucceedRule(expectedRuleId, stringBuilder.ToString());
		}
		return (string)FailRule(expectedRuleId);
	}

	public int? ParseInt()
	{
		int num = index;
		int num2 = characterInLineIndex;
		bool flag = ParseString("-") != null;
		ParseCharactersFromString(" \t");
		string text = ParseCharactersFromCharSet(numbersCharacterSet);
		if (text == null)
		{
			index = num;
			characterInLineIndex = num2;
			return null;
		}
		if (int.TryParse(text, out var result))
		{
			return flag ? (-result) : result;
		}
		Error("Failed to read integer value: " + text + ". Perhaps it's out of the range of acceptable numbers ink supports? (" + int.MinValue + " to " + int.MaxValue + ")");
		return null;
	}

	public float? ParseFloat()
	{
		int num = index;
		int num2 = characterInLineIndex;
		int? num3 = ParseInt();
		if (num3.HasValue && ParseString(".") != null)
		{
			string text = ParseCharactersFromCharSet(numbersCharacterSet);
			int? num4 = num3;
			return float.Parse(num4 + "." + text, CultureInfo.InvariantCulture);
		}
		index = num;
		characterInLineIndex = num2;
		return null;
	}

	protected string ParseNewline()
	{
		int expectedRuleId = BeginRule();
		ParseString("\r");
		if (ParseString("\n") == null)
		{
			return (string)FailRule(expectedRuleId);
		}
		return (string)SucceedRule(expectedRuleId, "\n");
	}
}
