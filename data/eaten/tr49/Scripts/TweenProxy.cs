using System;
using System.Collections.Generic;
using Godot;

public class TweenProxy
{
	private static float duration;

	private static Tween.TransitionType transition;

	private static Tween.EaseType ease;

	private static float accumulatedDelay;

	private static Tween currentTween;

	private static HashSet<TweenProxy> modifiedProxies = new HashSet<TweenProxy>();

	private Vector2 proxyPosition;

	private bool hasPosition;

	private bool hasUncommitedPosition;

	private float proxyRotation;

	private bool hasRotation;

	private bool hasUncommitedRotation;

	private Vector2 proxyScale;

	private bool hasScale;

	private bool hasUncommitedScale;

	private Vector2 proxySize;

	private bool hasSize;

	private bool hasUncommitedSize;

	private Color proxyModulate;

	private bool hasModulate;

	private bool hasUncommitedModulate;

	public Control Target { get; private set; }

	public Vector2 Position
	{
		get
		{
			if (currentTween != null && hasPosition)
			{
				return proxyPosition;
			}
			return Target.Position;
		}
		set
		{
			if (currentTween != null)
			{
				proxyPosition = value;
				hasPosition = true;
				hasUncommitedPosition = true;
				modifiedProxies.Add(this);
			}
			else
			{
				Target.Position = value;
			}
		}
	}

	public float Rotation
	{
		get
		{
			if (currentTween != null && hasRotation)
			{
				return proxyRotation;
			}
			return Target.Rotation;
		}
		set
		{
			if (currentTween != null)
			{
				proxyRotation = value;
				hasRotation = true;
				hasUncommitedRotation = true;
				modifiedProxies.Add(this);
			}
			else
			{
				Target.Rotation = value;
			}
		}
	}

	public Vector2 Scale
	{
		get
		{
			if (currentTween != null && hasScale)
			{
				return proxyScale;
			}
			return Target.Scale;
		}
		set
		{
			if (currentTween != null)
			{
				proxyScale = value;
				hasScale = true;
				hasUncommitedScale = true;
				modifiedProxies.Add(this);
			}
			else
			{
				Target.Scale = value;
			}
		}
	}

	public Vector2 Size
	{
		get
		{
			if (currentTween != null && hasSize)
			{
				return proxySize;
			}
			return Target.Size;
		}
		set
		{
			if (currentTween != null)
			{
				proxySize = value;
				hasSize = true;
				hasUncommitedSize = true;
				modifiedProxies.Add(this);
			}
			else
			{
				Target.Size = value;
			}
		}
	}

	public Color Modulate
	{
		get
		{
			if (currentTween != null && hasModulate)
			{
				return proxyModulate;
			}
			return Target.Modulate;
		}
		set
		{
			if (currentTween != null)
			{
				proxyModulate = value;
				hasModulate = true;
				hasUncommitedModulate = true;
				modifiedProxies.Add(this);
			}
			else
			{
				Target.Modulate = value;
			}
		}
	}

	public float Alpha
	{
		get
		{
			return Modulate.A;
		}
		set
		{
			Color modulate = Modulate;
			modulate.A = value;
			Modulate = modulate;
		}
	}

	public float X
	{
		get
		{
			return Position.X;
		}
		set
		{
			Vector2 position = Position;
			position.X = value;
			Position = position;
		}
	}

	public float Y
	{
		get
		{
			return Position.Y;
		}
		set
		{
			Vector2 position = Position;
			position.Y = value;
			Position = position;
		}
	}

	public float Width
	{
		get
		{
			return Size.X;
		}
		set
		{
			Vector2 size = Size;
			size.X = value;
			Size = size;
		}
	}

	public float Height
	{
		get
		{
			return Size.Y;
		}
		set
		{
			Vector2 size = Size;
			size.Y = value;
			Size = size;
		}
	}

	public TweenProxy(Control target)
	{
		Target = target;
	}

	public void AddDelay(float delay)
	{
		Commit();
		accumulatedDelay += delay;
	}

	private static void Commit()
	{
		foreach (TweenProxy modifiedProxy in modifiedProxies)
		{
			if (modifiedProxy.hasUncommitedPosition)
			{
				currentTween.TweenProperty(modifiedProxy.Target, "position", modifiedProxy.proxyPosition, duration).SetDelay(accumulatedDelay);
				modifiedProxy.hasUncommitedPosition = false;
			}
			if (modifiedProxy.hasUncommitedRotation)
			{
				currentTween.TweenProperty(modifiedProxy.Target, "rotation", modifiedProxy.proxyRotation, duration).SetDelay(accumulatedDelay);
				modifiedProxy.hasUncommitedRotation = false;
			}
			if (modifiedProxy.hasUncommitedScale)
			{
				currentTween.TweenProperty(modifiedProxy.Target, "scale", modifiedProxy.proxyScale, duration).SetDelay(accumulatedDelay);
				modifiedProxy.hasUncommitedScale = false;
			}
			if (modifiedProxy.hasUncommitedSize)
			{
				currentTween.TweenProperty(modifiedProxy.Target, "size", modifiedProxy.proxySize, duration).SetDelay(accumulatedDelay);
				modifiedProxy.hasUncommitedSize = false;
			}
			if (modifiedProxy.hasUncommitedModulate)
			{
				currentTween.TweenProperty(modifiedProxy.Target, "modulate", modifiedProxy.proxyModulate, duration).SetDelay(accumulatedDelay);
				modifiedProxy.hasUncommitedModulate = false;
			}
		}
	}

	public Tween CreateTween(float duration, Action block, Tween.TransitionType trans = Tween.TransitionType.Sine, Tween.EaseType ease = Tween.EaseType.InOut)
	{
		TweenProxy.duration = duration;
		transition = trans;
		TweenProxy.ease = ease;
		accumulatedDelay = 0f;
		currentTween = Target.CreateTween();
		currentTween.SetParallel();
		currentTween.SetTrans(transition);
		currentTween.SetEase(TweenProxy.ease);
		block();
		Commit();
		_ = currentTween;
		currentTween = null;
		modifiedProxies.Clear();
		return currentTween;
	}
}
