using Godot;

public partial class LoadingIcon : Control
{
	public static LoadingIcon instance;

	[Export(PropertyHint.None, "")]
	private Label[] charLabels;

	public bool wantsVisible;

	public float fadeDuration = 0.5f;

	public float minTimeToGlitch = 0.5f;

	public float maxTimeToGlitch = 2f;

	public float minGlitchDuration = 0.5f;

	public float maxGlitchDuration = 1f;

	private float stateTimeRemaining;

	private bool isGlitching;

	private int[] nextGlitchChars = new int[3] { 0, 1, 2 };

	private char[] glitchChars = new char[63]
	{
		'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
		'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
		'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3',
		'4', '5', '6', '7', '8', '9', '!', '@', '#', '$',
		'%', '^', '&', '*', '(', ')', '-', '_', '=', '+',
		'[', ']', '{', '}', '|', ':', ';', ',', '.', '<',
		'>', '/', '?'
	};

	public override void _EnterTree()
	{
		base.Modulate = new Color(1f, 1f, 1f, 0f);
		instance = this;
	}

	public override void _Process(double delta)
	{
		float to = (wantsVisible ? 1f : 0f);
		float a = base.Modulate.A;
		float value = Mathf.MoveToward(a, to, (float)delta / fadeDuration);
		base.Modulate = new Color(1f, 1f, 1f, Mathf.Clamp(value, 0f, 1f));
		if (!(a > 0f))
		{
			return;
		}
		stateTimeRemaining -= (float)delta;
		if (stateTimeRemaining < 0f)
		{
			isGlitching = !isGlitching;
			if (isGlitching)
			{
				stateTimeRemaining = (float)GD.RandRange(minGlitchDuration, maxGlitchDuration);
				nextGlitchChars[0] = GD.RandRange(0, charLabels.Length - 1);
				nextGlitchChars[1] = GD.RandRange(0, charLabels.Length - 1);
				nextGlitchChars[2] = GD.RandRange(0, charLabels.Length - 1);
				for (int i = 0; i < charLabels.Length; i++)
				{
					charLabels[i].Modulate = new Color(1f, 1f, 1f, (float)GD.RandRange(0.5, 1.0));
				}
			}
			else
			{
				stateTimeRemaining = (float)GD.RandRange(minTimeToGlitch, maxTimeToGlitch);
				charLabels[0].Text = "T";
				charLabels[1].Text = "R";
				charLabels[2].Text = "-";
				charLabels[3].Text = "4";
				charLabels[4].Text = "9";
				for (int j = 0; j < charLabels.Length; j++)
				{
					charLabels[j].Modulate = new Color(1f, 1f, 1f);
				}
			}
		}
		if (isGlitching && (int)(Time.GetTicksMsec() / 100) % 2 == 0)
		{
			for (int k = 0; k < nextGlitchChars.Length; k++)
			{
				int num = nextGlitchChars[k];
				char c = glitchChars[GD.RandRange(0, glitchChars.Length - 1)];
				charLabels[num].Text = c.ToString();
			}
		}
	}
}
