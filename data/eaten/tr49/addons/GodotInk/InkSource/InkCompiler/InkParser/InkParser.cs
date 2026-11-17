using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Ink.Parsed;
using Ink.Runtime;

namespace Ink;

public class InkParser : StringParser
{
	protected enum CustomFlags
	{
		ParsingString = 1,
		TagActive
	}

	protected class InfixOperator
	{
		public string type;

		public int precedence;

		public bool requireWhitespace;

		public InfixOperator(string type, int precedence, bool requireWhitespace)
		{
			this.type = type;
			this.precedence = precedence;
			this.requireWhitespace = requireWhitespace;
		}

		public override string ToString()
		{
			return type;
		}
	}

	protected class NameWithMetadata
	{
		public string name;

		public DebugMetadata metadata;
	}

	protected class FlowDecl
	{
		public Identifier name;

		public List<FlowBase.Argument> arguments;

		public bool isFunction;
	}

	protected enum StatementLevel
	{
		InnerBlock,
		Stitch,
		Knot,
		Top
	}

	private IFileHandler _fileHandler;

	private Ink.ErrorHandler _externalErrorHandler;

	private string _filename;

	public static readonly CharacterRange LatinBasic = CharacterRange.Define('A', 'z', new CharacterSet().AddRange('[', '`'));

	public static readonly CharacterRange LatinExtendedA = CharacterRange.Define('Ā', 'ſ');

	public static readonly CharacterRange LatinExtendedB = CharacterRange.Define('ƀ', 'ɏ');

	public static readonly CharacterRange Greek = CharacterRange.Define('Ͱ', 'Ͽ', new CharacterSet().AddRange('\u0378', '\u0385').AddCharacters("ʹ\u0375\u0378·\u038b\u038d\u03a2"));

	public static readonly CharacterRange Cyrillic = CharacterRange.Define('Ѐ', 'ӿ', new CharacterSet().AddRange('҂', '\u0489'));

	public static readonly CharacterRange Armenian = CharacterRange.Define('\u0530', '֏', new CharacterSet().AddCharacters("\u0530").AddRange('\u0557', 'ՠ').AddRange('ֈ', '֎'));

	public static readonly CharacterRange Hebrew = CharacterRange.Define('\u0590', '\u05ff', new CharacterSet());

	public static readonly CharacterRange Arabic = CharacterRange.Define('\u0600', 'ۿ', new CharacterSet());

	public static readonly CharacterRange Korean = CharacterRange.Define('가', '\ud7af', new CharacterSet());

	public static readonly CharacterRange Latin1Supplement = CharacterRange.Define('\u0080', 'ÿ', new CharacterSet());

	public static readonly CharacterRange Chinese = CharacterRange.Define('一', '鿿', new CharacterSet());

	private bool _parsingChoice;

	private CharacterSet _runtimePathCharacterSet;

	private CharacterSet _nonTextPauseCharacters;

	private CharacterSet _nonTextEndCharacters;

	private CharacterSet _notTextEndCharactersChoice;

	private CharacterSet _notTextEndCharactersString;

	private List<InfixOperator> _binaryOperators;

	private int _maxBinaryOpLength;

	private InkParser _rootParser;

	private HashSet<string> _openFilenames;

	private CharacterSet _identifierCharSet;

	private CharacterSet _sequenceTypeSymbols = new CharacterSet("!&~$");

	private ParseRule[][] _statementRulesAtLevel;

	private ParseRule[][] _statementBreakRulesAtLevel;

	private CharacterSet _inlineWhitespaceChars = new CharacterSet(" \t");

	protected bool parsingStringExpression
	{
		get
		{
			return GetFlag(1u);
		}
		set
		{
			SetFlag(1u, value);
		}
	}

	protected bool tagActive
	{
		get
		{
			return GetFlag(2u);
		}
		set
		{
			SetFlag(2u, value);
		}
	}

	private CharacterSet identifierCharSet
	{
		get
		{
			if (_identifierCharSet == null)
			{
				(_identifierCharSet = new CharacterSet()).AddRange('A', 'Z').AddRange('a', 'z').AddRange('0', '9')
					.Add('_');
				ExtendIdentifierCharacterRanges(_identifierCharSet);
			}
			return _identifierCharSet;
		}
	}

	public InkParser(string str, string filenameForMetadata = null, Ink.ErrorHandler externalErrorHandler = null, IFileHandler fileHandler = null)
		: this(str, filenameForMetadata, externalErrorHandler, null, fileHandler)
	{
	}

	private InkParser(string str, string inkFilename = null, Ink.ErrorHandler externalErrorHandler = null, InkParser rootParser = null, IFileHandler fileHandler = null)
		: base(str)
	{
		_filename = inkFilename;
		RegisterExpressionOperators();
		GenerateStatementLevelRules();
		base.errorHandler = OnStringParserError;
		_externalErrorHandler = externalErrorHandler;
		_fileHandler = fileHandler ?? new DefaultFileHandler();
		if (rootParser == null)
		{
			_rootParser = this;
			_openFilenames = new HashSet<string>();
			if (inkFilename != null)
			{
				string item = _fileHandler.ResolveInkFilename(inkFilename);
				_openFilenames.Add(item);
			}
		}
		else
		{
			_rootParser = rootParser;
		}
	}

	public Ink.Parsed.Story Parse()
	{
		return new Ink.Parsed.Story(StatementsAtLevel(StatementLevel.Top), _rootParser != this);
	}

	protected List<T> SeparatedList<T>(SpecificParseRule<T> mainRule, ParseRule separatorRule) where T : class
	{
		T val = Parse(mainRule);
		if (val == null)
		{
			return null;
		}
		List<T> list = new List<T>();
		list.Add(val);
		while (true)
		{
			int expectedRuleId = BeginRule();
			if (separatorRule() == null)
			{
				FailRule(expectedRuleId);
				break;
			}
			T val2 = Parse(mainRule);
			if (val2 == null)
			{
				FailRule(expectedRuleId);
				break;
			}
			SucceedRule(expectedRuleId);
			list.Add(val2);
		}
		return list;
	}

	protected override string PreProcessInputString(string str)
	{
		return new CommentEliminator(str).Process();
	}

	protected DebugMetadata CreateDebugMetadata(StringParserState.Element stateAtStart, StringParserState.Element stateAtEnd)
	{
		return new DebugMetadata
		{
			startLineNumber = stateAtStart.lineIndex + 1,
			endLineNumber = stateAtEnd.lineIndex + 1,
			startCharacterNumber = stateAtStart.characterInLineIndex + 1,
			endCharacterNumber = stateAtEnd.characterInLineIndex + 1,
			fileName = _filename
		};
	}

	protected override void RuleDidSucceed(object result, StringParserState.Element stateAtStart, StringParserState.Element stateAtEnd)
	{
		Ink.Parsed.Object obj = result as Ink.Parsed.Object;
		if ((bool)obj)
		{
			obj.debugMetadata = CreateDebugMetadata(stateAtStart, stateAtEnd);
			return;
		}
		if (result is List<Ink.Parsed.Object> list)
		{
			foreach (Ink.Parsed.Object item in list)
			{
				if (!item.hasOwnDebugMetadata)
				{
					item.debugMetadata = CreateDebugMetadata(stateAtStart, stateAtEnd);
				}
			}
		}
		if (result is Identifier identifier)
		{
			identifier.debugMetadata = CreateDebugMetadata(stateAtStart, stateAtEnd);
		}
	}

	private void OnStringParserError(string message, int index, int lineIndex, bool isWarning)
	{
		string text = (isWarning ? "WARNING:" : "ERROR:");
		string message2 = ((_filename == null) ? string.Format(text + " line {0}: {1}", lineIndex + 1, message) : string.Format(text + " '{0}' line {1}: {2}", _filename, lineIndex + 1, message));
		if (_externalErrorHandler != null)
		{
			_externalErrorHandler(message2, isWarning ? ErrorType.Warning : ErrorType.Error);
			return;
		}
		throw new Exception(message2);
	}

	protected AuthorWarning AuthorWarning()
	{
		Whitespace();
		Identifier identifier = Parse(IdentifierWithMetadata);
		if (identifier == null || identifier.name != "TODO")
		{
			return null;
		}
		Whitespace();
		ParseString(":");
		Whitespace();
		return new AuthorWarning(ParseUntilCharactersFromString("\n\r"));
	}

	private void ExtendIdentifierCharacterRanges(CharacterSet identifierCharSet)
	{
		CharacterRange[] array = ListAllCharacterRanges();
		foreach (CharacterRange characterRange in array)
		{
			identifierCharSet.AddCharacters(characterRange.ToCharacterSet());
		}
	}

