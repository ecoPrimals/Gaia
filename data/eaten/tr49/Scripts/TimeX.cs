using Godot;

public static class TimeX
{
	public const float kDampingLerpingExpectedFramerate = 30f;

	public const float targetFrameRateDeltaTime = 1f / 30f;

	public static float Damping(float damping, float deltaTime)
	{
		float num = 1f / 30f;
		float y = deltaTime / num;
		return Mathf.Pow(damping, y);
	}

	public static float Lerping(float lerping, float deltaTime)
	{
		return 1f - Damping(1f - lerping, deltaTime);
	}
}
