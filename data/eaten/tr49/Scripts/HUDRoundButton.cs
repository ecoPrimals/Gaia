using Godot;

public partial class HUDRoundButton : TextureButton
{
	[Export(PropertyHint.None, "")]
	private Texture2D normalInnerImage;

	[Export(PropertyHint.None, "")]
	private Texture2D highlightInnerImage;

	[Export(PropertyHint.None, "")]
	private Texture2D disabledInnerImage;

	[Export(PropertyHint.None, "")]
	private float pressedOffsetYNorm = 0.05f;

	[Export(PropertyHint.None, "")]
	private AudioStream clickDownSFX;

	[Export(PropertyHint.None, "")]
	private AudioStream clickUpSFX;

	[Export(PropertyHint.None, "")]
	private AudioStream clickHoverSFX;

	[Export(PropertyHint.None, "")]
	private AudioStream clickUnhoverSFX;

	private TextureRect innerTextureRect;

	private TextureRect glowTextureRect;

	private Vector2 innerTextureOriginalPosition;

	private AudioStreamPlayer clickSFXPlayer;

	private bool mouseInside;

	private bool buttonDown;

	private bool pressing;

	private bool _highlighted;

	private float glowFade;

	public bool highlighted
	{
		get
		{
			return _highlighted;
		}
		set
		{
			_highlighted = value;
			UpdateState();
		}
	}

	public new bool Disabled
	{
		get
		{
			return base.Disabled;
		}
		set
		{
			base.Disabled = value;
			UpdateState();
		}
	}

	public void PlayPressedSound()
	{
		if (!Disabled)
		{
			PlaySFX(clickDownSFX);
			GetTree().CreateTimer(0.20000000298023224).Timeout += delegate
			{
				PlaySFX(clickUpSFX, 0.6f);
			};
		}
	}

	public override void _Ready()
	{
		innerTextureRect = GetNode<TextureRect>("InnerImage");
		glowTextureRect = GetNode<TextureRect>("Glow");
		glowTextureRect.Texture = highlightInnerImage;
		base.MouseEntered += OnMouseEntered;
		base.MouseExited += OnMouseExited;
		base.ButtonDown += OnButtonDown;
		base.ButtonUp += OnButtonUp;
		innerTextureOriginalPosition = innerTextureRect.Position;
		clickSFXPlayer = new AudioStreamPlayer();
		clickSFXPlayer.Bus = "SFX";
		AddChild(clickSFXPlayer, forceReadableName: false, InternalMode.Disabled);
	}

	public override void _Process(double delta)
	{
		float num = 0.3f;
		float to = ((highlighted && !Disabled) ? 1f : 0f);
		glowFade = Mathf.MoveToward(glowFade, to, (float)delta / num);
		float num2 = (float)Time.GetTicksMsec() * 0.001f;
		float num3 = 0.65f;
		float weight = Mathf.Abs(Mathf.Sin(num2 * 8f) * 0.5f + 0.5f);
		glowTextureRect.Modulate = new Color(1f, 1f, 1f, glowFade * Mathf.Lerp(num3, 1f, weight));
	}

	private void UpdateState()
	{
		bool num = pressing;
		pressing = mouseInside && buttonDown;
		if (num != pressing)
		{
			float y = (pressing ? (pressedOffsetYNorm * base.Size.Y) : 0f);
			innerTextureRect.Position = innerTextureOriginalPosition + new Vector2(0f, y);
		}
		if (Disabled)
		{
			innerTextureRect.Texture = disabledInnerImage;
		}
		else
		{
			innerTextureRect.Texture = normalInnerImage;
		}
	}

	private void PlaySFX(AudioStream stream, float volumeScale = 1f)
	{
		clickSFXPlayer.Stop();
		clickSFXPlayer.Stream = stream;
		clickSFXPlayer.Play();
		clickSFXPlayer.VolumeDb = AudioX.VolumeDbFromNormalized(volumeScale);
		if (stream == clickDownSFX)
		{
			Haptic.instance.Tap();
		}
	}

	private void OnMouseEntered()
	{
		mouseInside = true;
		UpdateState();
		if (!Disabled)
		{
			PlaySFX(clickHoverSFX);
		}
	}

	private void OnMouseExited()
	{
		mouseInside = false;
		UpdateState();
		if (!Disabled)
		{
			PlaySFX(clickUnhoverSFX);
		}
	}

	private void OnButtonDown()
	{
		buttonDown = true;
		UpdateState();
		if (!Disabled)
		{
			PlaySFX(clickDownSFX);
		}
	}

	private void OnButtonUp()
	{
		buttonDown = false;
		UpdateState();
		if (!Disabled)
		{
			PlaySFX(clickUpSFX);
		}
	}
}
