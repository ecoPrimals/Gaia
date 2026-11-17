using Godot;

public partial class AmbientAudio : AudioStreamPlayer
{
	public static AmbientAudio instance;

	[Export(PropertyHint.None, "")]
	private float fadeUpTime = 4f;

	[Export(PropertyHint.None, "")]
	private float fadeDownTime = 10f;

	[Export(PropertyHint.None, "")]
	private Curve volumeCurve;

	public bool rampDownForCredits;

	private float volumeNormalized;

	private bool hasBegun;

	public override void _EnterTree()
	{
		instance = this;
		base.VolumeDb = -80f;
	}

	public void Begin()
	{
		hasBegun = true;
	}

	public override void _Process(double delta)
	{
		float num = ((hasBegun && !rampDownForCredits) ? 1f : 0f);
		float num2 = ((num > volumeNormalized) ? fadeUpTime : fadeDownTime);
		volumeNormalized = Mathf.MoveToward(volumeNormalized, num, (float)delta / num2);
		base.VolumeDb = Mathf.Lerp(-80f, 0f, volumeCurve.Sample(volumeNormalized));
	}
}
