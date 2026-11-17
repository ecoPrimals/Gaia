using System;
using System.Collections.Generic;
using Godot;

public partial class MachineAudio : Node
{
	[Export(PropertyHint.None, "")]
	private Viewport machineViewport;

	[ExportGroup("Gear Shifter", "")]
	[Export(PropertyHint.None, "")]
	private AudioStream gearSlideLoopSound;

	[Export(PropertyHint.None, "")]
	private AudioStream[] gearMovementStartSounds;

	[Export(PropertyHint.None, "")]
	private AudioStream gearHomeClunkSound;

	[Export(PropertyHint.None, "")]
	private float gearSlideLoopMaxSpeed = 0.1f;

	[Export(PropertyHint.None, "")]
	private AudioStream[] gearPassedCornerSounds;

	[Export(PropertyHint.None, "")]
	private AudioStream[] gearArrivedInGearSounds;

	[Export(PropertyHint.None, "")]
	private AudioStream[] gearReturnedToHomeSounds;

	[Export(PropertyHint.None, "")]
	private float gearShiftPitchVariance = 0.1f;

	[ExportGroup("Circle Selector", "")]
	[Export(PropertyHint.None, "")]
	private AudioStream circleSelectorKnobLoopSound;

	[Export(PropertyHint.None, "")]
	private float circleSelectorKnobLoopMaxSpeed = 0.1f;

	[Export(PropertyHint.None, "")]
	private AudioStream[] circleSelectorChangedCharacterSounds;

	[Export(PropertyHint.None, "")]
	private float circleSelectorChangedCharacterPitchVariance = 0.1f;

	[Export(PropertyHint.None, "")]
	private AudioStream[] circleSelectorPressedCharacterSounds;

	[Export(PropertyHint.None, "")]
	private float circleSelectorPressedCharacterPitchScale = 0.1f;

	[ExportGroup("Flipperty Digits, Batman!", "")]
	[Export(PropertyHint.None, "")]
	private AudioStream[] flipperDigitFlippedSounds;

	[Export(PropertyHint.None, "")]
	private float flipperDigitFlippedPitchVariance = 0.1f;

	[Export(PropertyHint.None, "")]
	private float flipperDigitFlippedPitchScale = 1f;

	[Export(PropertyHint.None, "")]
	private float flipperDigitMaxSpeed = 10f;

	private Dictionary<AudioStream, AudioStreamPlayer> loopingSFXPlayers = new Dictionary<AudioStream, AudioStreamPlayer>();

	[ExportGroup("Machine Screen and Content", "")]
	[Export(PropertyHint.None, "")]
	private AudioStream cardSectionUnlockedSound;

	[Export(PropertyHint.None, "")]
	private AudioStream loadingCardSound;

	[Export(PropertyHint.None, "")]
	private AudioStream cardMapMovementLoopSound;

	[Export(PropertyHint.None, "")]
	private float cardMapMovementMaxSpeed = 5000f;

	[Export(PropertyHint.None, "")]
	private int longTravelCardSlotCount = 5;

	[Export(PropertyHint.None, "")]
	private AudioStream cardMapMovementStartSound;

	[Export(PropertyHint.None, "")]
	private AudioStream cardMapMovementCompleteSound;

	[Export(PropertyHint.None, "")]
	private float cardLerpArrivalProximity = 0.1f;

	[Export(PropertyHint.None, "")]
	private AudioStream[] flickerStartedSounds;

	[ExportGroup("Link Buttons", "")]
	[Export(PropertyHint.None, "")]
	private AudioStream[] linkButtonHoverOrFocusChangeSounds;

	[Export(PropertyHint.None, "")]
	private float linkButtonHoverOrFocusChangePitchVariance = 0.15f;

	[Export(PropertyHint.None, "")]
	private float linkButtonHoverOrFocusChangeVolume = 0.7f;

	[Export(PropertyHint.None, "")]
	private AudioStream[] linkButtonPressedSounds;

