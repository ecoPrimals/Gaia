using Godot;

public partial class PuzzlePiece : BaseButton
{
	[Signal]
	public delegate void PickedUpEventHandler(PuzzlePiece puzzlePiece);

	[Signal]
	public delegate void MovedEventHandler(PuzzlePiece puzzlePiece);

	[Signal]
	public delegate void DroppedEventHandler(PuzzlePiece puzzlePiece);

	[Signal]
	public delegate void CancelledDragEventHandler(PuzzlePiece puzzlePiece);

	public enum State
	{
		Normal,
		Hovered,
		Dragging
	}

	[Export(PropertyHint.None, "")]
	public Control mainPart;

	[Export(PropertyHint.None, "")]
	public Label codeLabel;

	[Export(PropertyHint.None, "")]
	public Control shadow;

	[Export(PropertyHint.None, "")]
	public Control outline;

	[Export(PropertyHint.None, "")]
	public Color highlightedColor;

	[Export(PropertyHint.None, "")]
	public Color gamepadFocusedOutlineColor;

	[Export(PropertyHint.None, "")]
	public int gamepadFocussedOutlineBorderWidth = 4;

	[Export(PropertyHint.None, "")]
	public float gamepadDragSpeed = 600f;

	[Export(PropertyHint.None, "")]
	public float dropPosMagneticForce = 10f;

	[Export(PropertyHint.None, "")]
	public float xPosThresholdForMagneticDropForce = 400f;

	[Export(PropertyHint.None, "")]
	public float wibbleSpeed = 15f;

	[Export(PropertyHint.None, "")]
	public float wibbleAmount = 0.03f;

	[Export(PropertyHint.None, "")]
	public AudioStream pickUpSound;

	[Export(PropertyHint.None, "")]
	public AudioStream dropSound;

	public MainCodesPage mainCodesPage;

	public string code;

	private bool _highlighted;

	private bool _focused;

	public bool isTutorialPiece;

	private State _state;

	private bool dragIsWithMouse;

	private Vector2 dragGlobalMouseStartPosition;

	private Vector2 originalPreDragPositionForDragCancel;

	private Vector2 dragInitialOffset;

	private Vector2 dragOriginalPosition;

	private float originalRotation;

	private Tween hoverTween;

	private static StyleBoxFlat defaultOutlineStylebox;

	private static StyleBoxFlat gamepadFocusedOutlineStylebox;

	public bool highlighted
	{
		get
		{
			return _highlighted;
		}
		set
		{
			if (_highlighted != value)
			{
				_highlighted = value;
				if (_highlighted)
				{
					mainPart.SelfModulate = highlightedColor;
				}
			}
		}
	}

	public bool focused
	{
		get
		{
			return _focused;
		}
		set
		{
			if (_focused != value)
			{
				_focused = value;
				SetVisualState(_state, animated: true);
			}
		}
	}

	public State state
	{
		get
		{
			return _state;
		}
		private set
		{
			if (_state != value)
			{
				_state = value;
				base.Rotation = originalRotation;
				SetVisualState(_state, animated: true);
			}
		}
	}

	public override void _Ready()
	{
		base.MouseEntered += OnMouseEntered;
		base.MouseExited += OnMouseExited;
		originalRotation = base.Rotation;
		if (defaultOutlineStylebox == null)
		{
			defaultOutlineStylebox = outline.GetThemeStylebox("panel") as StyleBoxFlat;
			gamepadFocusedOutlineStylebox = defaultOutlineStylebox.Duplicate() as StyleBoxFlat;
			gamepadFocusedOutlineStylebox.BorderColor = gamepadFocusedOutlineColor;
			gamepadFocusedOutlineStylebox.BorderWidthTop = gamepadFocussedOutlineBorderWidth;
			gamepadFocusedOutlineStylebox.BorderWidthBottom = gamepadFocussedOutlineBorderWidth;
			gamepadFocusedOutlineStylebox.BorderWidthLeft = gamepadFocussedOutlineBorderWidth;
			gamepadFocusedOutlineStylebox.BorderWidthRight = gamepadFocussedOutlineBorderWidth;
		}
		SetVisualState(State.Normal, animated: false);
	}

	public override void _Input(InputEvent @event)
	{
		if (@event.IsActionPressed("ui_cancel") && state == State.Dragging)
		{
			this.SetInputAsHandled(@event);
			CreateTween().TweenProperty(this, "position", originalPreDragPositionForDragCancel, 0.10000000149011612);
			state = State.Normal;
			EmitSignal(SignalName.CancelledDrag, this);
		}
		if (focused && @event.IsActionPressed("ui_accept"))
		{
			this.SetInputAsHandled(@event);
			if (state == State.Normal)
			{
				PickUp(withMouse: false);
			}
			else
			{
				Drop();
			}
		}
	}

	public override void _GuiInput(InputEvent @event)
	{
		if (@event is InputEventMouseButton inputEventMouseButton && inputEventMouseButton.ButtonIndex == MouseButton.Left && inputEventMouseButton.Pressed && (!Platform.isSteamDeck || inputEventMouseButton.Device == 0))
		{
			PickUp(withMouse: true, inputEventMouseButton.GlobalPosition);
			AcceptEvent();
		}
	}

