using Godot;

public static class AudioX
{
	private static Curve _curve;

	private static Curve curve
	{
		get
		{
			if (_curve == null)
			{
				_curve = new Curve();
				_curve.MinDomain = 0f;
				_curve.MaxDomain = 1f;
				_curve.MinValue = -80f;
				_curve.MaxValue = 0f;
				_curve.AddPoint(new Vector2(0f, -80f), 0f, 0f, Curve.TangentMode.Free, Curve.TangentMode.Free);
				_curve.AddPoint(new Vector2(0.25f, -20f), 0f, 0f, Curve.TangentMode.Free, Curve.TangentMode.Free);
				_curve.AddPoint(new Vector2(0.5f, -5f), 0f, 0f, Curve.TangentMode.Free, Curve.TangentMode.Free);
				_curve.AddPoint(new Vector2(0.75f, -2f), 0f, 0f, Curve.TangentMode.Free, Curve.TangentMode.Free);
				_curve.AddPoint(new Vector2(1f, 0f), 0f, 0f, Curve.TangentMode.Free, Curve.TangentMode.Free);
				_curve.Bake();
			}
			return _curve;
		}
	}

	public static float VolumeDbFromNormalized(float normalized)
	{
		return curve.Sample(normalized);
	}
}
