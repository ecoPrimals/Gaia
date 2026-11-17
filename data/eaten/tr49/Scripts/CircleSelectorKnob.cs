using Godot;

public partial class CircleSelectorKnob : Node3D
{
	[Signal]
	public delegate void DraggingStartedEventHandler();

	[Export(PropertyHint.None, "")]
	private Area3D area3D;

	public bool canInteract = true;

	private Camera3D cachedCamera;

	public bool dragging { get; private set; }

	public Vector2 draggingTargetPositionXY { get; private set; } = Vector2.Zero;

	public override void _Ready()
	{
		area3D.InputEvent += OnAreaInputEvent;
	}

	private void OnAreaInputEvent(Node camera, InputEvent @event, Vector3 eventPosition, Vector3 normal, long shapeIdx)
	{
		cachedCamera = camera as Camera3D;
		if (canInteract && @event is InputEventMouseButton inputEventMouseButton && inputEventMouseButton.ButtonIndex == MouseButton.Left && inputEventMouseButton.Pressed)
		{
			this.SetInputAsHandled(@event);
			dragging = true;
			draggingTargetPositionXY = MousePosition3D.GetMousePositionOnXYPlane(cachedCamera, this);
			EmitSignal(SignalName.DraggingStarted);
		}
	}

	public override void _Process(double delta)
	{
		if (dragging)
		{
			if (!canInteract || !Input.IsMouseButtonPressed(MouseButton.Left))
			{
				dragging = false;
			}
			else
			{
				UpdateDrag();
			}
		}
	}

	private void UpdateDrag()
	{
		draggingTargetPositionXY = MousePosition3D.GetMousePositionOnXYPlane(cachedCamera, this);
	}
}
