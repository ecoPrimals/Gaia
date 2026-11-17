using System.Collections.Generic;
using Godot;

public partial class AsanaFeedbackForm : Control, IGlobalBackButtonHandler
{
	[Signal]
	public delegate void DidHideEventHandler();

	public static AsanaFeedbackForm instance;

	[Export(PropertyHint.None, "")]
	public LineEdit nameLineEdit;

	[Export(PropertyHint.None, "")]
	public LineEdit emailAddressLineEdit;

	[Export(PropertyHint.None, "")]
	public TextEdit textEdit;

	[Export(PropertyHint.None, "")]
	public CheckBox sendSaveDataCheckBox;

	[Export(PropertyHint.None, "")]
	public CheckBox sendScreenshotCheckBox;

	[Export(PropertyHint.None, "")]
	public CheckBox sendLogsCheckBox;

	[Export(PropertyHint.None, "")]
	public Button submitButton;

	[Export(PropertyHint.None, "")]
	public ProgressBar progressBar;

	[Export(PropertyHint.None, "")]
	public Asana asana;

	[Export(PropertyHint.None, "")]
	public string teamDefaultAssignee = "joseph.humfrey@inklestudios.com";

	private byte[] screenshotBytes;

	public override void _EnterTree()
	{
		instance = this;
	}

	public override void _Input(InputEvent @event)
	{
		if (!base.Visible && @event.IsActionPressed("send_feedback") && StoryController.platformCanFeedback)
		{
			this.SetInputAsHandled(@event);
			ShowFeedbackForm();
		}
		if (base.Visible && @event.IsActionPressed("ui_cancel"))
		{
			this.SetInputAsHandled(@event);
			HideFeedbackForm();
		}
	}

	public override void _UnhandledInput(InputEvent @event)
	{
		if (base.Visible)
		{
			this.SetInputAsHandled(@event);
		}
	}

	public override void _Ready()
	{
		submitButton.Pressed += OnSubmitButtonPressed;
		base.Visible = false;
		if (base.Owner == null)
		{
			ShowFeedbackForm();
		}
	}

	public void ShowFeedbackForm()
	{
		if (!base.Visible)
		{
			GlobalBackButton.instance.Push(this);
			screenshotBytes = GetViewport().GetTexture().GetImage().SaveJpgToBuffer();
			base.Visible = true;
			submitButton.Disabled = false;
			progressBar.Modulate = new Color(1f, 1f, 1f, 0f);
			LoadSavedUserData();
			SetInitialFocus();
		}
	}

	public void HideFeedbackForm()
	{
		base.Visible = false;
		GlobalBackButton.instance.Pop(this);
		submitButton.Disabled = false;
		progressBar.Modulate = new Color(1f, 1f, 1f, 0f);
		screenshotBytes = null;
		textEdit.Text = "";
		EmitSignal(SignalName.DidHide);
	}

	private void OnSubmitButtonPressed()
	{
		submitButton.Disabled = true;
		submitButton.ReleaseFocus();
		progressBar.Modulate = Colors.White;
		SaveUserData();
		string description = $"Name: {nameLineEdit.Text}\nEmail: {emailAddressLineEdit.Text}\nGame version: {ProjectSettings.GetSetting("application/config/version")}\nEnvironment: {OS.GetName()} / {OS.GetModelName()} / {OS.GetLocaleLanguage()}\nFeedback: {textEdit.Text}";
		string text = textEdit.Text.Substring(0, Mathf.Min(100, textEdit.Text.Length));
		string asanaTitle = "In-game feedback: " + text;
		List<Asana.Attachment> list = new List<Asana.Attachment>();
		if (sendSaveDataCheckBox.ButtonPressed)
		{
			using FileAccess fileAccess = FileAccess.Open("user://save.json", FileAccess.ModeFlags.Read);
			if (fileAccess != null)
			{
				byte[] buffer = fileAccess.GetBuffer((long)fileAccess.GetLength());
				list.Add(new Asana.Attachment
				{
					filename = "save.json",
					bytes = buffer,
					attachmentType = Asana.AttachmentType.Json
				});
			}
			using FileAccess fileAccess2 = FileAccess.Open("user://prevSave.json", FileAccess.ModeFlags.Read);
			if (fileAccess2 != null)
			{
				byte[] buffer2 = fileAccess2.GetBuffer((long)fileAccess2.GetLength());
				list.Add(new Asana.Attachment
				{
					filename = "prevSave.json",
					bytes = buffer2,
					attachmentType = Asana.AttachmentType.Json
				});
			}
		}
		if (sendScreenshotCheckBox.ButtonPressed)
		{
			list.Add(new Asana.Attachment
			{
				filename = "screenshot.jpg",
				bytes = screenshotBytes,
				attachmentType = Asana.AttachmentType.Jpg
			});
		}
		if (sendLogsCheckBox.ButtonPressed)
		{
			using FileAccess fileAccess3 = FileAccess.Open("user://logs/godot.log", FileAccess.ModeFlags.Read);
			if (fileAccess3 != null)
			{
				byte[] buffer3 = fileAccess3.GetBuffer((long)fileAccess3.GetLength());
				list.Add(new Asana.Attachment
				{
					filename = "godot.log",
					bytes = buffer3,
					attachmentType = Asana.AttachmentType.Txt
				});
			}
			string mostRecentLogFile = GetMostRecentLogFile();
			if (mostRecentLogFile != null)
			{
				using FileAccess fileAccess4 = FileAccess.Open(mostRecentLogFile, FileAccess.ModeFlags.Read);
				if (fileAccess4 != null)
				{
					byte[] buffer4 = fileAccess4.GetBuffer((long)fileAccess4.GetLength());
					list.Add(new Asana.Attachment
					{
						filename = "previous_godot.log",
						bytes = buffer4,
						attachmentType = Asana.AttachmentType.Txt
					});
				}
			}
		}
		asana.Upload(asanaTitle, description, list, teamDefaultAssignee, delegate(float progress, string error)
		{
			progressBar.Value = progress * 100f;
			if (progress >= 1f)
			{
				GD.Print("Task created successfully");
				GetTree().CreateTimer(1.0).Timeout += HideFeedbackForm;
			}
			return false;
		});
	}

