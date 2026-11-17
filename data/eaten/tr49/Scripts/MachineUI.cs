using System.Collections.Generic;
using System.Text;
using Godot;

public partial class MachineUI : Node3D
{
	[Signal]
	public delegate void CodeChangedEventHandler(string code);

	[Signal]
	public delegate void CloseCardPressedEventHandler();

	[Signal]
	public delegate void CardLinkPressedEventHandler(string link);

	[Signal]
	public delegate void CardArrivedInViewEventHandler();

	[Export(PropertyHint.None, "")]
	private string defaultCode = "AA00";

	[Export(PropertyHint.None, "")]
	private MeshInstance3D crtScreen;

	[Export(PropertyHint.None, "")]
	private BigContentMap bigContentMap;

	[Export(PropertyHint.None, "")]
	private float blurEffectSettleDuration = 0.6f;

	[Export(PropertyHint.None, "")]
	private TextureRect hiddenImage;

	[Export(PropertyHint.None, "")]
	private FlipperDigit[] flipperDigits;

	[Export(PropertyHint.None, "")]
	private CircleSelector circleSelector;

	[Export(PropertyHint.None, "")]
	private ScrollButton scrollUpButton;

	[Export(PropertyHint.None, "")]
	private ScrollButton scrollDownButton;

	[Export(PropertyHint.None, "")]
	private Control tutorialAnimatedThumbstick;

	[Export(PropertyHint.None, "")]
	private Control tutorialAnimatedThumbstickArrows;

	[Export(PropertyHint.None, "")]
	private GameCamera gameCamera;

	[Export(PropertyHint.None, "")]
	private GearShifter gearShifter;

	[Export(PropertyHint.None, "")]
	private MachineAudio machineAudio;

	[Export(PropertyHint.None, "")]
	private float intermediateImageChance = 0.33f;

	[Export(PropertyHint.None, "")]
	private float hiddenImageAlphaFadeInTime = 0.5f;

	[Export(PropertyHint.None, "")]
	private float hiddenImageAlphaFadeOutTime = 0.5f;

	[Export(PropertyHint.None, "")]
	private Curve screenTurnOnOffCurve;

	[Export(PropertyHint.None, "")]
	private float screenTurnOnOffDuration = 1f;

	[Export(PropertyHint.None, "")]
	private MachineFlicker machineFlicker;

	[Export(PropertyHint.None, "")]
	private FlickerSettings tr49CardFlickerSettings;

	[Export(PropertyHint.None, "")]
	private FlickerSettings lowCoherenceCardFlickerSettings;

	[Export(PropertyHint.None, "")]
	private float rippleScreenDuration = 3f;

	public CardView activeCardView;

	public bool canCloseCard;

	public bool menuStyleInput;

	public bool screenIsOn;

	public bool holdingTriggerForCodeEntry;

	private string lastSignalledCodeOnGamepad;

	private ShaderMaterial crtMaterial;

	private Tween cardSwapTween;

	private int activeFlipperDigitIndex = 4;

	private float cardLerp;

	private float targetCardLerp;

	private float lerpSpeed = 1f;

	private float targetBlurEffect;

	private float currentBlurEffect;

	private float rippleScreenTimer;

	private float hiddenImageAlpha;

	private bool hiddenImageShowing;

	private float screenTurnOnOffNorm;

	private float analogueScrollSpeed = 0.7f;

	private float digitalScrollSpeed = 0.5f;

	private bool leftOverLeftStickFromCodeEntry;

	private float lastMenuLeftStickInputTime;

	private float graceTimeRemainingAfterAutomaticCodeEntryExit;

	private float lastScreenScrollPosition;

	private bool tutorialPressAToConfirmCharacterActive;

	private float lastCharacterEntryTime;

	private Control focusOwnerBeforeCodeEntry;

	private bool screenFocusClearedThisCodeEntry;

	private string _code;

	private bool initialSetupIsComplete;

	private Tween gameMenuCardTween;

	private const float minTransitionTime = 1f;

	private const float maxTransitionTime = 4f;

	private CardView otherCardView
	{
		get
		{
			if (activeCardView != bigContentMap.cardView1)
			{
				return bigContentMap.cardView1;
			}
			return bigContentMap.cardView2;
		}
	}

	public bool codeEntryMode
	{
		get
		{
			if (activeFlipperDigitIndex >= 0)
			{
				return activeFlipperDigitIndex < 4;
			}
			return false;
		}
	}

	public bool preventInputByOtherUI
	{
		get
		{
			if (!Credits.instance.Visible && !TitleSplashScreen.instance.Visible && !AlertView.instance.Visible && !NotebookView.instance.Visible)
			{
				return SettingsView.instance.Visible;
			}
			return true;
		}
	}

	public bool isTransitioningBetweenCards => Mathf.Abs(cardLerp - targetCardLerp) > 0.05f;

	public string code
	{
		get
		{
			return _code;
		}
		set
		{
			if (_code != value)
			{
				_code = ValidateCode(value);
				UpdateFlippersAndCircleSelector();
			}
		}
	}

	private float transitionTime => Mathf.Lerp(1f, 4f, Mathf.Clamp(Mathf.InverseLerp(1000f, 20000f, (bigContentMap.cardView1.Position - bigContentMap.cardView2.Position).Length()), 0f, 1f));

