using Godot;

public partial class Haptic : Node
{
	public static Haptic instance;

	private float activeVibrationCombinedStrength;

	private float activeVibrationTimeRemaining;

	public override void _EnterTree()
	{
		instance = this;
	}

	public override void _Process(double delta)
	{
		if (activeVibrationTimeRemaining > 0f)
		{
			activeVibrationTimeRemaining -= (float)delta;
			if (activeVibrationTimeRemaining <= 0f)
			{
				activeVibrationCombinedStrength = 0f;
				activeVibrationTimeRemaining = 0f;
			}
		}
	}

	private void StartVibration(float weak, float strong, float duration)
	{
		if (Platform.isSwitch)
		{
			weak *= 0.04f;
			strong *= 0.08f;
			duration *= 0.7f;
		}
		float num = 0.5f * weak + strong;
		if (!(activeVibrationTimeRemaining > 0.05f) || !(num < activeVibrationCombinedStrength))
		{
			activeVibrationCombinedStrength = num;
			activeVibrationTimeRemaining = duration;
			Input.StartJoyVibration(0, weak, strong, duration);
		}
	}

	public void LittleTap()
	{
		if (GameSettings.instance.hapticsEnabled)
		{
			if (Platform.isMobile)
			{
				Input.VibrateHandheld(50, 0.1f);
			}
			else
			{
				StartVibration(1f, 0.3f, 0.15f);
			}
		}
	}

	public void Tap()
	{
		if (GameSettings.instance.hapticsEnabled)
		{
			if (Platform.isMobile)
			{
				Input.VibrateHandheld(50, 0.2f);
			}
			else
			{
				StartVibration(1f, 1f, 0.15f);
			}
		}
	}

	public void LightStep()
	{
		if (GameSettings.instance.hapticsEnabled)
		{
			if (Platform.isMobile)
			{
				Input.VibrateHandheld(50, 0.1f);
			}
			else
			{
				StartVibration(0.5f, 0.5f, 0.15f);
			}
		}
	}

	public void BigClunk()
	{
		if (GameSettings.instance.hapticsEnabled)
		{
			if (Platform.isMobile)
			{
				Input.VibrateHandheld(100, 0.6f);
			}
			else
			{
				StartVibration(1f, 1f, 0.4f);
			}
		}
	}

	public void SubtleWhoosh()
	{
		if (GameSettings.instance.hapticsEnabled)
		{
			if (Platform.isMobile)
			{
				Input.VibrateHandheld(500, 0.05f);
			}
			else
			{
				StartVibration(0.4f, 0.4f, 0.5f);
			}
		}
	}

	public void Whoosh()
	{
		if (GameSettings.instance.hapticsEnabled)
		{
			if (Platform.isMobile)
			{
				Input.VibrateHandheld(1000, 0.1f);
			}
			else
			{
				StartVibration(0.8f, 0.8f, 1f);
			}
		}
	}

	public void Stop()
	{
		Input.StopJoyVibration(0);
	}
}
