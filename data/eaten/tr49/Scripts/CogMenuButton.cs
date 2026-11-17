using Godot;

public partial class CogMenuButton : Button
{
	public override void _Ready()
	{
		base.Visible = Platform.isMobile;
	}
}
