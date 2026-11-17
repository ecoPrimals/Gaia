using Godot;

public static class InputX
{
	public static Vector2 GetLeftStick()
	{
		Vector2 zero = Vector2.Zero;
		foreach (int connectedJoypad in Input.GetConnectedJoypads())
		{
			Vector2 vector = new Vector2(Input.GetJoyAxis(connectedJoypad, JoyAxis.LeftX), Input.GetJoyAxis(connectedJoypad, JoyAxis.LeftY));
			if (Mathf.Abs(vector.X) > Mathf.Abs(zero.X))
			{
				zero.X = vector.X;
			}
			if (Mathf.Abs(vector.Y) > Mathf.Abs(zero.Y))
			{
				zero.Y = vector.Y;
			}
		}
		return zero;
	}

	public static Vector2I GetDPad()
	{
		Vector2I zero = Vector2I.Zero;
		foreach (int connectedJoypad in Input.GetConnectedJoypads())
		{
			if (Input.IsJoyButtonPressed(connectedJoypad, JoyButton.DpadRight))
			{
				zero.X = 1;
			}
			if (Input.IsJoyButtonPressed(connectedJoypad, JoyButton.DpadLeft))
			{
				zero.X = -1;
			}
			if (Input.IsJoyButtonPressed(connectedJoypad, JoyButton.DpadUp))
			{
				zero.Y = -1;
			}
			if (Input.IsJoyButtonPressed(connectedJoypad, JoyButton.DpadDown))
			{
				zero.Y = 1;
			}
		}
		return zero;
	}
}