	public override async void _Ready()
	{
		InitCode();
		for (int i = 0; i < flipperDigits.Length; i++)
		{
			FlipperDigit obj = flipperDigits[i];
			obj.digitIndex = i;
			obj.Clicked += OnFlipperDigitClicked;
		}
		circleSelector.ChangedCharacter += OnCircleSelectorChangedCharacter;
		circleSelector.CharacterDirectlyClicked += OnCircleSelectorCharacterDirectlyClicked;
		circleSelector.knob.DraggingStarted += OnCircleSelectorKnobDraggingStarted;
		gearShifter.DraggedToGear += OnGearShifterDraggedToGear;
		scrollUpButton.Pressing += delegate
		{
			OnPressingScrollButton(-1);
		};
		scrollDownButton.Pressing += delegate
		{
			OnPressingScrollButton(1);
		};
		UpdateFlippersAndCircleSelector();
		if (Platform.isSwitch)
		{
			crtScreen.GetNode<SubViewport>("ScreenViewport").Size = new Vector2I(1024, 1024);
		}
		crtMaterial = crtScreen.GetActiveMaterial(0) as ShaderMaterial;
		crtMaterial.SetShaderParameter("blur_effect", 0f);
		crtMaterial.SetShaderParameter("reduce_glitch_effects", GameSettings.instance.reduceGlitchEffects ? 1f : 0f);
		activeCardView = null;
		tutorialAnimatedThumbstick.Modulate = new Color(1f, 1f, 1f, 0f);
		tutorialAnimatedThumbstick.Visible = false;
		bigContentMap.cardView1.CardLinkPressed += delegate(string link)
		{
			OnCardLinkPressedOnCard(bigContentMap.cardView1, link);
		};
		bigContentMap.cardView2.CardLinkPressed += delegate(string link)
		{
			OnCardLinkPressedOnCard(bigContentMap.cardView2, link);
		};
		bigContentMap.cardView1.LinkButtonAppeared += delegate
		{
			machineAudio.LinkButtonAppeared();
		};
		bigContentMap.cardView2.LinkButtonAppeared += delegate
		{
			machineAudio.LinkButtonAppeared();
		};
		await ToSignal(bigContentMap, BigContentMap.SignalName.SlotsReady);
		initialSetupIsComplete = true;
		ClearAndTurnOffMachine();
		if (base.Owner == null)
		{
			ShowNextCard();
		}
		void ShowNextCard()
		{
			List<string> list = new List<string> { "The Quantum Sock Paradox", "How to Train Your Pet Rock", "Advanced Procrastination Techniques", "The Art of Making Coffee" };
			List<string> list2 = new List<string> { "Alice", "Beatrice", "Cecil" };
			ClearCard();
			activeCardView.StartSection("header");
			activeCardView.Append("title", list[GD.RandRange(0, list.Count - 1)]);
			activeCardView.StartRow();
			activeCardView.Append("Softback");
			activeCardView.Append("Joe's awesome book");
			activeCardView.Append("2005");
			activeCardView.EndRow();
			activeCardView.EndSection();
			activeCardView.StartSection(list2[GD.RandRange(0, list2.Count - 1)].ToLower());
			activeCardView.Append("");
			activeCardView.Append("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.");
			activeCardView.Append("Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.");
			activeCardView.Append("Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.");
			activeCardView.EndSection();
			activeCardView.StartSection("footer");
			activeCardView.StartRow();
			activeCardView.Append("Card made in 2025");
			activeCardView.Append("By Joe");
			activeCardView.EndRow();
			activeCardView.EndSection();
			PresentCard("TE57", allowTitleLinks: true, 1f, coherenceIsCriticallyLow: false, redacted: true);
		}
	}

	public void InitCode()
	{
		_code = defaultCode;
	}

	public Vector3 Get3DPositionOfControl(Control control)
	{
		Vector2 center = control.GetGlobalRect().GetCenter();
		Vector2 size = control.GetViewport().GetVisibleRect().Size;
		float weight = center.X / size.X;
		float weight2 = center.Y / size.Y;
		Vector3 vector = new Vector3(Mathf.Lerp(-0.5f, 0.5f, weight), Mathf.Lerp(0.5f, -0.5f, weight2), 0f);
		return crtScreen.GlobalTransform * vector;
	}

