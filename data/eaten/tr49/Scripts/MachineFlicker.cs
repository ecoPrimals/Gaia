using Godot;

public partial class MachineFlicker : Node
{
	public FlickerSettings activeFlicker;

	[Export(PropertyHint.None, "")]
	private StyleBoxFlat rowItemStyleBox;

	[Export(PropertyHint.None, "")]
	private Theme defaultCardTheme;

	[Export(PropertyHint.None, "")]
	private MachineAudio machineAudio;

	private float flickerTimeRemaining;

	private float timeToNextFlicker;

	public static float flicker { get; private set; } = 1f;

	public override void _Process(double delta)
	{
		if (activeFlicker != null && !GameSettings.instance.reduceGlitchEffects)
		{
			UpdateFlickerValue((float)delta);
		}
		else
		{
			flicker = 1f;
		}
		Color bgColor = rowItemStyleBox.BgColor;
		bgColor.A = flicker;
		rowItemStyleBox.BgColor = bgColor;
		foreach (Node item in GetTree().GetNodesInGroup("card_text_contents"))
		{
			if (item is CanvasItem { Modulate: var modulate } canvasItem)
			{
				modulate.A = flicker;
				canvasItem.Modulate = modulate;
			}
		}
	}

	private void UpdateFlickerValue(float delta)
	{
		if (flickerTimeRemaining == 0f)
		{
			if (timeToNextFlicker == 0f)
			{
				timeToNextFlicker = (float)GD.RandRange(activeFlicker.timeBetweenFlickerStartsMin, activeFlicker.timeBetweenFlickerStartsMax);
			}
			timeToNextFlicker -= delta;
			if (timeToNextFlicker < 0f)
			{
				machineAudio.FlickerStarted();
				timeToNextFlicker = 0f;
				flickerTimeRemaining = (float)GD.RandRange(activeFlicker.flickerDurationMin, activeFlicker.flickerDurationMax);
			}
		}
		else
		{
			flickerTimeRemaining -= delta;
			if (flickerTimeRemaining < 0f)
			{
				flickerTimeRemaining = 0f;
			}
		}
		if (flickerTimeRemaining > 0f)
		{
			float num = ((Mathf.Sin((float)Time.GetTicksMsec() * 0.001f * 100f) < 0.7f) ? activeFlicker.minAlpha : 1f);
			if (num < flicker)
			{
				flicker = num;
			}
			else
			{
				flicker = Mathf.MoveToward(flicker, num, delta * 5f);
			}
		}
		else
		{
			flicker = 1f;
		}
	}
}
