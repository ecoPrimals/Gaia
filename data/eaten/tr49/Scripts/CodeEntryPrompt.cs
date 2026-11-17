using Godot;

public partial class CodeEntryPrompt : Control
{
	[Export(PropertyHint.None, "")]
	public Control desktopPrompt;

	[Export(PropertyHint.None, "")]
	public Control gamepadPrompt;

	[Export(PropertyHint.None, "")]
	public MachineUI machineUI;

	[Export(PropertyHint.None, "")]
	private Label triggerLabel;

	private float gamepadAlpha = 1f;

	public override void _Ready()
	{
		triggerLabel.Text = (Platform.isSwitch ? "ZR" : "RT");
	}

	public override void _Process(double delta)
	{
		desktopPrompt.Visible = PrimaryInputManager.isKeyboard && !Platform.isMobile && !DebugOptions.instance.disableButtonPrompts;
		gamepadPrompt.Visible = PrimaryInputManager.isGamepad && !Platform.isMobile && !DebugOptions.instance.disableButtonPrompts;
		float to = ((machineUI.codeEntryMode && !machineUI.preventInputByOtherUI) ? 0f : 1f);
		gamepadAlpha = Mathf.MoveToward(gamepadAlpha, to, (float)delta * 10f);
		gamepadPrompt.Modulate = new Color(1f, 1f, 1f, gamepadAlpha);
	}
}