	public override void _UnhandledInput(InputEvent @event)
	{
		if (preventInputByOtherUI || !gameCamera.isCloseEnoughToInteract)
		{
			return;
		}
		if (@event.IsActionPressed("ui_accept") && codeEntryMode)
		{
			this.SetInputAsHandled(@event);
			ConfirmActiveCharacter();
		}
		else if (@event.IsActionPressed("ui_cancel") && codeEntryMode && PrimaryInputManager.isGamepad)
		{
			this.SetInputAsHandled(@event);
			if (activeFlipperDigitIndex > 0)
			{
				CancelCharacter();
			}
			else if (!holdingTriggerForCodeEntry)
			{
				StopCodeEntry();
			}
		}
		bool flag = Input.IsKeyPressed((Key)(Platform.isMac ? 4194327 : 4194326));
		if (@event is InputEventKey { Pressed: not false } inputEventKey && !flag)
		{
			if (inputEventKey.Keycode >= Key.A && inputEventKey.Keycode <= Key.Z)
			{
				this.SetInputAsHandled(@event);
				int index = (int)(inputEventKey.Keycode - 65);
				TryTypeCharacter(index, isLetter: true);
			}
			else if (inputEventKey.Keycode >= Key.Key0 && inputEventKey.Keycode <= Key.Key9)
			{
				this.SetInputAsHandled(@event);
				int index2 = (int)(inputEventKey.Keycode - 48);
				TryTypeCharacter(index2, isLetter: false);
			}
			else if (inputEventKey.Keycode >= Key.Kp0 && inputEventKey.Keycode <= Key.Kp9)
			{
				this.SetInputAsHandled(@event);
				int index3 = (int)(inputEventKey.Keycode - 4194438);
				TryTypeCharacter(index3, isLetter: false);
			}
			else if (inputEventKey.Keycode == Key.Backspace)
			{
				this.SetInputAsHandled(@event);
				CancelCharacter();
			}
			else if (@event.IsActionPressed("ui_cancel") && codeEntryMode && PrimaryInputManager.isKeyboard)
			{
				this.SetInputAsHandled(@event);
				StopCodeEntry();
			}
			else if (@event.IsActionPressed("ui_up") && codeEntryMode)
			{
				this.SetInputAsHandled(@event);
				IncrementDecrementFlipperDigit(-1);
			}
			else if (@event.IsActionPressed("ui_down") && codeEntryMode)
			{
				this.SetInputAsHandled(@event);
				IncrementDecrementFlipperDigit(1);
			}
		}
		if (@event.IsActionPressed("code_entry_left") && Input.IsActionJustPressed("code_entry_left") && codeEntryMode && activeFlipperDigitIndex > 0)
		{
			this.SetInputAsHandled(@event);
			SelectCharacterDirection(-1);
		}
		else if (@event.IsActionPressed("code_entry_right") && Input.IsActionJustPressed("code_entry_right") && codeEntryMode && activeFlipperDigitIndex < 3)
		{
			this.SetInputAsHandled(@event);
			SelectCharacterDirection(1);
		}
		if (@event is InputEventJoypadMotion { Axis: JoyAxis.LeftX } inputEventJoypadMotion && (inputEventJoypadMotion.AxisValue > 0.7f || inputEventJoypadMotion.AxisValue < -0.7f) && !codeEntryMode)
		{
			this.SetInputAsHandled(@event);
			activeCardView.FocusLeftRightLink((inputEventJoypadMotion.AxisValue > 0f) ? 1 : (-1));
		}
		if (@event.IsActionPressed("ui_left") && !codeEntryMode)
		{
			this.SetInputAsHandled(@event);
			activeCardView.FocusPrevNextLink(-1);
		}
		else if (@event.IsActionPressed("ui_right") && !codeEntryMode)
		{
			this.SetInputAsHandled(@event);
			activeCardView.FocusPrevNextLink(1);
		}
		else if (!codeEntryMode && menuStyleInput && @event.IsActionPressed("ui_down"))
		{
			this.SetInputAsHandled(@event);
			activeCardView.FocusPrevNextLink(1);
		}
		else if (!codeEntryMode && menuStyleInput && @event.IsActionPressed("ui_up"))
		{
			this.SetInputAsHandled(@event);
			activeCardView.FocusPrevNextLink(-1);
		}
		if (@event.IsActionPressed("code_entry_mode") && @event is InputEventJoypadMotion { AxisValue: >0.6f } && !holdingTriggerForCodeEntry)
		{
			if (!codeEntryMode)
			{
				this.SetInputAsHandled(@event);
				StartCodeEntry();
			}
			holdingTriggerForCodeEntry = true;
		}
		else if (@event.IsActionReleased("code_entry_mode") && @event is InputEventJoypadMotion { AxisValue: <0.3f } && holdingTriggerForCodeEntry)
		{
			if (codeEntryMode)
			{
				this.SetInputAsHandled(@event);
				StopCodeEntry();
			}
			holdingTriggerForCodeEntry = false;
			if (code != lastSignalledCodeOnGamepad)
			{
				lastSignalledCodeOnGamepad = code;
				EmitSignal(SignalName.CodeChanged, code);
			}
		}
		if (@event.IsActionPressed("code_entry_mode") && @event is InputEventKey)
		{
			this.SetInputAsHandled(@event);
			if (!codeEntryMode)
			{
				StartCodeEntry();
			}
			else
			{
				StopCodeEntry();
			}
		}
	}

	public void ClearAndTurnOffMachine()
	{
		if (initialSetupIsComplete)
		{
			StopCodeEntry();
			ClearCard();
			ClearCard();
			activeCardView = bigContentMap.cardView1;
			activeCardView.Name = "Card View (Active)";
			otherCardView.Name = "Card View (Other)";
			lastScreenScrollPosition = 0f;
			bigContentMap.ClearAllSlots();
			Vector2I slotXY = bigContentMap.SlotForCode("TR49");
			bigContentMap.PlaceCardInSlotXY(activeCardView, slotXY);
			targetCardLerp = (cardLerp = 0f);
			UpdateCardLerp(1f);
			rippleScreenTimer = 0f;
			screenIsOn = false;
		}
	}

	public void ClearCard()
	{
		focusOwnerBeforeCodeEntry = null;
		activeCardView = otherCardView;
		activeCardView.Name = "Card View (Active)";
		otherCardView.Name = "Card View (Other)";
		lastScreenScrollPosition = 0f;
		activeCardView.Modulate = new Color(1f, 1f, 1f);
		activeCardView.Visible = true;
		activeCardView.Clear();
		bigContentMap.ResetSlotForCard(activeCardView);
	}

