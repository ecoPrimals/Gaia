using Godot;

public partial class Loading : Control
{
	[Export(PropertyHint.None, "")]
	public TextureRect logo;

	[Export(PropertyHint.None, "")]
	public float fadeTime = 1f;

	[Export(PropertyHint.None, "")]
	public float waitTime = 1f;

	private double loadStartTime;

	public override void _Ready()
	{
		logo.Modulate = new Color(1f, 1f, 1f, 0f);
		Tween tween = CreateTween();
		tween.TweenCallback(new Callable(AmbientAudio.instance, "Begin"));
		tween.TweenProperty(logo, "modulate:a", 1f, fadeTime).SetDelay(0.5);
		tween.TweenProperty(logo, "modulate:a", 0f, fadeTime).SetDelay(waitTime);
		tween.Finished += delegate
		{
			FadeToBlack.instance.ShowBlack(0f);
			LoadingIcon.instance.wantsVisible = true;
			loadStartTime = Time.GetTicksMsec();
			ResourceLoader.LoadThreadedRequest("res://Scenes/main.tscn", "", useSubThreads: false, ResourceLoader.CacheMode.Reuse);
		};
	}

	public override void _Process(double delta)
	{
		if (ResourceLoader.LoadThreadedGetStatus("res://Scenes/main.tscn") == ResourceLoader.ThreadLoadStatus.Loaded)
		{
			PackedScene packedScene = (PackedScene)ResourceLoader.LoadThreadedGet("res://Scenes/main.tscn");
			GetTree().ChangeSceneToPacked(packedScene);
			double num = (double)Time.GetTicksMsec() - loadStartTime;
			GD.Print($"Loaded main scene in: {num / 1000.0:F3} seconds");
		}
	}
}