	public static CharacterRange[] ListAllCharacterRanges()
	{
		return new CharacterRange[11]
		{
			LatinBasic, LatinExtendedA, LatinExtendedB, Arabic, Armenian, Cyrillic, Greek, Hebrew, Korean, Latin1Supplement,
			Chinese
		};
	}

	protected Ink.Parsed.Choice Choice()
	{
		bool onceOnly = true;
		List<string> list = Interleave<string>(OptionalExclude(Whitespace), String("*"));
		if (list == null)
		{
			list = Interleave<string>(OptionalExclude(Whitespace), String("+"));
			if (list == null)
			{
				return null;
			}
			onceOnly = false;
		}
		Identifier identifier = Parse(BracketedName);
		Whitespace();
		if (identifier != null)
		{
			Newline();
		}
		Expression condition = Parse(ChoiceCondition);
		Whitespace();
		_parsingChoice = true;
		ContentList contentList = null;
		List<Ink.Parsed.Object> list2 = Parse(MixedTextAndLogic);
		if (list2 != null)
		{
			contentList = new ContentList(list2);
		}
		ContentList contentList2 = null;
		ContentList contentList3 = null;
		bool flag = ParseString("[") != null;
		if (flag)
		{
			EndTagIfNecessary(contentList);
			List<Ink.Parsed.Object> list3 = Parse(MixedTextAndLogic);
			if (list3 != null)
			{
				contentList2 = new ContentList(list3);
			}
			Expect(String("]"), "closing ']' for weave-style option");
			EndTagIfNecessary(contentList2);
			List<Ink.Parsed.Object> list4 = Parse(MixedTextAndLogic);
			if (list4 != null)
			{
				contentList3 = new ContentList(list4);
			}
		}
		Whitespace();
		EndTagIfNecessary(contentList3 ?? contentList);
		List<Ink.Parsed.Object> list5 = Parse(MultiDivert);
		_parsingChoice = false;
		Whitespace();
		bool flag2 = !contentList && !contentList3 && !contentList2;
		if (flag2 && list5 == null)
		{
			Warning("Choice is completely empty. Interpretting as a default fallback choice. Add a divert arrow to remove this warning: * ->");
		}
		else if ((!contentList & flag) && !contentList2)
		{
			Warning("Blank choice - if you intended a default fallback choice, use the `* ->` syntax");
		}
		if (!contentList3)
		{
			contentList3 = new ContentList();
		}
		EndTagIfNecessary(contentList3);
		if (list5 != null)
		{
			foreach (Ink.Parsed.Object item in list5)
			{
				Ink.Parsed.Divert divert = item as Ink.Parsed.Divert;
				if (!divert || !divert.isEmpty)
				{
					contentList3.AddContent(item);
				}
			}
		}
		contentList3.AddContent(new Text("\n"));
		return new Ink.Parsed.Choice(contentList, contentList2, contentList3)
		{
			identifier = identifier,
			indentationDepth = list.Count,
			hasWeaveStyleInlineBrackets = flag,
			condition = condition,
			onceOnly = onceOnly,
			isInvisibleDefault = flag2
		};
	}

	protected Expression ChoiceCondition()
	{
		List<Expression> list = Interleave<Expression>(ChoiceSingleCondition, ChoiceConditionsSpace);
		if (list == null)
		{
			return null;
		}
		if (list.Count == 1)
		{
			return list[0];
		}
		return new MultipleConditionExpression(list);
	}

	protected object ChoiceConditionsSpace()
	{
		Newline();
		Whitespace();
		return StringParser.ParseSuccess;
	}

	protected Expression ChoiceSingleCondition()
	{
		if (ParseString("{") == null)
		{
			return null;
		}
		Expression expression = Expect(Expression, "choice condition inside { }") as Expression;
		DisallowIncrement(expression);
		Expect(String("}"), "closing '}' for choice condition");
		return expression;
	}

	protected Gather Gather()
	{
		object obj = Parse(GatherDashes);
		if (obj == null)
		{
			return null;
		}
		int indentationDepth = (int)obj;
		Gather result = new Gather(Parse(BracketedName), indentationDepth);
		Newline();
		return result;
	}

	protected object GatherDashes()
	{
		Whitespace();
		int num = 0;
		while (ParseDashNotArrow() != null)
		{
			num++;
			Whitespace();
		}
		if (num == 0)
		{
			return null;
		}
		return num;
	}

	protected object ParseDashNotArrow()
	{
		int expectedRuleId = BeginRule();
		if (ParseString("->") == null && ParseSingleCharacter() == '-')
		{
			return SucceedRule(expectedRuleId);
		}
		return FailRule(expectedRuleId);
	}

	protected Identifier BracketedName()
	{
		if (ParseString("(") == null)
		{
			return null;
		}
		Whitespace();
		Identifier identifier = Parse(IdentifierWithMetadata);
		if (identifier == null)
		{
			return null;
		}
		Whitespace();
		Expect(String(")"), "closing ')' for bracketed name");
		return identifier;
	}

	public CommandLineInput CommandLineUserInput()
	{
		CommandLineInput commandLineInput = new CommandLineInput();
		Whitespace();
		if (ParseString("help") != null)
		{
			commandLineInput.isHelp = true;
			return commandLineInput;
		}
		if (ParseString("exit") != null || ParseString("quit") != null)
		{
			commandLineInput.isExit = true;
			return commandLineInput;
		}
		return (CommandLineInput)OneOf(DebugSource, DebugPathLookup, UserChoiceNumber, UserImmediateModeStatement);
	}

	private CommandLineInput DebugSource()
	{
		Whitespace();
		if (ParseString("DebugSource") == null)
		{
			return null;
		}
		Whitespace();
		string message = "character offset in parentheses, e.g. DebugSource(5)";
		if (Expect(String("("), message) == null)
		{
			return null;
		}
		Whitespace();
		int? debugSource = ParseInt();
		if (!debugSource.HasValue)
		{
			Error(message);
			return null;
		}
		Whitespace();
		Expect(String(")"), "closing parenthesis");
		return new CommandLineInput
		{
			debugSource = debugSource
		};
	}

	private CommandLineInput DebugPathLookup()
	{
		Whitespace();
		if (ParseString("DebugPath") == null)
		{
			return null;
		}
		if (Whitespace() == null)
		{
			return null;
		}
		string debugPathLookup = Expect(RuntimePath, "path") as string;
		return new CommandLineInput
		{
			debugPathLookup = debugPathLookup
		};
	}

	private string RuntimePath()
	{
		if (_runtimePathCharacterSet == null)
		{
			_runtimePathCharacterSet = new CharacterSet(identifierCharSet);
			_runtimePathCharacterSet.Add('-');
			_runtimePathCharacterSet.Add('.');
		}
		return ParseCharactersFromCharSet(_runtimePathCharacterSet);
	}

	private CommandLineInput UserChoiceNumber()
	{
		Whitespace();
		int? choiceInput = ParseInt();
		if (!choiceInput.HasValue)
		{
			return null;
		}
		Whitespace();
		if (Parse(EndOfLine) == null)
		{
			return null;
		}
		return new CommandLineInput
		{
			choiceInput = choiceInput
		};
	}

	private CommandLineInput UserImmediateModeStatement()
	{
		object userImmediateModeStatement = OneOf(SingleDivert, TempDeclarationOrAssignment, Expression);
		return new CommandLineInput
		{
			userImmediateModeStatement = userImmediateModeStatement
		};
	}

	protected Conditional InnerConditionalContent()
	{
		Expression initialQueryExpression = Parse(ConditionExpression);
		Conditional conditional = Parse(() => InnerConditionalContent(initialQueryExpression));
		if (conditional == null)
		{
			return null;
		}
		return conditional;
	}

