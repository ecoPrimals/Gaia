using Godot;

public partial class LinkButton : Button
{
	public string linkWithoutPrefix;

	public bool isTitle;

	public bool collected;

	private bool invertedColors;

	public void Setup(string text, string linkWithoutPrefix, bool isTitle, bool collected, bool invertedColors)
	{
		this.isTitle = isTitle;
		this.linkWithoutPrefix = linkWithoutPrefix;
		this.invertedColors = invertedColors;
		this.collected = collected;
		base.Text = text;
		base.Name = text;
		RefreshState();
	}

	public void SetAsCollected(bool collected)
	{
		this.collected = collected;
		RefreshState();
	}

	public void RefreshState()
	{
		Color color = (invertedColors ? Colors.Black : Colors.White);
		bool playerIsCollectingTitles = StoryController.instance.playerIsCollectingTitles;
		Color color2 = ((!playerIsCollectingTitles || !isTitle) ? color : ((!collected) ? color : Colors.Yellow));
		AddThemeColorOverride("font_color", color2);
		AddThemeColorOverride("font_color_bold", color2);
		bool flag = ((isTitle & playerIsCollectingTitles) && !collected) || !isTitle;
		base.Disabled = !flag;
		base.FocusMode = (FocusModeEnum)(flag ? 1 : 0);
		base.MouseFilter = (MouseFilterEnum)(flag ? 1 : 2);
	}
}
