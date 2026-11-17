using Godot;

public static class Platform
{
	public static bool isMobile = OS.HasFeature("mobile");

	public static bool isiPhone = OS.HasFeature("ios") && OS.GetModelName().Contains("iPhone");

	public static bool isiPad = OS.HasFeature("ios") && OS.GetModelName().Contains("iPad");

	public static bool isSwitch = OS.HasFeature("nx");

	public static bool isSteamDeck = false;

	public static bool isMac = OS.GetName().ToLower() == "macos";
}
