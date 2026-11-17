using Godot;

public partial class Slider : BaseButton
{
	[Signal]
	public delegate void ValueChangedEventHandler(int value);

	[Export(PropertyHint.None, "")]
	public bool hasFocusAtStart;

	[Export(PropertyHint.None, "")]
	public Path2D path;

	public bool manipulating;

	public bool dragging;

	public float speed = 10f;

	private int _currentValue;

	private float pathPosFromStartPixels;

	private Vector2 dragGlobalMouseStartPosition;

	private float dragPathPosStart;

	public int currentValue
	{
		get
		{
			return _currentValue;
		}
		set
		{
			if (_currentValue != value)
			{
				_currentValue = value;
				pathPosFromStartPixels = (float)value * path.Curve.GetBakedLength() / 9f;
				UpdatePositionFromPathPos();
			}
		}
	}

	public override void _Ready()
	{
		if (hasFocusAtStart)
		{
			GrabFocus();
		}
		pathPosFromStartPixels = path.Curve.GetClosestOffset(base.Position);
		UpdatePositionFromPathPos();
	}

	private void UpdatePositionFromPathPos()
	{
		Transform2D transform2D = path.Transform * path.Curve.SampleBakedWithRotation(pathPosFromStartPixels);
		base.Position = transform2D.Origin - base.PivotOffset;
		base.Rotation = transform2D.Rotation;
		int num = Mathf.RoundToInt(pathPosFromStartPixels / path.Curve.GetBakedLength() * 9f);
		if (_currentValue != num)
		{
			_currentValue = num;
			EmitSignal(SignalName.ValueChanged, num);
		}
	}

	public override void _Process(double delta)
	{
		if (IsPressed())
		{
			base.Modulate = new Color(0.7f, 0.7f, 0.7f);
		}
		else if (IsHovered())
		{
			base.Modulate = new Color(0.85f, 0.85f, 0.85f);
		}
		else if (HasFocus())
		{
			base.Modulate = new Color(0.95f, 0.95f, 0.5f);
		}
		else
		{
			base.Modulate = new Color(1f, 1f, 1f);
		}
		if (dragging)
		{
			UpdateDrag();
		}
	}

	public override void _GuiInput(InputEvent ev)
	{
		if (HasFocus() && ev is InputEventKey { Pressed: not false } inputEventKey)
		{
			if (inputEventKey.Keycode == Key.Enter)
			{
				manipulating = !manipulating;
				GD.Print($"Pressed Enter on {base.Name}");
				this.SetInputAsHandled(ev);
			}
			else if (manipulating && inputEventKey.Keycode == Key.Escape)
			{
				manipulating = false;
				GD.Print($"Pressed Escape on {base.Name}");
				this.SetInputAsHandled(ev);
			}
			if (manipulating)
			{
				Vector2 vector = default(Vector2);
				if (inputEventKey.Keycode == Key.Up)
				{
					vector.Y = -1f;
					this.SetInputAsHandled(ev);
				}
				else if (inputEventKey.Keycode == Key.Down)
				{
					vector.Y = 1f;
					this.SetInputAsHandled(ev);
				}
				else if (inputEventKey.Keycode == Key.Left)
				{
					vector.X = -1f;
					this.SetInputAsHandled(ev);
				}
				else if (inputEventKey.Keycode == Key.Right)
				{
					vector.X = 1f;
					this.SetInputAsHandled(ev);
				}
				if (vector != Vector2.Zero)
				{
					pathPosFromStartPixels += vector.X * speed;
					pathPosFromStartPixels = Mathf.Clamp(pathPosFromStartPixels, 0f, path.Curve.GetBakedLength());
					UpdatePositionFromPathPos();
				}
			}
		}
		if (ev is InputEventMouseButton inputEventMouseButton)
		{
			if (inputEventMouseButton.ButtonIndex == MouseButton.Left && inputEventMouseButton.Pressed)
			{
				dragging = true;
				dragGlobalMouseStartPosition = GetViewport().GetMousePosition();
				dragPathPosStart = pathPosFromStartPixels;
			}
			else if (inputEventMouseButton.ButtonIndex == MouseButton.Left && !inputEventMouseButton.Pressed)
			{
				UpdateDrag();
				dragging = false;
			}
		}
	}

	private void UpdateDrag()
	{
		Vector2 vector = GetViewport().GetMousePosition() - dragGlobalMouseStartPosition;
		pathPosFromStartPixels = Mathf.Clamp(dragPathPosStart + vector.X, 0f, path.Curve.GetBakedLength());
		UpdatePositionFromPathPos();
	}
}
