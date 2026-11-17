using System.Threading.Tasks;
using Godot;

public partial class Main : Node
{
	public override async void _Ready()
	{
		Node node = GetNode("Steam");
		if (node != null && node.Get("is_steam_deck").AsBool())
		{
			Platform.isSteamDeck = true;
			PrimaryInputManager.instance.RefreshBasedOnConnectedGamepadCount();
		}
		await ToSignal(GetTree(), "process_frame");
		if (SaveLoadManager.instance.TryLoad())
		{
			GD.Print("Loaded save file.");
		}
		await Task.Delay(300);
		StoryController.instance.BeginOrSetupFromLoadedState();
	}
}