	public void CloseCard()
	{
		ClearCard();
	}

	public void RippleScreen()
	{
		rippleScreenTimer = rippleScreenDuration;
		machineAudio.RippleScreen();
	}

	public void SetPresentingGameMenuCard(bool presentingActive, string lastCodeBeforeGameMenu = null)
	{
		if (!screenIsOn)
		{
			GD.PushError("Attempting to set presenting game menu card when screen is off. We should just disallow the game menu while screen is off.");
			return;
		}
		menuStyleInput = presentingActive;
		if (presentingActive)
		{
			activeCardView.Finalise("OP37", allowTitleLinks: false, 1f, coherenceIsCriticallyLow: false, redacted: false, immediate: false);
			activeCardView.Position = otherCardView.Position;
			activeCardView.Name = "Card View (Game Menu)";
			activeCardView.OnArrivedInView(this);
		}
		else
		{
			activeCardView = otherCardView;
			activeCardView.Name = "Card View (Active)";
			otherCardView.Name = "Card View (Previously Game Menu)";
			lastScreenScrollPosition = 0f;
			if (string.IsNullOrWhiteSpace(lastCodeBeforeGameMenu))
			{
				_code = defaultCode;
			}
			else
			{
				_code = lastCodeBeforeGameMenu;
			}
			for (int i = 0; i < flipperDigits.Length; i++)
			{
				FlipperDigit flipperDigit = flipperDigits[i];
				if (flipperDigit.useLetters)
				{
					flipperDigit.SetValue(code[i] - 65);
				}
				else
				{
					flipperDigit.SetValue(code[i] - 48);
				}
			}
		}
		if (gameMenuCardTween != null)
		{
			gameMenuCardTween.Kill();
			gameMenuCardTween = null;
		}
		activeCardView.Visible = true;
		activeCardView.Modulate = new Color(1f, 1f, 1f, 0f);
		gameMenuCardTween = CreateTween().SetParallel();
		Tween.TransitionType trans = (Tween.TransitionType)(GameSettings.instance.reduceGlitchEffects ? 0 : 9);
		gameMenuCardTween.SetTrans(trans);
		gameMenuCardTween.SetEase(Tween.EaseType.InOut);
		gameMenuCardTween.TweenProperty(otherCardView, "modulate:a", 0f, 0.4000000059604645);
		gameMenuCardTween.TweenProperty(activeCardView, "modulate:a", 1f, 0.4000000059604645).SetDelay(0.5);
		gameMenuCardTween.Finished += delegate
		{
			otherCardView.Visible = false;
		};
	}

	public void PresentCard(string code, bool allowTitleLinks, float coherence, bool coherenceIsCriticallyLow, bool redacted)
	{
		screenIsOn = true;
		if (cardSwapTween != null)
		{
			cardSwapTween.Kill();
		}
		focusOwnerBeforeCodeEntry = null;
		graceTimeRemainingAfterAutomaticCodeEntryExit = 0f;
		activeCardView.Finalise(code, allowTitleLinks, coherence, coherenceIsCriticallyLow, redacted, immediate: false);
		machineAudio.LoadingCard();
		Vector2I slotXY = bigContentMap.SlotForCode(activeCardView.title);
		bigContentMap.PlaceCardInSlotXY(activeCardView, slotXY);
		hiddenImage.Texture = null;
		hiddenImageShowing = false;
		if (((GD.Randf() < intermediateImageChance && hiddenImageAlpha < 0.1f) || base.Owner == null) && !string.IsNullOrWhiteSpace(activeCardView.sectionThemeName))
		{
			string text = "res://Images/Characters/Fisheye/" + activeCardView.sectionThemeName;
			if (DirAccess.DirExistsAbsolute(text))
			{
				string[] array = ResourceLoader.ListDirectory("res://Images/Characters/Fisheye/" + activeCardView.sectionThemeName);
				if (array.Length != 0)
				{
					string text2 = array[GD.RandRange(0, array.Length - 1)];
					hiddenImage.Texture = ResourceLoader.Load<Texture2D>(text + "/" + text2, null, ResourceLoader.CacheMode.Reuse);
					if (hiddenImage.Texture == null)
					{
						GD.PushError("Failed to load image despite seeing that the file exists: " + text2);
					}
					hiddenImageShowing = true;
				}
			}
		}
		targetCardLerp = ((activeCardView == bigContentMap.cardView1) ? 0f : 1f);
	}

