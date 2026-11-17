using System.Collections.Generic;
using System.Linq;
using Godot;

public partial class GameCamera : Camera3D
{
	[Signal]
	public delegate void MovedAcrossInteractionThresholdEventHandler(bool isCloseEnoughToInteract);

	public enum Who
	{
		None,
		MainOrInk,
		Notebook,
		Menu
	}

	public enum CameraPosition
	{
		None,
		InitialFarOut,
		In,
		Out,
		Notebook,
		SideCrossRef,
		Menu
	}

	[Export(PropertyHint.None, "")]
	public float initialZoomDuration = 6f;

	[Export(PropertyHint.None, "")]
	public float standardDuration = 2f;

	[Export(PropertyHint.None, "")]
	public Vector3 basePosition = new Vector3(0f, 0f, 0f);

	[Export(PropertyHint.None, "")]
	public Vector3 initialFarOutOffset = new Vector3(0f, 1f, 10f);

	[Export(PropertyHint.None, "")]
	public Vector3 outOffset = new Vector3(0f, 0f, 4f);

	[Export(PropertyHint.None, "")]
	public Vector3 notebookOffset = new Vector3(0f, 0f, 4f);

	[Export(PropertyHint.None, "")]
	public Vector3 sideCrossRefOffset = new Vector3(-2f, 0f, 1f);

	[Export(PropertyHint.None, "")]
	public Vector3 menuOffset = new Vector3(0f, 0f, 0f);

	[Export(PropertyHint.None, "")]
	private float closeEnoughToInteractThreshold = 0.2f;

	[Export(PropertyHint.None, "")]
	public WorldEnvironment worldEnvironment;

	[Export(PropertyHint.None, "")]
	public float desaturateModeBrightness = 1.7f;

	[Export(PropertyHint.None, "")]
	public float desaturateModeSaturation = 0.36f;

	[Export(PropertyHint.None, "")]
	public float desaturateModeContrast = 1.7f;

	[Export(PropertyHint.None, "")]
	private float openGLBrightnessMultiplier = 0.85f;

	[Export(PropertyHint.None, "")]
	private float openGLGlowIntensity = 0.26f;

	private float defaultBrightness;

	private Tween desaturateTween;

	private float defaultFov;

	private Vector2 lastScreenSizeSinceAspectResize;

	private float debugPositionNorm = -1f;

	private Vector3 targetOffset = new Vector3(0f, 0f, 0f);

	private Vector3 currentVelocity = new Vector3(0f, 0f, 0f);

	private float currentDuration;

	private bool wasCloseEnoughToInteract;

	private Dictionary<Who, CameraPosition> positionNames = new Dictionary<Who, CameraPosition> { 
	{
		Who.MainOrInk,
		CameraPosition.In
	} };

	[Export(PropertyHint.None, "")]
	public string cameraPositionDebug
	{
		get
		{
			IOrderedEnumerable<KeyValuePair<Who, CameraPosition>> source = positionNames.OrderByDescending((KeyValuePair<Who, CameraPosition> kv) => kv.Key);
			return string.Join(", ", source.Select((KeyValuePair<Who, CameraPosition> kv) => $"{kv.Key}: {kv.Value}"));
		}
		set
		{
		}
	}

	public CameraPosition currentPosition
	{
		get
		{
			if (positionNames.Count > 0)
			{
				Who key = positionNames.Keys.Max();
				return positionNames[key];
			}
			return CameraPosition.In;
		}
	}

	public bool isCloseEnoughToInteract => Mathf.Abs(base.Position.Z - basePosition.Z) < closeEnoughToInteractThreshold;

	public static CameraPosition GetPositionFromInkName(string name)
	{
		switch (name)
		{
		case "CameraInitialFarOut":
			return CameraPosition.InitialFarOut;
		case "CameraIn":
			return CameraPosition.In;
		case "CameraOut":
			return CameraPosition.Out;
		case "CameraNotebook":
			return CameraPosition.Notebook;
		case "CameraSideCrossRef":
			return CameraPosition.SideCrossRef;
		case "CameraForMenu":
			return CameraPosition.Menu;
		default:
			GD.PrintErr("Unknown camera position name: " + name);
			return CameraPosition.None;
		}
	}

