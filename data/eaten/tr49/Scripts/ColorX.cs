using Godot;

public static class ColorX
{
	public static Color WithAlpha(this Color color, float alpha)
	{
		return new Color(color.R, color.G, color.B, alpha);
	}
}
