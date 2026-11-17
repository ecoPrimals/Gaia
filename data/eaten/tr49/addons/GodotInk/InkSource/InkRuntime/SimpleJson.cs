using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Text;

namespace Ink.Runtime;

public static class SimpleJson
{
	private class Reader
	{
		private string _text;

		private int _offset;

		private object _rootObject;

		public Reader(string text)
		{
			_text = text;
			_offset = 0;
			SkipWhitespace();
			_rootObject = ReadObject();
		}

		public Dictionary<string, object> ToDictionary()
		{
			return (Dictionary<string, object>)_rootObject;
		}

		public List<object> ToArray()
		{
			return (List<object>)_rootObject;
		}

		private bool IsNumberChar(char c)
		{
			if ((c < '0' || c > '9') && c != '.' && c != '-' && c != '+' && c != 'E')
			{
				return c == 'e';
			}
			return true;
		}

		private bool IsFirstNumberChar(char c)
		{
			if ((c < '0' || c > '9') && c != '-')
			{
				return c == '+';
			}
			return true;
		}

		private object ReadObject()
		{
			char c = _text[_offset];
			switch (c)
			{
			case '{':
				return ReadDictionary();
			case '[':
				return ReadArray();
			case '"':
				return ReadString();
			default:
				if (IsFirstNumberChar(c))
				{
					return ReadNumber();
				}
				if (TryRead("true"))
				{
					return true;
				}
				if (TryRead("false"))
				{
					return false;
				}
				if (TryRead("null"))
				{
					return null;
				}
				throw new Exception("Unhandled object type in JSON: " + _text.Substring(_offset, 30));
			}
		}

		private Dictionary<string, object> ReadDictionary()
		{
			Dictionary<string, object> dictionary = new Dictionary<string, object>();
			Expect("{");
			SkipWhitespace();
			if (TryRead("}"))
			{
				return dictionary;
			}
			do
			{
				SkipWhitespace();
				string text = ReadString();
				Expect(text != null, "dictionary key");
				SkipWhitespace();
				Expect(":");
				SkipWhitespace();
				object obj = ReadObject();
				Expect(obj != null, "dictionary value");
				dictionary[text] = obj;
				SkipWhitespace();
			}
			while (TryRead(","));
			Expect("}");
			return dictionary;
		}

		private List<object> ReadArray()
		{
			List<object> list = new List<object>();
			Expect("[");
			SkipWhitespace();
			if (TryRead("]"))
			{
				return list;
			}
			do
			{
				SkipWhitespace();
				object item = ReadObject();
				list.Add(item);
				SkipWhitespace();
			}
			while (TryRead(","));
			Expect("]");
			return list;
		}

		private string ReadString()
		{
			Expect("\"");
			StringBuilder stringBuilder = new StringBuilder();
			for (; _offset < _text.Length; _offset++)
			{
				char c = _text[_offset];
				switch (c)
				{
				case '\\':
					_offset++;
					if (_offset >= _text.Length)
					{
						throw new Exception("Unexpected EOF while reading string");
					}
					c = _text[_offset];
					switch (c)
					{
					case '"':
					case '/':
					case '\\':
						stringBuilder.Append(c);
						break;
					case 'n':
						stringBuilder.Append('\n');
						break;
					case 't':
						stringBuilder.Append('\t');
						break;
					case 'u':
					{
						if (_offset + 4 >= _text.Length)
						{
							throw new Exception("Unexpected EOF while reading string");
						}
						if (int.TryParse(_text.Substring(_offset + 1, 4), NumberStyles.AllowHexSpecifier, CultureInfo.InvariantCulture, out var result))
						{
							stringBuilder.Append((char)result);
							_offset += 4;
							break;
						}
						throw new Exception("Invalid Unicode escape character at offset " + (_offset - 1));
					}
					default:
						throw new Exception("Invalid Unicode escape character at offset " + (_offset - 1));
					case 'b':
					case 'f':
					case 'r':
						break;
					}
					continue;
				default:
					stringBuilder.Append(c);
					continue;
				case '"':
					break;
				}
				break;
			}
			Expect("\"");
			return stringBuilder.ToString();
		}

