using Ink.Runtime;

namespace Ink.Parsed;

public class Choice : Object, IWeavePoint, INamedContent
{
	private ChoicePoint _runtimeChoice;

	private Container _innerContentContainer;

	private Container _outerContainer;

	private Container _startContentRuntimeContainer;

	private Ink.Runtime.Divert _divertToStartContentOuter;

	private Ink.Runtime.Divert _divertToStartContentInner;

	private Container _r1Label;

	private Container _r2Label;

	private DivertTargetValue _returnToR1;

	private DivertTargetValue _returnToR2;

	private Expression _condition;

	public ContentList startContent { get; protected set; }

	public ContentList choiceOnlyContent { get; protected set; }

	public ContentList innerContent { get; protected set; }

	public string name => identifier?.name;

	public Identifier identifier { get; set; }

	public Expression condition
	{
		get
		{
			return _condition;
		}
		set
		{
			_condition = value;
			if ((bool)_condition)
			{
				AddContent(_condition);
			}
		}
	}

	public bool onceOnly { get; set; }

	public bool isInvisibleDefault { get; set; }

	public int indentationDepth { get; set; }

	public bool hasWeaveStyleInlineBrackets { get; set; }

	public Container runtimeContainer => _innerContentContainer;

	public Container innerContentContainer => _innerContentContainer;

	public override Container containerForCounting => _innerContentContainer;

	public override Ink.Runtime.Path runtimePath => _innerContentContainer.path;

	public Choice(ContentList startContent, ContentList choiceOnlyContent, ContentList innerContent)
	{
		this.startContent = startContent;
		this.choiceOnlyContent = choiceOnlyContent;
		this.innerContent = innerContent;
		indentationDepth = 1;
		if ((bool)startContent)
		{
			AddContent(this.startContent);
		}
		if ((bool)choiceOnlyContent)
		{
			AddContent(this.choiceOnlyContent);
		}
		if ((bool)innerContent)
		{
			AddContent(this.innerContent);
		}
		onceOnly = true;
	}

	public override Ink.Runtime.Object GenerateRuntimeObject()
	{
		_outerContainer = new Container();
		_runtimeChoice = new ChoicePoint(onceOnly);
		_runtimeChoice.isInvisibleDefault = isInvisibleDefault;
		if ((bool)startContent || (bool)choiceOnlyContent || (bool)condition)
		{
			_outerContainer.AddContent(ControlCommand.EvalStart());
		}
		if ((bool)startContent)
		{
			_returnToR1 = new DivertTargetValue();
			_outerContainer.AddContent(_returnToR1);
			Ink.Runtime.VariableAssignment contentObj = new Ink.Runtime.VariableAssignment("$r", isNewDeclaration: true);
			_outerContainer.AddContent(contentObj);
			_outerContainer.AddContent(ControlCommand.BeginString());
			_divertToStartContentOuter = new Ink.Runtime.Divert();
			_outerContainer.AddContent(_divertToStartContentOuter);
			_startContentRuntimeContainer = startContent.GenerateRuntimeObject() as Container;
			_startContentRuntimeContainer.name = "s";
			Ink.Runtime.Divert divert = new Ink.Runtime.Divert();
			divert.variableDivertName = "$r";
			_startContentRuntimeContainer.AddContent(divert);
			_outerContainer.AddToNamedContentOnly(_startContentRuntimeContainer);
			_r1Label = new Container();
			_r1Label.name = "$r1";
			_outerContainer.AddContent(_r1Label);
			_outerContainer.AddContent(ControlCommand.EndString());
			_runtimeChoice.hasStartContent = true;
		}
		if ((bool)choiceOnlyContent)
		{
			_outerContainer.AddContent(ControlCommand.BeginString());
			Container otherContainer = choiceOnlyContent.GenerateRuntimeObject() as Container;
			_outerContainer.AddContentsOfContainer(otherContainer);
			_outerContainer.AddContent(ControlCommand.EndString());
			_runtimeChoice.hasChoiceOnlyContent = true;
		}
		if ((bool)condition)
		{
			condition.GenerateIntoContainer(_outerContainer);
			_runtimeChoice.hasCondition = true;
		}
		if ((bool)startContent || (bool)choiceOnlyContent || (bool)condition)
		{
			_outerContainer.AddContent(ControlCommand.EvalEnd());
		}
		_outerContainer.AddContent(_runtimeChoice);
		_innerContentContainer = new Container();
		if ((bool)startContent)
		{
			_returnToR2 = new DivertTargetValue();
			_innerContentContainer.AddContent(ControlCommand.EvalStart());
			_innerContentContainer.AddContent(_returnToR2);
			_innerContentContainer.AddContent(ControlCommand.EvalEnd());
			Ink.Runtime.VariableAssignment contentObj2 = new Ink.Runtime.VariableAssignment("$r", isNewDeclaration: true);
			_innerContentContainer.AddContent(contentObj2);
			_divertToStartContentInner = new Ink.Runtime.Divert();
			_innerContentContainer.AddContent(_divertToStartContentInner);
			_r2Label = new Container();
			_r2Label.name = "$r2";
			_innerContentContainer.AddContent(_r2Label);
		}
		if ((bool)innerContent)
		{
			Container otherContainer2 = innerContent.GenerateRuntimeObject() as Container;
			_innerContentContainer.AddContentsOfContainer(otherContainer2);
		}
		if (base.story.countAllVisits)
		{
			_innerContentContainer.visitsShouldBeCounted = true;
		}
		_innerContentContainer.countingAtStartOnly = true;
		return _outerContainer;
	}

	public override void ResolveReferences(Story context)
	{
		if ((bool)_innerContentContainer)
		{
			_runtimeChoice.pathOnChoice = _innerContentContainer.path;
			if (onceOnly)
			{
				_innerContentContainer.visitsShouldBeCounted = true;
			}
		}
		if ((bool)_returnToR1)
		{
			_returnToR1.targetPath = _r1Label.path;
		}
		if ((bool)_returnToR2)
		{
			_returnToR2.targetPath = _r2Label.path;
		}
		if ((bool)_divertToStartContentOuter)
		{
			_divertToStartContentOuter.targetPath = _startContentRuntimeContainer.path;
		}
		if ((bool)_divertToStartContentInner)
		{
			_divertToStartContentInner.targetPath = _startContentRuntimeContainer.path;
		}
		base.ResolveReferences(context);
		if (identifier != null && identifier.name.Length > 0)
		{
			context.CheckForNamingCollisions(this, identifier, Story.SymbolType.SubFlowAndWeave);
		}
	}

	public override string ToString()
	{
		if (choiceOnlyContent != null)
		{
			return $"* {startContent}[{choiceOnlyContent}]...";
		}
		return $"* {startContent}...";
	}
}
