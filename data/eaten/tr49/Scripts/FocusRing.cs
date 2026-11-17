using Godot;

public partial class FocusRing : Control
{
	[Export(PropertyHint.None, "")]
	private float ringSize = 1.4f;

	private Control target;

	private float t;

	public override void _Ready()
	{
		base.Modulate = new Color(1f, 1f, 1f, 0f);
	}

	public override void _Process(double delta)
	{
		t += (float)delta;
		Control control = GetViewport().GuiGetFocusOwner();
		if (control != null)
		{
			base.Size = ringSize * control.Size;
			base.PivotOffset = 0.5f * base.Size;
			this.SetGlobalPivotPosition(control.GetGlobalPivotPosition());
			Slider slider = control as Slider;
			Knob knob = control as Knob;
			if (slider != null && slider.manipulating)
			{
				base.Modulate = new Color(1f, 1f, 0f);
				return;
			}
			if (knob != null && knob.manipulating)
			{
				base.Modulate = new Color(1f, 1f, 0f);
				return;
			}
			float a = 0.7f + 0.3f * Mathf.Sin(t * 10f);
			base.Modulate = new Color(1f, 1f, 1f, a);
		}
		else
		{
			base.Modulate = new Color(1f, 1f, 1f, 0f);
			t = 0f;
		}
	}
}