		private object ReadNumber()
		{
			int offset = _offset;
			bool flag = false;
			while (_offset < _text.Length)
			{
				char c = _text[_offset];
				if (c == '.' || c == 'e' || c == 'E')
				{
					flag = true;
				}
				if (!IsNumberChar(c))
				{
					break;
				}
				_offset++;
			}
			string text = _text.Substring(offset, _offset - offset);
			int result2;
			if (flag)
			{
				if (float.TryParse(text, NumberStyles.Float, CultureInfo.InvariantCulture, out var result))
				{
					return result;
				}
			}
			else if (int.TryParse(text, out result2))
			{
				return result2;
			}
			throw new Exception("Failed to parse number value: " + text);
		}

		private bool TryRead(string textToRead)
		{
			if (_offset + textToRead.Length > _text.Length)
			{
				return false;
			}
			for (int i = 0; i < textToRead.Length; i++)
			{
				if (textToRead[i] != _text[_offset + i])
				{
					return false;
				}
			}
			_offset += textToRead.Length;
			return true;
		}

		private void Expect(string expectedStr)
		{
			if (!TryRead(expectedStr))
			{
				Expect(condition: false, expectedStr);
			}
		}

		private void Expect(bool condition, string message = null)
		{
			if (!condition)
			{
				message = ((message != null) ? ("Expected " + message) : "Unexpected token");
				message = message + " at offset " + _offset;
				throw new Exception(message);
			}
		}

		private void SkipWhitespace()
		{
			while (_offset < _text.Length)
			{
				char c = _text[_offset];
				if (c == ' ' || c == '\t' || c == '\n' || c == '\r')
				{
					_offset++;
					continue;
				}
				break;
			}
		}
	}

	public class Writer
	{
		private enum State
		{
			None,
			Object,
			Array,
			Property,
			PropertyName,
			String
		}

		private struct StateElement
		{
			public State type;

			public int childCount;
		}

		private Stack<StateElement> _stateStack = new Stack<StateElement>();

		private TextWriter _writer;

		private State state
		{
			get
			{
				if (_stateStack.Count > 0)
				{
					return _stateStack.Peek().type;
				}
				return State.None;
			}
		}

		private int childCount
		{
			get
			{
				if (_stateStack.Count > 0)
				{
					return _stateStack.Peek().childCount;
				}
				return 0;
			}
		}

		public Writer()
		{
			_writer = new StringWriter();
		}

		public Writer(Stream stream)
		{
			_writer = new StreamWriter(stream, Encoding.UTF8);
		}

		public void Clear()
		{
			((_writer as StringWriter) ?? throw new NotSupportedException("Writer.Clear() is only supported for the StringWriter variant, not for streams")).GetStringBuilder().Clear();
		}

		public void WriteObject(Action<Writer> inner)
		{
			WriteObjectStart();
			inner(this);
			WriteObjectEnd();
		}

		public void WriteObjectStart()
		{
			StartNewObject(container: true);
			_stateStack.Push(new StateElement
			{
				type = State.Object
			});
			_writer.Write("{");
		}

		public void WriteObjectEnd()
		{
			_writer.Write("}");
			_stateStack.Pop();
			if (state == State.None)
			{
				_writer.Flush();
			}
		}

		public void WriteProperty(string name, Action<Writer> inner)
		{
			WriteProperty<string>(name, inner);
		}

		public void WriteProperty(int id, Action<Writer> inner)
		{
			WriteProperty<int>(id, inner);
		}

		public void WriteProperty(string name, string content)
		{
			WritePropertyStart(name);
			Write(content);
			WritePropertyEnd();
		}

		public void WriteProperty(string name, int content)
		{
			WritePropertyStart(name);
			Write(content);
			WritePropertyEnd();
		}

		public void WriteProperty(string name, bool content)
		{
			WritePropertyStart(name);
			Write(content);
			WritePropertyEnd();
		}

		public void WritePropertyStart(string name)
		{
			WritePropertyStart<string>(name);
		}

		public void WritePropertyStart(int id)
		{
			WritePropertyStart<int>(id);
		}

		public void WritePropertyEnd()
		{
			_stateStack.Pop();
		}