	protected Conditional InnerConditionalContent(Expression initialQueryExpression)
	{
		bool flag = initialQueryExpression != null;
		bool flag2 = Parse(Newline) == null;
		if (flag2 && !flag)
		{
			return null;
		}
		List<ConditionalSingleBranch> list;
		if (flag2)
		{
			list = InlineConditionalBranches();
		}
		else
		{
			list = MultilineConditionalBranches();
			if (list == null)
			{
				if ((bool)initialQueryExpression)
				{
					List<Ink.Parsed.Object> list2 = StatementsAtLevel(StatementLevel.InnerBlock);
					if (list2 != null)
					{
						ConditionalSingleBranch item = new ConditionalSingleBranch(list2);
						list = new List<ConditionalSingleBranch>();
						list.Add(item);
						ConditionalSingleBranch conditionalSingleBranch = Parse(SingleMultilineCondition);
						if ((bool)conditionalSingleBranch)
						{
							if (!conditionalSingleBranch.isElse)
							{
								ErrorWithParsedObject("Expected an '- else:' clause here rather than an extra condition", conditionalSingleBranch);
								conditionalSingleBranch.isElse = true;
							}
							list.Add(conditionalSingleBranch);
						}
					}
				}
				if (list == null)
				{
					return null;
				}
			}
			else if (list.Count == 1 && list[0].isElse && (bool)initialQueryExpression)
			{
				ConditionalSingleBranch conditionalSingleBranch2 = new ConditionalSingleBranch(null);
				conditionalSingleBranch2.isTrueBranch = true;
				list.Insert(0, conditionalSingleBranch2);
			}
			if ((bool)initialQueryExpression)
			{
				bool flag3 = false;
				for (int i = 0; i < list.Count; i++)
				{
					ConditionalSingleBranch conditionalSingleBranch3 = list[i];
					bool flag4 = i == list.Count - 1;
					if ((bool)conditionalSingleBranch3.ownExpression)
					{
						conditionalSingleBranch3.matchingEquality = true;
						flag3 = true;
					}
					else if (flag3 & flag4)
					{
						conditionalSingleBranch3.matchingEquality = true;
						conditionalSingleBranch3.isElse = true;
					}
					else if (!flag4 && list.Count > 2)
					{
						ErrorWithParsedObject("Only final branch can be an 'else'. Did you miss a ':'?", conditionalSingleBranch3);
					}
					else if (i == 0)
					{
						conditionalSingleBranch3.isTrueBranch = true;
					}
					else
					{
						conditionalSingleBranch3.isElse = true;
					}
				}
			}
			else
			{
				for (int j = 0; j < list.Count; j++)
				{
					ConditionalSingleBranch conditionalSingleBranch4 = list[j];
					bool flag5 = j == list.Count - 1;
					if (!(conditionalSingleBranch4.ownExpression == null))
					{
						continue;
					}
					if (flag5)
					{
						conditionalSingleBranch4.isElse = true;
					}
					else if (conditionalSingleBranch4.isElse)
					{
						ConditionalSingleBranch conditionalSingleBranch5 = list[list.Count - 1];
						if (conditionalSingleBranch5.isElse)
						{
							ErrorWithParsedObject("Multiple 'else' cases. Can have a maximum of one, at the end.", conditionalSingleBranch5);
						}
						else
						{
							ErrorWithParsedObject("'else' case in conditional should always be the final one", conditionalSingleBranch4);
						}
					}
					else
					{
						ErrorWithParsedObject("Branch doesn't have condition. Are you missing a ':'? ", conditionalSingleBranch4);
					}
				}
				if (list.Count == 1 && list[0].ownExpression == null)
				{
					ErrorWithParsedObject("Condition block with no conditions", list[0]);
				}
			}
		}
		if (list == null)
		{
			return null;
		}
		foreach (ConditionalSingleBranch item2 in list)
		{
			item2.isInline = flag2;
		}
		return new Conditional(initialQueryExpression, list);
	}

	protected List<ConditionalSingleBranch> InlineConditionalBranches()
	{
		List<List<Ink.Parsed.Object>> list = Interleave<List<Ink.Parsed.Object>>(MixedTextAndLogic, Exclude(String("|")), null, flatten: false);
		if (list == null || list.Count == 0)
		{
			return null;
		}
		List<ConditionalSingleBranch> list2 = new List<ConditionalSingleBranch>();
		if (list.Count > 2)
		{
			Error("Expected one or two alternatives separated by '|' in inline conditional");
		}
		else
		{
			ConditionalSingleBranch conditionalSingleBranch = new ConditionalSingleBranch(list[0]);
			conditionalSingleBranch.isTrueBranch = true;
			list2.Add(conditionalSingleBranch);
			if (list.Count > 1)
			{
				ConditionalSingleBranch conditionalSingleBranch2 = new ConditionalSingleBranch(list[1]);
				conditionalSingleBranch2.isElse = true;
				list2.Add(conditionalSingleBranch2);
			}
		}
		return list2;
	}

	protected List<ConditionalSingleBranch> MultilineConditionalBranches()
	{
		MultilineWhitespace();
		List<object> list = OneOrMore(SingleMultilineCondition);
		if (list == null)
		{
			return null;
		}
		MultilineWhitespace();
		return list.Cast<ConditionalSingleBranch>().ToList();
	}

	protected ConditionalSingleBranch SingleMultilineCondition()
	{
		Whitespace();
		if (ParseString("->") != null)
		{
			return null;
		}
		if (ParseString("-") == null)
		{
			return null;
		}
		Whitespace();
		Expression expression = null;
		bool flag = Parse(ElseExpression) != null;
		if (!flag)
		{
			expression = Parse(ConditionExpression);
		}
		List<Ink.Parsed.Object> list = StatementsAtLevel(StatementLevel.InnerBlock);
		if (expression == null && list == null)
		{
			Error("expected content for the conditional branch following '-'");
			list = new List<Ink.Parsed.Object>();
			list.Add(new Text(""));
		}
		MultilineWhitespace();
		return new ConditionalSingleBranch(list)
		{
			ownExpression = expression,
			isElse = flag
		};
	}

	protected Expression ConditionExpression()
	{
		Expression expression = Parse(Expression);
		if (expression == null)
		{
			return null;
		}
		DisallowIncrement(expression);
		Whitespace();
		if (ParseString(":") == null)
		{
			return null;
		}
		return expression;
	}

	protected object ElseExpression()
	{
		if (ParseString("else") == null)
		{
			return null;
		}
		Whitespace();
		if (ParseString(":") == null)
		{
			return null;
		}
		return StringParser.ParseSuccess;
	}

	private void TrimEndWhitespace(List<Ink.Parsed.Object> mixedTextAndLogicResults, bool terminateWithSpace)
	{
		if (mixedTextAndLogicResults.Count <= 0)
		{
			return;
		}
		int num = mixedTextAndLogicResults.Count - 1;
		Ink.Parsed.Object obj = mixedTextAndLogicResults[num];
		if (obj is Text)
		{
			Text text = (Text)obj;
			text.text = text.text.TrimEnd(' ', '\t');
			if (terminateWithSpace)
			{
				text.text += " ";
			}
			else if (text.text.Length == 0)
			{
				mixedTextAndLogicResults.RemoveAt(num);
				TrimEndWhitespace(mixedTextAndLogicResults, terminateWithSpace: false);
			}
		}
	}

	protected List<Ink.Parsed.Object> LineOfMixedTextAndLogic()
	{
		Parse(Whitespace);
		List<Ink.Parsed.Object> list = Parse(MixedTextAndLogic);
		if (list == null || list.Count == 0)
		{
			return null;
		}
		Text text = list[0] as Text;
		if ((bool)text && text.text.StartsWith("return"))
		{
			Warning("Do you need a '~' before 'return'? If not, perhaps use a glue: <> (since it's lowercase) or rewrite somehow?");
		}
		if (list.Count == 0)
		{
			return null;
		}
		if (!(list[list.Count - 1] is Ink.Parsed.Divert))
		{
			TrimEndWhitespace(list, terminateWithSpace: false);
		}
		EndTagIfNecessary(list);
		if (list.Count <= 0 || !(list[0] is Ink.Parsed.Tag) || !((Ink.Parsed.Tag)list[0]).isStart)
		{
			list.Add(new Text("\n"));
		}
		Expect(EndOfLine, "end of line", SkipToNextLine);
		return list;
	}

	protected List<Ink.Parsed.Object> MixedTextAndLogic()
	{
		if (ParseObject(Spaced(String("~"))) != null)
		{
			Error("You shouldn't use a '~' here - tildas are for logic that's on its own line. To do inline logic, use { curly braces } instead");
		}
		List<Ink.Parsed.Object> list = Interleave<Ink.Parsed.Object>(Optional(ContentText), Optional(InlineLogicOrGlueOrStartTag));
		if (!_parsingChoice)
		{
			List<Ink.Parsed.Object> list2 = Parse(MultiDivert);
			if (list2 != null)
			{
				if (list == null)
				{
					list = new List<Ink.Parsed.Object>();
				}
				EndTagIfNecessary(list);
				TrimEndWhitespace(list, terminateWithSpace: true);
				list.AddRange(list2);
			}
		}
		if (list == null)
		{
			return null;
		}
		return list;
	}

	protected Text ContentText()
	{
		return ContentTextAllowingEcapeChar();
	}

