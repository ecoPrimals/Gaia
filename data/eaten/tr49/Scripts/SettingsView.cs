using System;
using Godot;

public partial class SettingsView : Control, IGlobalBackButtonHandler
{
	[Signal]
	public delegate void DidHideEventHandler();

	private struct FpsLimitOption
	{
		public string label;

		public int fps;
	}

	public static SettingsView instance;

	[Export(PropertyHint.None, "")]
	private CheckBox fullscreenButton;

	[Export(PropertyHint.None, "")]
	private CheckBox subtitlesButton;

	[Export(PropertyHint.None, "")]
	private CheckBox hapticButton;

	[Export(PropertyHint.None, "")]
	private CheckBox reduceGlitchEffectsButton;

	[Export(PropertyHint.None, "")]
	private CheckBox reduceHintsButton;

	[Export(PropertyHint.None, "")]
	private HSlider masterVolumeSlider;

	[Export(PropertyHint.None, "")]
	private HSlider sfxVolumeSlider;

	[Export(PropertyHint.None, "")]
	private HSlider voicesVolumeSlider;

	[Export(PropertyHint.None, "")]
	private HSlider musicVolumeSlider;

	[Export(PropertyHint.None, "")]
	private MenuButton fpsLimitMenuButton;

	private Control initialFocus;

	private Tween showHideTween;

	private FpsLimitOption[] fpsLimitOptions = new FpsLimitOption[4]
	{
		new FpsLimitOption
		{
			label = "30 fps",
			fps = 30
		},
		new FpsLimitOption
		{
			label = "60 fps",
			fps = 60
		},
		new FpsLimitOption
		{
			label = "120 fps",
			fps = 120
		},
		new FpsLimitOption
		{
			label = "Unlimited",
			fps = 0
		}
	};

	public override void _EnterTree()
	{
		instance = this;
	}

	public override async void _Ready()
	{
		base.Visible = false;
		fullscreenButton.Pressed += delegate
		{
			GameSettings.instance.fullscreen = fullscreenButton.IsPressed();
			Haptic.instance.Tap();
		};
		masterVolumeSlider.ValueChanged += delegate(double value)
		{
			GameSettings.instance.masterVolume = (float)value;
		};
		sfxVolumeSlider.ValueChanged += delegate(double value)
		{
			GameSettings.instance.sfxVolume = (float)value;
		};
		voicesVolumeSlider.ValueChanged += delegate(double value)
		{
			GameSettings.instance.voicesVolume = (float)value;
		};
		musicVolumeSlider.ValueChanged += delegate(double value)
		{
			GameSettings.instance.musicVolume = (float)value;
		};
		subtitlesButton.Pressed += delegate
		{
			GameSettings.instance.showSubtitles = subtitlesButton.IsPressed();
			Haptic.instance.Tap();
		};
		hapticButton.Pressed += delegate
		{
			GameSettings.instance.hapticsEnabled = hapticButton.IsPressed();
			Haptic.instance.Tap();
		};
		reduceGlitchEffectsButton.Pressed += delegate
		{
			GameSettings.instance.reduceGlitchEffects = reduceGlitchEffectsButton.IsPressed();
			Haptic.instance.Tap();
		};
		reduceHintsButton.Pressed += delegate
		{
			GameSettings.instance.reduceHints = reduceHintsButton.IsPressed();
			Haptic.instance.Tap();
		};
		FpsLimitOption[] array = fpsLimitOptions;
		for (int num = 0; num < array.Length; num++)
		{
			FpsLimitOption fpsLimitOption = array[num];
			fpsLimitMenuButton.GetPopup().AddItem(fpsLimitOption.label, -1, Key.None);
		}
		fpsLimitMenuButton.GetPopup().IndexPressed += delegate(long index)
		{
			GameSettings.instance.fpsLimit = fpsLimitOptions[index].fps;
			fpsLimitMenuButton.Text = fpsLimitOptions[index].label;
			Haptic.instance.Tap();
		};
		await ToSignal(GetTree(), "process_frame");
		if (Platform.isMobile || Platform.isSteamDeck || Platform.isSwitch)
		{
			fullscreenButton.Visible = false;
			masterVolumeSlider.GetParent<Control>().Visible = false;
		}
		if (Platform.isSwitch)
		{
			(fpsLimitMenuButton.GetParent() as Control).Visible = false;
		}
		initialFocus = (fullscreenButton.Visible ? fullscreenButton : subtitlesButton);
		if (base.Owner == null)
		{
			ShowSettings();
		}
	}

	public override void _Input(InputEvent @event)
	{
		if (base.Visible && @event.IsActionPressed("ui_cancel"))
		{
			this.SetInputAsHandled(@event);
			HideSettings();
		}
	}

	public void ShowSettings()
	{
		base.Visible = true;
		if (GlobalBackButton.instance != null)
		{
			GlobalBackButton.instance.Push(this);
		}
		if (showHideTween != null)
		{
			showHideTween.Kill();
			showHideTween = null;
		}
		initialFocus.GrabFocus();
		fullscreenButton.SetPressedNoSignal(GameSettings.instance.fullscreen);
		masterVolumeSlider.Value = GameSettings.instance.masterVolume;
		sfxVolumeSlider.Value = GameSettings.instance.sfxVolume;
		voicesVolumeSlider.Value = GameSettings.instance.voicesVolume;
		musicVolumeSlider.Value = GameSettings.instance.musicVolume;
		fpsLimitMenuButton.Text = Array.Find(fpsLimitOptions, (FpsLimitOption o) => o.fps == GameSettings.instance.fpsLimit).label;
		subtitlesButton.SetPressedNoSignal(GameSettings.instance.showSubtitles);
		hapticButton.SetPressedNoSignal(GameSettings.instance.hapticsEnabled);
		reduceGlitchEffectsButton.SetPressedNoSignal(GameSettings.instance.reduceGlitchEffects);
		reduceHintsButton.SetPressedNoSignal(GameSettings.instance.reduceHints);
		showHideTween = CreateTween();
		showHideTween.TweenProperty(this, "modulate:a", 1f, 0.30000001192092896);
		showHideTween.Finished += delegate
		{
			showHideTween = null;
		};
	}

	public void HideSettings()
	{
		if (showHideTween != null)
		{
			showHideTween.Kill();
			showHideTween = null;
		}
		if (GlobalBackButton.instance != null)
		{
			GlobalBackButton.instance.Pop(this);
		}
		EmitSignal(SignalName.DidHide);
		showHideTween = CreateTween();
		showHideTween.TweenProperty(this, "modulate:a", 0f, 0.30000001192092896);
		showHideTween.Finished += delegate
		{
			showHideTween = null;
			base.Visible = false;
		};
	}

	public void OnGlobalBackButtonPressed()
	{
		HideSettings();
	}
}
