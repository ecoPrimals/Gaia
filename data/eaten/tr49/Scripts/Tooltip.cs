using System;
using Godot;

public partial class Tooltip : Control
{
	public enum Direction
	{
		Up,
		Down
	}

	[Export(PropertyHint.None, "")]
	public Label label;

	[Export(PropertyHint.None, "")]
	public Control upNubbin;

	[Export(PropertyHint.None, "")]
	public Control downNubbin;

	public Control targetControl;

	public Vector3? targetPosition3D;

	public string tag;

	public Tween fadeInOutTween;

	public Vector2 offset;

	public bool fadingOut;

	private Direction _direction;

	public bool isValid
	{
		get
		{
			if (targetPosition3D.HasValue)
			{
				return true;
			}
			return targetControl != null && GodotObject.IsInstanceValid(targetControl) && !targetControl.IsQueuedForDeletion();
		}
	}

	public Direction direction
	{
		get
		{
			return _direction;
		}
		set
		{
			_direction = value;
			upNubbin.Visible = _direction == Direction.Up;
			downNubbin.Visible = _direction == Direction.Down;
		}
	}

	public void Setup(Control targetControl, Vector3? targetPosition3D, string text, string tag, float offsetX, float offsetY)
	{
		this.targetControl = targetControl;
		this.targetPosition3D = targetPosition3D;
		label.Text = text;
		this.tag = tag;
		offset = new Vector2(offsetX, offsetY);
		base.Modulate = new Color(1f, 1f, 1f, 0f);
		base.Scale = new Vector2(0.3f, 0.3f);
		direction = Direction.Up;
	}

	public void FadeIn(float delay = 0f, Action then = null)
	{
		FadeTo(0.2f, delay, 1f, 1f, then);
	}

	public void FadeOut(float delay = 0f, Action then = null)
	{
		fadingOut = true;
		FadeTo(0.3f, delay, 0f, 0.3f, then);
	}

	private void FadeTo(float duration, float delay, float targetAlpha, float targetScale, Action then = null)
	{
		if (fadeInOutTween != null)
		{
			fadeInOutTween.Kill();
			fadeInOutTween = null;
		}
		fadeInOutTween = CreateTween().SetParallel();
		fadeInOutTween.TweenProperty(this, "modulate:a", targetAlpha, duration).SetDelay(delay);
		fadeInOutTween.TweenProperty(this, "scale", new Vector2(targetScale, targetScale), duration).SetDelay(delay);
		fadeInOutTween.Finished += delegate
		{
			fadeInOutTween = null;
			then?.Invoke();
		};
	}
}
