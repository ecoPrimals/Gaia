using Godot;

public partial class Knob : BaseButton
{
	[Signal]
	public delegate void ValueChangedEventHandler(int value);

	[Export(PropertyHint.None, "")]
	public int valueCount = 10;

	[Export(PropertyHint.None, "")]
	public bool hasFocusAtStart;

	[Export(PropertyHint.None, "")]
	public float rotationSpeed = 10f;

	public bool manipulating;

	public bool dragging;

	private int _currentValue;

	private float rotation;

	private Vector2 dragGlobalMouseStartPosition;

	private float dragRotationStart;

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
				rotation = (float)value * 360f / (float)(valueCount - 1);
				UpdateRotation();
			}
		}
	}

	public override void _Ready()
	{
		if (hasFocusAtStart)
		{
			GrabFocus();
		}
		UpdateRotation();
	}

	private void UpdateRotation()
	{
		base.RotationDegrees = rotation;
		int num = Mathf.RoundToInt(rotation / 360f * (float)(valueCount - 1));
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
					rotation += vector.X * rotationSpeed;
					rotation = Mathf.PosMod(rotation, 360f);
					UpdateRotation();
				}
			}
		}
		if (ev is InputEventMouseButton inputEventMouseButton)
		{
			if (inputEventMouseButton.ButtonIndex == MouseButton.Left && inputEventMouseButton.Pressed)
			{
				dragging = true;
				dragGlobalMouseStartPosition = GetViewport().GetMousePosition();
				dragRotationStart = rotation;
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
		rotation = Mathf.PosMod(dragRotationStart + vector.X, 360f);
		UpdateRotation();
	}
}