	protected Text ContentTextAllowingEcapeChar()
	{
		StringBuilder stringBuilder = null;
		while (true)
		{
			string text = Parse(ContentTextNoEscape);
			bool flag = ParseString("\\") != null;
			if (!flag && text == null)
			{
				break;
			}
			if (stringBuilder == null)
			{
				stringBuilder = new StringBuilder();
			}
			if (text != null)
			{
				stringBuilder.Append(text);
			}
			if (flag)
			{
				char value = ParseSingleCharacter();
				stringBuilder.Append(value);
			}
		}
		if (stringBuilder != null)
		{
			return new Text(stringBuilder.ToString());
		}
		return null;
	}

	protected string ContentTextNoEscape()
	{
		if (_nonTextPauseCharacters == null)
		{
			_nonTextPauseCharacters = new CharacterSet("-<");
		}
		if (_nonTextEndCharacters == null)
		{
			_nonTextEndCharacters = new CharacterSet("{}|\n\r\\#");
			_notTextEndCharactersChoice = new CharacterSet(_nonTextEndCharacters);
			_notTextEndCharactersChoice.AddCharacters("[]");
			_notTextEndCharactersString = new CharacterSet(_nonTextEndCharacters);
			_notTextEndCharactersString.AddCharacters("\"");
		}
		ParseRule stopRule = () => OneOf(ParseDivertArrow, ParseThreadArrow, EndOfLine, Glue);
		CharacterSet characterSet = null;
		string text = ParseUntil(endCharacters: parsingStringExpression ? _notTextEndCharactersString : ((!_parsingChoice) ? _nonTextEndCharacters : _notTextEndCharactersChoice), stopRule: stopRule, pauseCharacters: _nonTextPauseCharacters);
		if (text != null)
		{
			return text;
		}
		return null;
	}

	protected List<Ink.Parsed.Object> MultiDivert()
	{
		Whitespace();
		List<Ink.Parsed.Object> list = null;
		Ink.Parsed.Divert divert = Parse(StartThread);
		if ((bool)divert)
		{
			list = new List<Ink.Parsed.Object>();
			list.Add(divert);
			return list;
		}
		List<object> list2 = Interleave<object>(ParseDivertArrowOrTunnelOnwards, DivertIdentifierWithArguments);
		if (list2 == null)
		{
			return null;
		}
		list = new List<Ink.Parsed.Object>();
		EndTagIfNecessary(list);
		for (int i = 0; i < list2.Count; i++)
		{
			if (i % 2 == 0)
			{
				if ((string)list2[i] == "->->")
				{
					if (i != 0 && i != list2.Count - 1 && i != list2.Count - 2)
					{
						Error("Tunnel onwards '->->' must only come at the begining or the start of a divert");
					}
					TunnelOnwards tunnelOnwards = new TunnelOnwards();
					if (i < list2.Count - 1)
					{
						Ink.Parsed.Divert divertAfter = list2[i + 1] as Ink.Parsed.Divert;
						tunnelOnwards.divertAfter = divertAfter;
					}
					list.Add(tunnelOnwards);
					break;
				}
			}
			else
			{
				Ink.Parsed.Divert divert2 = list2[i] as Ink.Parsed.Divert;
				if (i < list2.Count - 1)
				{
					divert2.isTunnel = true;
				}
				list.Add(divert2);
			}
		}
		if (list.Count == 0 && list2.Count == 1)
		{
			Ink.Parsed.Divert divert3 = new Ink.Parsed.Divert((Ink.Parsed.Object)null);
			divert3.isEmpty = true;
			list.Add(divert3);
			if (!_parsingChoice)
			{
				Error("Empty diverts (->) are only valid on choices");
			}
		}
		return list;
	}

	protected Ink.Parsed.Divert StartThread()
	{
		Whitespace();
		if (ParseThreadArrow() == null)
		{
			return null;
		}
		Whitespace();
		Ink.Parsed.Divert obj = Expect(DivertIdentifierWithArguments, "target for new thread", () => new Ink.Parsed.Divert((Ink.Parsed.Object)null)) as Ink.Parsed.Divert;
		obj.isThread = true;
		return obj;
	}

	protected Ink.Parsed.Divert DivertIdentifierWithArguments()
	{
		Whitespace();
		List<Identifier> list = Parse(DotSeparatedDivertPathComponents);
		if (list == null)
		{
			return null;
		}
		Whitespace();
		List<Expression> arguments = Parse(ExpressionFunctionCallArguments);
		Whitespace();
		return new Ink.Parsed.Divert(new Ink.Parsed.Path(list), arguments);
	}

	protected Ink.Parsed.Divert SingleDivert()
	{
		List<Ink.Parsed.Object> list = Parse(MultiDivert);
		if (list == null)
		{
			return null;
		}
		if (list.Count != 1)
		{
			return null;
		}
		if (list[0] is TunnelOnwards)
		{
			return null;
		}
		Ink.Parsed.Divert divert = list[0] as Ink.Parsed.Divert;
		if (divert.isTunnel)
		{
			return null;
		}
		return divert;
	}

	private List<Identifier> DotSeparatedDivertPathComponents()
	{
		return Interleave<Identifier>(Spaced(IdentifierWithMetadata), Exclude(String(".")));
	}

	protected string ParseDivertArrowOrTunnelOnwards()
	{
		int num = 0;
		while (ParseString("->") != null)
		{
			num++;
		}
		switch (num)
		{
		case 0:
			return null;
		case 1:
			return "->";
		case 2:
			return "->->";
		default:
			Error("Unexpected number of arrows in divert. Should only have '->' or '->->'");
			return "->->";
		}
	}

	protected string ParseDivertArrow()
	{
		return ParseString("->");
	}

	protected string ParseThreadArrow()
	{
		return ParseString("<-");
	}

	protected Ink.Parsed.Object TempDeclarationOrAssignment()
	{
		Whitespace();
		bool flag = ParseTempKeyword();
		Whitespace();
		Identifier identifier = null;
		identifier = ((!flag) ? Parse(IdentifierWithMetadata) : ((Identifier)Expect(IdentifierWithMetadata, "variable name")));
		if (identifier == null)
		{
			return null;
		}
		Whitespace();
		bool flag2 = ParseString("+") != null;
		bool flag3 = ParseString("-") != null;
		if (flag2 & flag3)
		{
			Error("Unexpected sequence '+-'");
		}
		if (ParseString("=") == null)
		{
			if (flag)
			{
				Error("Expected '='");
			}
			return null;
		}
		Expression expression = (Expression)Expect(Expression, "value expression to be assigned");
		if (flag2 | flag3)
		{
			return new IncDecExpression(identifier, expression, flag2);
		}
		return new Ink.Parsed.VariableAssignment(identifier, expression)
		{
			isNewTemporaryDeclaration = flag
		};
	}

	protected void DisallowIncrement(Ink.Parsed.Object expr)
	{
		if (expr is IncDecExpression)
		{
			Error("Can't use increment/decrement here. It can only be used on a ~ line");
		}
	}

	protected bool ParseTempKeyword()
	{
		int expectedRuleId = BeginRule();
		if (Parse(Identifier) == "temp")
		{
			SucceedRule(expectedRuleId);
			return true;
		}
		FailRule(expectedRuleId);
		return false;
	}

	protected Return ReturnStatement()
	{
		Whitespace();
		if (Parse(Identifier) != "return")
		{
			return null;
		}
		Whitespace();
		return new Return(Parse(Expression));
	}

	protected Expression Expression()
	{
		return Expression(0);
	}

	protected Expression Expression(int minimumPrecedence)
	{
		Whitespace();
		Expression expr = ExpressionUnary();
		if (expr == null)
		{
			return null;
		}
		Whitespace();
		int expectedRuleId;
		while (true)
		{
			expectedRuleId = BeginRule();
			InfixOperator infixOp = ParseInfixOperator();
			if (infixOp == null || infixOp.precedence <= minimumPrecedence)
			{
				break;
			}
			string message = $"right side of '{infixOp.type}' expression";
			object obj = Expect(() => ExpressionInfixRight(expr, infixOp), message);
			if (obj == null)
			{
				FailRule(expectedRuleId);
				return null;
			}
			expr = SucceedRule(expectedRuleId, obj) as Expression;
		}
		FailRule(expectedRuleId);
		Whitespace();
		return expr;
	}