	[Export(PropertyHint.None, "")]
	private float linkButtonPressedPitchVariance = 0.15f;

	[Export(PropertyHint.None, "")]
	private float linkButtonPressedVolume = 0.7f;

	[Export(PropertyHint.None, "")]
	private AudioStream[] linkButtonAppearedSounds;

	[Export(PropertyHint.None, "")]
	private float linkButtonAppearedPitchVariance = 0.15f;

	[Export(PropertyHint.None, "")]
	private float linkButtonAppearedVolume = 0.7f;

	[Export(PropertyHint.None, "")]
	private AudioStream[] rippleScreenSounds;

	[ExportGroup("Screen Scroll", "")]
	[Export(PropertyHint.None, "")]
	private AudioStream screenScrollLoopSound;

	[Export(PropertyHint.None, "")]
	private float screenScrollMaxSpeed = 1000f;

	[Export(PropertyHint.None, "")]
	private float screenScrollSmoothTime = 0.1f;

	[Export(PropertyHint.None, "")]
	private AudioStream scrollButtonPressedSound;

	[Export(PropertyHint.None, "")]
	private AudioStream scrollButtonReleasedSound;

	public bool machineScreenOn;

	private AudioStreamPlayer cardArrivalAudioPlayer;

	private float targetScreenScrollSpeed;

	private float smoothedScreenScrollSpeed;

	private LinkButton hoveredLinkButton;

	private LinkButton focusedLinkButton;

	public void GearSlideBegan()
	{
		Haptic.instance.LightStep();
		PlayRandomOneShotSfx(gearMovementStartSounds, gearShiftPitchVariance);
	}

	public void GearSlidePassedCorner()
	{
		Haptic.instance.LightStep();
		PlayRandomOneShotSfx(gearPassedCornerSounds, gearShiftPitchVariance);
	}

	public void GearSlideArrivedInGear()
	{
		Haptic.instance.BigClunk();
		PlayRandomOneShotSfx(gearArrivedInGearSounds, gearShiftPitchVariance);
	}

	public void GearSlideReturnedToHomePosition()
	{
		Haptic.instance.BigClunk();
		PlayRandomOneShotSfx(gearReturnedToHomeSounds, gearShiftPitchVariance);
	}

	public void GearSlidePassedGearNotch()
	{
		Haptic.instance.LightStep();
		PlayRandomOneShotSfx(gearPassedCornerSounds, gearShiftPitchVariance);
	}

	public void UpdateGearSlideAudioLoop(float gearSpeed)
	{
		UpdateLoopingSFX(volumeNorm: (!(Mathf.Abs(gearSpeed) > 0f)) ? 0f : Mathf.Clamp(Mathf.Abs(gearSpeed) / gearSlideLoopMaxSpeed, 0f, 1f), stream: gearSlideLoopSound);
	}

	public void FlipperDigitSelectionChanged()
	{
		Haptic.instance.Tap();
	}

	public void CircleSelectorChangedCharacter()
	{
		Haptic.instance.LittleTap();
		PlayRandomOneShotSfx(circleSelectorChangedCharacterSounds, circleSelectorChangedCharacterPitchVariance);
	}

	public void CircleSelectorPressedCharacter()
	{
		Haptic.instance.Tap();
		PlayRandomOneShotSfx(circleSelectorPressedCharacterSounds, circleSelectorPressedCharacterPitchScale, 1f, 0.5f);
	}

	public void UpdateCircleSelectorKnobAudioLoop(float circleSelectorKnobSpeed)
	{
		UpdateLoopingSFX(volumeNorm: (!(Mathf.Abs(circleSelectorKnobSpeed) > 0f)) ? 0f : Mathf.Clamp(Mathf.Abs(circleSelectorKnobSpeed) / circleSelectorKnobLoopMaxSpeed, 0f, 1f), stream: circleSelectorKnobLoopSound);
	}

