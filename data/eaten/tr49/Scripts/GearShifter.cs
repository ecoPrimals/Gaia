using Godot;

public partial class GearShifter : Node3D
{
	[Signal]
	public delegate void DraggedToGearEventHandler(int gearNumber);

	private enum SlideSection
	{
		Home,
		HomeToCorner,
		MainSlide,
		IntoGear,
		InGear
	}

	[Export(PropertyHint.None, "")]
	private Node3D gearStick;

	[Export(PropertyHint.None, "")]
	private Node3D[] positionAnchors;

	[Export(PropertyHint.None, "")]
	private Area3D area3D;

	[Export(PropertyHint.None, "")]
	private float smoothTime = 0.1f;

	[Export(PropertyHint.None, "")]
	private float maxSpeed = 10f;

	[Export(PropertyHint.None, "")]
	private float sinkSpeed = 0.1f;

	[Export(PropertyHint.None, "")]
	private float sinkXThreshold = 0.01f;

	[Export(PropertyHint.None, "")]
	private float dragSnapThreshold = 0.01f;

	[Export(PropertyHint.None, "")]
	private MachineAudio machineAudio;

	public bool canInteract = true;

	private float[] linearDistancesOfGears;

	private int targetGearNumber;

	private int lastSnappedGearNumber;

	private float horizontalSlideY;

	private float currentLinearDistance;

	private float currentSpeed;

	private bool dragging;

	private SlideSection currentSlideSection;

	private Vector2 dragMousePosStart;

	private Vector3 dragInitialGearStickPos;

	private Camera3D cachedCamera;

	public override void _EnterTree()
	{
		linearDistancesOfGears = new float[positionAnchors.Length];
		linearDistancesOfGears[0] = 0f;
		Vector2 vector = new Vector2(positionAnchors[0].Position.X, horizontalSlideY);
		float num = positionAnchors[0].Position.Y - vector.Y;
		float num2 = positionAnchors[1].Position.X - vector.X;
		linearDistancesOfGears[1] = num + num2;
		linearDistancesOfGears[2] = linearDistancesOfGears[1] + (positionAnchors[2].Position.X - positionAnchors[1].Position.X);
		linearDistancesOfGears[3] = linearDistancesOfGears[2] + (positionAnchors[3].Position.X - positionAnchors[2].Position.X);
		linearDistancesOfGears[4] = linearDistancesOfGears[3] + (positionAnchors[4].Position.X - positionAnchors[3].Position.X);
	}

	public override void _Ready()
	{
		horizontalSlideY = gearStick.Position.Y;
		gearStick.Position = GetPosition(0);
		targetGearNumber = 0;
		currentLinearDistance = 0f;
		lastSnappedGearNumber = 0;
		area3D.InputEvent += delegate(Node camera, InputEvent @event, Vector3 eventPosition, Vector3 normal, long shapeIdx)
		{
			OnClick(camera, @event);
		};
	}

	private void OnClick(Node camera, InputEvent @event)
	{
		cachedCamera = camera as Camera3D;
		if (canInteract && @event is InputEventMouseButton inputEventMouseButton && inputEventMouseButton.ButtonIndex == MouseButton.Left && inputEventMouseButton.Pressed && !dragging)
		{
			dragging = true;
			dragMousePosStart = MousePosition3D.GetMousePositionOnXYPlane(cachedCamera, gearStick);
			dragInitialGearStickPos = gearStick.Position;
			machineAudio.GearSlideBegan();
		}
	}

	public override void _Process(double delta)
	{
		SlideSection slideSection = currentSlideSection;
		if (dragging && (!canInteract || !Input.IsMouseButtonPressed(MouseButton.Left)))
		{
			dragging = false;
			SignalDraggedToGearIfNecessary();
		}
		if (dragging)
		{
			UpdateDrag((float)delta);
		}
		else
		{
			UpdatePositionFromTargetGearNumber((float)delta);
		}
		machineAudio.UpdateGearSlideAudioLoop(currentSpeed);
		if (slideSection != currentSlideSection)
		{
			if ((slideSection == SlideSection.HomeToCorner && currentSlideSection == SlideSection.MainSlide) || (slideSection == SlideSection.MainSlide && currentSlideSection == SlideSection.HomeToCorner))
			{
				machineAudio.GearSlidePassedCorner();
			}
			else if (currentSlideSection == SlideSection.InGear)
			{
				machineAudio.GearSlideArrivedInGear();
			}
			else if (currentSlideSection == SlideSection.Home)
			{
				machineAudio.GearSlideReturnedToHomePosition();
			}
		}
	}

	private void SignalDraggedToGearIfNecessary()
	{
		if (lastSnappedGearNumber != targetGearNumber)
		{
			lastSnappedGearNumber = targetGearNumber;
			EmitSignal(SignalName.DraggedToGear, lastSnappedGearNumber);
		}
	}

