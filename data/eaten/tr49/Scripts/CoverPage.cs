using Godot;

public partial class CoverPage : NotebookPage
{
	private RichTextLabel objectiveLabel;

	private RichTextLabel sourcesLabel;

	private RichTextLabel titlesLabel;

	public override void _Ready()
	{
		base._Ready();
		objectiveLabel = GetNode<RichTextLabel>("ObjectiveLabel");
		sourcesLabel = GetNode<RichTextLabel>("SourcesLabel");
		titlesLabel = GetNode<RichTextLabel>("TitlesLabel");
		Clear();
	}

	public void Setup(string objectiveText, string sourcesText, string titlesText)
	{
		objectiveLabel.Text = objectiveText;
		sourcesLabel.Text = sourcesText;
		titlesLabel.Text = titlesText;
	}

	public void Clear()
	{
		objectiveLabel.Text = "";
		sourcesLabel.Text = "";
		titlesLabel.Text = "";
	}
}