		public void WritePropertyNameStart()
		{
			if (childCount > 0)
			{
				_writer.Write(",");
			}
			_writer.Write("\"");
			IncrementChildCount();
			_stateStack.Push(new StateElement
			{
				type = State.Property
			});
			_stateStack.Push(new StateElement
			{
				type = State.PropertyName
			});
		}

		public void WritePropertyNameEnd()
		{
			_writer.Write("\":");
			_stateStack.Pop();
		}

		public void WritePropertyNameInner(string str)
		{
			_writer.Write(str);
		}

		private void WritePropertyStart<T>(T name)
		{
			if (childCount > 0)
			{
				_writer.Write(",");
			}
			_writer.Write("\"");
			_writer.Write(name);
			_writer.Write("\":");
			IncrementChildCount();
			_stateStack.Push(new StateElement
			{
				type = State.Property
			});
		}

		private void WriteProperty<T>(T name, Action<Writer> inner)
		{
			WritePropertyStart(name);
			inner(this);
			WritePropertyEnd();
		}

		public void WriteArrayStart()
		{
			StartNewObject(container: true);
			_stateStack.Push(new StateElement
			{
				type = State.Array
			});
			_writer.Write("[");
		}

		public void WriteArrayEnd()
		{
			_writer.Write("]");
			_stateStack.Pop();
		}

		public void Write(int i)
		{
			StartNewObject(container: false);
			_writer.Write(i);
		}

		public void Write(float f)
		{
			StartNewObject(container: false);
			string text = f.ToString(CultureInfo.InvariantCulture);
			switch (text)
			{
			case "Infinity":
				_writer.Write("3.4E+38");
				return;
			case "-Infinity":
				_writer.Write("-3.4E+38");
				return;
			case "NaN":
				_writer.Write("0.0");
				return;
			}
			_writer.Write(text);
			if (!text.Contains(".") && !text.Contains("E"))
			{
				_writer.Write(".0");
			}
		}

		public void Write(string str, bool escape = true)
		{
			StartNewObject(container: false);
			_writer.Write("\"");
			if (escape)
			{
				WriteEscapedString(str);
			}
			else
			{
				_writer.Write(str);
			}
			_writer.Write("\"");
		}

		public void Write(bool b)
		{
			StartNewObject(container: false);
			_writer.Write(b ? "true" : "false");
		}

		public void WriteNull()
		{
			StartNewObject(container: false);
			_writer.Write("null");
		}

		public void WriteStringStart()
		{
			StartNewObject(container: false);
			_stateStack.Push(new StateElement
			{
				type = State.String
			});
			_writer.Write("\"");
		}

		public void WriteStringEnd()
		{
			_writer.Write("\"");
			_stateStack.Pop();
		}

		public void WriteStringInner(string str, bool escape = true)
		{
			if (escape)
			{
				WriteEscapedString(str);
			}
			else
			{
				_writer.Write(str);
			}
		}

		private void WriteEscapedString(string str)
		{
			foreach (char c in str)
			{
				if (c < ' ')
				{
					switch (c)
					{
					case '\n':
						_writer.Write("\\n");
						break;
					case '\t':
						_writer.Write("\\t");
						break;
					}
				}
				else if (c == '"' || c == '\\')
				{
					_writer.Write("\\");
					_writer.Write(c);
				}
				else
				{
					_writer.Write(c);
				}
			}
		}

		private void StartNewObject(bool container)
		{
			if (state == State.Array && childCount > 0)
			{
				_writer.Write(",");
			}
			_ = state;
			_ = 3;
			if (state == State.Array || state == State.Property)
			{
				IncrementChildCount();
			}
		}

		private void IncrementChildCount()
		{
			StateElement item = _stateStack.Pop();
			item.childCount++;
			_stateStack.Push(item);
		}

		[Conditional("DEBUG")]
		private void Assert(bool condition)
		{
			if (!condition)
			{
				throw new Exception("Assert failed while writing JSON");
			}
		}

		public override string ToString()
		{
			return _writer.ToString();
		}
	}

	public static Dictionary<string, object> TextToDictionary(string text)
	{
		return new Reader(text).ToDictionary();
	}

	public static List<object> TextToArray(string text)
	{
		return new Reader(text).ToArray();
	}
}