	protected Expression ExpressionUnary()
	{
		Expression expression = Parse(ExpressionDivertTarget);
		if (expression != null)
		{
			return expression;
		}
		string text = (string)OneOf(String("-"), String("!"));
		if (text == null)
		{
			text = Parse(ExpressionNot);
		}
		Whitespace();
		Expression expression2 = OneOf(ExpressionList, ExpressionParen, ExpressionFunctionCall, ExpressionVariableName, ExpressionLiteral) as Expression;
		if (expression2 == null && text != null)
		{
			expression2 = ExpressionUnary();
		}
		if (expression2 == null)
		{
			return null;
		}
		if (text != null)
		{
			expression2 = UnaryExpression.WithInner(expression2, text);
		}
		Whitespace();
		string text2 = (string)OneOf(String("++"), String("--"));
		if (text2 != null)
		{
			bool isInc = text2 == "++";
			if (!(expression2 is Ink.Parsed.VariableReference))
			{
				Error("can only increment and decrement variables, but saw '" + expression2?.ToString() + "'");
			}
			else
			{
				expression2 = new IncDecExpression(((Ink.Parsed.VariableReference)expression2).identifier, isInc);
			}
		}
		return expression2;
	}

	protected string ExpressionNot()
	{
		string text = Identifier();
		if (text == "not")
		{
			return text;
		}
		return null;
	}

	protected Expression ExpressionLiteral()
	{
		return (Expression)OneOf(ExpressionFloat, ExpressionInt, ExpressionBool, ExpressionString);
	}

	protected Expression ExpressionDivertTarget()
	{
		Whitespace();
		Ink.Parsed.Divert divert = Parse(SingleDivert);
		if (divert == null)
		{
			return null;
		}
		if (divert.isThread)
		{
			return null;
		}
		Whitespace();
		return new DivertTarget(divert);
	}

	protected Number ExpressionInt()
	{
		int? num = ParseInt();
		if (!num.HasValue)
		{
			return null;
		}
		return new Number(num.Value);
	}

	protected Number ExpressionFloat()
	{
		float? num = ParseFloat();
		if (!num.HasValue)
		{
			return null;
		}
		return new Number(num.Value);
	}

	protected StringExpression ExpressionString()
	{
		if (ParseString("\"") == null)
		{
			return null;
		}
		parsingStringExpression = true;
		List<Ink.Parsed.Object> list = Parse(MixedTextAndLogic);
		Expect(String("\""), "close quote for string expression");
		parsingStringExpression = false;
		if (list == null)
		{
			list = new List<Ink.Parsed.Object>();
			list.Add(new Text(""));
		}
		else if (list.Exists((Ink.Parsed.Object c) => c is Ink.Parsed.Divert))
		{
			Error("String expressions cannot contain diverts (->)");
		}
		return new StringExpression(list);
	}

	protected Number ExpressionBool()
	{
		string text = Parse(Identifier);
		if (text == "true")
		{
			return new Number(true);
		}
		if (text == "false")
		{
			return new Number(false);
		}
		return null;
	}

	protected Expression ExpressionFunctionCall()
	{
		Identifier identifier = Parse(IdentifierWithMetadata);
		if (identifier == null)
		{
			return null;
		}
		Whitespace();
		List<Expression> list = Parse(ExpressionFunctionCallArguments);
		if (list == null)
		{
			return null;
		}
		return new FunctionCall(identifier, list);
	}

	protected List<Expression> ExpressionFunctionCallArguments()
	{
		if (ParseString("(") == null)
		{
			return null;
		}
		ParseRule ruleB = Exclude(String(","));
		List<Expression> list = Interleave<Expression>(Expression, ruleB);
		if (list == null)
		{
			list = new List<Expression>();
		}
		Whitespace();
		Expect(String(")"), "closing ')' for function call");
		return list;
	}

	protected Expression ExpressionVariableName()
	{
		List<Identifier> list = Interleave<Identifier>(IdentifierWithMetadata, Exclude(Spaced(String("."))));
		if (list == null || Ink.Parsed.Story.IsReservedKeyword(list[0].name))
		{
			return null;
		}
		return new Ink.Parsed.VariableReference(list);
	}

	protected Expression ExpressionParen()
	{
		if (ParseString("(") == null)
		{
			return null;
		}
		Expression expression = Parse(Expression);
		if (expression == null)
		{
			return null;
		}
		Whitespace();
		Expect(String(")"), "closing parenthesis ')' for expression");
		return expression;
	}

	protected Expression ExpressionInfixRight(Expression left, InfixOperator op)
	{
		Whitespace();
		Expression expression = Parse(() => Expression(op.precedence));
		if ((bool)expression)
		{
			return new BinaryExpression(left, expression, op.type);
		}
		return null;
	}

	private InfixOperator ParseInfixOperator()
	{
		foreach (InfixOperator binaryOperator in _binaryOperators)
		{
			int expectedRuleId = BeginRule();
			if (ParseString(binaryOperator.type) != null)
			{
				if (!binaryOperator.requireWhitespace || Whitespace() != null)
				{
					return (InfixOperator)SucceedRule(expectedRuleId, binaryOperator);
				}
				FailRule(expectedRuleId);
			}
			else
			{
				FailRule(expectedRuleId);
			}
		}
		return null;
	}

	protected List ExpressionList()
	{
		Whitespace();
		if (ParseString("(") == null)
		{
			return null;
		}
		Whitespace();
		List<Identifier> itemIdentifierList = SeparatedList(ListMember, Spaced(String(",")));
		Whitespace();
		if (ParseString(")") == null)
		{
			return null;
		}
		return new List(itemIdentifierList);
	}

	protected Identifier ListMember()
	{
		Whitespace();
		Identifier identifier = Parse(IdentifierWithMetadata);
		if (identifier == null)
		{
			return null;
		}
		if (ParseString(".") != null)
		{
			Identifier identifier2 = Expect(IdentifierWithMetadata, "element name within the set " + identifier) as Identifier;
			identifier.name = identifier.name + "." + identifier2?.name;
		}
		Whitespace();
		return identifier;
	}

	private void RegisterExpressionOperators()
	{
		_maxBinaryOpLength = 0;
		_binaryOperators = new List<InfixOperator>();
		RegisterBinaryOperator("&&", 1);
		RegisterBinaryOperator("||", 1);
		RegisterBinaryOperator("and", 1, requireWhitespace: true);
		RegisterBinaryOperator("or", 1, requireWhitespace: true);
		RegisterBinaryOperator("==", 2);
		RegisterBinaryOperator(">=", 2);
		RegisterBinaryOperator("<=", 2);
		RegisterBinaryOperator("<", 2);
		RegisterBinaryOperator(">", 2);
		RegisterBinaryOperator("!=", 2);
		RegisterBinaryOperator("?", 3);
		RegisterBinaryOperator("has", 3, requireWhitespace: true);
		RegisterBinaryOperator("!?", 3);
		RegisterBinaryOperator("hasnt", 3, requireWhitespace: true);
		RegisterBinaryOperator("^", 3);
		RegisterBinaryOperator("+", 4);
		RegisterBinaryOperator("-", 5);
		RegisterBinaryOperator("*", 6);
		RegisterBinaryOperator("/", 7);
		RegisterBinaryOperator("%", 8);
		RegisterBinaryOperator("mod", 8, requireWhitespace: true);
	}

	private void RegisterBinaryOperator(string op, int precedence, bool requireWhitespace = false)
	{
		_binaryOperators.Add(new InfixOperator(op, precedence, requireWhitespace));
		_maxBinaryOpLength = Math.Max(_maxBinaryOpLength, op.Length);
	}

	protected object IncludeStatement()
	{
		Whitespace();
		if (ParseString("INCLUDE") == null)
		{
			return null;
		}
		Whitespace();
		string text = (string)Expect(() => ParseUntilCharactersFromString("\n\r"), "filename for include statement");
		text = text.TrimEnd(' ', '\t');
		string text2 = _rootParser._fileHandler.ResolveInkFilename(text);
		if (FilenameIsAlreadyOpen(text2))
		{
			Error("Recursive INCLUDE detected: '" + text2 + "' is already open.");
			ParseUntilCharactersFromString("\r\n");
			return new IncludedFile(null);
		}
		AddOpenFilename(text2);
		Ink.Parsed.Story includedStory = null;
		string text3 = null;
		try
		{
			text3 = _rootParser._fileHandler.LoadInkFileContents(text2);
		}
		catch
		{
			Error("Failed to load: '" + text + "'");
		}
		if (text3 != null)
		{
			includedStory = new InkParser(text3, text, _externalErrorHandler, _rootParser).Parse();
		}
		RemoveOpenFilename(text2);
		return new IncludedFile(includedStory);
	}

	private bool FilenameIsAlreadyOpen(string fullFilename)
	{
		return _rootParser._openFilenames.Contains(fullFilename);
	}

	private void AddOpenFilename(string fullFilename)
	{
		_rootParser._openFilenames.Add(fullFilename);
	}

	private void RemoveOpenFilename(string fullFilename)
	{
		_rootParser._openFilenames.Remove(fullFilename);
	}

