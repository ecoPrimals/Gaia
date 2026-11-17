using Godot;

public partial class ParallaxCameraTest : Camera2D
{
	[Export(PropertyHint.None, "")]
	public float startX = -1000f;

	[Export(PropertyHint.None, "")]
	public float targetX = 1184.28f;

	[Export(PropertyHint.None, "")]
	public float horizontalDuration = 6f;

	[Export(PropertyHint.None, "")]
	public float targetY = 753.33f;

	[Export(PropertyHint.None, "")]
	public float verticalDuration = 2.5f;

	[Export(PropertyHint.None, "")]
	public float verticalDelay = 4f;

	[Export(PropertyHint.None, "")]
	public float targetZoom = 5.79f;

	[Export(PropertyHint.None, "")]
	public float zoomDuration = 3f;

	[Export(PropertyHint.None, "")]
	public float zoomDelay = 5f;

	private Vector2 _originalPosition;

	public override void _Ready()
	{
		_originalPosition = base.Position;
		Tween tween = CreateTween();
		tween.SetTrans(Tween.TransitionType.Sine);
		tween.SetEase(Tween.EaseType.InOut);
		tween.TweenProperty(this, "position:x", targetX, horizontalDuration);
		Tween tween2 = CreateTween();
		tween2.SetTrans(Tween.TransitionType.Sine);
		tween2.SetEase(Tween.EaseType.InOut);
		tween2.TweenProperty(this, "position:y", targetY, verticalDuration).SetDelay(verticalDelay);
		Tween tween3 = CreateTween();
		tween3.SetParallel();
		tween3.SetTrans(Tween.TransitionType.Sine);
		tween3.SetEase(Tween.EaseType.InOut);
		tween3.TweenProperty(this, "zoom:x", targetZoom, zoomDuration).SetDelay(zoomDelay);
		tween3.TweenProperty(this, "zoom:y", targetZoom, zoomDuration).SetDelay(zoomDelay);
	}
}
