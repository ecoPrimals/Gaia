using Godot;

public partial class FadeToBlack : ColorRect
{
	public static FadeToBlack instance;

	private Tween tween;

	public override void _EnterTree()
	{
		instance = this;
		base.Visible = false;
		base.Modulate = new Color(0f, 0f, 0f, 0f);
	}

	public void ShowBlack(float time = 1f)
	{
		ShowHideBlack(show: true, 0f, time);
	}

	public void HideBlack(float delay = 0f, float time = 1f)
	{
		ShowHideBlack(show: false, delay, time);
	}

	private void ShowHideBlack(bool show, float delay, float time)
	{
		if (tween != null)
		{
			tween.Kill();
			tween = null;
		}
		base.Visible = true;
		tween = CreateTween();
		tween.TweenProperty(this, "modulate:a", show ? 1f : 0f, time).SetDelay(delay);
		tween.Finished += delegate
		{
			if (!show)
			{
				base.Visible = false;
			}
			tween = null;
		};
	}
}
