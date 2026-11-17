using Godot;

[GlobalClass]
public partial class HUDButtons : Control
{
	[Export(PropertyHint.None, "")]
	private float anchorOffsetWhenOnSideX = 575f;

	[Export(PropertyHint.None, "")]
	private ButtonPrompt[] LRButtonPromptsForSwitch;

	private Tween slideTween;

	public float currentOffsetNorm;

	public override void _Ready()
	{
		Clear();
		if (Platform.isSwitch)
		{
			RestyleLRButtonsForSwitch();
		}
	}

	private async void RestyleLRButtonsForSwitch()
	{
		StyleBoxFlat styleBoxFlat = null;
		ButtonPrompt[] lRButtonPromptsForSwitch = LRButtonPromptsForSwitch;
		foreach (ButtonPrompt obj in lRButtonPromptsForSwitch)
		{
			PanelContainer node = obj.GetNode<PanelContainer>("PanelContainer");
			Vector2 size = node.Size;
			size.Y = 32f;
			node.Size = size;
			styleBoxFlat = styleBoxFlat ?? ((StyleBoxFlat)node.GetThemeStylebox("panel").Duplicate());
			styleBoxFlat.SetCornerRadiusAll(10);
			node.AddThemeStyleboxOverride("panel", styleBoxFlat);
			Label node2 = obj.GetNode<Label>("PanelContainer/TextMarginContainer/Text");
			node2.HorizontalAlignment = HorizontalAlignment.Center;
			node2.ClipText = true;
			Vector2 customMinimumSize = node2.CustomMinimumSize;
			customMinimumSize.X = 35f;
			node2.CustomMinimumSize = customMinimumSize;
		}
		await ToSignal(GetTree(), "process_frame");
		lRButtonPromptsForSwitch = LRButtonPromptsForSwitch;
		foreach (ButtonPrompt buttonPrompt in lRButtonPromptsForSwitch)
		{
			Control parent = buttonPrompt.GetParent<Control>();
			float x = buttonPrompt.Size.X;
			float x2 = (parent.Size.X - x) / 2f;
			buttonPrompt.Position = new Vector2(x2, buttonPrompt.Position.Y + 4f);
		}
	}

	public override void _Process(double delta)
	{
		float offsetRight = (base.OffsetLeft = currentOffsetNorm * anchorOffsetWhenOnSideX);
		base.OffsetRight = offsetRight;
	}

	public void Clear()
	{
		SetIsCentred(isCentred: true, immediate: true);
	}

	public void SetIsCentred(bool isCentred, bool immediate = false)
	{
		if (slideTween != null)
		{
			slideTween.Kill();
			slideTween = null;
		}
		float num = (isCentred ? 0f : 1f);
		if (immediate)
		{
			currentOffsetNorm = num;
			return;
		}
		slideTween = CreateTween();
		slideTween.SetTrans(Tween.TransitionType.Sine);
		slideTween.SetEase(Tween.EaseType.InOut);
		slideTween.TweenProperty(this, "currentOffsetNorm", num, 0.5);
	}
}
