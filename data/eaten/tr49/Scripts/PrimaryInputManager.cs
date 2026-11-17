using System.Collections.Generic;
using Godot;
using Godot.Collections;

public partial class PrimaryInputManager : Node
{
	public enum PrimaryInputType
	{
		Keyboard,
		Gamepad
	}

	[Signal]
	public delegate void PrimaryInputTypeChangedEventHandler();

	public static PrimaryInputManager instance;

	public PrimaryInputType CurrentInputType { get; private set; } = PrimaryInputType.Gamepad;

	public static bool isGamepad => instance.CurrentInputType == PrimaryInputType.Gamepad;

	public static bool isKeyboard => instance.CurrentInputType == PrimaryInputType.Keyboard;

	public override void _EnterTree()
	{
		instance = this;
		RefreshBasedOnConnectedGamepadCount();
		Input.JoyConnectionChanged += delegate
		{
			RefreshBasedOnConnectedGamepadCount();
		};
		if (Platform.isSwitch)
		{
			SwapSwitchButtonMappings();
		}
	}

	public void RefreshBasedOnConnectedGamepadCount()
	{
		if (Input.GetConnectedJoypads().Count > 0)
		{
			SetInputType(PrimaryInputType.Gamepad);
		}
		else
		{
			SetInputType(PrimaryInputType.Keyboard);
		}
	}

	public override void _Input(InputEvent @event)
	{
		if (@event is InputEventJoypadButton)
		{
			SetInputType(PrimaryInputType.Gamepad);
		}
		else if (@event is InputEventJoypadMotion inputEventJoypadMotion && Mathf.Abs(inputEventJoypadMotion.AxisValue) > 0.5f)
		{
			SetInputType(PrimaryInputType.Gamepad);
		}
		else if ((@event is InputEventKey || @event is InputEventMouseButton) && !Platform.isSteamDeck && !Platform.isMobile && !Platform.isSwitch)
		{
			SetInputType(PrimaryInputType.Keyboard);
		}
		if (@event is InputEventMouseMotion { Relative: var relative } && relative.Length() > 20f && CurrentInputType == PrimaryInputType.Gamepad && !Platform.isSteamDeck && !Platform.isSwitch)
		{
			Input.SetMouseMode(Input.MouseModeEnum.Visible);
		}
	}

	private void SetInputType(PrimaryInputType newType)
	{
		if ((newType == PrimaryInputType.Gamepad || Platform.isSteamDeck) && !Platform.isSwitch)
		{
			Input.SetMouseMode(Input.MouseModeEnum.Hidden);
		}
		if (newType != CurrentInputType)
		{
			CurrentInputType = newType;
			GD.Print("PrimaryInputType changed to " + newType);
			EmitSignal(SignalName.PrimaryInputTypeChanged);
		}
	}

	private void SwapSwitchButtonMappings()
	{
		foreach (StringName action in InputMap.GetActions())
		{
			string text = action;
			Array<InputEvent> array = InputMap.ActionGetEvents(text);
			List<InputEvent> list = new List<InputEvent>();
			bool flag = false;
			foreach (InputEvent item in array)
			{
				if (item is InputEventJoypadButton inputEventJoypadButton && (inputEventJoypadButton.Device == -1 || inputEventJoypadButton.Device == 0))
				{
					int num = (int)inputEventJoypadButton.ButtonIndex;
					int num2 = num;
					switch (num)
					{
					case 0:
						num2 = 1;
						break;
					case 1:
						num2 = 0;
						break;
					case 2:
						num2 = 3;
						break;
					case 3:
						num2 = 2;
						break;
					}
					if (num2 != num)
					{
						InputEventJoypadButton inputEventJoypadButton2 = new InputEventJoypadButton();
						inputEventJoypadButton2.Device = inputEventJoypadButton.Device;
						inputEventJoypadButton2.ButtonIndex = (JoyButton)num2;
						inputEventJoypadButton2.Pressed = inputEventJoypadButton.Pressed;
						list.Add(inputEventJoypadButton2);
						flag = true;
						continue;
					}
				}
				list.Add(item);
			}
			if (!flag)
			{
				continue;
			}
			InputMap.ActionEraseEvents(text);
			foreach (InputEvent item2 in list)
			{
				InputMap.ActionAddEvent(text, item2);
			}
		}
	}
}
