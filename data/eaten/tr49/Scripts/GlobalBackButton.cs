using System.Collections.Generic;
using Godot;

public partial class GlobalBackButton : Control
{
	public static GlobalBackButton instance;

	[Export(PropertyHint.None, "")]
	private float fadeDuration = 0.3f;

	[Export(PropertyHint.None, "")]
	private ButtonWithPrompt desktopAndConsoleButton;

	[Export(PropertyHint.None, "")]
	private Button mobileButton;

	private List<IGlobalBackButtonHandler> backButtonHandlerStack = new List<IGlobalBackButtonHandler>();

	public bool WantsVisible => backButtonHandlerStack.Count > 0;

	public override void _EnterTree()
	{
		instance = this;
	}

	public void Push(IGlobalBackButtonHandler handler, bool strict = true)
	{
		if (backButtonHandlerStack.Contains(handler))
		{
			if (strict)
			{
				GD.PushError($"GlobalBackButton: Tried to push {handler}, but it was already in the stack.");
			}
		}
		else
		{
			backButtonHandlerStack.Add(handler);
		}
	}

	public void Pop(IGlobalBackButtonHandler handler, bool strict = true)
	{
		if (backButtonHandlerStack.Count > 0 && backButtonHandlerStack[backButtonHandlerStack.Count - 1] == handler)
		{
			backButtonHandlerStack.RemoveAt(backButtonHandlerStack.Count - 1);
		}
		else if (backButtonHandlerStack.Contains(handler))
		{
			backButtonHandlerStack.Remove(handler);
			if (strict)
			{
				GD.PushError($"GlobalBackButton: Tried to pop {handler}, but it was not at end of stack.");
			}
		}
	}

	public bool HasPushed(IGlobalBackButtonHandler handler)
	{
		return backButtonHandlerStack.Contains(handler);
	}

	public override void _Ready()
	{
		base.Modulate = new Color(1f, 1f, 1f, 0f);
		if (Platform.isMobile)
		{
			mobileButton.Visible = true;
			desktopAndConsoleButton.Visible = false;
			mobileButton.Pressed += OnPressed;
		}
		else
		{
			mobileButton.Visible = false;
			desktopAndConsoleButton.Visible = true;
			desktopAndConsoleButton.Pressed += OnPressed;
		}
	}

	private void OnPressed()
	{
		if (backButtonHandlerStack.Count > 0)
		{
			backButtonHandlerStack[backButtonHandlerStack.Count - 1].OnGlobalBackButtonPressed();
		}
		else
		{
			GD.PushError("GlobalBackButton: Pressed back, but there was nothing left to handle it.");
		}
	}

	public override void _Process(double delta)
	{
		if (DebugOptions.instance.disableButtonPrompts)
		{
			base.Visible = false;
			return;
		}
		float to = 0f;
		if (backButtonHandlerStack.Count > 0 && backButtonHandlerStack[backButtonHandlerStack.Count - 1].CanUseGlobalBackButton())
		{
			to = 1f;
		}
		Color modulate = base.Modulate;
		modulate.A = Mathf.MoveToward(modulate.A, to, (float)delta / fadeDuration);
		base.Modulate = modulate;
	}
}
