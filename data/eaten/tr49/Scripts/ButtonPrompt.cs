using System;
using System.Collections.Generic;
using Godot;
using Godot.Collections;

[Tool]
public partial class ButtonPrompt : Control
{
	[Export(PropertyHint.None, "")]
	public string actionName = "ui_accept";

	[Export(PropertyHint.None, "")]
	public bool hideWhenParentDisabled = true;

	private Control _rootPanelContainer;

	private Control _textContainer;

	private Label _textLabel;

	private TextureRect _icon;

	private BaseButton parentButton;

	private const string buttonIconsPrefix = "res://Images/UI/button_icons/";

	private static System.Collections.Generic.Dictionary<JoyButton, Texture2D> joypadButtonIcons = new System.Collections.Generic.Dictionary<JoyButton, Texture2D>
	{
		{
			JoyButton.A,
			GD.Load<Texture2D>("res://Images/UI/button_icons/" + (Platform.isSwitch ? "B.png" : "A.png"))
		},
		{
			JoyButton.B,
			GD.Load<Texture2D>("res://Images/UI/button_icons/" + (Platform.isSwitch ? "A.png" : "B.png"))
		},
		{
			JoyButton.X,
			GD.Load<Texture2D>("res://Images/UI/button_icons/" + (Platform.isSwitch ? "Y.png" : "X.png"))
		},
		{
			JoyButton.Y,
			GD.Load<Texture2D>("res://Images/UI/button_icons/" + (Platform.isSwitch ? "X.png" : "Y.png"))
		}
	};

	private static System.Collections.Generic.Dictionary<JoyAxis, Texture2D> joypadAxisIcons = new System.Collections.Generic.Dictionary<JoyAxis, Texture2D>
	{
		{
			JoyAxis.LeftX,
			GD.Load<Texture2D>("res://Images/UI/button_icons/LeftStick.png")
		},
		{
			JoyAxis.LeftY,
			GD.Load<Texture2D>("res://Images/UI/button_icons/LeftStick.png")
		},
		{
			JoyAxis.RightX,
			GD.Load<Texture2D>("res://Images/UI/button_icons/RightStick.png")
		},
		{
			JoyAxis.RightY,
			GD.Load<Texture2D>("res://Images/UI/button_icons/RightStick.png")
		}
	};

	private static System.Collections.Generic.Dictionary<JoyButton, string> joypadButtonTextNames = new System.Collections.Generic.Dictionary<JoyButton, string>
	{
		{
			JoyButton.LeftShoulder,
			Platform.isSwitch ? "L" : "LB"
		},
		{
			JoyButton.RightShoulder,
			Platform.isSwitch ? "R" : "RB"
		}
	};

	private static System.Collections.Generic.Dictionary<JoyAxis, string> joypadAxisTextNames = new System.Collections.Generic.Dictionary<JoyAxis, string>
	{
		{
			JoyAxis.TriggerLeft,
			Platform.isSwitch ? "ZL" : "LT"
		},
		{
			JoyAxis.TriggerRight,
			Platform.isSwitch ? "ZR" : "RT"
		}
	};

	private static System.Collections.Generic.Dictionary<Key, string> keyboardKeyNameOverrides = new System.Collections.Generic.Dictionary<Key, string>
	{
		{
			Key.Enter,
			"↩"
		},
		{
			Key.KpEnter,
			"↩"
		},
		{
			Key.Escape,
			"ESC"
		},
		{
			Key.Backspace,
			"⬅"
		},
		{
			Key.Delete,
			"DEL"
		},
		{
			Key.Slash,
			"/"
		},
		{
			Key.Period,
			"."
		},
		{
			Key.Comma,
			","
		},
		{
			Key.Semicolon,
			";"
		},
		{
			Key.Quotedbl,
			"\""
		},
		{
			Key.Backslash,
			"\\"
		},
		{
			Key.Question,
			"?"
		},
		{
			Key.Exclam,
			"!"
		},
		{
			Key.Apostrophe,
			"'"
		}
	};

	private StyleBoxFlat[] styleBoxes;

	private Control rootPanelContainer
	{
		get
		{
			if (_rootPanelContainer == null)
			{
				_rootPanelContainer = GetNode<Control>("PanelContainer");
			}
			return _rootPanelContainer;
		}
	}

	private Control textContainer
	{
		get
		{
			if (_textContainer == null)
			{
				_textContainer = rootPanelContainer.GetNode<Control>("TextMarginContainer");
			}
			return _textContainer;
		}
	}

	private Label textLabel
	{
		get
		{
			if (_textLabel == null)
			{
				_textLabel = textContainer.GetNode<Label>("Text");
			}
			return _textLabel;
		}
	}

