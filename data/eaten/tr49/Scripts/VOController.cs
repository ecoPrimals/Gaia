using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Godot;

public partial class VOController : Control
{
	[Signal]
	public delegate void CompleteOrCancelledEventHandler();

	[Export(PropertyHint.None, "")]
	private PackedScene subtitleScene;

	[Export(PropertyHint.None, "")]
	private AudioStreamPlayer staticAudioPlayer;

	[Export(PropertyHint.None, "")]
	private AudioStreamPlayer walkieTalkieNoise;

	[Export(PropertyHint.None, "")]
	private float subtitleSpacing = 20f;

	public bool cuttable;

	private AudioStreamPlayer currentAudioPlayer;

	private const string staticAudioFile = "Audio/SFX/static.ogg";

	private bool completeOrCancelled = true;

	private int busIndex;

	private float subtitlesTopMargin;

	private List<SubtitleView> visibleSubtitleViews = new List<SubtitleView>();

	private Tween subtitlesLayoutTween;

	private Tween fadeTween;

	private float _initialClarityValue;

	private bool _currentSubtitleIsCentred;

	private SubtitleView currentSubtitleView
	{
		get
		{
			if (visibleSubtitleViews.Count <= 0)
			{
				return null;
			}
			return visibleSubtitleViews[visibleSubtitleViews.Count - 1];
		}
	}

	public override void _Ready()
	{
		busIndex = AudioServer.GetBusIndex("Distortion");
		staticAudioPlayer.Stop();
		if (base.Owner == null)
		{
			TestPresent();
		}
	}

	private async void TestPresent()
	{
		await ToSignal(GetTree().CreateTimer(0.5), "timeout");
		string audioFile = null;
		string[] testTexts = new string[3] { "This is a simple test sentence for the subtitle view.", "A short message", "A longer message that should wrap across multiple lines, and has some punctuation as well as wrapping." };
		int testTextIndex = 0;
		while (true)
		{
			await Present(audioFile, testTexts[testTextIndex]);
			testTextIndex = (testTextIndex + 1) % testTexts.Length;
		}
	}

	public void PlaySFX(string audioFile, Action sfxFinishedCallback = null)
	{
		string text = "res://" + audioFile;
		if (ResourceLoader.Exists(text))
		{
			AudioStream stream = ResourceLoader.Load<AudioStream>(text, null, ResourceLoader.CacheMode.Reuse);
			AudioStreamPlayer sfxAudioPlayer = new AudioStreamPlayer();
			sfxAudioPlayer.Bus = "SFX";
			sfxAudioPlayer.Stream = stream;
			AddChild(sfxAudioPlayer, forceReadableName: false, InternalMode.Disabled);
			sfxAudioPlayer.Play();
			sfxAudioPlayer.Finished += delegate
			{
				sfxAudioPlayer.QueueFree();
				if (sfxFinishedCallback != null)
				{
					sfxFinishedCallback();
				}
			};
		}
		else
		{
			GD.PrintErr("Warning: SFX doesn't exist at path: " + text);
		}
	}

	public async Task Present(string audioFile, string subtitle, bool cuttable = false, float audioClarity = 1f, bool subtitleCentre = false)
	{
		this.cuttable = cuttable;
		bool flag = string.IsNullOrEmpty(subtitle);
		if (currentSubtitleView != null)
		{
			currentSubtitleView.Hide(audioDidJustFinish: false);
		}
		if (currentAudioPlayer != null)
		{
			currentAudioPlayer.QueueFree();
			currentAudioPlayer = null;
		}
		if (!string.IsNullOrEmpty(audioFile))
		{
			string text = "res://" + audioFile;
			if (ResourceLoader.Exists(text))
			{
				AudioStream stream = ResourceLoader.Load<AudioStream>(text, null, ResourceLoader.CacheMode.Reuse);
				currentAudioPlayer = new AudioStreamPlayer();
				currentAudioPlayer.Bus = (flag ? "MachineVoices" : "VO");
				_initialClarityValue = audioClarity;
				currentAudioPlayer.Stream = stream;
				AddChild(currentAudioPlayer, forceReadableName: false, InternalMode.Disabled);
				currentAudioPlayer.Play();
				if (audioClarity < 1f)
				{
					staticAudioPlayer.Play();
					currentAudioPlayer.Bus = "Distortion";
					SetClarity(audioClarity);
					staticAudioPlayer.Play();
				}
				currentAudioPlayer.Finished += delegate
				{
					if (currentSubtitleView != null)
					{
						currentSubtitleView.Hide(audioDidJustFinish: true);
					}
					currentAudioPlayer.QueueFree();
					currentAudioPlayer = null;
					staticAudioPlayer.Stop();
				};
			}
			else
			{
				GD.PrintErr("Warning: VO audio doesn't exist at path: " + text);
			}
		}
		if (!string.IsNullOrEmpty(subtitle) && (subtitleCentre || GameSettings.instance.showSubtitles))
		{
			SubtitleView subtitleView = subtitleScene.Instantiate<SubtitleView>(PackedScene.GenEditState.Disabled);
			AddChild(subtitleView, forceReadableName: false, InternalMode.Disabled);
			subtitleView.Setup(subtitle, currentAudioPlayer != null);
			subtitleView.Name = subtitle;
			_currentSubtitleIsCentred = subtitleCentre;
			subtitleView.DidHide += OnSubtitleViewDidHide;
			if (subtitlesTopMargin == 0f)
			{
				subtitlesTopMargin = subtitleView.Position.Y;
			}
			SubtitleView subtitleView2 = currentSubtitleView;
			visibleSubtitleViews.Add(subtitleView);
			if (subtitleCentre)
			{
				Vector2 position = currentSubtitleView.Position;
				currentSubtitleView.Position = new Vector2(position.X, 500f);
			}
			else if (subtitleView2 != null)
			{
				float num = subtitleView2.Position.Y + subtitleView2.Size.Y;
				Vector2 position2 = currentSubtitleView.Position;
				currentSubtitleView.Position = new Vector2(position2.X, num + subtitleSpacing);
			}
		}
		completeOrCancelled = false;
		await ToSignal(this, SignalName.CompleteOrCancelled);
	}

