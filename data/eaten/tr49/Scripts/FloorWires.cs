using Godot;

public partial class FloorWires : MeshInstance3D
{
	private ShaderMaterial material;

	public Texture2D lightingTexture
	{
		get
		{
			return (Texture2D)(GodotObject)material.GetShaderParameter("lighting_texture");
		}
		set
		{
			material.SetShaderParameter("lighting_texture", value);
		}
	}

	public override void _EnterTree()
	{
		material = GetActiveMaterial(0) as ShaderMaterial;
		if (LightsController.instance != null)
		{
			LightsController.instance.RegisterFloorWires(this);
		}
	}
}
