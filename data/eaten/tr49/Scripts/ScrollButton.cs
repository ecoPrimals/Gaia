using Godot;

public partial class ScrollButton : Node3D
{
	[Signal]
	public delegate void PressingEventHandler();

	[Export(PropertyHint.None, "")]
	private Area3D area3D;

	[Export(PropertyHint.None, "")]
	private Sprite3D sprite;

	[Export(PropertyHint.None, "")]
	private Texture2D normal;

	[Export(PropertyHint.None, "")]
	private Texture2D pressed;

	[Export(PropertyHint.None, "")]
	private Texture2D lit;

	[Export(PropertyHint.None, "")]
	private Texture2D litPressed;

	[Export(PropertyHint.None, "")]
	private MachineAudio machineAudio;

	private bool pressing;

	private float timeToVisualRelease;

	private bool _visuallyPressing;

	private bool _disabled;

	public bool visuallyPressing
	{
		get
		{
			return _visuallyPressing;
		}
		set
		{
			_visuallyPressing = value;
			if (_visuallyPressing)
			{
				UpdateTexture();
				timeToVisualRelease = 0f;
			}
			else
			{
				timeToVisualRelease = 0.2f;
			}
		}
	}

	public bool disabled
	{
		get
		{
			return _disabled;
		}
		set
		{
			_disabled = value;
			UpdateTexture();
		}
	}

	public override void _Ready()
	{
		area3D.InputEvent += delegate(Node camera, InputEvent @event, Vector3 eventPosition, Vector3 normal, long shapeIdx)
		{
			OnClick(@event);
		};
	}

	public override void _Process(double delta)
	{
		if (pressing && !Input.IsMouseButtonPressed(MouseButton.Left))
		{
			pressing = false;
			machineAudio.ScrollButtonPressed(down: false);
		}
		if (pressing)
		{
			EmitSignal(SignalName.Pressing);
		}
		if (timeToVisualRelease > 0f)
		{
			timeToVisualRelease -= (float)delta;
			if (timeToVisualRelease <= 0f)
			{
				UpdateTexture();
				timeToVisualRelease = 0f;
			}
		}
	}

	private void UpdateTexture()
	{
		if (visuallyPressing)
		{
			sprite.Texture = (disabled ? pressed : litPressed);
		}
		else
		{
			sprite.Texture = (disabled ? normal : lit);
		}
	}

	private void OnClick(InputEvent @event)
	{
		if (@event is InputEventMouseButton inputEventMouseButton && inputEventMouseButton.ButtonIndex == MouseButton.Left && inputEventMouseButton.Pressed && !pressing)
		{
			pressing = true;
			machineAudio.ScrollButtonPressed(down: true);
		}
	}
}