	public override void _Process(double delta)
	{
		bool isCloseEnoughToInteract = gameCamera.isCloseEnoughToInteract;
		circleSelector.canInteract = isCloseEnoughToInteract;
		circleSelector.knob.canInteract = isCloseEnoughToInteract;
		gearShifter.canInteract = isCloseEnoughToInteract;
		FlipperDigit[] array = flipperDigits;
		for (int i = 0; i < array.Length; i++)
		{
			array[i].canInteract = isCloseEnoughToInteract;
		}
		UpdateCardLerp((float)delta);
		UpdateScreenScroll();
		screenTurnOnOffNorm = Mathf.MoveToward(screenTurnOnOffNorm, screenIsOn ? 1f : 0f, (float)delta / screenTurnOnOffDuration);
		float num = screenTurnOnOffCurve.Sample(screenTurnOnOffNorm);
		crtMaterial.SetShaderParameter("turn_off_effect", num);
		rippleScreenTimer = Mathf.MoveToward(rippleScreenTimer, 0f, (float)delta);
		crtMaterial.SetShaderParameter("ripple_progress", 1f - rippleScreenTimer / rippleScreenDuration);
		crtMaterial.SetShaderParameter("reduce_glitch_effects", GameSettings.instance.reduceGlitchEffects ? 1f : 0f);
		if (((cardLerp == targetCardLerp && activeCardView != null) & isCloseEnoughToInteract) && !codeEntryMode)
		{
			scrollUpButton.disabled = !activeCardView.canScrollUp;
			scrollDownButton.disabled = !activeCardView.canScrollDown;
		}
		else
		{
			scrollUpButton.disabled = true;
			scrollDownButton.disabled = true;
		}
		machineFlicker.activeFlicker = null;
		if (activeCardView != null)
		{
			if (string.IsNullOrWhiteSpace(activeCardView.code) && activeCardView.currentCoherence < 0.6f)
			{
				machineFlicker.activeFlicker = tr49CardFlickerSettings;
			}
			else if (activeCardView.currentCoherence < 0.8f)
			{
				machineFlicker.activeFlicker = lowCoherenceCardFlickerSettings;
			}
		}
		if (!isCloseEnoughToInteract)
		{
			(activeCardView?.GetViewport().GuiGetFocusOwner())?.ReleaseFocus();
			focusOwnerBeforeCodeEntry = null;
		}
		else if (codeEntryMode)
		{
			if (!screenFocusClearedThisCodeEntry)
			{
				screenFocusClearedThisCodeEntry = true;
				Control control = activeCardView?.GetViewport().GuiGetFocusOwner();
				if (control != null)
				{
					focusOwnerBeforeCodeEntry = control;
					control.ReleaseFocus();
				}
				else
				{
					focusOwnerBeforeCodeEntry = null;
				}
			}
		}
		else
		{
			screenFocusClearedThisCodeEntry = false;
			if (focusOwnerBeforeCodeEntry != null && graceTimeRemainingAfterAutomaticCodeEntryExit <= 0f && activeCardView?.GetViewport().GuiGetFocusOwner() == null && focusOwnerBeforeCodeEntry != null && (GodotObject.IsInstanceValid(focusOwnerBeforeCodeEntry) & !focusOwnerBeforeCodeEntry.IsQueuedForDeletion()))
			{
				if (StoryController.instance.canLinkButtonGrabFocus)
				{
					focusOwnerBeforeCodeEntry.GrabFocus();
				}
				focusOwnerBeforeCodeEntry = null;
			}
		}
		if (!codeEntryMode && graceTimeRemainingAfterAutomaticCodeEntryExit > 0f)
		{
			graceTimeRemainingAfterAutomaticCodeEntryExit -= (float)delta;
			if (graceTimeRemainingAfterAutomaticCodeEntryExit <= 0f)
			{
				graceTimeRemainingAfterAutomaticCodeEntryExit = 0f;
			}
		}
		if (activeCardView != null)
		{
			float num2 = (activeCardView.currentScrollPosition - lastScreenScrollPosition) / (float)delta;
			machineAudio.UpdateScreenScrollAudioLoop(num2);
			lastScreenScrollPosition = activeCardView.currentScrollPosition;
			if (num2 < 0f)
			{
				scrollUpButton.visuallyPressing = true;
			}
			else if (num2 > 0f)
			{
				scrollDownButton.visuallyPressing = true;
			}
			else
			{
				scrollUpButton.visuallyPressing = false;
				scrollDownButton.visuallyPressing = false;
			}
		}
		else
		{
			lastScreenScrollPosition = 0f;
			machineAudio.UpdateScreenScrollAudioLoop(0f);
			scrollUpButton.visuallyPressing = false;
			scrollDownButton.visuallyPressing = false;
		}
		bool flag = PrimaryInputManager.isGamepad && codeEntryMode && !StoryController.instance.tutorialGamepadThumbstickComplete && gameCamera.isCloseEnoughToInteract;
		if (flag)
		{
			tutorialAnimatedThumbstick.Visible = true;
		}
		if (tutorialAnimatedThumbstick.Visible)
		{
			float a = tutorialAnimatedThumbstick.Modulate.A;
			a = Mathf.MoveToward(a, flag ? 1f : 0f, (float)delta / 0.15f);
			tutorialAnimatedThumbstick.Modulate = new Color(1f, 1f, 1f, a);
			float num3 = Mathf.Lerp(0.5f, 1f, a);
			tutorialAnimatedThumbstick.Scale = new Vector2(num3, num3);
			tutorialAnimatedThumbstickArrows.Rotation = circleSelector.currentKnobAnglePos;
			if (a == 0f && !flag)
			{
				tutorialAnimatedThumbstick.Visible = false;
			}
		}
		float num4 = (float)Time.GetTicksMsec() / 1000f;
		bool flag2 = PrimaryInputManager.isGamepad && codeEntryMode && StoryController.instance.tutorialGamepadCharactersConfirmed < 5 && gameCamera.isCloseEnoughToInteract;
		if (flag2 && circleSelector.isLeftStickActive && num4 - lastCharacterEntryTime > 2f)
		{
			tutorialPressAToConfirmCharacterActive = true;
		}
		else if (tutorialPressAToConfirmCharacterActive && !flag2)
		{
			tutorialPressAToConfirmCharacterActive = false;
		}
		if (tutorialPressAToConfirmCharacterActive)
		{
			float num5 = 0f;
			Tooltip.Direction direction = Tooltip.Direction.Up;
			if (Mathf.Abs(Mathf.AngleDifference(circleSelector.currentKnobAnglePos, 0f)) < Mathf.DegToRad(90f))
			{
				direction = Tooltip.Direction.Down;
				num5 = -40f;
			}
			else
			{
				direction = Tooltip.Direction.Up;
				num5 = 40f;
			}
			Tooltips.instance.ShowTooltip(circleSelector.knob.GlobalPosition, "Press A to confirm", "tutorial_press_a_to_confirm_character", direction, 0f, num5, 1f);
		}
		else
		{
			Tooltips.instance.RemoveTooltip("tutorial_press_a_to_confirm_character");
		}
		machineAudio.machineScreenOn = screenIsOn;
	}

