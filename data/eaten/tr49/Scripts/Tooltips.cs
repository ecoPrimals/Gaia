using System.Collections.Generic;
using Godot;

public partial class Tooltips : Control
{
	[Export(PropertyHint.None, "")]
	public PackedScene tooltipPackedScene;

	[Export(PropertyHint.None, "")]
	public Camera3D camera;

	public static Tooltips instance;

	private List<Tooltip> tooltips = new List<Tooltip>();

	public override void _Ready()
	{
		instance = this;
	}

	public void ShowTooltip(Control targetControl, string text, string tag = null, Tooltip.Direction direction = Tooltip.Direction.Down, float offsetX = 0f, float offsetY = 0f, float delay = 0f)
	{
		if (DebugOptions.instance.disableTooltips)
		{
			return;
		}
		foreach (Tooltip tooltip2 in tooltips)
		{
			if (tooltip2.targetControl == targetControl)
			{
				tooltip2.label.Text = text;
				UpdatePositionFromControl(tooltip2, direction);
				return;
			}
		}
		Tooltip tooltip = tooltipPackedScene.Instantiate<Tooltip>(PackedScene.GenEditState.Disabled);
		tooltip.Setup(targetControl, null, text, tag, offsetX, offsetY);
		tooltip.FadeIn(delay);
		AddChild(tooltip, forceReadableName: false, InternalMode.Disabled);
		tooltips.Add(tooltip);
		UpdatePositionFromControl(tooltip, direction);
	}

	public void ShowTooltip(Vector3 targetPosition3D, string text, string tag, Tooltip.Direction direction = Tooltip.Direction.Down, float offsetX = 0f, float offsetY = 0f, float delay = 0f)
	{
		if (DebugOptions.instance.disableTooltips)
		{
			return;
		}
		foreach (Tooltip tooltip2 in tooltips)
		{
			if (tooltip2.tag == tag)
			{
				tooltip2.label.Text = text;
				tooltip2.targetPosition3D = targetPosition3D;
				tooltip2.offset = new Vector2(offsetX, offsetY);
				UpdatePositionFromPosition3D(tooltip2, direction);
				return;
			}
		}
		Tooltip tooltip = tooltipPackedScene.Instantiate<Tooltip>(PackedScene.GenEditState.Disabled);
		tooltip.Setup(null, targetPosition3D, text, tag, offsetX, offsetY);
		tooltip.FadeIn(delay);
		AddChild(tooltip, forceReadableName: false, InternalMode.Disabled);
		tooltips.Add(tooltip);
		UpdatePositionFromPosition3D(tooltip, direction);
	}

	public void RemoveTooltip(string tag)
	{
		for (int num = tooltips.Count - 1; num >= 0; num--)
		{
			Tooltip tooltip = tooltips[num];
			if (tooltip.tag == tag && !tooltip.fadingOut)
			{
				tooltip.FadeOut(0f, delegate
				{
					if (tooltips.Remove(tooltip))
					{
						tooltip.QueueFree();
					}
				});
			}
		}
	}

	public override void _Process(double delta)
	{
		for (int num = tooltips.Count - 1; num >= 0; num--)
		{
			Tooltip tooltip = tooltips[num];
			if (!tooltip.fadingOut && !tooltip.isValid)
			{
				tooltip.FadeOut(0f, delegate
				{
					if (tooltips.Remove(tooltip))
					{
						tooltip.QueueFree();
					}
				});
			}
			else if (tooltip.targetControl != null)
			{
				UpdatePositionFromControl(tooltip, tooltip.direction);
			}
		}
	}

	private void UpdatePositionFromControl(Tooltip tooltip, Tooltip.Direction direction)
	{
		Vector2 position = tooltip.GetParent<Control>().GetGlobalRect().Position;
		Vector2 position2 = tooltip.targetControl.GetParent<Control>().GetGlobalRect().Position;
		Control targetControl = tooltip.targetControl;
		Vector2 vector = targetControl.Position + targetControl.PivotOffset;
		Vector2 vector2 = targetControl.PivotOffset / targetControl.Size;
		Vector2 vector3 = targetControl.Size * targetControl.Scale;
		Vector2 vector4 = vector - vector2 * vector3;
		Rect2 rect = new Rect2(position2 + vector4, vector3);
		Vector2 vector5 = new Vector2(0.5f * rect.Size.X + rect.Position.X, rect.Position.Y);
		Vector2 vector6 = ((direction == Tooltip.Direction.Down) ? Vector2.Zero : new Vector2(0f, 70f));
		tooltip.Position = vector5 - position + tooltip.offset + vector6;
		tooltip.direction = direction;
	}

	private void UpdatePositionFromPosition3D(Tooltip tooltip, Tooltip.Direction direction)
	{
		Vector2 position = tooltip.GetParent<Control>().GetGlobalRect().Position;
		Vector3? targetPosition3D = tooltip.targetPosition3D;
		Vector2 vector = camera.UnprojectPosition(targetPosition3D.Value) + tooltip.offset - position;
		Vector2 vector2 = ((direction == Tooltip.Direction.Down) ? Vector2.Zero : new Vector2(0f, 70f));
		tooltip.Position = vector + vector2;
		tooltip.direction = direction;
	}
}