	protected Knot KnotDefinition()
	{
		FlowDecl flowDecl = Parse(KnotDeclaration);
		if (flowDecl == null)
		{
			return null;
		}
		Expect(EndOfLine, "end of line after knot name definition", SkipToNextLine);
		ParseRule rule = () => StatementsAtLevel(StatementLevel.Knot);
		List<Ink.Parsed.Object> topLevelObjects = Expect(rule, "at least one line within the knot", KnotStitchNoContentRecoveryRule) as List<Ink.Parsed.Object>;
		return new Knot(flowDecl.name, topLevelObjects, flowDecl.arguments, flowDecl.isFunction);
	}

	protected FlowDecl KnotDeclaration()
	{
		Whitespace();
		if (KnotTitleEquals() == null)
		{
			return null;
		}
		Whitespace();
		Identifier identifier = Parse(IdentifierWithMetadata);
		bool flag = identifier?.name == "function";
		Identifier identifier2;
		if (flag)
		{
			Expect(Whitespace, "whitespace after the 'function' keyword");
			identifier2 = Parse(IdentifierWithMetadata);
		}
		else
		{
			identifier2 = identifier;
		}
		if (identifier2 == null)
		{
			Error("Expected the name of the " + (flag ? "function" : "knot"));
			identifier2 = new Identifier
			{
				name = ""
			};
		}
		Whitespace();
		List<FlowBase.Argument> arguments = Parse(BracketedKnotDeclArguments);
		Whitespace();
		Parse(KnotTitleEquals);
		return new FlowDecl
		{
			name = identifier2,
			arguments = arguments,
			isFunction = flag
		};
	}

	protected string KnotTitleEquals()
	{
		string text = ParseCharactersFromString("=");
		if (text == null || text.Length <= 1)
		{
			return null;
		}
		return text;
	}

	protected object StitchDefinition()
	{
		FlowDecl flowDecl = Parse(StitchDeclaration);
		if (flowDecl == null)
		{
			return null;
		}
		Expect(EndOfLine, "end of line after stitch name", SkipToNextLine);
		ParseRule rule = () => StatementsAtLevel(StatementLevel.Stitch);
		List<Ink.Parsed.Object> topLevelObjects = Expect(rule, "at least one line within the stitch", KnotStitchNoContentRecoveryRule) as List<Ink.Parsed.Object>;
		return new Stitch(flowDecl.name, topLevelObjects, flowDecl.arguments, flowDecl.isFunction);
	}

	protected FlowDecl StitchDeclaration()
	{
		Whitespace();
		if (ParseString("=") == null)
		{
			return null;
		}
		if (ParseString("=") != null)
		{
			return null;
		}
		Whitespace();
		bool flag = ParseString("function") != null;
		if (flag)
		{
			Whitespace();
		}
		Identifier identifier = Parse(IdentifierWithMetadata);
		if (identifier == null)
		{
			return null;
		}
		Whitespace();
		List<FlowBase.Argument> arguments = Parse(BracketedKnotDeclArguments);
		Whitespace();
		return new FlowDecl
		{
			name = identifier,
			arguments = arguments,
			isFunction = flag
		};
	}

	protected object KnotStitchNoContentRecoveryRule()
	{
		ParseUntil(KnotDeclaration, new CharacterSet("="));
		return new List<Ink.Parsed.Object>
		{
			new Text("<ERROR IN FLOW>")
		};
	}

	protected List<FlowBase.Argument> BracketedKnotDeclArguments()
	{
		if (ParseString("(") == null)
		{
			return null;
		}
		List<FlowBase.Argument> list = Interleave<FlowBase.Argument>(Spaced(FlowDeclArgument), Exclude(String(",")));
		Expect(String(")"), "closing ')' for parameter list");
		if (list == null)
		{
			list = new List<FlowBase.Argument>();
		}
		return list;
	}

	protected FlowBase.Argument FlowDeclArgument()
	{
		Identifier identifier = Parse(IdentifierWithMetadata);
		Whitespace();
		string text = ParseDivertArrow();
		Whitespace();
		Identifier identifier2 = Parse(IdentifierWithMetadata);
		if (identifier == null && identifier2 == null)
		{
			return null;
		}
		FlowBase.Argument argument = new FlowBase.Argument();
		if (text != null)
		{
			argument.isDivertTarget = true;
		}
		if (identifier != null && identifier.name == "ref")
		{
			if (identifier2 == null)
			{
				Error("Expected an parameter name after 'ref'");
			}
			argument.identifier = identifier2;
			argument.isByReference = true;
		}
		else
		{
			if (argument.isDivertTarget)
			{
				argument.identifier = identifier2;
			}
			else
			{
				argument.identifier = identifier;
			}
			if (argument.identifier == null)
			{
				Error("Expected an parameter name");
			}
			argument.isByReference = false;
		}
		return argument;
	}

	protected ExternalDeclaration ExternalDeclaration()
	{
		Whitespace();
		Identifier identifier = Parse(IdentifierWithMetadata);
		if (identifier == null || identifier.name != "EXTERNAL")
		{
			return null;
		}
		Whitespace();
		Identifier identifier2 = (Expect(IdentifierWithMetadata, "name of external function") as Identifier) ?? new Identifier();
		Whitespace();
		List<FlowBase.Argument> list = Expect(BracketedKnotDeclArguments, "declaration of arguments for EXTERNAL, even if empty, i.e. 'EXTERNAL " + identifier2?.ToString() + "()'") as List<FlowBase.Argument>;
		if (list == null)
		{
			list = new List<FlowBase.Argument>();
		}
		List<string> argumentNames = list.Select((FlowBase.Argument arg) => arg.identifier?.name).ToList();
		return new ExternalDeclaration(identifier2, argumentNames);
	}

	protected Ink.Parsed.Object LogicLine()
	{
		Whitespace();
		if (ParseString("~") == null)
		{
			return null;
		}
		Whitespace();
		ParseRule rule = () => OneOf(ReturnStatement, TempDeclarationOrAssignment, Expression);
		Ink.Parsed.Object obj = Expect(rule, "expression after '~'", SkipToNextLine) as Ink.Parsed.Object;
		if (obj == null)
		{
			return new ContentList();
		}
		if (obj is Expression && !(obj is FunctionCall) && !(obj is IncDecExpression))
		{
			Ink.Parsed.VariableReference variableReference = obj as Ink.Parsed.VariableReference;
			if ((bool)variableReference && variableReference.name == "include")
			{
				Error("'~ include' is no longer the correct syntax - please use 'INCLUDE your_filename.ink', without the tilda, and in block capitals.");
			}
			else
			{
				Error("Logic following a '~' can't be that type of expression. It can only be something like:\n\t~ return\n\t~ var x = blah\n\t~ x++\n\t~ myFunction()");
			}
		}
		FunctionCall functionCall = obj as FunctionCall;
		if ((bool)functionCall)
		{
			functionCall.shouldPopReturnedValue = true;
		}
		if (obj.Find<FunctionCall>() != null)
		{
			obj = new ContentList(obj, new Text("\n"));
		}
		Expect(EndOfLine, "end of line", SkipToNextLine);
		return obj;
	}

	protected Ink.Parsed.Object VariableDeclaration()
	{
		Whitespace();
		if (Parse(Identifier) != "VAR")
		{
			return null;
		}
		Whitespace();
		Identifier identifier = Expect(IdentifierWithMetadata, "variable name") as Identifier;
		Whitespace();
		Expect(String("="), "the '=' for an assignment of a value, e.g. '= 5' (initial values are mandatory)");
		Whitespace();
		Expression expression = Expect(Expression, "initial value for ") as Expression;
		if ((bool)expression)
		{
			if (!(expression is Number) && !(expression is StringExpression) && !(expression is DivertTarget) && !(expression is Ink.Parsed.VariableReference) && !(expression is List))
			{
				Error("initial value for a variable must be a number, constant, list or divert target");
			}
			if (Parse(ListElementDefinitionSeparator) != null)
			{
				Error("Unexpected ','. If you're trying to declare a new list, use the LIST keyword, not VAR");
			}
			else if (expression is StringExpression && !(expression as StringExpression).isSingleString)
			{
				Error("Constant strings cannot contain any logic.");
			}
			return new Ink.Parsed.VariableAssignment(identifier, expression)
			{
				isGlobalDeclaration = true
			};
		}
		return null;
	}

	protected Ink.Parsed.VariableAssignment ListDeclaration()
	{
		Whitespace();
		if (Parse(Identifier) != "LIST")
		{
			return null;
		}
		Whitespace();
		Identifier identifier = Expect(IdentifierWithMetadata, "list name") as Identifier;
		Whitespace();
		Expect(String("="), "the '=' for an assignment of the list definition");
		Whitespace();
		Ink.Parsed.ListDefinition listDefinition = Expect(ListDefinition, "list item names") as Ink.Parsed.ListDefinition;
		if ((bool)listDefinition)
		{
			listDefinition.identifier = identifier;
			return new Ink.Parsed.VariableAssignment(identifier, listDefinition);
		}
		return null;
	}

