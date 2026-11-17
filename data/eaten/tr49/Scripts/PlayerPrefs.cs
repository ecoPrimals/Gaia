using System;
using System.Timers;
using Godot;
using Godot.Collections;

public partial class PlayerPrefs : Node
{
	private static readonly object _syncRoot = new object();

	private static readonly Dictionary _data = LoadFromDisk();

	private static readonly TimeSpan _minSaveInterval = TimeSpan.FromSeconds(5.0);

	private static DateTime _lastSaveUtc = DateTime.MinValue;

	private static bool _pendingSave = false;

	private static System.Timers.Timer _debounceTimer;

	private static string prefsFilePath => "user://prefs.json";

	public static string Get(string key, string defaultValue)
	{
		lock (_syncRoot)
		{
			Variant value;
			return _data.TryGetValue(key, out value) ? value.AsString() : defaultValue;
		}
	}

	public static int Get(string key, int defaultValue)
	{
		lock (_syncRoot)
		{
			Variant value;
			return _data.TryGetValue(key, out value) ? value.AsInt32() : defaultValue;
		}
	}

	public static float Get(string key, float defaultValue)
	{
		lock (_syncRoot)
		{
			Variant value;
			return _data.TryGetValue(key, out value) ? value.AsSingle() : defaultValue;
		}
	}

	public static bool Get(string key, bool defaultValue)
	{
		lock (_syncRoot)
		{
			Variant value;
			return _data.TryGetValue(key, out value) ? value.AsBool() : defaultValue;
		}
	}

	public static void Set(string key, string value)
	{
		lock (_syncRoot)
		{
			_data[key] = value;
			ScheduleSaveLocked();
		}
	}

	public static void Set(string key, int value)
	{
		lock (_syncRoot)
		{
			_data[key] = value;
			ScheduleSaveLocked();
		}
	}

	public static void Set(string key, float value)
	{
		lock (_syncRoot)
		{
			_data[key] = value;
			ScheduleSaveLocked();
		}
	}

	public static void Set(string key, bool value)
	{
		lock (_syncRoot)
		{
			_data[key] = value;
			ScheduleSaveLocked();
		}
	}

	public static void Flush()
	{
		lock (_syncRoot)
		{
			SaveToDiskLocked();
		}
	}

	private static void EnsureTimerLocked()
	{
		if (_debounceTimer != null)
		{
			return;
		}
		_debounceTimer = new System.Timers.Timer
		{
			AutoReset = false,
			Enabled = false
		};
		_debounceTimer.Elapsed += delegate
		{
			lock (_syncRoot)
			{
				if (_pendingSave)
				{
					SaveToDiskLocked();
				}
			}
		};
	}

	private static void ScheduleSaveLocked()
	{
		TimeSpan timeSpan = DateTime.UtcNow - _lastSaveUtc;
		if (timeSpan >= _minSaveInterval)
		{
			SaveToDiskLocked();
			return;
		}
		_pendingSave = true;
		EnsureTimerLocked();
		TimeSpan timeSpan2 = _minSaveInterval - timeSpan;
		if (timeSpan2 < TimeSpan.Zero)
		{
			timeSpan2 = TimeSpan.Zero;
		}
		_debounceTimer.Interval = Math.Max(1.0, timeSpan2.TotalMilliseconds);
		_debounceTimer.Stop();
		_debounceTimer.Start();
	}

	private static void SaveToDiskLocked()
	{
		try
		{
			string text = Json.Stringify(_data, "\t");
			using FileAccess fileAccess = FileAccess.Open(prefsFilePath, FileAccess.ModeFlags.Write);
			if (fileAccess != null)
			{
				fileAccess.StoreString(text);
				fileAccess.Close();
				_lastSaveUtc = DateTime.UtcNow;
				_pendingSave = false;
			}
			else
			{
				GD.PrintErr("PlayerPrefs: Failed to open file for writing: " + prefsFilePath);
			}
		}
		catch (Exception ex)
		{
			GD.PrintErr("PlayerPrefs save failed: " + ex.Message);
		}
	}

	private static Dictionary LoadFromDisk()
	{
		Dictionary result = new Dictionary();
		try
		{
			if (!FileAccess.FileExists(prefsFilePath))
			{
				return result;
			}
			using FileAccess fileAccess = FileAccess.Open(prefsFilePath, FileAccess.ModeFlags.Read);
			if (fileAccess == null)
			{
				GD.PrintErr("PlayerPrefs: Failed to open file for reading: " + prefsFilePath);
				return result;
			}
			string asText = fileAccess.GetAsText();
			fileAccess.Close();
			if (string.IsNullOrWhiteSpace(asText))
			{
				return result;
			}
			Variant variant = Json.ParseString(asText);
			if (variant.VariantType != Variant.Type.Dictionary)
			{
				GD.PrintErr($"PlayerPrefs: Result is not a dictionary: {variant.VariantType}");
				return result;
			}
			result = variant.AsGodotDictionary();
		}
		catch (Exception ex)
		{
			GD.PrintErr("PlayerPrefs load failed: " + ex.Message);
		}
		return result;
	}
}