	private TextureRect icon
	{
		get
		{
			if (_icon == null)
			{
				_icon = rootPanelContainer.GetNode<TextureRect>("Icon");
			}
			return _icon;
		}
	}

	public override void _Ready()
	{
		if (GetParent() is BaseButton baseButton)
		{
			parentButton = baseButton;
		}
		if (Platform.isMobile)
		{
			base.Visible = false;
			return;
		}
		if (PrimaryInputManager.instance != null)
		{
			PrimaryInputManager.instance.PrimaryInputTypeChanged += Refresh;
		}
		Refresh();
	}

	public override void _ExitTree()
	{
		if (PrimaryInputManager.instance != null)
		{
			PrimaryInputManager.instance.PrimaryInputTypeChanged -= Refresh;
		}
	}

	public override void _Process(double delta)
	{
		if (DebugOptions.instance != null && DebugOptions.instance.disableButtonPrompts)
		{
			base.Visible = false;
		}
		else if (Platform.isMobile)
		{
			base.Visible = false;
		}
		else if (parentButton != null)
		{
			if (hideWhenParentDisabled)
			{
				base.Visible = !parentButton.Disabled;
			}
			else
			{
				base.Modulate = new Color(1f, 1f, 1f, parentButton.Disabled ? 0.5f : 1f);
			}
		}
	}

	public override Vector2 _GetMinimumSize()
	{
		Vector2 minimumSize = rootPanelContainer.GetMinimumSize();
		return new Vector2(Math.Max(minimumSize.X, 40f), Math.Max(minimumSize.Y, 40f));
	}

	public void Refresh()
	{
		RefreshIconAndText();
		UpdateMinimumSize();
	}

	private void RefreshOwnSizingAndMargin()
	{
		Vector2 size = base.Size;
		size.X = rootPanelContainer.Size.X;
		base.Size = size;
		StyleBoxFlat[] array = styleBoxes;
		foreach (StyleBoxFlat styleBoxFlat in array)
		{
			if (styleBoxFlat != null)
			{
				styleBoxFlat.ContentMarginLeft = size.X + 20f;
			}
		}
	}

	private void RefreshIconAndText()
	{
		Array<InputEvent> array = InputMap.ActionGetEvents(actionName);
		if (array.Count == 0)
		{
			if (!Engine.IsEditorHint())
			{
				GD.PushError($"ButtonPrompt '{base.Name}': No input events at all found for action '{actionName}'");
			}
			return;
		}
		InputEvent inputEvent = null;
		bool flag = PrimaryInputManager.instance != null && PrimaryInputManager.instance.CurrentInputType == PrimaryInputManager.PrimaryInputType.Gamepad;
		foreach (InputEvent item in array)
		{
			if (flag && (item is InputEventJoypadButton || item is InputEventJoypadMotion))
			{
				if (item is InputEventJoypadButton inputEventJoypadButton)
				{
					if (joypadButtonIcons.TryGetValue(inputEventJoypadButton.ButtonIndex, out var value))
					{
						SetIcon(value);
						return;
					}
					if (joypadButtonTextNames.TryGetValue(inputEventJoypadButton.ButtonIndex, out var value2))
					{
						SetText(value2);
						return;
					}
				}
				else if (item is InputEventJoypadMotion inputEventJoypadMotion)
				{
					if (joypadAxisIcons.TryGetValue(inputEventJoypadMotion.Axis, out var value3))
					{
						SetIcon(value3);
						return;
					}
					if (joypadAxisTextNames.TryGetValue(inputEventJoypadMotion.Axis, out var value4))
					{
						SetText(value4);
						return;
					}
				}
				if (inputEvent == null)
				{
					inputEvent = item;
				}
			}
			else if (!flag && item is InputEventKey inputEventKey)
			{
				Key key = ((inputEventKey.Keycode != Key.None) ? inputEventKey.Keycode : inputEventKey.PhysicalKeycode);
				if (key != Key.None && keyboardKeyNameOverrides.TryGetValue(key, out var value5))
				{
					SetText(value5);
				}
				else
				{
					SetText(inputEventKey.AsText().ToUpper().Replace("(PHYSICAL)", "")
						.Trim());
				}
				return;
			}
		}
		if (inputEvent == null)
		{
			SetText("");
			return;
		}
		GD.PushError($"ButtonPrompt '{base.Name}': Unknown input event type: {inputEvent.AsText()} for action '{actionName}' for primary input type {PrimaryInputManager.instance.CurrentInputType}");
	}

	private void SetText(string text)
	{
		textLabel.Text = text;
		textContainer.Visible = true;
		icon.Visible = false;
	}

	private void SetIcon(Texture2D texture)
	{
		icon.Texture = texture;
		icon.Visible = true;
		textContainer.Visible = false;
	}
}
