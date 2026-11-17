using System;
using Godot;

public partial class CircleSelector : Node3D
{
	[Signal]
	public delegate void ChangedCharacterEventHandler(int value);

	[Signal]
	public delegate void CharacterDirectlyClickedEventHandler(int value);

	public enum Mode
	{
		Off,
		Letters,
		Numbers
	}

	[Export(PropertyHint.None, "")]
	public CircleSelectorKnob knob;

	[Export(PropertyHint.None, "")]
	private PackedScene singleCharacterPackedScene;

	[Export(PropertyHint.None, "")]
	private MachineAudio machineAudio;

	[Export(PropertyHint.None, "")]
	private float knobRadius = 0.26f;

	[Export(PropertyHint.None, "")]
	private float petalsRadius = 0.25f;

	[Export(PropertyHint.None, "")]
	private float irisHideRotationNorm = 0.15f;

	[Export(PropertyHint.None, "")]
	private float irisHideScale = 1.15f;

	[Export(PropertyHint.None, "")]
	private float irisSpringInTime = 0.6f;

	[Export(PropertyHint.None, "")]
	private float irisSlideOutTime = 0.3f;

	public bool canInteract = true;

	private Node3D letterRing;

	private Node3D numberRing;

	public int currentIndex;

	public int flipperIndex = -1;

	private bool wasAPressedLastFrame;

	private bool wasBPressedLastFrame;

	private float targetSnappedAngle;

	private Mode _mode;

	private Tween _modeTween;

	private Vector2 leftStick = Vector2.Zero;

	private int previousFlipperIndex = -1;

	private bool hasMovedSinceLastFlipperChange;

	private float stickAngleAtLastCharacterChange = float.MaxValue;

	private float stickAngleLastFrame = -1000f;

	private float stickAngle = float.MaxValue;

	private float stickContinuousRoll;

	private int lastEmittedIndex = -1;

	public bool isLeftStickActive => leftStick.Length() > 0.5f;

	public float currentKnobAnglePos { get; private set; }

	public Mode mode
	{
		get
		{
			return _mode;
		}
		set
		{
			if (_mode == value)
			{
				return;
			}
			_mode = value;
			if (_modeTween != null)
			{
				_modeTween.Kill();
				_modeTween = null;
			}
			if (_mode == Mode.Letters && !letterRing.Visible)
			{
				letterRing.Show();
			}
			if (_mode == Mode.Numbers && !numberRing.Visible)
			{
				numberRing.Show();
			}
			_modeTween = CreateTween().SetParallel();
			Tween tween = CreateTween().SetParallel();
			bool num = _mode == Mode.Letters;
			float num2 = (num ? irisSpringInTime : irisSlideOutTime);
			if (num)
			{
				tween.SetTrans(Tween.TransitionType.Spring);
				tween.SetEase(Tween.EaseType.Out);
			}
			else
			{
				tween.SetEase(Tween.EaseType.InOut);
			}
			tween.TweenProperty(letterRing, "rotation:z", (_mode == Mode.Letters) ? 0f : ((0f - irisHideRotationNorm) * (float)Math.PI), num2);
			tween.TweenProperty(letterRing, "scale:x", (_mode == Mode.Letters) ? 1f : irisHideScale, num2);
			tween.TweenProperty(letterRing, "scale:y", (_mode == Mode.Letters) ? 1f : irisHideScale, num2);
			if (!num)
			{
				tween.Finished += delegate
				{
					letterRing.Hide();
				};
			}
			_modeTween.TweenSubtween(tween);
			Tween tween2 = CreateTween().SetParallel();
			bool num3 = _mode == Mode.Numbers;
			float num4 = (num3 ? irisSpringInTime : irisSlideOutTime);
			if (num3)
			{
				tween2.SetTrans(Tween.TransitionType.Spring);
				tween2.SetEase(Tween.EaseType.Out);
			}
			else
			{
				tween2.SetEase(Tween.EaseType.InOut);
			}
			tween2.TweenProperty(numberRing, "rotation:z", (_mode == Mode.Numbers) ? 0f : ((0f - irisHideRotationNorm) * (float)Math.PI), num4);
			tween2.TweenProperty(numberRing, "scale:x", (_mode == Mode.Numbers) ? 1f : irisHideScale, num4);
			tween2.TweenProperty(numberRing, "scale:y", (_mode == Mode.Numbers) ? 1f : irisHideScale, num4);
			if (!num3)
			{
				tween2.Finished += delegate
				{
					numberRing.Hide();
				};
			}
			_modeTween.TweenSubtween(tween2);
			_modeTween.Finished += delegate
			{
				_modeTween = null;
			};
		}
	}

