using Godot;

public static class TransformExtensions
{
	public static Vector2 GetGlobalPivotPosition(this Control control)
	{
		return control.GetGlobalTransform() * control.PivotOffset;
	}

	public static void SetGlobalPivotPosition(this Control control, Vector2 globalPivotPos)
	{
		Vector2 vector = control.GetGlobalTransform().BasisXform(control.PivotOffset);
		control.SetGlobalPosition(globalPivotPos - vector);
	}
}