	private void UpdateScreenScroll()
	{
		if (preventInputByOtherUI || !gameCamera.isCloseEnoughToInteract)
		{
			return;
		}
		bool flag = Input.IsActionPressed("scroll_machine_screen_up_analogue") || Input.IsActionPressed("scroll_machine_screen_down_analogue");
		if (menuStyleInput && !flag)
		{
			lastMenuLeftStickInputTime = 0f;
		}
		if (!codeEntryMode && !menuStyleInput)
		{
			if (!flag)
			{
				leftOverLeftStickFromCodeEntry = false;
			}
			else if (leftOverLeftStickFromCodeEntry)
			{
				return;
			}
			float num = 0f;
			if (Input.IsActionPressed("scroll_machine_screen_up_analogue"))
			{
				num += (0f - analogueScrollSpeed) * Input.GetActionStrength("scroll_machine_screen_up_analogue");
			}
			if (Input.IsActionPressed("scroll_machine_screen_down_analogue"))
			{
				num += analogueScrollSpeed * Input.GetActionStrength("scroll_machine_screen_down_analogue");
			}
			if (Input.IsActionPressed("scroll_machine_screen_down"))
			{
				num += digitalScrollSpeed;
			}
			if (Input.IsActionPressed("scroll_machine_screen_up"))
			{
				num += 0f - digitalScrollSpeed;
			}
			if (num != 0f)
			{
				activeCardView.Scroll(num);
			}
		}
		else if ((!codeEntryMode && menuStyleInput) & flag)
		{
			if ((float)Time.GetTicksMsec() - lastMenuLeftStickInputTime > 200f)
			{
				lastMenuLeftStickInputTime = Time.GetTicksMsec();
				activeCardView.FocusPrevNextLink((!(Input.GetActionStrength("scroll_machine_screen_up_analogue") > 0f)) ? 1 : (-1));
			}
		}
		else if (codeEntryMode)
		{
			leftOverLeftStickFromCodeEntry = flag;
		}
	}

	private void UpdateCardLerp(float delta)
	{
		float num = cardLerp;
		cardLerp = Mathf.MoveToward(cardLerp, targetCardLerp, delta / transitionTime);
		bool flag = false;
		if (cardLerp == 1f && num != 1f)
		{
			bigContentMap.cardView2.OnArrivedInView(this);
			flag = true;
		}
		else if (cardLerp == 0f && num != 0f)
		{
			bigContentMap.cardView1.OnArrivedInView(this);
			flag = true;
		}
		if (flag)
		{
			EmitSignal(SignalName.CardArrivedInView);
		}
		float to = Mathf.Lerp(0.6f, 0.2f, transitionTime / 4f);
		float weight = ((cardLerp < 0.4f) ? (cardLerp / 0.4f) : ((!(cardLerp > 0.6f)) ? 1f : ((1f - cardLerp) / 0.4f)));
		float weight2 = Mathf.Pow(Mathf.SmoothStep(0f, 1f, weight), 0.5f);
		bigContentMap.Scale = Vector2.One * Mathf.Lerp(1f, to, weight2);
		Vector2 position = bigContentMap.Position;
		float weight3 = Mathf.InverseLerp(0.1f, 0.9f, cardLerp);
		float weight4 = Mathf.SmoothStep(0f, 1f, weight3);
		Vector2 vector = bigContentMap.cardView1.Position.Lerp(bigContentMap.cardView2.Position, weight4);
		bigContentMap.PivotOffset = vector + 0.5f * bigContentMap.cardView1.Size;
		bigContentMap.Position = -vector;
		targetBlurEffect = Mathf.Clamp(Mathf.InverseLerp(0f, 0.3f, weight), 0f, 1f);
		if (targetBlurEffect > currentBlurEffect)
		{
			currentBlurEffect = targetBlurEffect;
		}
		else
		{
			currentBlurEffect = Mathf.MoveToward(currentBlurEffect, targetBlurEffect, delta / blurEffectSettleDuration);
		}
		crtMaterial.SetShaderParameter("blur_effect", currentBlurEffect);
		if (hiddenImageShowing)
		{
			hiddenImageAlpha = Mathf.MoveToward(hiddenImageAlpha, 1f, delta / hiddenImageAlphaFadeInTime);
			if (hiddenImageAlpha >= 0.97f)
			{
				hiddenImageShowing = false;
			}
		}
		else
		{
			hiddenImageAlpha = Mathf.MoveToward(hiddenImageAlpha, 0f, delta / hiddenImageAlphaFadeOutTime);
		}
		hiddenImage.Modulate = new Color(1f, 1f, 1f, hiddenImageAlpha);
		if (activeCardView != null && otherCardView != null && screenIsOn)
		{
			float travelDistance = (activeCardView.Position - otherCardView.Position).Length();
			float movementSpeed = ((Mathf.Abs(delta) > 0f) ? ((bigContentMap.Position - position).Length() / delta) : 0f);
			machineAudio.UpdateCardMapMovementAudioLoop(movementSpeed, travelDistance, targetCardLerp, cardLerp);
		}
	}