	private void UpdateDrag(float delta)
	{
		Vector2 vector = MousePosition3D.GetMousePositionOnXYPlane(cachedCamera, gearStick) - dragMousePosStart;
		Vector3 vector2 = dragInitialGearStickPos + new Vector3(vector.X, vector.Y, 0f);
		float num = Mathf.Clamp(vector2.X, positionAnchors[0].Position.X, positionAnchors[positionAnchors.Length - 1].Position.X);
		int num2 = -1;
		float num3 = float.MaxValue;
		for (int i = 1; i < positionAnchors.Length; i++)
		{
			float num4 = Mathf.Abs(num - positionAnchors[i].Position.X);
			if (num4 < num3)
			{
				num3 = num4;
				num2 = i;
			}
		}
		targetGearNumber = num2;
		if (num3 < dragSnapThreshold)
		{
			UpdatePositionFromTargetGearNumber(delta);
			SignalDraggedToGearIfNecessary();
			return;
		}
		float targetLinearDistance;
		if (num < positionAnchors[0].Position.X + dragSnapThreshold)
		{
			float y = positionAnchors[0].Position.Y;
			float min = horizontalSlideY;
			targetLinearDistance = Mathf.Abs(Mathf.Clamp(vector2.Y, min, y) - y);
			targetGearNumber = 0;
		}
		else
		{
			Vector2 vector3 = new Vector2(positionAnchors[0].Position.X, horizontalSlideY);
			float num5 = num - vector3.X;
			targetLinearDistance = Mathf.Abs(positionAnchors[0].Position.Y - vector3.Y) + num5;
		}
		UpdatePositionFromLinearDistance(targetLinearDistance, delta);
	}

	private void UpdatePositionFromTargetGearNumber(float delta)
	{
		float targetLinearDistance = linearDistancesOfGears[targetGearNumber];
		UpdatePositionFromLinearDistance(targetLinearDistance, delta);
	}

	private void UpdatePositionFromLinearDistance(float targetLinearDistance, float delta)
	{
		float num = currentLinearDistance;
		currentLinearDistance = MathX.SmoothDamp(currentLinearDistance, targetLinearDistance, ref currentSpeed, smoothTime, maxSpeed, delta);
		currentLinearDistance = Mathf.Clamp(currentLinearDistance, 0f, linearDistancesOfGears[linearDistancesOfGears.Length - 1]);
		int num2 = linearDistancesOfGears.Length - 2;
		for (int i = 0; i < linearDistancesOfGears.Length - 1; i++)
		{
			if (currentLinearDistance >= linearDistancesOfGears[i] && currentLinearDistance <= linearDistancesOfGears[i + 1])
			{
				num2 = i;
				break;
			}
		}
		float num3 = Mathf.InverseLerp(linearDistancesOfGears[num2], linearDistancesOfGears[num2 + 1], currentLinearDistance);
		for (int j = 0; j < linearDistancesOfGears.Length; j++)
		{
			if ((num < linearDistancesOfGears[j] && currentLinearDistance >= linearDistancesOfGears[j]) || (num > linearDistancesOfGears[j] && currentLinearDistance <= linearDistancesOfGears[j]))
			{
				machineAudio.GearSlidePassedGearNotch();
			}
		}
		Vector3 position = gearStick.Position;
		if (num2 == 0)
		{
			Vector3 to = new Vector3(positionAnchors[0].Position.X, horizontalSlideY, position.Z);
			if (num3 < 0.6f)
			{
				float weight = Mathf.InverseLerp(0f, 0.6f, num3);
				position = positionAnchors[0].Position.Lerp(to, weight);
				currentSlideSection = ((!(currentLinearDistance < 0.01f)) ? SlideSection.HomeToCorner : SlideSection.Home);
			}
			else
			{
				float weight2 = Mathf.InverseLerp(0.6f, 1f, num3);
				position = to.Lerp(positionAnchors[num2 + 1].Position, weight2);
				position.Y = horizontalSlideY;
				currentSlideSection = SlideSection.MainSlide;
			}
		}
		else
		{
			Vector3 position2 = positionAnchors[num2].Position;
			Vector3 position3 = positionAnchors[num2 + 1].Position;
			position = position2.Lerp(position3, num3);
			position.Y = horizontalSlideY;
			currentSlideSection = SlideSection.MainSlide;
		}
		if (num2 == 0 && num3 < 0.6f)
		{
			gearStick.Position = position;
			return;
		}
		int num4 = ((!(num3 < 0.5f)) ? (num2 + 1) : num2);
		float x = positionAnchors[num4].Position.X;
		if (num4 == targetGearNumber && Mathf.Abs(position.X - x) < sinkXThreshold)
		{
			float y = positionAnchors[num4].Position.Y;
			float num5 = Mathf.MoveToward(gearStick.Position.Y, y, sinkSpeed * delta);
			gearStick.Position = new Vector3(position.X, num5, gearStick.Position.Z);
			currentSpeed = 0f;
			bool flag = Mathf.Abs(num5 - y) < 0.01f;
			currentSlideSection = (flag ? SlideSection.InGear : SlideSection.IntoGear);
		}
		else
		{
			position.Y = horizontalSlideY;
			gearStick.Position = position;
		}
	}

	public void SetGear(int positionIdx, bool immediate = false)
	{
		int num = targetGearNumber;
		targetGearNumber = positionIdx;
		if (immediate)
		{
			gearStick.Position = GetPosition(positionIdx);
			currentLinearDistance = linearDistancesOfGears[positionIdx];
		}
		else if (num != targetGearNumber)
		{
			machineAudio.GearSlideBegan();
		}
	}

	private Vector3 GetPosition(int positionIdx)
	{
		Vector3 position = gearStick.Position;
		if (positionIdx < 0 || positionIdx >= positionAnchors.Length)
		{
			GD.PushError($"Unknown position number: {positionIdx}");
			return position;
		}
		Vector3 position2 = positionAnchors[positionIdx].Position;
		return new Vector3(position2.X, position2.Y, position.Z);
	}
}
