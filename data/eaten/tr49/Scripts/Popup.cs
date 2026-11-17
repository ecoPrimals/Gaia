using System;
using Godot;

public partial class Popup : Control
{
	public enum Priority
	{
		Null,
		Titling,
		ExplicitInk
	}

	private enum AttachSide
	{
		Top,
		Left
	}

	private RichTextLabel headingLabel;

	private RichTextLabel textLabel;

	private Button invisibleButton;

	private TextureRect tail;

	private TextureRect closeButton;

	private Timer timeoutTimer;

	private Control panelContainer;

	[Export(PropertyHint.None, "")]
	private Control attachTo;

	[Export(PropertyHint.None, "")]
	private AttachSide attachSide;

	[Export(PropertyHint.None, "")]
	private Popup collidingPopup;

	[Export(PropertyHint.None, "")]
	private float overlapExtensionOffset;

	private Tween hideShowTween;

	private Tween collidingTween;

	private Button button;

	private float defaultTailLength;

	private float defaultPivotY;

	private Vector2 defaultPosition;

	private bool wasColliding;

	private Vector2 targetPosition;

	private Priority priority;

	private string _pendingLine1;

	private string _pendingLine2;

	private bool isColliding
	{
		get
		{
			if (collidingPopup != null)
			{
				return collidingPopup.Visible;
			}
			return false;
		}
	}

	private bool popupPending => !string.IsNullOrWhiteSpace(_pendingLine1);

	public override void _Ready()
	{
		headingLabel = GetNodeOrNull<RichTextLabel>("PanelContainer/MarginContainer/VBoxContainer/HeaderLabel");
		textLabel = GetNodeOrNull<RichTextLabel>("PanelContainer/MarginContainer/VBoxContainer/MainTextLabel");
		invisibleButton = GetNodeOrNull<Button>("PanelContainer/Button");
		tail = GetNodeOrNull<TextureRect>("Tail");
		closeButton = GetNodeOrNull<TextureRect>("CloseX");
		timeoutTimer = GetNodeOrNull<Timer>("TimeoutTimer");
		panelContainer = GetNodeOrNull<Control>("PanelContainer");
		if (headingLabel == null)
		{
			GD.PushError($"{base.Name} missing node for heading label");
		}
		if (textLabel == null)
		{
			GD.PushError($"{base.Name} missing node for main text label");
		}
		if (invisibleButton == null)
		{
			GD.PushError($"{base.Name} missing node for invisible button");
		}
		if (tail == null)
		{
			GD.PushError($"{base.Name} missing node for tail");
		}
		if (closeButton == null)
		{
			GD.PushError($"{base.Name} missing node for close button");
		}
		if (timeoutTimer == null)
		{
			GD.PushError($"{base.Name} missing node for timeout timer");
		}
		if (panelContainer == null)
		{
			GD.PushError($"{base.Name} missing node for panel container");
		}
		base.Modulate = new Color(1f, 1f, 1f, 0f);
		base.Visible = false;
		if (closeButton != null)
		{
			closeButton.Visible = false;
		}
		defaultTailLength = ((tail != null) ? tail.Size.Y : 0f);
		defaultPivotY = base.PivotOffset.Y;
		defaultPosition = base.Position;
		if (timeoutTimer != null)
		{
			timeoutTimer.Timeout += delegate
			{
				Hide();
			};
		}
		if (invisibleButton != null)
		{
			invisibleButton.Pressed += delegate
			{
				Hide();
			};
		}
	}

	public void Prepare(string line1, string line2, Priority priority)
	{
		if (this.priority != Priority.Null)
		{
			string value = null;
			if (headingLabel != null && headingLabel.Visible && textLabel != null)
			{
				value = headingLabel.Text + " -- " + textLabel.Text;
			}
			else if (textLabel != null)
			{
				value = textLabel.Text;
			}
			if (priority < this.priority)
			{
				GD.Print($"{base.Name} requested priority ({priority}) for '{line1 + line2}' is lower than existing priority of '{value}' ({this.priority}), so not showing");
				return;
			}
			GD.Print($"{base.Name} requested priority ({priority}) for '{line1 + line2}' is higher (or equal) than existing priority of '{value}' ({this.priority}), so overriding");
		}
		this.priority = priority;
		_pendingLine1 = line1;
		_pendingLine2 = line2;
	}

