using System;
using Godot;

[Tool]
public partial class ButtonWithPrompt : Container
{
	[Signal]
	public delegate void PressedEventHandler();

	[Signal]
	public delegate void ButtonUpEventHandler();

	[Signal]
	public delegate void ButtonDownEventHandler();

	[Signal]
	public delegate void ToggledEventHandler(bool toggledOn);

	private const float promptInsetX = 8f;

	private const float requiredExtraTextMargin = 30f;

	private const float minimumHeight = 54f;

	private string _text;

	private string _actionName;

	private Button _button;

	private Label _label;

	private ButtonPrompt _buttonPrompt;

	[Export(PropertyHint.None, "")]
	public string text
	{
		get
		{
			if (label != null)
			{
				return label.Text;
			}
			return _text;
		}
		set
		{
			_text = value;
			if (label != null)
			{
				label.Text = value;
				UpdateMinimumSize();
				QueueSort();
			}
		}
	}

	[Export(PropertyHint.None, "")]
	public string actionName
	{
		get
		{
			if (buttonPrompt != null)
			{
				return buttonPrompt.actionName ?? "";
			}
			return _actionName ?? "";
		}
		set
		{
			_actionName = value;
			if (buttonPrompt != null)
			{
				buttonPrompt.actionName = value;
				buttonPrompt.Refresh();
				UpdateMinimumSize();
				QueueSort();
			}
		}
	}

	private Button button
	{
		get
		{
			if (_button == null && IsInsideTree())
			{
				_button = GetNode<Button>("Button");
			}
			return _button;
		}
	}

	private Label label
	{
		get
		{
			if (_label == null && IsInsideTree())
			{
				_label = GetNode<Label>("Label");
			}
			return _label;
		}
	}

	private ButtonPrompt buttonPrompt
	{
		get
		{
			if (_buttonPrompt == null && IsInsideTree())
			{
				_buttonPrompt = GetNode<ButtonPrompt>("ButtonPrompt");
			}
			return _buttonPrompt;
		}
	}

	public override void _Ready()
	{
		button.Pressed += delegate
		{
			EmitSignal(SignalName.Pressed);
		};
		button.ButtonUp += delegate
		{
			EmitSignal(SignalName.ButtonUp);
		};
		button.ButtonDown += delegate
		{
			EmitSignal(SignalName.ButtonDown);
		};
		button.Toggled += delegate(bool toggledOn)
		{
			EmitSignal(SignalName.Toggled, toggledOn);
		};
		buttonPrompt.VisibilityChanged += delegate
		{
			QueueSort();
		};
		if (!string.IsNullOrEmpty(_text))
		{
			label.Text = _text;
		}
		if (!string.IsNullOrEmpty(_actionName))
		{
			buttonPrompt.actionName = _actionName;
			buttonPrompt.Refresh();
		}
		UpdateMinimumSize();
		QueueSort();
	}

	public override void _Notification(int what)
	{
		if ((long)what == 51)
		{
			PerformLayout();
		}
	}

	public override Vector2 _GetMinimumSize()
	{
		float num = 0f;
		float val = 0f;
		if (buttonPrompt != null && buttonPrompt.Visible)
		{
			Vector2 minimumSize = buttonPrompt.GetMinimumSize();
			num += 8f + minimumSize.X;
			val = Math.Max(val, minimumSize.Y);
		}
		if (label != null)
		{
			Vector2 minimumSize2 = label.GetMinimumSize();
			num += minimumSize2.X;
			val = Math.Max(val, minimumSize2.Y);
		}
		num += 30f;
		val = Math.Max(val, 54f);
		return new Vector2(num, val);
	}

	private void PerformLayout()
	{
		if (button != null && label != null && buttonPrompt != null)
		{
			Vector2 size = base.Size;
			button.Position = new Vector2(0f, 0f);
			button.Size = size;
			float num = 0f;
			if (buttonPrompt.Visible)
			{
				buttonPrompt.Position = new Vector2(8f, 0.5f * size.Y - 0.5f * buttonPrompt.Size.Y);
				num = buttonPrompt.Position.X + buttonPrompt.Size.X;
			}
			label.Position = new Vector2(num, 0f);
			label.Size = new Vector2(size.X - num, size.Y);
		}
	}
}
