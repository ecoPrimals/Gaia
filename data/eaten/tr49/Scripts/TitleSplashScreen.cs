using Godot;

public partial class TitleSplashScreen : Control
{
	[Export(PropertyHint.None, "")]
	private CreditsLabel title;

	[Export(PropertyHint.None, "")]
	private AudioStreamPlayer titleRevealSFX;

	[Export(PropertyHint.None, "")]
	private SubViewportContainer titleViewportContainer;

	[Export(PropertyHint.None, "")]
	private AudioStream[] characterWriteInSFX;

	[Export(PropertyHint.None, "")]
	private AudioStream deconstructSFX;

	public static TitleSplashScreen instance;

	private Tween tween;

	public override void _EnterTree()
	{
		instance = this;
		base.Visible = false;
		titleViewportContainer.Visible = false;
		base.MouseFilter = MouseFilterEnum.Ignore;
	}

	public override void _Ready()
	{
		if (base.Owner == null)
		{
			ShowSplash();
		}
	}

	public override void _Input(InputEvent @event)
	{
		if (base.Visible)
		{
			this.SetInputAsHandled(@event);
		}
	}

	public void ShowSplash()
	{
		if (tween == null)
		{
			base.MouseFilter = MouseFilterEnum.Stop;
			titleRevealSFX.Play();
			title.writeInProportion = 0f;
			title.randomVisibleProportion = 1f;
			title.fuzzStrength = 0f;
			base.Visible = true;
			base.Modulate = new Color(1f, 1f, 1f, 0f);
			tween = CreateTween();
			tween.TweenProperty(this, "modulate:a", 1f, 1.0).SetDelay(0.5);
			tween.TweenCallback(Callable.From(delegate
			{
				titleViewportContainer.Visible = true;
			}));
			tween.TweenSubtween(Credits.CreateLabelWriteInTween(this, title, "TR-49", 1.5f));
			tween.TweenCallback(Callable.From(delegate
			{
				titleViewportContainer.Visible = false;
			}));
			tween.TweenProperty(this, "modulate:a", 0f, 1.0).SetDelay(0.5);
			tween.Finished += delegate
			{
				tween = null;
				base.MouseFilter = MouseFilterEnum.Ignore;
				base.Visible = false;
			};
		}
	}
}
