using Godot;

public partial class GameSettings : Node
{
	public static GameSettings instance;

	[Export(PropertyHint.None, "")]
	private Curve volumeCurve;

	private int masterBusIndex;

	private int sfxBusIndex;

	private int machineVoicesBusIndex;

	private int voBusIndex;

	private int musicBusIndex;

	private float defaultMasterVolume;

	private float defaultSfxVolume;

	private float defaultMusicVolume;

	private float defaultVoicesVolume;

	public bool fullscreen
	{
		get
		{
			return PlayerPrefs.Get("fullscreen", defaultValue: true);
		}
		set
		{
			PlayerPrefs.Set("fullscreen", value);
			DisplayServer.WindowSetMode((DisplayServer.WindowMode)(value ? 3 : 0));
		}
	}

	public float masterVolume
	{
		get
		{
			return PlayerPrefs.Get("masterVolume", 1f);
		}
		set
		{
			PlayerPrefs.Set("masterVolume", value);
			SetVolumeDb(value, masterBusIndex, defaultMasterVolume);
		}
	}

	public float sfxVolume
	{
		get
		{
			return PlayerPrefs.Get("sfxVolume", 1f);
		}
		set
		{
			PlayerPrefs.Set("sfxVolume", value);
			SetVolumeDb(value, sfxBusIndex, defaultSfxVolume);
		}
	}

	public float voicesVolume
	{
		get
		{
			return PlayerPrefs.Get("voicesVolume", 1f);
		}
		set
		{
			PlayerPrefs.Set("voicesVolume", value);
			SetVolumeDb(value, machineVoicesBusIndex, defaultVoicesVolume);
			SetVolumeDb(value, voBusIndex, defaultVoicesVolume);
		}
	}

	public float musicVolume
	{
		get
		{
			return PlayerPrefs.Get("musicVolume", 1f);
		}
		set
		{
			PlayerPrefs.Set("musicVolume", value);
			SetVolumeDb(value, musicBusIndex, defaultMusicVolume);
		}
	}

	public int fpsLimit
	{
		get
		{
			return PlayerPrefs.Get("fpsLimit", 60);
		}
		set
		{
			PlayerPrefs.Set("fpsLimit", value);
			Engine.MaxFps = value;
		}
	}

	public bool showSubtitles
	{
		get
		{
			return PlayerPrefs.Get("show_subtitles", defaultValue: true);
		}
		set
		{
			PlayerPrefs.Set("show_subtitles", value);
		}
	}

	public bool hapticsEnabled
	{
		get
		{
			return PlayerPrefs.Get("haptic_enabled", defaultValue: true);
		}
		set
		{
			PlayerPrefs.Set("haptic_enabled", value);
		}
	}

	public bool reduceGlitchEffects
	{
		get
		{
			return PlayerPrefs.Get("reduce_glitch_effects", defaultValue: false);
		}
		set
		{
			PlayerPrefs.Set("reduce_glitch_effects", value);
		}
	}

	public bool reduceHints
	{
		get
		{
			return PlayerPrefs.Get("reduce_hints", defaultValue: false);
		}
		set
		{
			PlayerPrefs.Set("reduce_hints", value);
		}
	}

	private void SetVolumeDb(float valueNorm, int busIndex, float defaultDb)
	{
		float weight = volumeCurve.Sample(valueNorm);
		float volumeDb = Mathf.Lerp(-80f, defaultDb, weight);
		AudioServer.SetBusVolumeDb(busIndex, volumeDb);
	}

	public override void _EnterTree()
	{
		instance = this;
	}

	public override void _Ready()
	{
		if (!OS.HasFeature("editor"))
		{
			DisplayServer.WindowSetMode((DisplayServer.WindowMode)(fullscreen ? 3 : 0));
		}
		masterBusIndex = AudioServer.GetBusIndex("Master");
		sfxBusIndex = AudioServer.GetBusIndex("SFX");
		machineVoicesBusIndex = AudioServer.GetBusIndex("MachineVoices");
		voBusIndex = AudioServer.GetBusIndex("VO");
		musicBusIndex = AudioServer.GetBusIndex("Music");
		defaultMasterVolume = AudioServer.GetBusVolumeDb(masterBusIndex);
		defaultSfxVolume = AudioServer.GetBusVolumeDb(sfxBusIndex);
		defaultVoicesVolume = AudioServer.GetBusVolumeDb(machineVoicesBusIndex);
		defaultMusicVolume = AudioServer.GetBusVolumeDb(musicBusIndex);
		masterVolume = masterVolume;
		sfxVolume = sfxVolume;
		voicesVolume = voicesVolume;
		musicVolume = musicVolume;
		fpsLimit = fpsLimit;
	}
}
