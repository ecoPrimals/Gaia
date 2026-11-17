using Godot;

public static class NodeExtensions
{
	public static void SetInputAsHandled(this Node node, InputEvent @event)
	{
		node.GetViewport().SetInputAsHandled();
	}
}
