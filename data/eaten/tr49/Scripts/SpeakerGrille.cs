using Godot;

public partial class SpeakerGrille : Sprite3D
{
	[Export(PropertyHint.None, "")]
	private float threshold = 0.01f;

	[Export(PropertyHint.None, "")]
	private float levelFalloffTime = 0.5f;

	[Export(PropertyHint.None, "")]
	private float pulseSpeed = 5f;

	[Export(PropertyHint.None, "")]
	private float pulseMinBrightness = 0.5f;

	private int machineVoicesBusIndex;

	private int distortionBusIndex;

	private float levelSmoothed;

	public override void _Ready()
	{
		machineVoicesBusIndex = AudioServer.GetBusIndex("MachineVoices");
		distortionBusIndex = AudioServer.GetBusIndex("Distortion");
	}

	public override void _Process(double delta)
	{
		float busLevel = GetBusLevel(machineVoicesBusIndex);
		float busLevel2 = GetBusLevel(distortionBusIndex);
		float num = Mathf.Clamp(Mathf.Max(busLevel, busLevel2) / threshold, 0f, 1f);
		if (num > levelSmoothed)
		{
			levelSmoothed = num;
		}
		else
		{
			levelSmoothed = Mathf.MoveToward(levelSmoothed, num, (float)delta / levelFalloffTime);
		}
		float num2 = (float)Time.GetTicksMsec() * 0.001f;
		float weight = Mathf.Sin(pulseSpeed * num2) * 0.5f + 0.5f;
		float num3 = Mathf.Lerp(pulseMinBrightness, 1f, weight);
		base.Modulate = new Color(1f, 1f, 1f, levelSmoothed * num3);
	}

	private float GetBusLevel(int busIndex)
	{
		int effectIdx = AudioServer.GetBusEffectCount(busIndex) - 1;
		AudioEffectCapture obj = (AudioEffectCapture)AudioServer.GetBusEffect(busIndex, effectIdx);
		Vector2[] buffer = obj.GetBuffer(obj.GetFramesAvailable());
		if (buffer.Length == 0)
		{
			return 0f;
		}
		float num = 0f;
		for (int i = 0; i < buffer.Length; i++)
		{
			num += Mathf.Abs(buffer[i].Y);
		}
		return num / (float)buffer.Length;
	}
}