	public void SetDesaturateMode(bool desaturate, bool immediate = false)
	{
		float num = (desaturate ? desaturateModeBrightness : defaultBrightness);
		float num2 = (desaturate ? desaturateModeSaturation : 1f);
		float num3 = (desaturate ? desaturateModeContrast : 1f);
		if (RenderingServer.GetRenderingDevice() == null)
		{
			num *= openGLBrightnessMultiplier;
		}
		if (desaturateTween != null)
		{
			desaturateTween.Kill();
		}
		desaturateTween = CreateTween().SetParallel();
		desaturateTween.TweenProperty(worldEnvironment.Environment, "adjustment_brightness", num, immediate ? 0f : 0.5f);
		desaturateTween.TweenProperty(worldEnvironment.Environment, "adjustment_saturation", num2, immediate ? 0f : 0.5f);
		desaturateTween.TweenProperty(worldEnvironment.Environment, "adjustment_contrast", num3, immediate ? 0f : 0.5f);
	}

	public void ChangePosition(Who owner, CameraPosition position, bool immediate = false)
	{
		CameraPosition num = currentPosition;
		if (position != CameraPosition.None)
		{
			positionNames[owner] = position;
		}
		else
		{
			positionNames.Remove(owner);
		}
		CameraPosition cameraPosition = currentPosition;
		if (num == CameraPosition.InitialFarOut || cameraPosition == CameraPosition.InitialFarOut)
		{
			currentDuration = initialZoomDuration;
		}
		else
		{
			currentDuration = standardDuration;
		}
		if (immediate)
		{
			UpdatePosition(0f, immediate: true);
		}
	}

	public void ResetPosition(Who owner, bool immediate = false)
	{
		ChangePosition(owner, CameraPosition.None, immediate);
	}

	public override void _EnterTree()
	{
		defaultBrightness = worldEnvironment.Environment.AdjustmentBrightness;
		if (RenderingServer.GetRenderingDevice() == null)
		{
			GD.Print("Using OpenGL or Compatibility mode");
			worldEnvironment.Environment.GlowIntensity = openGLGlowIntensity;
			worldEnvironment.Environment.AdjustmentBrightness = defaultBrightness * openGLBrightnessMultiplier;
		}
		if (Platform.isSwitch)
		{
			worldEnvironment.Environment.GlowEnabled = false;
			worldEnvironment.Environment.AdjustmentBrightness = 1.2f;
		}
	}

	public override void _Ready()
	{
		Clear();
		if (DebugOptions.instance.artMode)
		{
			SetDebugPosition(0f);
		}
	}

	public void Clear()
	{
		positionNames.Clear();
		ChangePosition(Who.MainOrInk, CameraPosition.InitialFarOut, immediate: true);
		currentDuration = initialZoomDuration;
	}

	public override void _Process(double delta)
	{
		UpdatePosition((float)delta);
		bool flag = isCloseEnoughToInteract;
		if (flag != wasCloseEnoughToInteract)
		{
			wasCloseEnoughToInteract = flag;
			EmitSignal(SignalName.MovedAcrossInteractionThreshold, flag);
		}
		Vector2 size = GetViewport().GetVisibleRect().Size;
		if (size != lastScreenSizeSinceAspectResize)
		{
			lastScreenSizeSinceAspectResize = size;
			float num = size.X / size.Y;
			if (defaultFov == 0f)
			{
				defaultFov = base.Fov;
			}
			if (num < 1.7777778f)
			{
				float num2 = Mathf.DegToRad(defaultFov);
				float num3 = 1.7777778f / num;
				float rad = 2f * Mathf.Atan(num3 * Mathf.Tan(num2 / 2f));
				base.Fov = Mathf.RadToDeg(rad);
			}
			else
			{
				base.Fov = defaultFov;
			}
		}
	}

	private void UpdatePosition(float delta, bool immediate = false)
	{
		if (debugPositionNorm >= 0f)
		{
			Vector3 vector = initialFarOutOffset.Lerp(Vector3.Zero, debugPositionNorm);
			base.Position = basePosition + vector;
			return;
		}
		Vector3 zero = Vector3.Zero;
		switch (currentPosition)
		{
		case CameraPosition.InitialFarOut:
			zero = initialFarOutOffset;
			break;
		case CameraPosition.In:
			zero = Vector3.Zero;
			break;
		case CameraPosition.Out:
			zero = outOffset;
			break;
		case CameraPosition.Notebook:
			zero = notebookOffset;
			break;
		case CameraPosition.SideCrossRef:
			zero = sideCrossRefOffset;
			break;
		case CameraPosition.Menu:
			zero = menuOffset;
			break;
		}
		Vector3 vector2 = basePosition + zero;
		if (immediate)
		{
			base.Position = vector2;
			currentVelocity = Vector3.Zero;
			currentDuration = standardDuration;
		}
		else
		{
			Vector3 position = MathX.SmoothDamp(base.Position, vector2, ref currentVelocity, currentDuration, 10f, delta);
			base.Position = position;
		}
	}

	public void SetDebugPosition(float posNorm)
	{
		debugPositionNorm = posNorm;
	}
}
