using Godot;

public partial class MobileFastForwardButton : Button
{
	[Export(PropertyHint.None, "")]
	public GameCamera gameCamera;

	public static bool isPressed;

	public override void _Ready()
	{
		base._Ready();
		if (!Platform.isMobile)
		{
			QueueFree();
			return;
		}
		base.Modulate = new Color(1f, 1f, 1f, 0f);
		base.Visible = false;
	}

	public override void _Process(double delta)
	{
		isPressed = IsPressed();
		bool isCloseEnoughToInteract = gameCamera.isCloseEnoughToInteract;
		float num = Mathf.MoveToward(base.Modulate.A, isCloseEnoughToInteract ? 1f : 0f, (float)delta);
		base.Modulate = new Color(1f, 1f, 1f, num);
		base.Visible = num > 0f;
	}
}
