using Godot;

public partial class PopupManager : Control
{
	[Export(PropertyHint.None, "")]
	public Popup titlePopup;

	[Export(PropertyHint.None, "")]
	public Popup intercomPopup;

	[Export(PropertyHint.None, "")]
	public Popup notebookPopup;

	[Export(PropertyHint.None, "")]
	public Popup cornerPopup;

	[Export(PropertyHint.None, "")]
	public HUDRoundButton notebookButton;

	public static PopupManager instance;

	private Popup[] allPopups;

	public void Prepare(string lines, string namedPopup, Popup.Priority priority)
	{
		if (DebugOptions.instance.disablePopups)
		{
			return;
		}
		string[] array = lines.Split('\n');
		string line = array[0];
		string line2 = ((array.Length > 1) ? array[1] : null);
		if (namedPopup == "notebook")
		{
			if (notebookButton.Visible)
			{
				if (cornerPopup.Visible)
				{
					cornerPopup.Hide();
				}
				notebookPopup.Prepare(line, line2, priority);
			}
			else
			{
				cornerPopup.Prepare(line, line2, priority);
			}
		}
		else
		{
			GetPopup(namedPopup).Prepare(line, line2, priority);
		}
	}

	private Popup GetPopup(string namedPopup)
	{
		switch (namedPopup)
		{
		case "title":
			return titlePopup;
		case "intercom":
			return intercomPopup;
		case "notebook":
			return notebookPopup;
		case "corner":
			return cornerPopup;
		default:
			GD.PushError("Unhandled popup: " + namedPopup);
			return null;
		}
	}

	public void ClearPopup(string namedPopup)
	{
		GetPopup(namedPopup).Clear();
	}

	public void ShowPendingPopups()
	{
		Popup[] array = allPopups;
		for (int i = 0; i < array.Length; i++)
		{
			array[i].ShowIfPending();
		}
	}

	public void HideAll()
	{
		Popup[] array = allPopups;
		for (int i = 0; i < array.Length; i++)
		{
			array[i].Hide();
		}
	}

	public override void _Ready()
	{
		instance = this;
		allPopups = new Popup[4] { titlePopup, intercomPopup, notebookPopup, cornerPopup };
	}

	public void DebugToggleTitlePopup()
	{
		if (titlePopup.Visible)
		{
			titlePopup.Hide();
		}
		else
		{
			titlePopup.Prepare("This is a test popup from DebugTest!", null, Popup.Priority.ExplicitInk);
		}
	}

	public void DebugToggleIntercomPopup()
	{
		if (intercomPopup.Visible)
		{
			intercomPopup.Hide();
		}
		else
		{
			intercomPopup.Prepare("This is a test popup from DebugTest!", null, Popup.Priority.ExplicitInk);
		}
	}

	public void DebugToggleNotebookPopup()
	{
		if (notebookPopup.Visible)
		{
			notebookPopup.Hide();
		}
		else
		{
			notebookPopup.Prepare("This is a test popup from DebugTest!", null, Popup.Priority.ExplicitInk);
		}
	}
}
