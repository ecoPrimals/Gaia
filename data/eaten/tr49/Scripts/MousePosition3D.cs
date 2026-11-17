using Godot;

public static class MousePosition3D
{
	public static Vector2 GetMousePositionOnXYPlane(Camera3D camera, Node3D node3D)
	{
		Vector2 mousePosition = camera.GetViewport().GetMousePosition();
		Vector3 vector = camera.ProjectRayOrigin(mousePosition);
		Vector3 dir = camera.ProjectRayNormal(mousePosition);
		Plane plane = new Plane(node3D.GlobalTransform.Basis.Z, node3D.GlobalTransform.Origin);
		Vector3? vector2 = plane.IntersectsRay(vector, dir);
		if (vector2.HasValue)
		{
			Vector3 vector3 = node3D.GetParent<Node3D>().ToLocal(vector2.Value);
			return new Vector2(vector3.X, vector3.Y);
		}
		return Vector2.Zero;
	}
}
