using System;
using System.IO;
using System.Linq;
using Godot;

public partial class DebugSavePicker : MenuButton
{
	private struct SaveItem
	{
		public string path;

		public DateTime modified;
	}

	private static bool hasPlayerPrefEnabled;

	private static bool allowSavePicker
	{
		get
		{
			if (hasPlayerPrefEnabled || OS.HasFeature("editor"))
			{
				return true;
			}
			return false;
		}
	}

	public override void _Ready()
	{
		base.AboutToPopup += OnAboutToPopup;
		GetPopup().IdPressed += OnPopupIdPressed;
		hasPlayerPrefEnabled = PlayerPrefs.Get("debugSavePicker", defaultValue: false);
	}

	public override void _Process(double delta)
	{
		if (allowSavePicker)
		{
			if (Input.IsKeyPressed((Key)(Platform.isMac ? 4194327 : 4194326)) && Input.IsKeyPressed(Key.L))
			{
				base.Visible = true;
				RefreshMenuItems();
				GetPopup().Popup();
			}
			else if (base.Visible && !GetPopup().Visible)
			{
				base.Visible = false;
			}
		}
	}

	private void OnAboutToPopup()
	{
		RefreshMenuItems();
	}

	private void RefreshMenuItems()
	{
		PopupMenu popup = GetPopup();
		popup.Clear();
		string text = ProjectSettings.GlobalizePath("user://saves");
		try
		{
			if (!Directory.Exists(text))
			{
				Directory.CreateDirectory(text);
			}
			SaveItem[] array = (from path in Directory.GetFiles(text, "*.json", SearchOption.TopDirectoryOnly)
				select new SaveItem
				{
					path = path,
					modified = File.GetLastWriteTime(path)
				}).ToArray();
			Array.Sort(array, (SaveItem a, SaveItem b) => b.modified.CompareTo(a.modified));
			int num = 0;
			string text2 = ProjectSettings.GlobalizePath("user://save.json");
			popup.AddItem("RELOAD CURRENT SAVE", num, Key.None);
			popup.SetItemMetadata(num, text2);
			num++;
			SaveItem[] array2 = array;
			for (int num2 = 0; num2 < array2.Length; num2++)
			{
				SaveItem saveItem = array2[num2];
				string label = $" {Path.GetFileName(saveItem.path)} [{saveItem.modified:yyyy-MM-dd HH:mm}]";
				popup.AddItem(label, num, Key.None);
				popup.SetItemMetadata(num, saveItem.path);
				num++;
			}
			if (num == 0)
			{
				AddEmptyStateItem(popup);
			}
		}
		catch (Exception ex)
		{
			GD.PrintErr("DebugSavePicker: Failed to list saves in '" + text + "': " + ex.Message);
			AddEmptyStateItem(popup);
		}
	}

	private void AddEmptyStateItem(PopupMenu popup)
	{
		popup.AddItem("No saves found", -1, Key.None);
		int index = popup.ItemCount - 1;
		popup.SetItemDisabled(index, disabled: true);
	}

	private void OnPopupIdPressed(long id)
	{
		PopupMenu popup = GetPopup();
		int itemIndex = popup.GetItemIndex((int)id);
		if (itemIndex >= 0)
		{
			Variant itemMetadata = popup.GetItemMetadata(itemIndex);
			string itemText = popup.GetItemText(itemIndex);
			string text = ((itemMetadata.VariantType == Variant.Type.Nil) ? itemText : itemMetadata.AsString());
			GD.Print("DebugSavePicker: Loading save from '" + text + "'");
			string text2 = ProjectSettings.GlobalizePath("user://save.json");
			string text3 = ProjectSettings.GlobalizePath(text);
			if (text2 != text3)
			{
				File.Copy(text3, text2, overwrite: true);
			}
			StoryController.instance.LoadSave(text);
			base.Visible = false;
		}
	}
}