	public override void _Ready()
	{
		letterRing = GetNode<Node3D>("LetterRing");
		for (int i = 0; i < 26; i++)
		{
			Node3D node3D = singleCharacterPackedScene.Instantiate<Node3D>(PackedScene.GenEditState.Disabled);
			char value = (char)(65 + i);
			node3D.GetNode<Sprite3D>("FullGraphic").Texture = GD.Load<Texture2D>($"res://Images/Petals/Single Petal {value}.png");
			int letterIdx = i;
			node3D.GetNode<Area3D>("Area3D").InputEvent += delegate(Node camera, InputEvent @event, Vector3 eventPosition, Vector3 normal, long shapeIdx)
			{
				OnCharacterInputEvent(letterIdx, @event);
			};
			float num = (float)(-i) * ((float)Math.PI * 2f) / 26f;
			node3D.Position = new Vector3(Mathf.Cos(num + (float)Math.PI / 2f), Mathf.Sin(num + (float)Math.PI / 2f), 0f) * petalsRadius;
			node3D.Rotation = new Vector3(0f, 0f, num);
			letterRing.AddChild(node3D, forceReadableName: false, InternalMode.Disabled);
		}
		numberRing = GetNode<Node3D>("NumberRing");
		for (int num2 = 0; num2 < 10; num2++)
		{
			Node3D node3D2 = singleCharacterPackedScene.Instantiate<Node3D>(PackedScene.GenEditState.Disabled);
			node3D2.GetNode<Sprite3D>("FullGraphic").Texture = GD.Load<Texture2D>($"res://Images/Petals/Single Petal {num2}.png");
			int numberIdx = num2;
			node3D2.GetNode<Area3D>("Area3D").InputEvent += delegate(Node camera, InputEvent @event, Vector3 eventPosition, Vector3 normal, long shapeIdx)
			{
				OnCharacterInputEvent(numberIdx, @event);
			};
			float num3 = (float)(-num2) * ((float)Math.PI * 2f) / 10f;
			node3D2.Position = new Vector3(Mathf.Cos(num3 + (float)Math.PI / 2f), Mathf.Sin(num3 + (float)Math.PI / 2f), 0f) * petalsRadius;
			node3D2.Rotation = new Vector3(0f, 0f, num3);
			numberRing.AddChild(node3D2, forceReadableName: false, InternalMode.Disabled);
		}
		letterRing.Scale = new Vector3(irisHideScale, irisHideScale, 1f);
		letterRing.Hide();
		numberRing.Scale = new Vector3(irisHideScale, irisHideScale, 1f);
		numberRing.Hide();
	}

	private void OnCharacterInputEvent(int index, InputEvent @event)
	{
		if (canInteract && @event is InputEventMouseButton inputEventMouseButton && inputEventMouseButton.ButtonIndex == MouseButton.Left && inputEventMouseButton.Pressed && (!Platform.isSteamDeck || inputEventMouseButton.Device == 0))
		{
			this.SetInputAsHandled(@event);
			currentIndex = index;
			lastEmittedIndex = currentIndex;
			machineAudio.CircleSelectorPressedCharacter();
			DarkenCurrentCharacter();
			EmitSignal(SignalName.ChangedCharacter, currentIndex);
			EmitSignal(SignalName.CharacterDirectlyClicked, currentIndex);
		}
	}

	public void DarkenCurrentCharacter()
	{
		Node3D node3D = ((mode == Mode.Letters) ? letterRing : numberRing);
		if (currentIndex >= 0 && currentIndex < node3D.GetChildCount())
		{
			Node child = node3D.GetChild(currentIndex);
			Sprite3D characterSprite = child.GetNode<Sprite3D>("FullGraphic");
			characterSprite.Modulate = new Color(0.5f, 0.5f, 0.5f);
			GetTree().CreateTimer(0.20000000298023224).Timeout += delegate
			{
				characterSprite.Modulate = new Color(1f, 1f, 1f);
			};
		}
	}

	public override void _Input(InputEvent @event)
	{
		if (canInteract && mode != Mode.Off && @event is InputEventJoypadMotion inputEventJoypadMotion && (inputEventJoypadMotion.Axis == JoyAxis.LeftX || inputEventJoypadMotion.Axis == JoyAxis.LeftY))
		{
			if (inputEventJoypadMotion.Axis == JoyAxis.LeftX)
			{
				leftStick.X = inputEventJoypadMotion.AxisValue;
			}
			if (inputEventJoypadMotion.Axis == JoyAxis.LeftY)
			{
				leftStick.Y = inputEventJoypadMotion.AxisValue;
			}
			this.SetInputAsHandled(@event);
		}
	}

