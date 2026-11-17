using System.Collections.Generic;
using System.Text.RegularExpressions;
using Godot;

public partial class SubtitleView : Control
{
	[Signal]
	public delegate void DidHideEventHandler(SubtitleView subtitleView);

	[Export(PropertyHint.None, "")]
	private Control shadow;

	[Export(PropertyHint.None, "")]
	private TextureRect portrait;

	[Export(PropertyHint.None, "")]
	private float spaceWidth = 10f;

	[Export(PropertyHint.None, "")]
	private float lineHeight = 50f;

	[Export(PropertyHint.None, "")]
	private float preAudioShowDelay = 1f;

	[Export(PropertyHint.None, "")]
	private float postAudioHideDelay = 1f;

	[Export(PropertyHint.None, "")]
	private float fadeTime = 0.5f;

	[Export(PropertyHint.None, "")]
	private float fadeInDelayPerWord = 0.1f;

	[Export(PropertyHint.None, "")]
	private float fadeInPunctuationDelay = 0.3f;

	[Export(PropertyHint.None, "")]
	private float readTimeWhenFullyVisible = 1f;

	[Export(PropertyHint.None, "")]
	private float maxShadowOpacity = 0.5f;

	[Export(PropertyHint.None, "")]
	private float portraitMarginX = 6f;

	[Export(PropertyHint.None, "")]
	private float portraitOffsetY = -4f;

	private Dictionary<string, string> characterTagToPortraitName = new Dictionary<string, string>
	{
		{ "VOICE", "liam" },
		{ "LIAM", "liam" },
		{ "VO", "liam" },
		{ "ME", "AbbiportraitYoung" },
		{ "CC", "Cecil_Portrait" },
		{ "AC", "Aliz_Portrait" },
		{ "SR", "soldier" }
	};

	private string fallbackPortraitName = "liam";

	private Regex speakerTagRegex = new Regex("\\s*([\\w_]+):\\s*");

	private Tween showTween;

	private string voLine;

	private bool hiding;

	private List<RichTextLabel> labels = new List<RichTextLabel>();

	private List<float> wordOffsets = new List<float>();

	private double _setupTimeMsec;

	public bool syncingToAudio { get; private set; }

	public float age => (float)((double)Time.GetTicksMsec() - _setupTimeMsec) / 1000f;

	public void Setup(string voLine, bool syncingToAudio)
	{
		this.syncingToAudio = syncingToAudio;
		this.voLine = voLine;
		_setupTimeMsec = Time.GetTicksMsec();
		string text = voLine;
		string text2 = null;
		string text3 = null;
		Match match = speakerTagRegex.Match(voLine);
		if (match.Success)
		{
			text3 = match.Groups[1].Value;
			text2 = ((!characterTagToPortraitName.TryGetValue(text3, out var value)) ? fallbackPortraitName : value);
			text = voLine.Substring(match.Length).Trim();
		}
		portrait.Visible = false;
		if (text2 != null)
		{
			string path = "res://Images/Characters/Portraits/" + text2 + ".png";
			if (ResourceLoader.Exists(path))
			{
				portrait.Texture = ResourceLoader.Load<Texture2D>(path, null, ResourceLoader.CacheMode.Reuse);
				portrait.Visible = true;
			}
			else
			{
				GD.PushError($"Portrait image for character tag '{text3}' not found: {text2}.png");
			}
		}
		string[] array = text.Split(' ');
		foreach (string text4 in array)
		{
			RichTextLabel richTextLabel = new RichTextLabel();
			if (!string.IsNullOrEmpty(text4))
			{
				richTextLabel.Name = text4;
			}
			richTextLabel.Text = text4;
			richTextLabel.FitContent = true;
			richTextLabel.ScrollActive = false;
			richTextLabel.AutowrapMode = TextServer.AutowrapMode.Off;
			richTextLabel.Modulate = new Color(1f, 1f, 1f, 0f);
			labels.Add(richTextLabel);
			AddChild(richTextLabel, forceReadableName: false, InternalMode.Disabled);
		}
		base.Size = PerformLayout();
		float num = AnimateIn(syncingToAudio ? preAudioShowDelay : 0f);
		if (!syncingToAudio)
		{
			GetTree().CreateTimer(num + readTimeWhenFullyVisible).Timeout += delegate
			{
				Hide(audioDidJustFinish: false);
			};
		}
	}

