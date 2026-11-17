using Godot;

[GlobalClass]
public partial class FlickerSettings : Resource
{
	[Export(PropertyHint.None, "")]
	public float timeBetweenFlickerStartsMin = 0.2f;

	[Export(PropertyHint.None, "")]
	public float timeBetweenFlickerStartsMax = 1.5f;

	[Export(PropertyHint.None, "")]
	public float flickerDurationMin = 0.1f;

	[Export(PropertyHint.None, "")]
	public float flickerDurationMax = 0.8f;

	[Export(PropertyHint.None, "")]
	public float minAlpha = 0.3f;
}
