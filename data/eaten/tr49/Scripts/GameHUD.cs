using System.Collections.Generic;
using System.Linq;
using Godot;

public partial class GameHUD : Control
{
	public enum Who
	{
		Self,
		Menu,
		Notebook
	}

	public static GameHUD instance;

	[Export(PropertyHint.None, "")]
	private float fadeDuration = 0.3f;

	[Export(PropertyHint.None, "")]
	private float offscreenOffsetY = 100f;

	[Export(PropertyHint.None, "")]
	private HUDButtons hudButtons;

	[Export(PropertyHint.None, "")]
	private ProjectedControl flipperButtonPrompt;

	[Export(PropertyHint.None, "")]
	private GameCamera gameCamera;

	private bool hasCompletedSidewaysShift;

	private Vector2 lastScreenSizeSinceAspectResize;

	private Dictionary<Who, bool> visibilityOwners = new Dictionary<Who, bool>();

	private Tween visibilityTween;

	public bool visibility
	{
		get
		{
			if (visibilityOwners.Count > 0)
			{
				Who key = visibilityOwners.Keys.Max();
				return visibilityOwners[key];
			}
			return false;
		}
	}

	public override void _EnterTree()
	{
		instance = this;
	}

	public override void _Ready()
	{
		Clear();
		gameCamera.MovedAcrossInteractionThreshold += OnCameraMovedAcrossInteractionThreshold;
	}

	public void Clear()
	{
		visibilityOwners.Clear();
		visibilityOwners[Who.Self] = true;
		UpdateVisibility(immediate: true);
		hudButtons.Clear();
		flipperButtonPrompt.Visible = false;
		hasCompletedSidewaysShift = false;
		hudButtons.SetIsCentred(isCentred: true, immediate: true);
	}

	public void MoveHUDButtonsToSide(bool isOnSide, bool immediate)
	{
		hudButtons.SetIsCentred(!isOnSide, immediate);
		hasCompletedSidewaysShift = isOnSide;
	}

	public void SetVisibility(Who who, bool visible, bool immediate = false)
	{
		bool num = visibility;
		visibilityOwners[who] = visible;
		if (num != visible)
		{
			UpdateVisibility(immediate);
		}
	}

	public void ResetVisibility(Who who, bool immediate = false)
	{
		bool num = visibility;
		visibilityOwners.Remove(who);
		if (num != visibility)
		{
			UpdateVisibility(immediate);
		}
	}

	private void UpdateVisibility(bool immediate)
	{
		if (visibilityTween != null)
		{
			visibilityTween.Kill();
			visibilityTween = null;
		}
		if (immediate)
		{
			base.Modulate = new Color(1f, 1f, 1f, visibility ? 1 : 0);
			base.Visible = visibility;
			base.Position = new Vector2(0f, visibility ? 0f : offscreenOffsetY);
			return;
		}
		if (visibility)
		{
			base.Visible = true;
		}
		visibilityTween = CreateTween().SetParallel().SetEase(Tween.EaseType.InOut).SetTrans(Tween.TransitionType.Sine);
		visibilityTween.TweenProperty(this, "modulate:a", visibility ? 1 : 0, fadeDuration);
		visibilityTween.TweenProperty(this, "position:y", visibility ? 0f : offscreenOffsetY, fadeDuration);
		if (!visibility)
		{
			visibilityTween.Finished += delegate
			{
				base.Visible = false;
			};
		}
	}

	public override void _Process(double delta)
	{
		Vector2 size = GetViewport().GetVisibleRect().Size;
		if (size != lastScreenSizeSinceAspectResize)
		{
			lastScreenSizeSinceAspectResize = size;
			UpdateSizeForAspect(size);
		}
	}

	private void UpdateSizeForAspect(Vector2 screenSize)
	{
		if (screenSize.X / screenSize.Y > 2.17f)
		{
			float num = 2.17f * screenSize.Y;
			float num2 = (base.AnchorLeft = (screenSize.X - num) / 2f / screenSize.X);
			base.AnchorRight = 1f - num2;
		}
		else
		{
			SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect, LayoutPresetMode.Minsize);
		}
		if (Platform.isiPhone)
		{
			base.OffsetBottom = -40f;
		}
	}

	private void OnCameraMovedAcrossInteractionThreshold(bool isCloseEnoughToInteract)
	{
		if (isCloseEnoughToInteract)
		{
			hasCompletedSidewaysShift = true;
		}
		hudButtons.SetIsCentred(!hasCompletedSidewaysShift);
		flipperButtonPrompt.Visible = isCloseEnoughToInteract;
	}
}