	private void LoadSavedUserData()
	{
		string text = PlayerPrefs.Get("feedback_user_name", "");
		string text2 = PlayerPrefs.Get("feedback_user_email", "");
		bool buttonPressed = PlayerPrefs.Get("feedback_send_save_data", defaultValue: true);
		bool buttonPressed2 = PlayerPrefs.Get("feedback_send_screenshot", defaultValue: true);
		bool buttonPressed3 = PlayerPrefs.Get("feedback_send_logs", defaultValue: true);
		if (!string.IsNullOrEmpty(text))
		{
			nameLineEdit.Text = text;
		}
		if (!string.IsNullOrEmpty(text2))
		{
			emailAddressLineEdit.Text = text2;
		}
		sendSaveDataCheckBox.ButtonPressed = buttonPressed;
		sendScreenshotCheckBox.ButtonPressed = buttonPressed2;
		sendLogsCheckBox.ButtonPressed = buttonPressed3;
	}

	private void SaveUserData()
	{
		if (!string.IsNullOrEmpty(nameLineEdit.Text))
		{
			PlayerPrefs.Set("feedback_user_name", nameLineEdit.Text);
		}
		if (!string.IsNullOrEmpty(emailAddressLineEdit.Text))
		{
			PlayerPrefs.Set("feedback_user_email", emailAddressLineEdit.Text);
		}
		PlayerPrefs.Set("feedback_send_save_data", sendSaveDataCheckBox.ButtonPressed);
		PlayerPrefs.Set("feedback_send_screenshot", sendScreenshotCheckBox.ButtonPressed);
		PlayerPrefs.Set("feedback_send_logs", sendLogsCheckBox.ButtonPressed);
	}

	private void SetInitialFocus()
	{
		bool num = !string.IsNullOrEmpty(PlayerPrefs.Get("feedback_user_name", ""));
		bool flag = !string.IsNullOrEmpty(PlayerPrefs.Get("feedback_user_email", ""));
		if (!num)
		{
			nameLineEdit.GrabFocus();
		}
		else if (!flag)
		{
			emailAddressLineEdit.GrabFocus();
		}
		else
		{
			textEdit.GrabFocus();
		}
	}

	private string GetMostRecentLogFile()
	{
		string text = "user://logs/";
		DirAccess dirAccess = DirAccess.Open(text);
		if (dirAccess == null)
		{
			return null;
		}
		string result = null;
		ulong num = 0uL;
		dirAccess.ListDirBegin();
		string next = dirAccess.GetNext();
		while (next != "")
		{
			if (next != "godot.log" && next.EndsWith(".log"))
			{
				string text2 = text + next;
				ulong modifiedTime = FileAccess.GetModifiedTime(text2);
				if (modifiedTime > num)
				{
					num = modifiedTime;
					result = text2;
				}
			}
			next = dirAccess.GetNext();
		}
		dirAccess.ListDirEnd();
		return result;
	}

	public void OnGlobalBackButtonPressed()
	{
		HideFeedbackForm();
	}
}