	public void EditFromFlipperDigit(int index)
	{
		activeFlipperDigitIndex = index;
		UpdateFlippersAndCircleSelector();
	}

	private void UpdateFlippersAndCircleSelector()
	{
		bool flag = false;
		for (int i = 0; i < flipperDigits.Length; i++)
		{
			FlipperDigit flipperDigit = flipperDigits[i];
			if (flipperDigit.useLetters)
			{
				flipperDigit.SetValue(code[i] - 65);
			}
			else
			{
				flipperDigit.SetValue(code[i] - 48);
			}
			bool isSelected = flipperDigit.isSelected;
			flipperDigit.SetSelected(i == activeFlipperDigitIndex);
			if (isSelected != flipperDigit.isSelected)
			{
				flag = true;
			}
		}
		if (flag)
		{
			machineAudio.FlipperDigitSelectionChanged();
		}
		if (activeFlipperDigitIndex == 0 || activeFlipperDigitIndex == 1)
		{
			circleSelector.mode = CircleSelector.Mode.Letters;
		}
		else if (activeFlipperDigitIndex == 2 || activeFlipperDigitIndex == 3)
		{
			circleSelector.mode = CircleSelector.Mode.Numbers;
		}
		else
		{
			circleSelector.mode = CircleSelector.Mode.Off;
		}
		if (activeFlipperDigitIndex >= 0 && activeFlipperDigitIndex < 4)
		{
			circleSelector.currentIndex = ((activeFlipperDigitIndex >= 2) ? (code[activeFlipperDigitIndex] - 48) : (code[activeFlipperDigitIndex] - 65));
			circleSelector.flipperIndex = activeFlipperDigitIndex;
		}
		else
		{
			circleSelector.flipperIndex = -1;
		}
		if (activeFlipperDigitIndex >= 0 && activeFlipperDigitIndex < 4)
		{
			gearShifter.SetGear(activeFlipperDigitIndex + 1);
		}
		else
		{
			gearShifter.SetGear(0);
		}
	}

	private void UpdateCodeWithNewCharacterIndex(int index)
	{
		string text = code;
		StringBuilder stringBuilder = new StringBuilder(code);
		bool flag = activeFlipperDigitIndex == 0 || activeFlipperDigitIndex == 1;
		stringBuilder[activeFlipperDigitIndex] = (flag ? ((char)(65 + index)) : ((char)(48 + index)));
		code = stringBuilder.ToString();
		flipperDigits[activeFlipperDigitIndex].SetValue(index);
		circleSelector.currentIndex = index;
		circleSelector.flipperIndex = activeFlipperDigitIndex;
		if (code != text && !holdingTriggerForCodeEntry)
		{
			EmitSignal(SignalName.CodeChanged, code);
		}
	}

	private void IncrementDecrementFlipperDigit(int direction)
	{
		if (activeFlipperDigitIndex < 0 || activeFlipperDigitIndex >= 4)
		{
			return;
		}
		char c = code[activeFlipperDigitIndex];
		int num;
		int num2;
		if (activeFlipperDigitIndex != 0)
		{
			num = ((activeFlipperDigitIndex == 1) ? 1 : 0);
			if (num == 0)
			{
				num2 = 10;
				goto IL_0042;
			}
		}
		else
		{
			num = 1;
		}
		num2 = 26;
		goto IL_0042;
		IL_0042:
		int num3 = num2;
		int index = (((num != 0) ? (c - 65) : (c - 48)) + direction + num3) % num3;
		UpdateCodeWithNewCharacterIndex(index);
	}

	private void DidExitCodeEntryAutomatically()
	{
		graceTimeRemainingAfterAutomaticCodeEntryExit = 1f;
	}

	private void OnCircleSelectorChangedCharacter(int newValue)
	{
		if (activeFlipperDigitIndex >= 0 && activeFlipperDigitIndex < 4)
		{
			UpdateCodeWithNewCharacterIndex(newValue);
		}
	}

	private void OnCircleSelectorCharacterDirectlyClicked(int index)
	{
		bool flag = codeEntryMode;
		bool flag2 = false;
		activeFlipperDigitIndex++;
		if (activeFlipperDigitIndex >= 4)
		{
			if (holdingTriggerForCodeEntry)
			{
				activeFlipperDigitIndex = 3;
			}
			else
			{
				activeFlipperDigitIndex = 4;
				if (flag)
				{
					flag2 = true;
				}
			}
		}
		UpdateFlippersAndCircleSelector();
		if (flag2)
		{
			DidExitCodeEntryAutomatically();
		}
	}

