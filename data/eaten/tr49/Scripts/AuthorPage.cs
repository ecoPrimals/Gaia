using System.Collections.Generic;
using Godot;

public partial class AuthorPage : NotebookPage
{
	private struct PublicationRow
	{
		public Control control;

		public RichTextLabel titleLabel;

		public string code;

		public Button codeButton;

		public Control selection;
	}

	[Export(PropertyHint.None, "")]
	private TextureRect image;

	[Export(PropertyHint.None, "")]
	private RichTextLabel titleLabel;

	[Export(PropertyHint.None, "")]
	private RichTextLabel descriptionLabel;

	[Export(PropertyHint.None, "")]
	private Button characterCodeButton;

	[Export(PropertyHint.None, "")]
	private Control descriptionContainer;

	[Export(PropertyHint.None, "")]
	private Control illustrationContainer;

	[Export(PropertyHint.None, "")]
	private Control publicationsContainer;

	[Export(PropertyHint.None, "")]
	private VBoxContainer publicationsList;

	[Export(PropertyHint.None, "")]
	private PackedScene publicationScene;

	[Export(PropertyHint.None, "")]
	private float publicationsYWhenAtTop = 50f;

	[Export(PropertyHint.None, "")]
	private float illustrationYOffsetWhenAtBottom = 50f;

	[Export(PropertyHint.None, "")]
	private float paperLineHeight = 41f;

	[Export(PropertyHint.None, "")]
	private int smallDescriptionFontSizeVariant = 24;

	[Export(PropertyHint.None, "")]
	private int smallDescriptionLineSeparationVariant = -5;

	private List<PublicationRow> publicationRows = new List<PublicationRow>();

	private int selectedPublicationIdx = -1;

	private static float defaultPublicationsY;

	private static float defaultIllustrationY;

	private static float defaultDescriptionHeight;

	public override void _EnterTree()
	{
		base._EnterTree();
		if (defaultPublicationsY == 0f)
		{
			defaultPublicationsY = publicationsContainer.Position.Y;
			defaultIllustrationY = illustrationContainer.Position.Y;
			defaultDescriptionHeight = descriptionLabel.Size.Y;
		}
	}

	public override void _Ready()
	{
		base._Ready();
		if (GetParent() == GetTree().GetRoot())
		{
			NotebookAuthorPage authorPage = new NotebookAuthorPage
			{
				name = "Joseph Humfrey",
				prefixLetters = "JH",
				imagePath = "Images/Characters/Notebook/Aliz_Notebook.png",
				blurb = "Born in 1984?\nVery extremely smart and handsome.\nHe once mistook a typewriter for a hat.\nHe didn't realise that geese are actually dinosaurs.\nBeware: may randomly honk inspirational quotes.\nBorn in 1984?\nVery extremely smart and handsome.\nHe once mistook a typewriter for a hat.\nHe didn't realise that geese are actually dinosaurs.\nBeware: may randomly honk inspirational quotes.",
				publications = new List<NotebookAuthorPublication>()
			};
			List<string> list = new List<string> { "On the Intangibility of Matter", "\"I have decided to take over my father's work...\"" };
			for (int i = 0; i < 2; i++)
			{
				authorPage.publications.Add(new NotebookAuthorPublication
				{
					code = $"JH-{80 + i}",
					titleApplied = list[i % list.Count],
					isDefinitive = (i < 5)
				});
			}
			Setup(authorPage);
		}
	}

