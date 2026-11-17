using Godot;

public partial class LitSprite3D : Sprite3D
{
	[Export(PropertyHint.None, "")]
	public int lightingGroup = 1;

	[Export(PropertyHint.None, "")]
	public Texture2D litTexture;

	[Export(PropertyHint.None, "")]
	public Texture2D unlitTexture;

	[Export(PropertyHint.None, "")]
	public Color litColor = new Color(1f, 1f, 1f);

	[Export(PropertyHint.None, "")]
	public Color unlitColor = new Color(0f, 0f, 0f);

	private Texture2D originalTexture;

	private bool isTurnedOn;

	public override void _EnterTree()
	{
		originalTexture = base.Texture;
		if (LightsController.instance != null)
		{
			SetTurnedOn(LightsController.instance.isTurnedOn);
			LightsController.instance.RegisterLitSprite3D(this);
		}
		else
		{
			SetTurnedOn(turnedOn: true);
		}
	}

	public void SetTurnedOn(bool turnedOn)
	{
		isTurnedOn = turnedOn;
		if (litTexture != null)
		{
			Texture2D texture2D = litTexture ?? originalTexture;
			Texture2D texture2D2 = unlitTexture ?? originalTexture;
			base.Texture = (turnedOn ? texture2D : texture2D2);
		}
		if (turnedOn)
		{
			base.Modulate = litColor;
		}
		else
		{
			base.Modulate = unlitColor;
		}
	}
}
