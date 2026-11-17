using Godot;

public partial class MachineScreen : Control
{
	[Export(PropertyHint.None, "")]
	public SubViewport[] Viewports;

	[Export(PropertyHint.None, "")]
	public Vector2 fudgeScale = new Vector2(0.988f, 0.988f);

	[Export(PropertyHint.None, "")]
	public Vector2 fudgeOffset = new Vector2(5f, 0f);

	public override void _Input(InputEvent @event)
	{
		for (int i = 0; i < Viewports.Length; i++)
		{
			InputEvent inputEvent = (InputEvent)@event.Duplicate();
			if (inputEvent is InputEventMouse inputEventMouse)
			{
				Vector2 size = base.Size;
				Vector2I size2 = Viewports[i].Size;
				inputEventMouse.Position = (inputEventMouse.Position - base.Position) * (size2 / size) * fudgeScale + fudgeOffset;
			}
			Viewports[i].PushInput(inputEvent);
		}
	}
}
