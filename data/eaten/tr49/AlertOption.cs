using System;

public struct AlertOption
{
	public string text;

	public Action action;

	public bool isPrimary;

	public bool isCancel;

	public bool dontCloseOnAction;

	public static AlertOption Primary(string text, Action action)
	{
		return new AlertOption
		{
			text = text,
			action = action,
			isPrimary = true
		};
	}

	public static AlertOption Secondary(string text, Action action)
	{
		return new AlertOption
		{
			text = text,
			action = action
		};
	}

	public static AlertOption Cancel(Action action = null)
	{
		return new AlertOption
		{
			text = "Cancel",
			action = action,
			isCancel = true
		};
	}
}