	public override void _Process(double delta)
	{
		if (state == State.Dragging)
		{
			if (dragIsWithMouse)
			{
				if (!Input.IsMouseButtonPressed(MouseButton.Left))
				{
					Drop();
				}
				else
				{
					Vector2 vector = GetViewport().GetMousePosition() + dragInitialOffset - 0.5f * base.Size;
					base.Position = (GetParent() as Control).GetGlobalTransformWithCanvas().AffineInverse() * vector;
				}
			}
			else
			{
				Vector2 vector2 = InputX.GetLeftStick();
				float x = (Input.IsActionPressed("ui_right") ? 1f : 0f) + (Input.IsActionPressed("ui_left") ? (-1f) : 0f);
				float y = (Input.IsActionPressed("ui_up") ? (-1f) : 0f) + (Input.IsActionPressed("ui_down") ? 1f : 0f);
				Vector2 vector3 = new Vector2(x, y);
				if (vector3.Length() > 0.15f)
				{
					vector2 = vector3;
				}
				if (vector2.Length() > 0.15f)
				{
					base.Position += vector2 * gamepadDragSpeed * (float)delta;
					EmitSignal(SignalName.Moved, this);
				}
				else
				{
					Vector2 vector4 = 0.5f * base.Size;
					Vector2 vector5 = base.Position + vector4;
					if (mainCodesPage.TryGetNearestDroppableCentrePosition(this, out var nearestDroppableCentrePosition) && base.Position.X > xPosThresholdForMagneticDropForce)
					{
						float num = dropPosMagneticForce * (nearestDroppableCentrePosition - vector5).Length();
						Vector2 vector6 = vector5.MoveToward(nearestDroppableCentrePosition, num * (float)delta);
						base.Position = vector6 - vector4;
					}
				}
			}
			if (dragOriginalPosition.DistanceTo(base.Position) > 1f)
			{
				EmitSignal(SignalName.Moved, this);
			}
		}
		if (state == State.Dragging || isTutorialPiece)
		{
			base.Rotation = originalRotation + Mathf.Sin((float)Time.GetTicksMsec() * 0.001f * wibbleSpeed) * wibbleAmount;
		}
		else
		{
			base.Rotation = originalRotation;
		}
	}

	private void Drop()
	{
		state = State.Normal;
		PlaySFX(dropSound);
		Haptic.instance.Tap();
		EmitSignal(SignalName.Dropped, this);
	}

	public void LoseFocusAndCancelDragIfNecessary()
	{
		focused = false;
		if (state == State.Dragging)
		{
			state = State.Normal;
			EmitSignal(SignalName.CancelledDrag, this);
		}
	}

	public void PickUp(bool withMouse, Vector2? globalClickPosition = null)
	{
		state = State.Dragging;
		dragIsWithMouse = withMouse;
		if (withMouse)
		{
			dragGlobalMouseStartPosition = globalClickPosition ?? GetViewport().GetMousePosition();
		}
		Vector2 vector = GetGlobalPosition() + 0.5f * base.Size;
		originalPreDragPositionForDragCancel = base.Position;
		dragInitialOffset = vector - dragGlobalMouseStartPosition;
		dragOriginalPosition = base.Position;
		focused = true;
		PlaySFX(pickUpSound);
		Haptic.instance.LightStep();
		EmitSignal(SignalName.PickedUp, this);
	}

	private void PlaySFX(AudioStream stream)
	{
		AudioStreamPlayer audioStreamPlayer = new AudioStreamPlayer();
		audioStreamPlayer.Bus = "SFX";
		audioStreamPlayer.Stream = stream;
		audioStreamPlayer.VolumeDb = AudioX.VolumeDbFromNormalized(0.5f);
		AddChild(audioStreamPlayer, forceReadableName: false, InternalMode.Disabled);
		audioStreamPlayer.Play();
	}

	private void SetVisualState(State newState, bool animated)
	{
		if (hoverTween != null)
		{
			hoverTween.Kill();
			hoverTween = null;
		}
		float num = ((newState == State.Normal) ? 0.2f : 0.05f);
		float num2 = 0.25f;
		float num3 = -2f;
		float num4 = 0f;
		switch (newState)
		{
		case State.Hovered:
			num2 = 0.8f;
			num3 = 2f;
			num4 = -4f;
			break;
		case State.Dragging:
			num2 = 1f;
			num3 = 2f;
			num4 = -8f;
			break;
		}
		if (animated)
		{
			hoverTween = CreateTween().SetParallel();
			hoverTween.SetTrans(Tween.TransitionType.Cubic);
			hoverTween.SetEase(Tween.EaseType.InOut);
			hoverTween.TweenProperty(shadow, "modulate:a", num2, num);
			hoverTween.TweenProperty(shadow, "position:y", num3, num);
			hoverTween.TweenProperty(mainPart, "position:y", num4, num);
		}
		else
		{
			shadow.Modulate = new Color(1f, 1f, 1f, num2);
			shadow.Position = new Vector2(shadow.Position.X, num3);
			mainPart.Position = new Vector2(mainPart.Position.X, num4);
		}
		if (newState == State.Dragging || newState == State.Hovered || focused)
		{
			base.ZIndex = 5;
		}
		else
		{
			base.ZIndex = 0;
		}
		if (focused)
		{
			outline.AddThemeStyleboxOverride("panel", gamepadFocusedOutlineStylebox);
		}
		else
		{
			outline.AddThemeStyleboxOverride("panel", defaultOutlineStylebox);
		}
	}

	private void OnMouseEntered()
	{
		if (state == State.Normal && !Input.IsMouseButtonPressed(MouseButton.Left))
		{
			state = State.Hovered;
		}
	}

	private void OnMouseExited()
	{
		if (state == State.Hovered)
		{
			state = State.Normal;
		}
	}
}
