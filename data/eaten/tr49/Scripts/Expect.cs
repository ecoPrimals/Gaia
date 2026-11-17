using Godot;

public static class Expect
{
	public static void That(bool condition, string message)
	{
		if (!condition)
		{
			GD.Print("Expected " + message);
		}
	}
}
