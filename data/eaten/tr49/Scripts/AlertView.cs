using System;
using System.Collections.Generic;
using Godot;

public partial class AlertView : Control, IGlobalBackButtonHandler
{
	[Signal]
	public delegate void DidHideEventHandler();

	[Export(PropertyHint.None, "")]
	private Control background;

	[Export(PropertyHint.None, "")]
	private Control alertBox;

	[Export(PropertyHint.None, "")]
	private Label headingLabel;

	[Export(PropertyHint.None, "")]
	private PackedScene buttonScene;

	[Export(PropertyHint.None, "")]
	private Control buttonsContainer;

	public static AlertView instance;

	private float defaultPrimaryButtonX;

	private float defaultSecondaryButtonX;

	private float defaultBackgroundAlpha;

	private List<AlertOption> options = new List<AlertOption>();

	private Tween activeTween;

	private bool hiding;

	private bool hasCancelOption => options.Exists((AlertOption o) => o.isCancel);

	public override void _EnterTree()
	{
		instance = this;
	}

	public override void _Ready()
	{
		defaultBackgroundAlpha = background.Modulate.A;
		base.Visible = false;
		background.Modulate = new Color(0f, 0f, 0f, 0f);
		alertBox.Modulate = new Color(1f, 1f, 1f, 0f);
		if (base.Owner == null)
		{
			TestAlert();
		}
	}

	public async void TestAlert()
	{
		await ToSignal(GetTree().CreateTimer(1.0), "timeout");
		instance.ShowAlert("Thank you for playing TR-49.", AlertOption.Primary("Resume from before epilogue", delegate
		{
			GD.Print("Resume from before epilogue");
		}), AlertOption.Secondary("Reset", delegate
		{
			GD.Print("Reset");
		}), AlertOption.Secondary("Quit", delegate
		{
			GetTree().Quit();
		}));
	}

	public override void _Input(InputEvent @event)
	{
		if (base.Visible && activeTween == null && @event.IsActionPressed("ui_cancel") && hasCancelOption)
		{
			this.SetInputAsHandled(@event);
			Action action = options.Find((AlertOption o) => o.isCancel).action;
			HideAlert();
			action?.Invoke();
		}
	}

	public override void _UnhandledInput(InputEvent @event)
	{
		if (base.Visible || activeTween != null)
		{
			this.SetInputAsHandled(@event);
		}
	}

	public void ShowAlert(string heading, params AlertOption[] options)
	{
		headingLabel.Text = heading;
		this.options.AddRange(options);
		for (int i = 0; i < options.Length; i++)
		{
			AlertOption option = options[i];
			Button button = buttonScene.Instantiate<Button>(PackedScene.GenEditState.Disabled);
			button.Text = option.text;
			button.Pressed += delegate
			{
				if (!option.dontCloseOnAction)
				{
					HideAlert();
				}
				option.action?.Invoke();
			};
			buttonsContainer.AddChild(button, forceReadableName: false, InternalMode.Disabled);
		}
		base.Visible = true;
		GlobalBackButton.instance.Push(this);
		if (activeTween != null)
		{
			activeTween.Kill();
		}
		activeTween = CreateTween().SetParallel();
		activeTween.TweenProperty(background, "modulate:a", defaultBackgroundAlpha, 0.5);
		activeTween.TweenProperty(alertBox, "modulate:a", 1f, 0.25);
		activeTween.Finished += delegate
		{
			activeTween = null;
		};
		int num = this.options.FindIndex((AlertOption o) => o.isPrimary);
		if (num != -1)
		{
			buttonsContainer.GetChild<Button>(num).GrabFocus();
			return;
		}
		int idx = buttonsContainer.GetChildCount() - 1;
		buttonsContainer.GetChild<Button>(idx).GrabFocus();
	}

	private void HideAlert()
	{
		if (hiding)
		{
			return;
		}
		hiding = true;
		if (activeTween != null)
		{
			activeTween.Kill();
		}
		GlobalBackButton.instance.Pop(this);
		options.Clear();
		activeTween = CreateTween().SetParallel();
		activeTween.TweenProperty(background, "modulate:a", 0, 0.5);
		activeTween.TweenProperty(alertBox, "modulate:a", 0, 0.25);
		activeTween.Finished += delegate
		{
			foreach (Node child in buttonsContainer.GetChildren())
			{
				child.QueueFree();
			}
			base.Visible = false;
			hiding = false;
			activeTween = null;
			EmitSignal(SignalName.DidHide);
		};
	}

	public void OnGlobalBackButtonPressed()
	{
		if (hasCancelOption)
		{
			HideAlert();
		}
	}

	public bool CanUseGlobalBackButton()
	{
		return hasCancelOption;
	}
}
