using System;
using System.Collections.Generic;
using Ink.Parsed;
using Ink.Runtime;

namespace Ink;

public class Compiler
{
	public class Options
	{
		public string sourceFilename;

		public List<string> pluginDirectories;

		public bool countAllVisits;

		public ErrorHandler errorHandler;

		public IFileHandler fileHandler;
	}

	public class CommandLineInputResult
	{
		public bool requestsExit;

		public int choiceIdx = -1;

		public string divertedPath;

		public string output;
	}

	public struct DebugSourceRange
	{
		public int length;

		public DebugMetadata debugMetadata;

		public string text;
	}

	private string _inputString;

	private Options _options;

	private InkParser _parser;

	private Ink.Parsed.Story _parsedStory;

	private Ink.Runtime.Story _runtimeStory;

	private PluginManager _pluginManager;

	private bool _hadParseError;

	private List<DebugSourceRange> _debugSourceRanges = new List<DebugSourceRange>();

	public Ink.Parsed.Story parsedStory => _parsedStory;

	public Compiler(string inkSource, Options options = null)
	{
		_inputString = inkSource;
		_options = options ?? new Options();
		if (_options.pluginDirectories != null)
		{
			_pluginManager = new PluginManager(_options.pluginDirectories);
		}
	}

	public Ink.Parsed.Story Parse()
	{
		_parser = new InkParser(_inputString, _options.sourceFilename, OnParseError, _options.fileHandler);
		_parsedStory = _parser.Parse();
		return _parsedStory;
	}

	public Ink.Runtime.Story Compile()
	{
		if (_pluginManager != null)
		{
			_inputString = _pluginManager.PreParse(_inputString);
		}
		Parse();
		if (_pluginManager != null)
		{
			_parsedStory = _pluginManager.PostParse(_parsedStory);
		}
		if (_parsedStory != null && !_hadParseError)
		{
			_parsedStory.countAllVisits = _options.countAllVisits;
			_runtimeStory = _parsedStory.ExportRuntime(_options.errorHandler);
			if (_pluginManager != null)
			{
				_runtimeStory = _pluginManager.PostExport(_parsedStory, _runtimeStory);
			}
		}
		else
		{
			_runtimeStory = null;
		}
		return _runtimeStory;
	}

	public CommandLineInputResult HandleInput(CommandLineInput inputResult)
	{
		CommandLineInputResult commandLineInputResult = new CommandLineInputResult();
		if (inputResult.debugSource.HasValue)
		{
			int value = inputResult.debugSource.Value;
			DebugMetadata debugMetadata = DebugMetadataForContentAtOffset(value);
			if (debugMetadata != null)
			{
				commandLineInputResult.output = "DebugSource: " + debugMetadata.ToString();
			}
			else
			{
				commandLineInputResult.output = "DebugSource: Unknown source";
			}
		}
		else
		{
			if (inputResult.debugPathLookup == null)
			{
				if (inputResult.userImmediateModeStatement != null)
				{
					Ink.Parsed.Object parsedObj = inputResult.userImmediateModeStatement as Ink.Parsed.Object;
					return ExecuteImmediateStatement(parsedObj);
				}
				return null;
			}
			string debugPathLookup = inputResult.debugPathLookup;
			DebugMetadata debugMetadata2 = _runtimeStory.ContentAtPath(new Ink.Runtime.Path(debugPathLookup)).obj.debugMetadata;
			if (debugMetadata2 != null)
			{
				commandLineInputResult.output = "DebugSource: " + debugMetadata2.ToString();
			}
			else
			{
				commandLineInputResult.output = "DebugSource: Unknown source";
			}
		}
		return commandLineInputResult;
	}

	private CommandLineInputResult ExecuteImmediateStatement(Ink.Parsed.Object parsedObj)
	{
		CommandLineInputResult commandLineInputResult = new CommandLineInputResult();
		if (parsedObj is Ink.Parsed.VariableAssignment)
		{
			Ink.Parsed.VariableAssignment variableAssignment = (Ink.Parsed.VariableAssignment)parsedObj;
			if (variableAssignment.isNewTemporaryDeclaration)
			{
				_parsedStory.TryAddNewVariableDeclaration(variableAssignment);
			}
		}
		parsedObj.parent = _parsedStory;
		Ink.Runtime.Object runtimeObject = parsedObj.runtimeObject;
		parsedObj.ResolveReferences(_parsedStory);
		if (!_parsedStory.hadError)
		{
			if (parsedObj is Ink.Parsed.Divert)
			{
				Ink.Parsed.Divert divert = parsedObj as Ink.Parsed.Divert;
				commandLineInputResult.divertedPath = divert.runtimeDivert.targetPath.ToString();
			}
			else if (parsedObj is Expression || parsedObj is Ink.Parsed.VariableAssignment)
			{
				Ink.Runtime.Object obj = _runtimeStory.EvaluateExpression((Container)runtimeObject);
				if (obj != null)
				{
					commandLineInputResult.output = obj.ToString();
				}
			}
		}
		else
		{
			_parsedStory.ResetError();
		}
		return commandLineInputResult;
	}

	public void RetrieveDebugSourceForLatestContent()
	{
		foreach (Ink.Runtime.Object item2 in _runtimeStory.state.outputStream)
		{
			StringValue stringValue = item2 as StringValue;
			if (stringValue != null)
			{
				DebugSourceRange item = new DebugSourceRange
				{
					length = stringValue.value.Length,
					debugMetadata = stringValue.debugMetadata,
					text = stringValue.value
				};
				_debugSourceRanges.Add(item);
			}
		}
	}

	private DebugMetadata DebugMetadataForContentAtOffset(int offset)
	{
		int num = 0;
		DebugMetadata result = null;
		foreach (DebugSourceRange debugSourceRange in _debugSourceRanges)
		{
			if (debugSourceRange.debugMetadata != null)
			{
				result = debugSourceRange.debugMetadata;
			}
			if (offset >= num && offset < num + debugSourceRange.length)
			{
				return result;
			}
			num += debugSourceRange.length;
		}
		return null;
	}

	private void OnParseError(string message, ErrorType errorType)
	{
		if (errorType == ErrorType.Error)
		{
			_hadParseError = true;
		}
		if (_options.errorHandler != null)
		{
			_options.errorHandler(message, errorType);
			return;
		}
		throw new Exception(message);
	}
}