	public void ShowIfPending()
	{
		if (!popupPending)
		{
			return;
		}
		if (hideShowTween != null)
		{
			hideShowTween.Stop();
			hideShowTween = null;
		}
		if (textLabel != null)
		{
			if (_pendingLine2 != null && _pendingLine2.Contains("None assigned"))
			{
				textLabel.Modulate = new Color(1f, 1f, 1f, 0.5f);
			}
			else
			{
				textLabel.Modulate = new Color(1f, 1f, 1f);
			}
		}
		if (attachTo != null)
		{
			Rect2 globalRect = attachTo.GetGlobalRect();
			Vector2 vector = attachSide switch
			{
				AttachSide.Top => new Vector2(globalRect.Position.X + globalRect.Size.X / 2f, globalRect.Position.Y), 
				AttachSide.Left => new Vector2(globalRect.Position.X, globalRect.Position.Y + globalRect.Size.Y / 2f), 
				_ => throw new Exception("Unhandled attach side: " + attachSide), 
			};
			Vector2 globalPosition = GetParent<Control>().GetGlobalPosition();
			Vector2 vector2 = vector - globalPosition;
			switch (attachSide)
			{
			case AttachSide.Top:
				targetPosition = vector2 + new Vector2(-0.5f * base.Size.X, 0f - base.Size.Y - defaultTailLength);
				break;
			case AttachSide.Left:
				targetPosition = vector2 + new Vector2(0f - base.Size.X - defaultTailLength, -0.5f * base.Size.Y);
				break;
			default:
				throw new Exception("Unhandled attach side: " + attachSide);
			}
		}
		else
		{
			float y = GetViewport().GetVisibleRect().Size.Y;
			Rect2 globalRect = new Rect2(0f, y, 0f, 0f);
			targetPosition = defaultPosition;
		}
		if (!string.IsNullOrWhiteSpace(_pendingLine1) && !string.IsNullOrWhiteSpace(_pendingLine2))
		{
			if (headingLabel != null)
			{
				headingLabel.Text = _pendingLine1;
				headingLabel.Visible = true;
			}
			if (textLabel != null)
			{
				textLabel.Text = _pendingLine2;
			}
		}
		else
		{
			if (headingLabel != null)
			{
				headingLabel.Text = _pendingLine1;
				headingLabel.Visible = false;
			}
			if (textLabel != null)
			{
				textLabel.Text = _pendingLine1;
			}
		}
		_pendingLine1 = (_pendingLine2 = null);
		base.Visible = true;
		if (collidingPopup != null && tail != null)
		{
			tail.Size = new Vector2(tail.Size.X, defaultTailLength);
			base.PivotOffset = new Vector2(base.PivotOffset.X, defaultPivotY);
		}
		if (base.Modulate.A == 0f)
		{
			base.Scale = new Vector2(0.5f, 0.5f);
			Vector2 vector3 = ((attachSide == AttachSide.Top) ? new Vector2(0f, 120f) : new Vector2(-120f, 0f));
			base.Position = targetPosition + vector3;
		}
		hideShowTween = CreateTween().SetParallel();
		hideShowTween.SetTrans(Tween.TransitionType.Spring);
		hideShowTween.SetEase(Tween.EaseType.Out);
		hideShowTween.TweenProperty(this, "modulate:a", 1f, 0.30000001192092896);
		hideShowTween.TweenProperty(this, "position:x", targetPosition.X, 0.30000001192092896);
		hideShowTween.TweenProperty(this, "position:y", targetPosition.Y + (isColliding ? (0f - overlapExtensionOffset) : 0f), 0.30000001192092896);
		hideShowTween.TweenProperty(this, "scale:x", 1f, 0.30000001192092896);
		hideShowTween.TweenProperty(this, "scale:y", 1f, 0.30000001192092896);
		if (isColliding && tail != null)
		{
			hideShowTween.TweenProperty(tail, "size:y", defaultTailLength + overlapExtensionOffset, 0.30000001192092896);
			hideShowTween.TweenProperty(this, "pivot_offset:y", defaultPivotY + overlapExtensionOffset, 0.30000001192092896);
			wasColliding = true;
		}
		hideShowTween.Finished += delegate
		{
			hideShowTween = null;
		};
		if (timeoutTimer != null)
		{
			timeoutTimer.Start();
		}
	}

	public override void _Process(double delta)
	{
		if (!base.Visible || hideShowTween != null)
		{
			return;
		}
		bool flag = isColliding;
		if (flag != wasColliding)
		{
			wasColliding = flag;
			if (collidingTween != null)
			{
				collidingTween.Stop();
				collidingTween = null;
			}
			float num = (flag ? (defaultTailLength + overlapExtensionOffset) : defaultTailLength);
			float num2 = (flag ? (defaultPivotY + overlapExtensionOffset) : defaultPivotY);
			collidingTween = CreateTween().SetParallel();
			if (tail != null)
			{
				collidingTween.TweenProperty(tail, "size:y", num, 0.10000000149011612);
			}
			collidingTween.TweenProperty(this, "pivot_offset:y", num2, 0.10000000149011612);
			collidingTween.TweenProperty(this, "position:y", targetPosition.Y + (flag ? (0f - overlapExtensionOffset) : 0f), 0.10000000149011612);
			collidingTween.Finished += delegate
			{
				collidingTween = null;
			};
		}
		if (closeButton == null)
		{
			return;
		}
		if ((invisibleButton != null && invisibleButton.IsHovered()) || Platform.isMobile)
		{
			closeButton.Visible = true;
			if (panelContainer != null)
			{
				closeButton.Position = panelContainer.Position + new Vector2(10f, 10f);
			}
		}
		else
		{
			closeButton.Visible = false;
		}
	}

	public new void Hide()
	{
		_pendingLine1 = (_pendingLine2 = null);
		if (base.Visible)
		{
			priority = Priority.Null;
			if (timeoutTimer != null)
			{
				timeoutTimer.Stop();
			}
			if (hideShowTween != null)
			{
				hideShowTween.Stop();
				hideShowTween = null;
			}
			hideShowTween = CreateTween().SetParallel();
			hideShowTween.SetTrans(Tween.TransitionType.Cubic);
			hideShowTween.SetEase(Tween.EaseType.In);
			hideShowTween.TweenProperty(this, "modulate:a", 0f, 0.30000001192092896);
			hideShowTween.TweenProperty(this, "scale:x", 0.5f, 0.30000001192092896);
			hideShowTween.TweenProperty(this, "scale:y", 0.5f, 0.30000001192092896);
			hideShowTween.Finished += delegate
			{
				base.Visible = false;
				hideShowTween = null;
			};
		}
	}

	public void Clear()
	{
		if (hideShowTween != null)
		{
			hideShowTween.Stop();
			hideShowTween = null;
		}
		if (timeoutTimer != null)
		{
			timeoutTimer.Stop();
		}
		base.Visible = false;
		base.Modulate = new Color(1f, 1f, 1f, 0f);
		base.Scale = new Vector2(1f, 1f);
		priority = Priority.Null;
		_pendingLine1 = (_pendingLine2 = null);
	}
}
