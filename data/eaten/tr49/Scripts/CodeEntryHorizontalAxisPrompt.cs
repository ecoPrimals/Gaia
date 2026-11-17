using Godot;

public partial class CodeEntryHorizontalAxisPrompt : Control
{
	[Export(PropertyHint.None, "")]
	public MachineUI machineUI;

	private float fadeInOutAlpha = 1f;

	public override void _Process(double delta)
	{
		float to = ((PrimaryInputManager.isGamepad && !Platform.isMobile && machineUI.codeEntryMode && !machineUI.preventInputByOtherUI) ? 1f : 0f);
		fadeInOutAlpha = Mathf.MoveToward(fadeInOutAlpha, to, (float)delta * 10f);
		base.Modulate = new Color(1f, 1f, 1f, fadeInOutAlpha);
	}
}
