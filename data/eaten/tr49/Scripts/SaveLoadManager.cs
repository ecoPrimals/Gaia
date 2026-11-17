using System;
using Godot;

public partial class SaveLoadManager : Node
{
	private const string saveFileVersionPrefix = "TR49-v";

	private const int saveFileVersion = 1;

	public static SaveLoadManager instance;

	[Export(PropertyHint.None, "")]
	private MachineUI machineUI;

	[Export(PropertyHint.None, "")]
	private BackgroundMusicPlayer backgroundMusicPlayer;

	private DateTime _timeOfLastSave = DateTime.MaxValue;

	public int secondsSinceSave
	{
		get
		{
			if (_timeOfLastSave > DateTime.Now)
			{
				return -1;
			}
			return (int)(DateTime.Now - _timeOfLastSave).TotalSeconds;
		}
	}

	public void ResetSaveTimer()
	{
		_timeOfLastSave = DateTime.Now;
	}

	public override void _EnterTree()
	{
		instance = this;
	}

	public void TrySave()
	{
		if (DebugOptions.instance.neverSave)
		{
			GD.Print("DebugOptions.neverSave is enabled, skipping save.");
			return;
		}
		if (PlayerPrefs.Get("debugNeverSave", defaultValue: false))
		{
			GD.Print("PlayerPrefs.debugNeverSave is enabled, skipping save.");
			return;
		}
		DirAccess dirAccess = DirAccess.Open("user://");
		if (dirAccess != null && dirAccess.FileExists("save.json"))
		{
			if (dirAccess.FileExists("prevSave.json"))
			{
				dirAccess.Remove("prevSave.json");
			}
			dirAccess.Rename("save.json", "prevSave.json");
		}
		string line = StoryController.instance.SaveState();
		using FileAccess fileAccess = FileAccess.Open("user://save.json", FileAccess.ModeFlags.Write);
		fileAccess.StoreLine($"{"TR49-v"}{1}");
		fileAccess.StoreLine(line);
		fileAccess.StoreLine(StoryController.instance.currentCardCode);
		fileAccess.StoreLine(StoryController.instance.UIUnlockStateReached.ToString());
		fileAccess.StoreLine(backgroundMusicPlayer.currentMusicFromInk);
		string text = ProjectSettings.GlobalizePath("user://save.json");
		GD.Print("Saved game to: " + text);
		ResetSaveTimer();
	}

	public bool TryLoad(string filePathOverride = null)
	{
		using FileAccess fileAccess = FileAccess.Open(filePathOverride ?? ProjectSettings.GlobalizePath("user://save.json"), FileAccess.ModeFlags.Read);
		if (fileAccess == null)
		{
			GD.Print("No save file found.");
			return false;
		}
		try
		{
			string line = fileAccess.GetLine();
			if (!line.StartsWith("TR49-v"))
			{
				throw new Exception("Save file is not a valid TR49 save file.");
			}
			if (int.Parse(line.Substring("TR49-v".Length)) > 1)
			{
				throw new Exception("Couldn't load save file because it was made with a newer incompatible version of the game.");
			}
			string line2 = fileAccess.GetLine();
			string text = fileAccess.GetLine();
			if (text.Length != 4)
			{
				if (string.IsNullOrEmpty(text))
				{
					GD.PushWarning("Machine code loaded from save file was empty instead of having 4 digits. Resetting to AA00.");
				}
				else
				{
					GD.PushWarning("Machine code loaded from save file wasn't the expected 4 digits: " + text + ". Resetting to AA00.");
				}
				text = "AA00";
			}
			string text2 = fileAccess.GetLine();
			if (text2.Length != 1)
			{
				GD.PushError("UI unlock state wasn't a single digit as expected: " + text2);
				text2 = "1";
			}
			string line3 = fileAccess.GetLine();
			StoryController.instance.LoadState(line2, text, int.Parse(text2), line3);
		}
		catch (Exception ex)
		{
			MoveIncompatibleSaveFileToBackup();
			GD.Print("Error loading save file. Moved to save-couldnt-load.json and starting new game. " + ex.Message);
			return false;
		}
		return true;
	}

	private void MoveIncompatibleSaveFileToBackup()
	{
		DirAccess dirAccess = DirAccess.Open("user://");
		if (dirAccess != null && dirAccess.FileExists("save.json"))
		{
			dirAccess.Rename("save.json", "save-couldnt-load.json");
		}
	}
}
