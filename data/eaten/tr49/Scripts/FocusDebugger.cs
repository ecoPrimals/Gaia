using Godot;

public partial class FocusDebugger : Control
{
	private Node lastFocusOwner;

	public override void _Ready()
	{
		GetViewport().GuiFocusChanged += OnFocusChanged;
	}

	public override void _Process(double delta)
	{
		Control control = GetViewport().GuiGetFocusOwner();
		if (control != lastFocusOwner)
		{
			if (control != null)
			{
				GD.PushError($"New focus owner (process): {control.Name}");
			}
			else
			{
				GD.PushError("New focus owner (process): null");
			}
			lastFocusOwner = control;
		}
	}

	private void OnFocusChanged(Node newNode)
	{
		GD.PushError($"New focus owner (signal): {newNode.Name}");
		lastFocusOwner = newNode;
	}
}