	protected Ink.Parsed.ListDefinition ListDefinition()
	{
		AnyWhitespace();
		List<ListElementDefinition> list = SeparatedList(ListElementDefinition, ListElementDefinitionSeparator);
		if (list == null)
		{
			return null;
		}
		return new Ink.Parsed.ListDefinition(list);
	}

	protected string ListElementDefinitionSeparator()
	{
		AnyWhitespace();
		if (ParseString(",") == null)
		{
			return null;
		}
		AnyWhitespace();
		return ",";
	}

	protected ListElementDefinition ListElementDefinition()
	{
		bool flag = ParseString("(") != null;
		bool flag2 = flag;
		Whitespace();
		Identifier identifier = Parse(IdentifierWithMetadata);
		if (identifier == null)
		{
			return null;
		}
		Whitespace();
		if (flag && ParseString(")") != null)
		{
			flag2 = false;
			Whitespace();
		}
		int? explicitValue = null;
		if (ParseString("=") != null)
		{
			Whitespace();
			Number number = Expect(ExpressionInt, "value to be assigned to list item") as Number;
			if (number != null)
			{
				explicitValue = (int)number.value;
			}
			if (flag2)
			{
				Whitespace();
				if (ParseString(")") != null)
				{
					flag2 = false;
				}
			}
		}
		if (flag2)
		{
			Error("Expected closing ')'");
		}
		return new ListElementDefinition(identifier, flag, explicitValue);
	}

	protected Ink.Parsed.Object ConstDeclaration()
	{
		Whitespace();
		if (Parse(Identifier) != "CONST")
		{
			return null;
		}
		Whitespace();
		Identifier name = Expect(IdentifierWithMetadata, "constant name") as Identifier;
		Whitespace();
		Expect(String("="), "the '=' for an assignment of a value, e.g. '= 5' (initial values are mandatory)");
		Whitespace();
		Expression expression = Expect(Expression, "initial value for ") as Expression;
		if (!(expression is Number) && !(expression is DivertTarget) && !(expression is StringExpression))
		{
			Error("initial value for a constant must be a number or divert target");
		}
		else if (expression is StringExpression && !(expression as StringExpression).isSingleString)
		{
			Error("Constant strings cannot contain any logic.");
		}
		return new ConstantDeclaration(name, expression);
	}

	protected Ink.Parsed.Object InlineLogicOrGlueOrStartTag()
	{
		return (Ink.Parsed.Object)OneOf(InlineLogic, Glue, StartTag);
	}

	protected Ink.Parsed.Glue Glue()
	{
		if (ParseString("<>") != null)
		{
			return new Ink.Parsed.Glue(new Ink.Runtime.Glue());
		}
		return null;
	}

	protected Ink.Parsed.Object InlineLogic()
	{
		if (ParseString("{") == null)
		{
			return null;
		}
		bool flag = parsingStringExpression;
		bool flag2 = tagActive;
		Whitespace();
		Ink.Parsed.Object obj = (Ink.Parsed.Object)Expect(InnerLogic, "some kind of logic, conditional or sequence within braces: { ... }");
		if (obj == null)
		{
			parsingStringExpression = flag;
			return null;
		}
		DisallowIncrement(obj);
		ContentList contentList = obj as ContentList;
		if (!contentList)
		{
			contentList = new ContentList(obj);
		}
		Whitespace();
		Expect(String("}"), "closing brace '}' for inline logic");
		parsingStringExpression = flag;
		if (!flag2)
		{
			EndTagIfNecessary(contentList);
		}
		return contentList;
	}

	protected Ink.Parsed.Object InnerLogic()
	{
		Whitespace();
		SequenceType? sequenceType = (SequenceType?)ParseObject(SequenceTypeAnnotation);
		if (sequenceType.HasValue)
		{
			List<ContentList> list = (List<ContentList>)Expect(InnerSequenceObjects, "sequence elements (for cycle/stoping etc)");
			if (list == null)
			{
				return null;
			}
			return new Sequence(list, sequenceType.Value);
		}
		Expression initialQueryExpression = Parse(ConditionExpression);
		if ((bool)initialQueryExpression)
		{
			return (Conditional)Expect(() => InnerConditionalContent(initialQueryExpression), "conditional content following query");
		}
		ParseRule[] obj = new ParseRule[3] { InnerConditionalContent, InnerSequence, InnerExpression };
		_ = tagActive;
		ParseRule[] array = obj;
		foreach (ParseRule rule in array)
		{
			int expectedRuleId = BeginRule();
			Ink.Parsed.Object obj2 = ParseObject(rule) as Ink.Parsed.Object;
			if ((bool)obj2)
			{
				if (Peek(Spaced(String("}"))) != null)
				{
					return (Ink.Parsed.Object)SucceedRule(expectedRuleId, obj2);
				}
				FailRule(expectedRuleId);
			}
			else
			{
				FailRule(expectedRuleId);
			}
		}
		return null;
	}

	protected Ink.Parsed.Object InnerExpression()
	{
		Expression expression = Parse(Expression);
		if ((bool)expression)
		{
			expression.outputWhenComplete = true;
		}
		return expression;
	}

	protected Identifier IdentifierWithMetadata()
	{
		string text = Identifier();
		if (text == null)
		{
			return null;
		}
		return new Identifier
		{
			name = text,
			debugMetadata = null
		};
	}

	protected string Identifier()
	{
		string text = ParseCharactersFromCharSet(identifierCharSet);
		if (text == null)
		{
			return null;
		}
		bool flag = true;
		string text2 = text;
		foreach (char c in text2)
		{
			if (c < '0' || c > '9')
			{
				flag = false;
				break;
			}
		}
		if (flag)
		{
			return null;
		}
		return text;
	}

	protected Sequence InnerSequence()
	{
		Whitespace();
		SequenceType sequenceType = SequenceType.Stopping;
		SequenceType? sequenceType2 = (SequenceType?)Parse(SequenceTypeAnnotation);
		if (sequenceType2.HasValue)
		{
			sequenceType = sequenceType2.Value;
		}
		List<ContentList> list = Parse(InnerSequenceObjects);
		if (list == null || list.Count <= 1)
		{
			return null;
		}
		return new Sequence(list, sequenceType);
	}

	protected object SequenceTypeAnnotation()
	{
		SequenceType? sequenceType = (SequenceType?)Parse(SequenceTypeSymbolAnnotation);
		if (!sequenceType.HasValue)
		{
			sequenceType = (SequenceType?)Parse(SequenceTypeWordAnnotation);
		}
		if (!sequenceType.HasValue)
		{
			return null;
		}
		switch (sequenceType.Value)
		{
		default:
			Error("Sequence type combination not supported: " + sequenceType.Value);
			return SequenceType.Stopping;
		case SequenceType.Stopping:
		case SequenceType.Cycle:
		case SequenceType.Shuffle:
		case SequenceType.Stopping | SequenceType.Shuffle:
		case SequenceType.Once:
		case SequenceType.Shuffle | SequenceType.Once:
			return sequenceType;
		}
	}

	protected object SequenceTypeSymbolAnnotation()
	{
		if (_sequenceTypeSymbols == null)
		{
			_sequenceTypeSymbols = new CharacterSet("!&~$ ");
		}
		SequenceType sequenceType = (SequenceType)0;
		string text = ParseCharactersFromCharSet(_sequenceTypeSymbols);
		if (text == null)
		{
			return null;
		}
		string text2 = text;
		for (int i = 0; i < text2.Length; i++)
		{
			switch (text2[i])
			{
			case '!':
				sequenceType |= SequenceType.Once;
				break;
			case '&':
				sequenceType |= SequenceType.Cycle;
				break;
			case '~':
				sequenceType |= SequenceType.Shuffle;
				break;
			case '$':
				sequenceType |= SequenceType.Stopping;
				break;
			}
		}
		if (sequenceType == (SequenceType)0)
		{
			return null;
		}
		return sequenceType;
	}

	protected object SequenceTypeWordAnnotation()
	{
		List<SequenceType?> list = Interleave<SequenceType?>(SequenceTypeSingleWord, Exclude(Whitespace));
		if (list == null || list.Count == 0)
		{
			return null;
		}
		if (ParseString(":") == null)
		{
			return null;
		}
		SequenceType sequenceType = (SequenceType)0;
		foreach (SequenceType? item in list)
		{
			sequenceType |= item.Value;
		}
		return sequenceType;
	}

