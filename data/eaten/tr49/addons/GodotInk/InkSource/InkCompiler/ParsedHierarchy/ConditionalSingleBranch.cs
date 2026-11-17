using System.Collections.Generic;
using Ink.Runtime;

namespace Ink.Parsed;

public class ConditionalSingleBranch : Object
{
	private Container _contentContainer;

	private Ink.Runtime.Divert _conditionalDivert;

	private Expression _ownExpression;

	private Weave _innerWeave;

	public bool isTrueBranch { get; set; }

	public Expression ownExpression
	{
		get
		{
			return _ownExpression;
		}
		set
		{
			_ownExpression = value;
			if ((bool)_ownExpression)
			{
				AddContent(_ownExpression);
			}
		}
	}

	public bool matchingEquality { get; set; }

	public bool isElse { get; set; }

	public bool isInline { get; set; }

	public Ink.Runtime.Divert returnDivert { get; protected set; }

	public ConditionalSingleBranch(List<Object> content)
	{
		if (content != null)
		{
			_innerWeave = new Weave(content);
			AddContent(_innerWeave);
		}
	}

	public override Ink.Runtime.Object GenerateRuntimeObject()
	{
		if ((bool)_innerWeave)
		{
			foreach (Object item in _innerWeave.content)
			{
				Text text = item as Text;
				if ((bool)text && text.text.StartsWith("else:"))
				{
					Warning("Saw the text 'else:' which is being treated as content. Did you mean '- else:'?", text);
				}
			}
		}
		Container container = new Container();
		int num;
		if (matchingEquality)
		{
			num = ((!isElse) ? 1 : 0);
			if (num != 0)
			{
				container.AddContent(ControlCommand.Duplicate());
			}
		}
		else
		{
			num = 0;
		}
		_conditionalDivert = new Ink.Runtime.Divert();
		_conditionalDivert.isConditional = !isElse;
		if (!isTrueBranch && !isElse)
		{
			bool num2 = ownExpression != null;
			if (num2)
			{
				container.AddContent(ControlCommand.EvalStart());
			}
			if ((bool)ownExpression)
			{
				ownExpression.GenerateIntoContainer(container);
			}
			if (matchingEquality)
			{
				container.AddContent(NativeFunctionCall.CallWithName("=="));
			}
			if (num2)
			{
				container.AddContent(ControlCommand.EvalEnd());
			}
		}
		container.AddContent(_conditionalDivert);
		_contentContainer = GenerateRuntimeForContent();
		_contentContainer.name = "b";
		if (!isInline)
		{
			_contentContainer.InsertContent(new StringValue("\n"), 0);
		}
		if (num != 0 || (isElse && matchingEquality))
		{
			_contentContainer.InsertContent(ControlCommand.PopEvaluatedValue(), 0);
		}
		container.AddToNamedContentOnly(_contentContainer);
		returnDivert = new Ink.Runtime.Divert();
		_contentContainer.AddContent(returnDivert);
		return container;
	}

	private Container GenerateRuntimeForContent()
	{
		if (_innerWeave == null)
		{
			return new Container();
		}
		return _innerWeave.rootContainer;
	}

	public override void ResolveReferences(Story context)
	{
		_conditionalDivert.targetPath = _contentContainer.path;
		base.ResolveReferences(context);
	}
}
