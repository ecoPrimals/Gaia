using Godot;

public partial class NotebookPage : Control
{
	[Signal]
	public delegate void WasClickedEventHandler(NotebookPage page);

	[Signal]
	public delegate void CodeLinkPressedEventHandler(string link);

	[Export(PropertyHint.None, "")]
	public Panel shadow;

	[Export(PropertyHint.None, "")]
	private Draggable draggable;

	public bool selectMode;

	protected BaseButton fullPageButton;

	public bool isCurrentActivePage { get; private set; }

	public override void _Ready()
	{
		fullPageButton = new TextureButton();
		fullPageButton.Name = "InvisibleFullPageButton";
		fullPageButton.Size = base.Size;
		fullPageButton.Pressed += delegate
		{
			EmitSignal(SignalName.WasClicked, this);
		};
		AddChild(fullPageButton, forceReadableName: false, InternalMode.Disabled);
	}

	public void SetCurrentActivePage(bool isActivePage)
	{
		fullPageButton.Visible = !isActivePage;
		fullPageButton.MouseFilter = (MouseFilterEnum)((!isActivePage) ? 1 : 2);
		if (draggable != null)
		{
			draggable.dragEnabled = isActivePage;
		}
		isCurrentActivePage = isActivePage;
	}

	public virtual void ClearForPageChange()
	{
		SetSelectMode(enabled: false);
	}

	public virtual void SetSelectMode(bool enabled)
	{
		selectMode = enabled;
	}

	public void MakeLabelsClickable(RichTextLabel label)
	{
		label.MetaClicked += OnTextLabelLinkClicked;
	}

	public void MakeLabelsClickable(RichTextLabel[] labels)
	{
		foreach (RichTextLabel label in labels)
		{
			MakeLabelsClickable(label);
		}
	}

	public void OnTextLabelLinkClicked(Variant meta)
	{
		EmitSignal(SignalName.CodeLinkPressed, meta);
	}
}