	public void FlipperDigitFlipped(float velocity)
	{
		float weight = Mathf.Clamp(Mathf.Abs(velocity) / flipperDigitMaxSpeed, 0f, 1f);
		float volumeScale = Mathf.Lerp(1f, 0.6f, weight);
		PlayRandomOneShotSfx(flipperDigitFlippedSounds, flipperDigitFlippedPitchVariance, flipperDigitFlippedPitchScale, volumeScale);
	}

	public void CardSectionUnlocked()
	{
		PlayOneShotSfx(cardSectionUnlockedSound, "MachineLoading");
	}

	public void LoadingCard()
	{
		PlayOneShotSfx(loadingCardSound, "MachineLoading");
	}

	public void UpdateCardMapMovementAudioLoop(float movementSpeed, float travelDistance, float targetCardLerp, float cardLerp)
	{
		float num = Mathf.Abs(movementSpeed);
		float volumeNorm = Mathf.Clamp(num / cardMapMovementMaxSpeed, 0f, 1f);
		bool flag = travelDistance / 1000f > (float)longTravelCardSlotCount;
		UpdateLoopingSFX(cardMapMovementLoopSound, volumeNorm, flag ? cardMapMovementStartSound : null, "MachineLoading");
		if (!((num > 10f) & flag))
		{
			return;
		}
		if ((targetCardLerp == 0f && cardLerp < cardLerpArrivalProximity && cardLerp > 0f) || (targetCardLerp == 1f && cardLerp > 1f - cardLerpArrivalProximity && cardLerp < 1f))
		{
			if (cardArrivalAudioPlayer == null)
			{
				cardArrivalAudioPlayer = PlayOneShotSfx(cardMapMovementCompleteSound, "MachineLoading", 0f, 1f, 1f, delegate
				{
					cardArrivalAudioPlayer = null;
				});
			}
		}
		else if (cardArrivalAudioPlayer != null)
		{
			cardArrivalAudioPlayer.Stop();
			cardArrivalAudioPlayer.QueueFree();
			cardArrivalAudioPlayer = null;
		}
	}

	public void UpdateScreenScrollAudioLoop(float scrollSpeed)
	{
		targetScreenScrollSpeed = Mathf.Abs(scrollSpeed);
	}

	public void ScrollButtonPressed(bool down)
	{
		Haptic.instance.Tap();
		if (down)
		{
			PlayOneShotSfx(scrollButtonPressedSound, null, 0.15f);
		}
		else
		{
			PlayOneShotSfx(scrollButtonReleasedSound, null, 0.15f);
		}
	}

	public void LinkButtonPressed()
	{
		if (machineScreenOn)
		{
			Haptic.instance.LightStep();
			PlayRandomOneShotSfx(linkButtonPressedSounds, linkButtonPressedPitchVariance, 1f, linkButtonPressedVolume);
		}
	}

	public void LinkButtonAppeared()
	{
		if (machineScreenOn)
		{
			PlayRandomOneShotSfx(linkButtonAppearedSounds, linkButtonAppearedPitchVariance, 1f, linkButtonAppearedVolume);
		}
	}

	public void FlickerStarted()
	{
		if (machineScreenOn)
		{
			Haptic.instance.LightStep();
			PlayRandomOneShotSfx(flickerStartedSounds, 0.15f);
		}
	}

	public void RippleScreen()
	{
		Haptic.instance.Whoosh();
		PlayRandomOneShotSfx(rippleScreenSounds);
	}

