using Godot;

public partial class DebugOptions : Resource
{
	private static DebugOptions _instance;

	[Export(PropertyHint.None, "")]
	public bool perfectCoherence;

	[Export(PropertyHint.None, "")]
	public bool debugLogInk;

	[Export(PropertyHint.None, "")]
	public bool debugLogNotebook;

	[Export(PropertyHint.None, "")]
	public bool disableTooltips;

	[Export(PropertyHint.None, "")]
	public bool disablePopups;

	[Export(PropertyHint.None, "")]
	public bool disableButtonPrompts;

	[Export(PropertyHint.None, "")]
	public bool disableScoresView;

	[Export(PropertyHint.None, "")]
	public bool hideIntercomButton;

	[Export(PropertyHint.None, "")]
	public bool neverSave;

	[Export(PropertyHint.None, "")]
	public bool artMode;

	[Export(PropertyHint.None, "")]
	public bool clearAllAchievementsOnLoad;

	private static DebugOptions releaseBuildDebugOptions => new DebugOptions
	{
		debugLogInk = !Platform.isSwitch,
		debugLogNotebook = !Platform.isSwitch
	};

	private static DebugOptions testingBuildDebugOptions => new DebugOptions
	{
		debugLogInk = !Platform.isSwitch,
		debugLogNotebook = !Platform.isSwitch
	};

	public static DebugOptions instance
	{
		get
		{
			if (_instance == null)
			{
				try
				{
					if (Engine.IsEditorHint())
					{
						return null;
					}
					if (OS.HasFeature("editor") && ResourceLoader.Exists("res://debug_options.tres"))
					{
						_instance = ResourceLoader.Load<DebugOptions>("res://debug_options.tres", null, ResourceLoader.CacheMode.Reuse);
					}
					else if (OS.HasFeature("testing_debug_options"))
					{
						_instance = testingBuildDebugOptions;
					}
				}
				catch
				{
					GD.PushError("Failed to load debug options from resource file.");
				}
				if (_instance == null)
				{
					_instance = releaseBuildDebugOptions;
				}
			}
			return _instance;
		}
	}
}
