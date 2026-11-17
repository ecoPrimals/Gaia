using Godot;

public partial class ProjectedControl : Control
{
	[Export(PropertyHint.None, "")]
	public Node3D target;

	public override void _EnterTree()
	{
		base.VisibilityChanged += Refresh;
	}

	public override void _ExitTree()
	{
		base.VisibilityChanged -= Refresh;
	}

	public override void _Process(double delta)
	{
		Refresh();
	}

	private void Refresh()
	{
		if (DebugOptions.instance.disablePopups)
		{
			base.Visible = false;
		}
		else
		{
			if (target == null || !base.Visible)
			{
				return;
			}
			Camera3D camera3D = target.GetViewport().GetCamera3D();
			if (camera3D != null)
			{
				if (camera3D.IsPositionBehind(target.GlobalPosition))
				{
					base.Position = new Vector2(-10000f, -10000f);
					return;
				}
				Vector2 position = camera3D.UnprojectPosition(target.GlobalPosition);
				position -= GetParent<Control>().GetGlobalRect().Position;
				base.Position = position;
			}
		}
	}
}
