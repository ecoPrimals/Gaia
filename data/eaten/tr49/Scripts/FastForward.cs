using Godot;

public partial class FastForward : Node
{
	private const float FastForwardTimeScale = 10f;

	public override void _Process(double delta)
	{
		if (Input.IsActionPressed("fast_forward") || MobileFastForwardButton.isPressed)
		{
			Engine.TimeScale = 10.0;
		}
		else
		{
			Engine.TimeScale = 1.0;
		}
	}
}