	private void OnSubtitleViewDidHide(SubtitleView subtitleView)
	{
		if (visibleSubtitleViews.Contains(subtitleView))
		{
			visibleSubtitleViews.Remove(subtitleView);
			AnimateSubtitleViewsLayout();
		}
	}

	private void AnimateSubtitleViewsLayout()
	{
		if (subtitlesLayoutTween != null)
		{
			subtitlesLayoutTween.Kill();
			subtitlesLayoutTween = null;
		}
		if (_currentSubtitleIsCentred || visibleSubtitleViews.Count == 0)
		{
			return;
		}
		float num = subtitlesTopMargin;
		subtitlesLayoutTween = CreateTween().SetParallel();
		foreach (SubtitleView visibleSubtitleView in visibleSubtitleViews)
		{
			subtitlesLayoutTween.TweenProperty(visibleSubtitleView, "position:y", num, 0.20000000298023224);
			num += visibleSubtitleView.Size.Y + subtitleSpacing;
		}
		subtitlesLayoutTween.Finished += delegate
		{
			subtitlesLayoutTween = null;
		};
	}

	public void SetClarity(float clarityValue)
	{
		if (clarityValue >= 0.95f)
		{
			staticAudioPlayer.VolumeDb = -18f;
		}
		else
		{
			clarityValue = Mathf.Clamp(Mathf.Pow(clarityValue, 3.5f), 0f, 1f);
			staticAudioPlayer.VolumeDb = Mathf.Lerp(-8f, -40f, 1f - clarityValue);
		}
		currentAudioPlayer.VolumeDb = Mathf.Lerp(-60f, 0f, clarityValue);
		if (AudioServer.GetBusEffect(busIndex, 0) is AudioEffectDistortion audioEffectDistortion)
		{
			audioEffectDistortion.Drive = 1f - clarityValue;
			audioEffectDistortion.KeepHfHz = Mathf.Lerp(200f, 12000f, clarityValue);
		}
		if (AudioServer.GetBusEffect(busIndex, 1) is AudioEffectFilter audioEffectFilter)
		{
			audioEffectFilter.CutoffHz = Mathf.Lerp(100f, 10000f, clarityValue);
		}
	}

	public void CutIfCuttable()
	{
		if (currentAudioPlayer != null && cuttable)
		{
			Clear();
		}
	}

	public bool Skip()
	{
		float num = ((currentAudioPlayer != null) ? ((float)currentAudioPlayer.GetStreamPlayback().GetPlaybackPosition()) : float.MaxValue);
		float num2 = ((currentSubtitleView != null) ? currentSubtitleView.age : float.MaxValue);
		if ((currentAudioPlayer != null || currentSubtitleView != null) && num > 0.5f && num2 > 0.5f)
		{
			Clear();
			return true;
		}
		return false;
	}

	public void Clear(bool immediate = false)
	{
		foreach (SubtitleView visibleSubtitleView in visibleSubtitleViews)
		{
			visibleSubtitleView.Hide(audioDidJustFinish: false, fast: true, immediate);
		}
		if (immediate)
		{
			visibleSubtitleViews.Clear();
		}
		if (currentAudioPlayer != null)
		{
			currentAudioPlayer.Stop();
			currentAudioPlayer.QueueFree();
			currentAudioPlayer = null;
		}
		staticAudioPlayer.Stop();
		if (!completeOrCancelled)
		{
			completeOrCancelled = true;
			EmitSignal(SignalName.CompleteOrCancelled);
		}
		_initialClarityValue = 0f;
	}

	public override void _Process(double delta)
	{
		if (!completeOrCancelled && (currentSubtitleView == null || currentSubtitleView.syncingToAudio) && currentAudioPlayer == null)
		{
			completeOrCancelled = true;
			EmitSignal(SignalName.CompleteOrCancelled);
		}
		else if (cuttable && currentAudioPlayer != null && _initialClarityValue < 0.95f)
		{
			float num = ((_initialClarityValue < 0.5f) ? 3.5f : 8f);
			float num2 = Mathf.Lerp(_initialClarityValue, 0f, Mathf.Clamp(currentAudioPlayer.GetPlaybackPosition() / num, 0f, 1f));
			SetClarity(num2);
			if (num2 < 0.001f)
			{
				Clear();
			}
		}
	}

	public void PlayWalkieTalkieSFX()
	{
		uint value = GD.Randi() % 4;
		string text = $"WalkeTalkieOn{value}.ogg";
		string path = "res://Audio/SFX/" + text;
		if (ResourceLoader.Exists(path))
		{
			AudioStream stream = ResourceLoader.Load<AudioStream>(path, null, ResourceLoader.CacheMode.Reuse);
			walkieTalkieNoise.Stream = stream;
			walkieTalkieNoise.Play();
		}
	}

	public void SetPaused(bool paused)
	{
		if (currentAudioPlayer != null)
		{
			currentAudioPlayer.StreamPaused = paused;
		}
		if (fadeTween != null)
		{
			fadeTween.Kill();
			fadeTween = null;
		}
		float num = (paused ? 0f : 1f);
		fadeTween = CreateTween();
		fadeTween.TweenProperty(this, "modulate:a", num, 0.20000000298023224);
		fadeTween.Finished += delegate
		{
			fadeTween = null;
		};
	}
}
