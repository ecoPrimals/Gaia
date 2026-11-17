using Godot;

public class MathX
{
	public static Vector3 SmoothDamp(Vector3 current, Vector3 target, ref Vector3 currentVelocity, float smoothTime, float maxSpeed, float deltaTime)
	{
		return new Vector3(SmoothDamp(current.X, target.X, ref currentVelocity.X, smoothTime, maxSpeed, deltaTime), SmoothDamp(current.Y, target.Y, ref currentVelocity.Y, smoothTime, maxSpeed, deltaTime), SmoothDamp(current.Z, target.Z, ref currentVelocity.Z, smoothTime, maxSpeed, deltaTime));
	}

	public static float SmoothDamp(float current, float target, ref float currentVelocity, float smoothTime, float maxSpeed, float deltaTime)
	{
		smoothTime = Mathf.Max(0.0001f, smoothTime);
		float num = 2f / smoothTime;
		float num2 = num * deltaTime;
		float num3 = 1f / (1f + num2 + 0.48f * num2 * num2 + 0.235f * num2 * num2 * num2);
		float value = current - target;
		float num4 = target;
		float num5 = maxSpeed * smoothTime;
		value = Mathf.Clamp(value, 0f - num5, num5);
		target = current - value;
		float num6 = (currentVelocity + num * value) * deltaTime;
		currentVelocity = (currentVelocity - num * num6) * num3;
		float num7 = target + (value + num6) * num3;
		if (num4 - current > 0f == num7 > num4)
		{
			num7 = num4;
			currentVelocity = (num7 - num4) / deltaTime;
		}
		return num7;
	}
}