	public void Setup(NotebookAuthorPage authorPage)
	{
		base.Name = authorPage.prefixLetters + " author page";
		titleLabel.Text = authorPage.name;
		if (authorPage.prefixLetters != "")
		{
			characterCodeButton.Text = authorPage.prefixLetters;
			characterCodeButton.Pressed += delegate
			{
				EmitSignal(NotebookPage.SignalName.CodeLinkPressed, authorPage.prefixLetters);
			};
		}
		else
		{
			characterCodeButton.Text = "??";
		}
		image.Texture = null;
		if (!string.IsNullOrEmpty(authorPage.imagePath))
		{
			string text = "res://" + authorPage.imagePath;
			if (ResourceLoader.Exists(text))
			{
				image.Texture = ResourceLoader.Load<Texture2D>(text, null, ResourceLoader.CacheMode.Reuse);
			}
			else
			{
				GD.PrintErr("Portrait image for character " + authorPage.name + " not found: " + text);
			}
		}
		descriptionLabel.Text = authorPage.blurb ?? "";
		illustrationContainer.Visible = image.Texture != null;
		descriptionContainer.Visible = !string.IsNullOrEmpty(authorPage.blurb);
		float y = ((!descriptionContainer.Visible) ? publicationsYWhenAtTop : defaultPublicationsY);
		publicationsContainer.Position = new Vector2(publicationsContainer.Position.X, y);
		illustrationContainer.Position = new Vector2(illustrationContainer.Position.X, defaultIllustrationY);
		string text2 = "";
		string text3 = "";
		foreach (NotebookAuthorPublication publication in authorPage.publications)
		{
			PublicationRow row = default(PublicationRow);
			row.code = publication.code;
			row.control = publicationScene.Instantiate<Control>(PackedScene.GenEditState.Disabled);
			text2 = ((!publication.isDefinitive) ? " (?)" : "");
			text3 = (publication.isNotFullyLinked ? " (*)" : "");
			row.control.GetNode<RichTextLabel>("Title").Text = $"- {publication.titleApplied} {text2} {text3}";
			row.selection = row.control.GetNode<Control>("Selection");
			row.selection.Visible = false;
			Button node = row.control.GetNode<Button>("CodeLinkButton");
			node.Text = publication.code;
			node.Pressed += delegate
			{
				EmitSignal(NotebookPage.SignalName.CodeLinkPressed, row.code);
			};
			publicationRows.Add(row);
			publicationsList.AddChild(row.control, forceReadableName: false, InternalMode.Disabled);
		}
		int childCount = publicationsList.GetChildCount();
		if (!descriptionContainer.Visible && childCount > 0)
		{
			float y2 = publicationsContainer.Position.Y + publicationsList.Position.Y + paperLineHeight * (float)childCount + illustrationYOffsetWhenAtBottom;
			illustrationContainer.Position = new Vector2(illustrationContainer.Position.X, y2);
		}
		CallDeferred(new StringName("CheckForTextOverflow"));
	}

	private void CheckForTextOverflow()
	{
		if (descriptionLabel.Size.Y > defaultDescriptionHeight)
		{
			descriptionLabel.FitContent = false;
			descriptionLabel.Text = descriptionLabel.Text.Replace("\n", " • ");
			descriptionLabel.AddThemeFontSizeOverride("normal_font_size", smallDescriptionFontSizeVariant);
			descriptionLabel.AddThemeConstantOverride("paragraph_separation", 0);
			descriptionLabel.AddThemeConstantOverride("line_separation", smallDescriptionLineSeparationVariant);
			descriptionLabel.Size = new Vector2(descriptionLabel.Size.X, defaultDescriptionHeight);
		}
	}

	public override void SetSelectMode(bool enabled)
	{
		base.SetSelectMode(enabled);
		if (enabled && selectedPublicationIdx == -1)
		{
			selectedPublicationIdx = 0;
		}
		else if (!enabled)
		{
			selectedPublicationIdx = -1;
		}
		RefreshSelection();
	}

	public override void ClearForPageChange()
	{
		base.ClearForPageChange();
		selectedPublicationIdx = -1;
	}

	public override void _Input(InputEvent @event)
	{
		if (selectMode)
		{
			int num = 0;
			if (@event.IsActionPressed("ui_up"))
			{
				this.SetInputAsHandled(@event);
				num = -1;
			}
			else if (@event.IsActionPressed("ui_down"))
			{
				this.SetInputAsHandled(@event);
				num = 1;
			}
			else if (@event.IsActionPressed("ui_accept") && selectedPublicationIdx != -1)
			{
				this.SetInputAsHandled(@event);
				EmitSignal(NotebookPage.SignalName.CodeLinkPressed, publicationRows[selectedPublicationIdx].code);
			}
			if (num != 0)
			{
				selectedPublicationIdx = Mathf.Clamp(selectedPublicationIdx + num, 0, publicationRows.Count - 1);
				RefreshSelection();
			}
		}
	}

	private void RefreshSelection()
	{
		for (int i = 0; i < publicationRows.Count; i++)
		{
			publicationRows[i].selection.Visible = selectedPublicationIdx == i;
		}
	}
}