	private Vector2 PerformLayout()
	{
		float availableWidth = base.Size.X;
		Vector2 result = new Vector2(availableWidth, 0f);
		float x = 0f;
		float y = 0f;
		int firstWordIndex = 0;
		float num = 0f;
		for (int i = 0; i < labels.Count; i++)
		{
			Vector2 combinedMinimumSize = labels[i].GetCombinedMinimumSize();
			if (x + combinedMinimumSize.X > availableWidth)
			{
				PositionWords(firstWordIndex, i - 1);
				x = 0f;
				y += lineHeight;
				firstWordIndex = i;
			}
			wordOffsets.Add(x);
			x += combinedMinimumSize.X + spaceWidth;
			num = Mathf.Max(num, x);
		}
		PositionWords(firstWordIndex, labels.Count - 1);
		wordOffsets.Clear();
		result.Y = y + lineHeight;
		shadow.Size = new Vector2(num - 40f, result.Y - 40f);
		shadow.Position = new Vector2(0.5f * availableWidth - 0.5f * num + 20f, 20f);
		if (portrait.Visible)
		{
			portrait.Position = new Vector2(0.5f * availableWidth - 0.5f * num - portrait.Size.X - portraitMarginX, 0.5f * lineHeight - 0.5f * portrait.Size.Y + portraitOffsetY);
		}
		return result;
		void PositionWords(int num4, int lastWordIndex)
		{
			float num2 = x;
			float num3 = (availableWidth - num2) / 2f;
			for (int j = num4; j <= lastWordIndex; j++)
			{
				labels[j].Position = new Vector2(num3 + wordOffsets[j], y);
			}
		}
	}

	private float AnimateIn(float initialDelay)
	{
		showTween = CreateTween().SetParallel();
		float num = initialDelay;
		foreach (RichTextLabel label in labels)
		{
			showTween.TweenProperty(label, "modulate", new Color(1f, 1f, 1f), fadeTime).SetDelay(num);
			num += fadeInDelayPerWord;
			if (label.Text.Contains(".") || label.Text.Contains(",") || label.Text.Contains("!") || label.Text.Contains("?") || label.Text.Contains(":") || label.Text.Contains(";"))
			{
				num += fadeInPunctuationDelay;
			}
		}
		shadow.Modulate = new Color(1f, 1f, 1f, 0f);
		showTween.TweenProperty(shadow, "modulate", new Color(1f, 1f, 1f, maxShadowOpacity), fadeTime).SetDelay(initialDelay);
		float num2 = 0.3f * fadeTime;
		float num3 = Mathf.Max(initialDelay - 0.3f, 0f);
		portrait.Modulate = new Color(1f, 1f, 1f, 0f);
		portrait.Scale = new Vector2(0.5f, 0.5f);
		showTween.TweenProperty(portrait, "modulate", new Color(1f, 1f, 1f), num2).SetDelay(num3);
		showTween.TweenProperty(portrait, "scale", new Vector2(1f, 1f), num2).SetDelay(num3).SetTrans(Tween.TransitionType.Spring)
			.SetEase(Tween.EaseType.Out);
		showTween.Finished += delegate
		{
			showTween = null;
		};
		return num + fadeTime;
	}

	public void Hide(bool audioDidJustFinish, bool fast = false, bool immediate = false)
	{
		if (hiding)
		{
			return;
		}
		hiding = true;
		if (immediate)
		{
			QueueFree();
			EmitSignal(SignalName.DidHide, this);
			return;
		}
		float delayBeforeHide = ((audioDidJustFinish && !fast) ? postAudioHideDelay : 0f);
		if (showTween != null && !fast)
		{
			showTween.Finished += delegate
			{
				CreateAndRunHideTween(delayBeforeHide, fast);
			};
		}
		else
		{
			CreateAndRunHideTween(delayBeforeHide, fast);
		}
	}

	private void CreateAndRunHideTween(float hideDelay, bool fast)
	{
		float num = (fast ? 0.15f : fadeTime);
		Tween tween = CreateTween();
		tween.TweenProperty(this, "modulate", new Color(1f, 1f, 1f, 0f), num).SetDelay(fast ? 0f : hideDelay);
		tween.Finished += delegate
		{
			if (showTween != null)
			{
				showTween.Kill();
				showTween = null;
			}
			EmitSignal(SignalName.DidHide, this);
			QueueFree();
		};
	}
}