	public override void _Process(double delta)
	{
		if (flipperIndex != previousFlipperIndex)
		{
			hasMovedSinceLastFlipperChange = false;
			stickAngleAtLastCharacterChange = stickAngle;
			previousFlipperIndex = flipperIndex;
		}
		int num = ((mode == Mode.Letters) ? 26 : 10);
		if (mode == Mode.Off || !canInteract)
		{
			leftStick = Vector2.Zero;
		}
		if (leftStick.Length() > 0.5f)
		{
			stickAngle = Mathf.Atan2(leftStick.Y, leftStick.X) - (float)Math.PI / 2f;
			if (stickAngle < 0f)
			{
				stickAngle += (float)Math.PI * 2f;
			}
			int num2 = Mathf.RoundToInt((stickAngle / ((float)Math.PI * 2f) + 0.5f) * (float)num) % num;
			if (num2 != currentIndex)
			{
				currentIndex = num2;
			}
			if (!hasMovedSinceLastFlipperChange && Mathf.Abs(Mathf.AngleDifference(stickAngleAtLastCharacterChange, stickAngle)) > Mathf.DegToRad(13.846154f))
			{
				hasMovedSinceLastFlipperChange = true;
			}
			if (!StoryController.instance.tutorialGamepadThumbstickComplete)
			{
				if (stickAngleLastFrame != -1000f)
				{
					float s = Mathf.RadToDeg(Mathf.AngleDifference(stickAngleLastFrame, stickAngle));
					stickContinuousRoll += Mathf.Abs(s);
					if (stickContinuousRoll > 20f)
					{
						StoryController.instance.tutorialGamepadThumbstickDegreesRolled += stickContinuousRoll;
						stickContinuousRoll = 0f;
					}
				}
				stickAngleLastFrame = stickAngle;
			}
			if (lastEmittedIndex != currentIndex && hasMovedSinceLastFlipperChange)
			{
				lastEmittedIndex = currentIndex;
				machineAudio.CircleSelectorChangedCharacter();
				EmitSignal(SignalName.ChangedCharacter, currentIndex);
			}
		}
		else
		{
			hasMovedSinceLastFlipperChange = false;
			lastEmittedIndex = -1;
			stickAngleLastFrame = -1000f;
			stickContinuousRoll = 0f;
		}
		if (knob.dragging)
		{
			stickAngle = float.MaxValue;
			Vector2 draggingTargetPositionXY = knob.draggingTargetPositionXY;
			int num3 = Mathf.RoundToInt((Mathf.Atan2(0f - draggingTargetPositionXY.Y, draggingTargetPositionXY.X) + (float)Math.PI / 2f + (float)Math.PI * 2f) / ((float)Math.PI * 2f) * (float)num) % num;
			if (num3 != currentIndex)
			{
				currentIndex = num3;
				lastEmittedIndex = currentIndex;
				machineAudio.CircleSelectorChangedCharacter();
				EmitSignal(SignalName.ChangedCharacter, currentIndex);
			}
		}
		if (mode != Mode.Off)
		{
			targetSnappedAngle = (float)currentIndex * ((float)Math.PI * 2f) / (float)num;
		}
		float num4 = currentKnobAnglePos;
		currentKnobAnglePos = Mathf.Atan2(0f - knob.Position.Y, knob.Position.X) + (float)Math.PI / 2f;
		float lerping = (knob.dragging ? 0.8f : 0.4f);
		float to = Mathf.LerpAngle(currentKnobAnglePos, targetSnappedAngle, TimeX.Lerping(lerping, (float)delta));
		float value = Mathf.AngleDifference(currentKnobAnglePos, to);
		float num5 = 10f * (float)delta;
		float num6 = Mathf.Clamp(value, 0f - num5, num5);
		float num7 = currentKnobAnglePos + num6;
		knob.Position = new Vector3(knobRadius * Mathf.Cos(num7 - (float)Math.PI / 2f), knobRadius * (0f - Mathf.Sin(num7 - (float)Math.PI / 2f)), knob.Position.Z);
		knob.Rotation = new Vector3(0f, 0f, 0f - num7);
		float circleSelectorKnobSpeed = ((Mathf.Abs((float)delta) > 0.001f) ? (Mathf.Abs(currentKnobAnglePos - num4) / (float)delta) : 0f);
		machineAudio.UpdateCircleSelectorKnobAudioLoop(circleSelectorKnobSpeed);
	}
}
