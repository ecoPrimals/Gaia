using Godot;

public partial class LightVisibilityNode : Node3D
{
	[Export(PropertyHint.None, "")]
	public int lightingGroup = 1;

	public override void _EnterTree()
	{
		if (LightsController.instance != null)
		{
			SetTurnedOn(turnedOn: false);
			LightsController.instance.RegisterLightVisibilityNode(this);
		}
		else
		{
			SetTurnedOn(turnedOn: true);
		}
	}

	public void SetTurnedOn(bool turnedOn)
	{
		base.Visible = turnedOn;
	}
}