	public override void _Process(double delta)
	{
		smoothedScreenScrollSpeed = Mathf.MoveToward(smoothedScreenScrollSpeed, targetScreenScrollSpeed, (float)delta * screenScrollMaxSpeed / screenScrollSmoothTime);
		float volumeNorm = Mathf.Clamp(smoothedScreenScrollSpeed / screenScrollMaxSpeed, 0f, 1f);
		UpdateLoopingSFX(screenScrollLoopSound, volumeNorm);
		LinkButton linkButton = hoveredLinkButton;
		LinkButton linkButton2 = focusedLinkButton;
		hoveredLinkButton = machineViewport.GuiGetHoveredControl() as LinkButton;
		focusedLinkButton = machineViewport.GuiGetFocusOwner() as LinkButton;
		if (linkButton != hoveredLinkButton)
		{
			Haptic.instance.LightStep();
			PlayRandomOneShotSfx(linkButtonHoverOrFocusChangeSounds, linkButtonHoverOrFocusChangePitchVariance, 1f, linkButtonHoverOrFocusChangeVolume);
		}
		if (linkButton2 != focusedLinkButton)
		{
			Haptic.instance.LightStep();
			PlayRandomOneShotSfx(linkButtonHoverOrFocusChangeSounds, linkButtonHoverOrFocusChangePitchVariance, 1f, linkButtonHoverOrFocusChangeVolume);
		}
	}

	private AudioStreamPlayer CreateAudioPlayer()
	{
		AudioStreamPlayer audioStreamPlayer = new AudioStreamPlayer();
		audioStreamPlayer.Bus = "MachineFoley";
		AddChild(audioStreamPlayer, forceReadableName: false, InternalMode.Disabled);
		return audioStreamPlayer;
	}

	private AudioStreamPlayer PlayRandomOneShotSfx(AudioStream[] streams, float pitchVariance = 0f, float pitchScale = 1f, float volumeScale = 1f, Action finishedCallback = null)
	{
		if (streams == null || streams.Length == 0)
		{
			return null;
		}
		long num = GD.Randi() % streams.Length;
		return PlayOneShotSfx(streams[num], null, pitchVariance, pitchScale, volumeScale, finishedCallback);
	}

	private AudioStreamPlayer PlayOneShotSfx(AudioStream stream, string busOverride = null, float pitchVariance = 0f, float pitchScale = 1f, float volumeScale = 1f, Action finishedCallback = null)
	{
		if (stream == null)
		{
			return null;
		}
		AudioStreamPlayer sfxPlayer = new AudioStreamPlayer();
		sfxPlayer.Bus = busOverride ?? "MachineFoley";
		sfxPlayer.Stream = stream;
		sfxPlayer.PitchScale = pitchScale * (float)GD.RandRange(1f / (1f + pitchVariance), 1f + pitchVariance);
		sfxPlayer.VolumeDb = AudioX.VolumeDbFromNormalized(volumeScale);
		AddChild(sfxPlayer, forceReadableName: false, InternalMode.Disabled);
		sfxPlayer.Play();
		sfxPlayer.Finished += delegate
		{
			sfxPlayer.QueueFree();
			finishedCallback?.Invoke();
		};
		return sfxPlayer;
	}

	private void UpdateLoopingSFX(AudioStream stream, float volumeNorm, AudioStream startAudioStream = null, string busOverride = null)
	{
		loopingSFXPlayers.TryGetValue(stream, out var value);
		if (volumeNorm > 0f && value == null)
		{
			AudioStreamPlayer audioStreamPlayer = CreateAudioPlayer();
			audioStreamPlayer.Bus = busOverride ?? "MachineFoley";
			audioStreamPlayer.Stream = stream;
			audioStreamPlayer.VolumeDb = AudioX.VolumeDbFromNormalized(volumeNorm);
			audioStreamPlayer.Play();
			loopingSFXPlayers[stream] = audioStreamPlayer;
			if (startAudioStream != null)
			{
				AudioStreamPlayer startPlayer = CreateAudioPlayer();
				startPlayer.Bus = busOverride ?? "MachineFoley";
				startPlayer.Stream = startAudioStream;
				startPlayer.Play();
				startPlayer.Finished += delegate
				{
					startPlayer.QueueFree();
				};
			}
		}
		else if (value != null)
		{
			if (volumeNorm == 0f)
			{
				value.Stop();
				loopingSFXPlayers.Remove(stream);
				value.QueueFree();
			}
			else
			{
				value.VolumeDb = AudioX.VolumeDbFromNormalized(volumeNorm);
			}
		}
	}
}