	private void OnCircleSelectorKnobDraggingStarted()
	{
		if (!codeEntryMode)
		{
			activeFlipperDigitIndex = 0;
			UpdateFlippersAndCircleSelector();
		}
	}

	private void OnPressingScrollButton(int direction)
	{
		if (activeCardView != null)
		{
			activeCardView.Scroll(0.5f * (float)direction);
		}
	}

	private void OnFlipperDigitClicked(FlipperDigit digit)
	{
		if (digit.digitIndex != activeFlipperDigitIndex)
		{
			activeFlipperDigitIndex = digit.digitIndex;
			UpdateFlippersAndCircleSelector();
		}
	}

	private void OnGearShifterDraggedToGear(int gearNumber)
	{
		if (gearNumber == 0)
		{
			activeFlipperDigitIndex = 4;
		}
		else
		{
			activeFlipperDigitIndex = gearNumber - 1;
		}
		UpdateFlippersAndCircleSelector();
	}

	private void ConfirmActiveCharacter()
	{
		if (activeFlipperDigitIndex < 0 || activeFlipperDigitIndex >= 4)
		{
			return;
		}
		machineAudio.CircleSelectorPressedCharacter();
		circleSelector.DarkenCurrentCharacter();
		UpdateCodeWithNewCharacterIndex(circleSelector.currentIndex);
		bool flag = codeEntryMode;
		bool flag2 = false;
		activeFlipperDigitIndex++;
		if (activeFlipperDigitIndex >= 4)
		{
			if (holdingTriggerForCodeEntry)
			{
				activeFlipperDigitIndex = 3;
			}
			else
			{
				activeFlipperDigitIndex = 4;
				if (flag)
				{
					flag2 = true;
				}
			}
		}
		UpdateFlippersAndCircleSelector();
		if (PrimaryInputManager.isGamepad)
		{
			StoryController.instance.tutorialGamepadCharactersConfirmed++;
		}
		tutorialPressAToConfirmCharacterActive = false;
		lastCharacterEntryTime = (float)Time.GetTicksMsec() / 1000f;
		if (flag2)
		{
			DidExitCodeEntryAutomatically();
		}
		if (flag && !codeEntryMode && holdingTriggerForCodeEntry && code != lastSignalledCodeOnGamepad)
		{
			lastSignalledCodeOnGamepad = code;
			EmitSignal(SignalName.CodeChanged, code);
		}
	}

	private void SelectCharacterDirection(int direction)
	{
		if ((direction <= 0 || activeFlipperDigitIndex < 3) && (direction >= 0 || activeFlipperDigitIndex > 0))
		{
			if (direction > 0)
			{
				activeFlipperDigitIndex++;
			}
			else
			{
				activeFlipperDigitIndex--;
			}
			UpdateFlippersAndCircleSelector();
		}
	}

	private void CancelCharacter()
	{
		if (codeEntryMode && activeFlipperDigitIndex > 0)
		{
			activeFlipperDigitIndex--;
			UpdateFlippersAndCircleSelector();
		}
	}

	private void StartCodeEntry()
	{
		activeFlipperDigitIndex = 0;
		UpdateFlippersAndCircleSelector();
		lastSignalledCodeOnGamepad = code;
	}

	public void StopCodeEntry()
	{
		activeFlipperDigitIndex = 4;
		UpdateFlippersAndCircleSelector();
	}

	private void TryTypeCharacter(int index, bool isLetter)
	{
		if (activeFlipperDigitIndex >= 4 || activeFlipperDigitIndex < 0)
		{
			activeFlipperDigitIndex = ((!isLetter) ? 2 : 0);
		}
		if ((activeFlipperDigitIndex == 0 || activeFlipperDigitIndex == 1) == isLetter)
		{
			UpdateCodeWithNewCharacterIndex(index);
			ConfirmActiveCharacter();
			UpdateFlippersAndCircleSelector();
		}
	}

	private string ValidateCode(string newCode)
	{
		StringBuilder stringBuilder = new StringBuilder();
		string text = _code;
		for (int i = 0; i < 4; i++)
		{
			if (i >= newCode.Length)
			{
				stringBuilder.Append(text[i]);
				continue;
			}
			bool flag = i == 0 || i == 1;
			bool flag2 = newCode[i] >= 'A' && newCode[i] <= 'Z';
			bool flag3 = newCode[i] >= '0' && newCode[i] <= '9';
			if ((flag && !flag2) || (!flag && !flag3))
			{
				stringBuilder.Append(text[i]);
			}
			else
			{
				stringBuilder.Append(newCode[i]);
			}
		}
		return stringBuilder.ToString();
	}

	private void OnCardLinkPressedOnCard(CardView cardView, string link)
	{
		if (cardView == activeCardView)
		{
			if (graceTimeRemainingAfterAutomaticCodeEntryExit > 0f)
			{
				GD.Print("Grace period after automatic code entry exit, ignoring link press. Grace time remaining: " + graceTimeRemainingAfterAutomaticCodeEntryExit);
				return;
			}
			machineAudio.LinkButtonPressed();
			EmitSignal(SignalName.CardLinkPressed, link);
		}
	}

	public void DebugToggleScreen()
	{
		screenIsOn = !screenIsOn;
	}
}