	protected object SequenceTypeSingleWord()
	{
		SequenceType? sequenceType = null;
		Identifier identifier = Parse(IdentifierWithMetadata);
		if (identifier != null)
		{
			switch (identifier.name)
			{
			case "once":
				sequenceType = SequenceType.Once;
				break;
			case "cycle":
				sequenceType = SequenceType.Cycle;
				break;
			case "shuffle":
				sequenceType = SequenceType.Shuffle;
				break;
			case "stopping":
				sequenceType = SequenceType.Stopping;
				break;
			}
		}
		if (!sequenceType.HasValue)
		{
			return null;
		}
		return sequenceType;
	}

	protected List<ContentList> InnerSequenceObjects()
	{
		bool num = Parse(Newline) != null;
		List<ContentList> list = null;
		if (num)
		{
			return Parse(InnerMultilineSequenceObjects);
		}
		return Parse(InnerInlineSequenceObjects);
	}

	protected List<ContentList> InnerInlineSequenceObjects()
	{
		List<object> list = Interleave<object>(Optional(MixedTextAndLogic), String("|"), null, flatten: false);
		if (list == null)
		{
			return null;
		}
		List<ContentList> list2 = new List<ContentList>();
		bool flag = false;
		foreach (object item in list)
		{
			if (item as string == "|")
			{
				if (!flag)
				{
					list2.Add(new ContentList());
				}
				flag = false;
			}
			else
			{
				if (!(item is List<Ink.Parsed.Object> objects))
				{
					Error("Expected content, but got " + item?.ToString() + " (this is an ink compiler bug!)");
				}
				else
				{
					list2.Add(new ContentList(objects));
				}
				flag = true;
			}
		}
		if (!flag)
		{
			list2.Add(new ContentList());
		}
		return list2;
	}

	protected List<ContentList> InnerMultilineSequenceObjects()
	{
		MultilineWhitespace();
		return OneOrMore(SingleMultilineSequenceElement)?.Cast<ContentList>().ToList();
	}

	protected ContentList SingleMultilineSequenceElement()
	{
		Whitespace();
		if (ParseString("->") != null)
		{
			return null;
		}
		if (ParseString("-") == null)
		{
			return null;
		}
		Whitespace();
		List<Ink.Parsed.Object> list = StatementsAtLevel(StatementLevel.InnerBlock);
		if (list == null)
		{
			MultilineWhitespace();
		}
		else
		{
			list.Insert(0, new Text("\n"));
		}
		return new ContentList(list);
	}

	protected List<Ink.Parsed.Object> StatementsAtLevel(StatementLevel level)
	{
		if (level == StatementLevel.InnerBlock && Parse(GatherDashes) != null)
		{
			Error("You can't use a gather (the dashes) within the { curly braces } context. For multi-line sequences and conditions, you should only use one dash.");
		}
		return Interleave<Ink.Parsed.Object>(Optional(MultilineWhitespace), () => StatementAtLevel(level), () => StatementsBreakForLevel(level));
	}

	protected object StatementAtLevel(StatementLevel level)
	{
		ParseRule[] array = _statementRulesAtLevel[(int)level];
		object obj = OneOf(array);
		if (level == StatementLevel.Top && obj is Return)
		{
			Error("should not have return statement outside of a knot");
		}
		return obj;
	}

	protected object StatementsBreakForLevel(StatementLevel level)
	{
		Whitespace();
		ParseRule[] array = _statementBreakRulesAtLevel[(int)level];
		object obj = OneOf(array);
		if (obj == null)
		{
			return null;
		}
		return obj;
	}

	private void GenerateStatementLevelRules()
	{
		List<StatementLevel> list = Enum.GetValues(typeof(StatementLevel)).Cast<StatementLevel>().ToList();
		_statementRulesAtLevel = new ParseRule[list.Count][];
		_statementBreakRulesAtLevel = new ParseRule[list.Count][];
		foreach (StatementLevel item in list)
		{
			List<ParseRule> list2 = new List<ParseRule>();
			List<ParseRule> list3 = new List<ParseRule>();
			list2.Add(Line(MultiDivert));
			if (item >= StatementLevel.Top)
			{
				list2.Add(KnotDefinition);
			}
			list2.Add(Line(Choice));
			list2.Add(Line(AuthorWarning));
			if (item > StatementLevel.InnerBlock)
			{
				list2.Add(Gather);
			}
			if (item >= StatementLevel.Knot)
			{
				list2.Add(StitchDefinition);
			}
			list2.Add(Line(ListDeclaration));
			list2.Add(Line(VariableDeclaration));
			list2.Add(Line(ConstDeclaration));
			list2.Add(Line(ExternalDeclaration));
			list2.Add(Line(IncludeStatement));
			list2.Add(LogicLine);
			list2.Add(LineOfMixedTextAndLogic);
			if (item <= StatementLevel.Knot)
			{
				list3.Add(KnotDeclaration);
			}
			if (item <= StatementLevel.Stitch)
			{
				list3.Add(StitchDeclaration);
			}
			if (item <= StatementLevel.InnerBlock)
			{
				list3.Add(ParseDashNotArrow);
				list3.Add(String("}"));
			}
			_statementRulesAtLevel[(int)item] = list2.ToArray();
			_statementBreakRulesAtLevel[(int)item] = list3.ToArray();
		}
	}

	protected object SkipToNextLine()
	{
		ParseUntilCharactersFromString("\n\r");
		ParseNewline();
		return StringParser.ParseSuccess;
	}

	protected ParseRule Line(ParseRule inlineRule)
	{
		return delegate
		{
			object obj = ParseObject(inlineRule);
			if (obj == null)
			{
				return (object)null;
			}
			Expect(EndOfLine, "end of line", SkipToNextLine);
			return obj;
		};
	}

	protected Ink.Parsed.Object StartTag()
	{
		Whitespace();
		if (ParseString("#") == null)
		{
			return null;
		}
		if (parsingStringExpression)
		{
			Error("Tags aren't allowed inside of strings. Please use \\# if you want a hash symbol.");
		}
		Ink.Parsed.Object obj = null;
		if (tagActive)
		{
			ContentList contentList = new ContentList();
			contentList.AddContent(new Ink.Parsed.Tag
			{
				isStart = false
			});
			contentList.AddContent(new Ink.Parsed.Tag
			{
				isStart = true
			});
			obj = contentList;
		}
		else
		{
			obj = new Ink.Parsed.Tag
			{
				isStart = true
			};
		}
		tagActive = true;
		Whitespace();
		return obj;
	}

	protected void EndTagIfNecessary(List<Ink.Parsed.Object> outputContentList)
	{
		if (tagActive)
		{
			outputContentList?.Add(new Ink.Parsed.Tag
			{
				isStart = false
			});
			tagActive = false;
		}
	}

	protected void EndTagIfNecessary(ContentList outputContentList)
	{
		if (tagActive)
		{
			if (outputContentList != null)
			{
				outputContentList.AddContent(new Ink.Parsed.Tag
				{
					isStart = false
				});
			}
			tagActive = false;
		}
	}

	protected object EndOfLine()
	{
		return OneOf(Newline, EndOfFile);
	}

	protected object Newline()
	{
		Whitespace();
		if (ParseNewline() == null)
		{
			return null;
		}
		return StringParser.ParseSuccess;
	}

	protected object EndOfFile()
	{
		Whitespace();
		if (!base.endOfInput)
		{
			return null;
		}
		return StringParser.ParseSuccess;
	}

	protected object MultilineWhitespace()
	{
		List<object> list = OneOrMore(Newline);
		if (list == null)
		{
			return null;
		}
		if (list.Count >= 1)
		{
			return StringParser.ParseSuccess;
		}
		return null;
	}

	protected object Whitespace()
	{
		if (ParseCharactersFromCharSet(_inlineWhitespaceChars) != null)
		{
			return StringParser.ParseSuccess;
		}
		return null;
	}

	protected ParseRule Spaced(ParseRule rule)
	{
		return delegate
		{
			Whitespace();
			object obj = ParseObject(rule);
			if (obj == null)
			{
				return (object)null;
			}
			Whitespace();
			return obj;
		};
	}

	protected object AnyWhitespace()
	{
		bool flag = false;
		while (OneOf(Whitespace, MultilineWhitespace) != null)
		{
			flag = true;
		}
		if (!flag)
		{
			return null;
		}
		return StringParser.ParseSuccess;
	}

	protected ParseRule MultiSpaced(ParseRule rule)
	{
		return delegate
		{
			AnyWhitespace();
			object obj = ParseObject(rule);
			if (obj == null)
			{
				return (object)null;
			}
			AnyWhitespace();
			return obj;
		};
	}
}
