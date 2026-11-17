using Godot;

public partial class SingleScore : Control
{
	[Export(PropertyHint.None, "")]
	private RichTextLabel scoreLabel;

	[Export(PropertyHint.None, "")]
	private Label textLabel;

	[Export(PropertyHint.None, "")]
	private TextureRect psiImage;

	private Score _score;

	public Score score
	{
		get
		{
			return _score;
		}
		set
		{
			_score = value;
			string text = $"[b][font_size=40]{_score.value}[/font_size][/b]";
			if (score.total > 0)
			{
				string text2 = $"[color=gray][font_size=22]/{score.total}[/font_size][/color]";
				scoreLabel.Text = text + text2;
			}
			else
			{
				scoreLabel.Text = text;
			}
			if (score.label == "PSICHAR")
			{
				psiImage.Visible = true;
				textLabel.Visible = false;
			}
			else
			{
				textLabel.Text = score.label;
				psiImage.Visible = false;
				textLabel.Visible = true;
			}
		}
	}
}
