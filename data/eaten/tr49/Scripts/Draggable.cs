using Godot;

public partial class Draggable : Control
{
	[Export(PropertyHint.None, "")]
	public bool dragEnabled = true;

	[Export(PropertyHint.None, "")]
	public ScrollContainer scrollContainer;

	[Export(PropertyHint.None, "")]
	private float dragMomentumDamping = 0.9f;

	[Export(PropertyHint.None, "")]
	private float dragMomentumDeadSpeed = 0.1f;

	private float dragStartMouseY;

	private float dragStartScrollY;

	private bool dragging;

	private float dragSpeed;

	private float lastMouseY = -1f;

	public override void _GuiInput(InputEvent @event)
	{
		if (dragEnabled && @event is InputEventMouseButton inputEventMouseButton && inputEventMouseButton.ButtonIndex == MouseButton.Left && inputEventMouseButton.Pressed)
		{
			dragStartMouseY = GetViewport().GetMousePosition().Y;
			dragStartScrollY = scrollContainer.ScrollVertical;
			dragSpeed = 0f;
			lastMouseY = -1f;
			dragging = true;
		}
	}

	public override void _Process(double delta)
	{
		if (dragging && dragEnabled)
		{
			if (!Input.IsMouseButtonPressed(MouseButton.Left))
			{
				dragging = false;
			}
			else
			{
				float y = GetViewport().GetMousePosition().Y;
				float num = y - dragStartMouseY;
				if (lastMouseY != -1f)
				{
					float to = (0f - (y - lastMouseY)) / (float)delta;
					dragSpeed = Mathf.Lerp(dragSpeed, to, TimeX.Lerping(0.5f, (float)delta));
				}
				lastMouseY = y;
				scrollContainer.ScrollVertical = (int)(dragStartScrollY - num);
			}
		}
		else if (!Input.IsMouseButtonPressed(MouseButton.Left) || !dragEnabled)
		{
			dragging = false;
		}
		if (!dragging && dragSpeed != 0f)
		{
			scrollContainer.ScrollVertical += Mathf.RoundToInt(dragSpeed * (float)delta);
			dragSpeed *= TimeX.Damping(dragMomentumDamping, (float)delta);
			if (Mathf.Abs(dragSpeed) < dragMomentumDeadSpeed)
			{
				dragSpeed = 0f;
			}
		}
	}
}
