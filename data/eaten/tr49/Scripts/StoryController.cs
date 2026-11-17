using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text.RegularExpressions;
using Godot;
using Godot.Collections;
using GodotInk;
using Ink;
using Ink.Runtime;

public partial class StoryController : Node, IGlobalBackButtonHandler
{
	[Signal]
	public delegate void InkStoryReadyEventHandler();

	private enum BookNameContexts
	{
		OnPickUp,
		OnWrongAssignment,
		OnCorrectAssignement
	}

	private struct PropertyTag
	{
		public string property;

		public string val;
	}

	public static StoryController instance;

	public const string menuShowCode = "OP37";

	public const string menuContinueCode = "PL47";

	public const string menuRestartCode = "RE80";

	public const string menuSettingsCode = "SE77";

	public const string menuSendFeedbackCode = "FE30";

	public const string menuCreditsCode = "CR30";

	public const string menuInkleCode = "NK13";

	public const string menuQuitCode = "QU17";

	[Export(PropertyHint.None, "")]
	private InkStory story;

	[Export(PropertyHint.None, "")]
	private GameCamera gameCamera;

	[Export(PropertyHint.None, "")]
	private MachineUI machineUI;

	[Export(PropertyHint.None, "")]
	private VOController voController;

	[Export(PropertyHint.None, "")]
	private NotebookView notebookView;

	[Export(PropertyHint.None, "")]
	private HUDRoundButton notebookButton;

	[Export(PropertyHint.None, "")]
	private HUDRoundButton nameButton;

	[Export(PropertyHint.None, "")]
	private HUDRoundButton talkButton;

	[Export(PropertyHint.None, "")]
	private HUDButtons hudButtons;

	[Export(PropertyHint.None, "")]
	private ScoresView scoresView;

	[Export(PropertyHint.None, "")]
	private CogMenuButton menuButton;

	[Export(PropertyHint.None, "")]
	private MachineAudio machineAudio;

	[Export(PropertyHint.None, "")]
	private BackgroundMusicPlayer backgroundMusicPlayer;

	[Export(PropertyHint.None, "")]
	private AudioStreamPlayer musicPlayer;

	[Export(PropertyHint.None, "")]
	private ColorRect introFadeFromBlack;

	[Export(PropertyHint.None, "")]
	private float slowIntroFadeDuration = 20f;

	[Export(PropertyHint.None, "")]
	private Node steamWrapper;

	private System.Collections.Generic.Dictionary<string, int> choiceTextIndex = new System.Collections.Generic.Dictionary<string, int>();

	private bool generatingCardContent;

	private bool generatingNotebookContent;

	private NotebookMode targetNotebookMode;

	private string latestTitleCodeCollected = "";

	private List<string> notebookContent = new List<string>();

	private string notebookPerformedNewlyCorrectCodeAssignmentWhileOpen;

	private Queue<TimedContent> timedContentQueue = new Queue<TimedContent>();

	private List<SearchChoice> searchChoices;

	private InkChoice notebookChoice;

	private InkChoice nameChoice;

	private InkChoice talkChoice;

	private InkChoice continueChoice;

	private string codeThatGeneratedCurrentCard;

	private TimedContent _currentlyPresentingContent;

	private bool presenting;

	public bool gameMenuVisible;

	private Timer delayTimer;

	private Timer intercomDelayTimer;

	private Timer machineCodeDelayBeforeSearchTimer;

	private bool timersPaused;

	private Control previousGameMenuFocusOwner;

	private InkRelationStore inkRelationStore;

	private Ink.Runtime.InkList lastObservedAchievements;

	private List<Score> cachedScores = new List<Score>();

	private int _tutorialGamepadCharactersConfirmed;

	private float _tutorialGamepadThumbstickDegreesRolled;

	private float timerUntilTitleCollectionTooltipIsShown = -1f;

	private bool _generatedNewAudioThisTurn;

	private const int PROMPT_DELAY_BETWEEN_TALKING = 25;

	private List<TimedContent> timedElementsToSkip = new List<TimedContent>();

	private bool cuttingContinueChoice;

	private bool _inEndgame;

	private System.Collections.Generic.Dictionary<string, int> _codeIntCache = new System.Collections.Generic.Dictionary<string, int>();

	private string _mostRecentQuotePlayed;

	private const float kCriticalCoherence = 0.7f;

	private float _cachedCoherence = -1f;

	private System.Collections.Generic.Dictionary<int, string> _cachedJunkTitles = new System.Collections.Generic.Dictionary<int, string>();

	private System.Collections.Generic.Dictionary<Ink.Runtime.InkList, Ink.Runtime.InkList> _cacheCharacterCodeForCardCode = new System.Collections.Generic.Dictionary<Ink.Runtime.InkList, Ink.Runtime.InkList>();

	private static readonly Regex ScoreRegex = new Regex("^\\s*(\\d+)\\s*(?:\\/\\s*(\\d+)\\s*)?(.+)$");

	private IEnumerable<TimedContent> timedContentQueueIncludingCurrent
	{
		get
		{
			if (presenting)
			{
				return timedContentQueue.Append(_currentlyPresentingContent);
			}
			return timedContentQueue;
		}
	}

	private bool presentingUncuttableContent
	{
		get
		{
			if (presenting)
			{
				return timedContentQueueIncludingCurrent.Any((TimedContent t) => !t.cuttable);
			}
			return false;
		}
	}

	public int tutorialGamepadCharactersConfirmed
	{
		get
		{
			return _tutorialGamepadCharactersConfirmed;
		}
		set
		{
			_tutorialGamepadCharactersConfirmed = value;
			story.runtimeStory.variablesState["TUTORIAL_GAMEPAD_CHARACTERS_CONFIRMED"] = value;
		}
	}

	public bool tutorialGamepadThumbstickComplete => tutorialGamepadThumbstickDegreesRolled >= 720f;

	public float tutorialGamepadThumbstickDegreesRolled
	{
		get
		{
			return _tutorialGamepadThumbstickDegreesRolled;
		}
		set
		{
			_tutorialGamepadThumbstickDegreesRolled = value;
			story.runtimeStory.variablesState["TUTORIAL_GAMEPAD_THUMBSTICK_DEGREES_ROLLED"] = value;
		}
	}

	public bool canLinkButtonGrabFocus
	{
		get
		{
			if (!AlertView.instance.Visible && !SettingsView.instance.Visible && !notebookView.Visible)
			{
				return !AsanaFeedbackForm.instance.Visible;
			}
			return false;
		}
	}

	public static bool platformCanFeedback
	{
		get
		{
			if (!Platform.isMobile && !Platform.isSteamDeck)
			{
				return !Platform.isSwitch;
			}
			return false;
		}
	}

	public static bool platformCanLink => !Platform.isSwitch;

	public static bool platformCanQuit
	{
		get
		{
			if (!Platform.isMobile)
			{
				return !Platform.isSwitch;
			}
			return false;
		}
	}

	private bool lightsAreUp => (bool)story.runtimeStory.variablesState["LightsUp"];

	public string currentCardCode
	{
		get
		{
			if (story == null)
			{
				return "";
			}
			return (string)story.EvaluateFunction("currentCodeAsString");
		}
	}

	private bool canSave
	{
		get
		{
			if (!_inEndgame && story.runtimeStory.state.callstackDepth <= 1 && !generatingNotebookContent && !IsGameMenuCode(machineUI.code))
			{
				return !string.IsNullOrWhiteSpace(currentCardCode);
			}
			return false;
		}
	}

	private bool talkReminderTimeoutComplete => (int)story.runtimeStory.variablesState["TalkTimeout"] < 0;

	private bool talkedRecently => (int)story.runtimeStory.variablesState["TalkTimeout"] > 20;

	private bool immediateTalkFollowup
	{
		get
		{
			if (story.CurrentChoices.Count >= 1)
			{
				return story.CurrentChoices[0].inner.text.Contains("TALK");
			}
			return false;
		}
	}

	private bool doneIntro => (bool)story.runtimeStory.variablesState["LightsUp"];

	public int UIUnlockStateReached
	{
		get
		{
			if (nameButton.Visible)
			{
				return 3;
			}
			if (notebookButton.Visible)
			{
				return 2;
			}
			if (talkButton.Visible)
			{
				return 1;
			}
			return 0;
		}
	}

	public bool playerIsCollectingTitles { get; private set; }

	private int currentDelayChoiceIndex => story.runtimeStory.currentChoices.FindIndex((Choice c) => c.text.StartsWith("DELAY"));

	private float lengthOfDelay
	{
		get
		{
			string text = story.runtimeStory.currentChoices[currentDelayChoiceIndex].text;
			return ParseTextAsFloat(text.Split(' ').LastOrDefault(), (float)GD.RandRange(1.2000000476837158, 2.200000047683716) * minimumLengthOfRefreshDelay);
		}
	}

	private float minimumLengthOfRefreshDelay => Mathf.Max(4f, maxLengthOfIntercomDelay);

	private float maxLengthOfIntercomDelay
	{
		get
		{
			if (talkChoice == null || talkChoice.inner == null)
			{
				return 4f;
			}
			string text = talkChoice.inner.text.Split(' ').LastOrDefault();
			if (text == "FAST")
			{
				return 0.32f;
			}
			float num = ParseTextAsFloat(text, float.MaxValue);
			if (num <= 0f)
			{
				return 0.01f;
			}
			if (num > 0f && num < 20f)
			{
				return num;
			}
			if (talkedRecently && !immediateTalkFollowup)
			{
				return 8.5f;
			}
			return 2.5f;
		}
	}

	private bool machineIsRunning => !machineCodeDelayBeforeSearchTimer.IsStopped();

	public float coherence
	{
		get
		{
			if (_cachedCoherence < 0f)
			{
				_cachedCoherence = (float)story.EvaluateFunction("coherenceStat");
			}
			return _cachedCoherence;
		}
	}

	private float coherenceUncached
	{
		get
		{
			_cachedCoherence = -1f;
			return coherence;
		}
	}

	private bool animatingDecoherence => (float)story.FetchVariable("decoheringAnimatedStat") > 0f;

	public bool coherenceIsCriticallyLow => coherence < 0.7f;

	public bool currentCardIsRedacted
	{
		get
		{
			if (coherence < 1f)
			{
				return (bool)story.EvaluateFunction("currentCardNeedsName");
			}
			return false;
		}
	}

	private float audioClarityForCurrentCardQuote
	{
		get
		{
			if (!animatingDecoherence)
			{
				if (coherenceUncached != 1f && currentCardIsRedacted)
				{
					return 0.5f;
				}
				return 0.95f;
			}
			return 0.475f;
		}
	}

	public Array<string> GetAchievementNames()
	{
		if (instance.story.runtimeStory.listDefinitions.TryListGetDefinition("Achievements", out var def))
		{
			return new Array<string>(def.items.Keys.Select((InkListItem item) => item.itemName));
		}
		GD.PrintErr("Achievements list not found in ink");
		return new Array<string>();
	}

	public string CodeInStandardFormat(string code)
	{
		return code.Trim().ToUpper().Substring(0, Math.Min(5, code.Length))
			.Trim()
			.Replace("-", "")
			.Replace("_", "");
	}

	public override async void _Ready()
	{
		instance = this;
		delayTimer = GetNode<Timer>("DelayTimer");
		delayTimer.Timeout += delegate
		{
			OnDelayTimerTimeout();
		};
		intercomDelayTimer = GetNode<Timer>("IntercomDelayTimer");
		intercomDelayTimer.Timeout += delegate
		{
			OnIntercomTimerTimeout();
		};
		machineCodeDelayBeforeSearchTimer = GetNode<Timer>("MachineCodeDelayBeforeSearchTimer");
		machineCodeDelayBeforeSearchTimer.Timeout += delegate
		{
			OnMachineCodeDelayBeforeSearchTimerTimeout();
		};
		machineUI.CodeChanged += OnMachineCodeChanged;
		machineUI.CardLinkPressed += OnPressLink;
		machineUI.CardArrivedInView += OnCardArrivedInView;
		notebookButton.Pressed += OnPressNotebookButton;
		notebookButton.Visible = false;
		talkButton.Pressed += OnPressTalkButton;
		talkButton.Visible = false;
		nameButton.Pressed += OnPressNameButton;
		nameButton.Visible = false;
		menuButton.Pressed += OnPressMenuButton;
		notebookView.WillOpen += OnNotebookOpen;
		notebookView.CodeLinkPressed += OnNotebookPressCodeLink;
		notebookView.DidHide += OnNotebookViewDidHide;
		notebookView.mainCodesPage.AssignedCode += OnNotebookMainCodesPageAssignedCode;
		Credits.instance.DidComplete += OnCreditsDidComplete;
		Credits.instance.DidHide += OnCreditsDidHide;
		SettingsView.instance.DidHide += OnSettingsViewDidHide;
		AsanaFeedbackForm.instance.DidHide += OnAsanaFeedbackFormDidHide;
		AlertView.instance.DidHide += OnAlertViewDidHide;
		introFadeFromBlack.Visible = true;
		introFadeFromBlack.Modulate = new Color(1f, 1f, 1f);
		story.runtimeStory.allowExternalFunctionFallbacks = false;
		story.runtimeStory.onError += delegate(string error, ErrorType errorType)
		{
			GD.PushError($"Ink {errorType}: {error}");
		};
		if (DebugOptions.instance.clearAllAchievementsOnLoad)
		{
			steamWrapper.Connect("achievements_received_from_steam", Callable.From(delegate
			{
				steamWrapper.Call("clear_all_achievements");
			}));
		}
		SetupStory();
		story.StoryLoaded += delegate
		{
			GD.Print("Story changed, hot reloading");
			SetupStory();
			ReloadCurrentSave();
		};
		await ToSignal(GetTree(), "process_frame");
		notebookView.HideNotebook();
		if (DebugOptions.instance.hideIntercomButton)
		{
			talkButton.Modulate = new Color(1f, 1f, 1f, 0f);
		}
		gameCamera.SetDesaturateMode(desaturate: false);
	}

	private void OnCreditsDidComplete()
	{
		if (Credits.instance.context == ShowCreditsContext.EndOfGame)
		{
			story.EvaluateFunction("ClosingSummary", out string textOutput);
			story.EvaluateFunction("ClosingRewindText", out string textOutput2);
			string heading = InkStylingUtility.ProcessText(textOutput, terminatingPunctuation: true, stripSquareBrackets: true);
			string text = InkStylingUtility.ProcessText(textOutput2, terminatingPunctuation: false, stripSquareBrackets: true);
			List<AlertOption> list = new List<AlertOption>();
			list.Add(AlertOption.Primary(text, delegate
			{
				_inEndgame = false;
				ReloadCurrentSave();
			}));
			list.Add(AlertOption.Secondary("Reset", delegate
			{
				Restart();
			}));
			if (platformCanLink)
			{
				list.Add(new AlertOption
				{
					text = "More inkle games",
					action = delegate
					{
						OS.ShellOpen("https://www.inklestudios.com");
					},
					dontCloseOnAction = true
				});
			}
			if (platformCanQuit)
			{
				list.Add(AlertOption.Secondary("Quit", delegate
				{
					GetTree().Quit();
				}));
			}
			AlertView.instance.ShowAlert(heading, list.ToArray());
		}
		else
		{
			Credits.instance.HideCredits();
		}
	}

	private void CaptureGameMenuFocusOwner()
	{
		previousGameMenuFocusOwner = machineUI.activeCardView?.GetViewport().GuiGetFocusOwner();
	}

	private void TryRestorePreviousGameMenuFocusOwner()
	{
		if (previousGameMenuFocusOwner != null && (GodotObject.IsInstanceValid(previousGameMenuFocusOwner) & !previousGameMenuFocusOwner.IsQueuedForDeletion()))
		{
			previousGameMenuFocusOwner.GrabFocus();
			previousGameMenuFocusOwner = null;
		}
		else if (gameMenuVisible)
		{
			machineUI.activeCardView?.GrabFocusOnFirstButton();
		}
	}

	private void OnSettingsViewDidHide()
	{
		SyncReduceHintsOptionFromSettings();
		if (machineUI.code == "SE77")
		{
			machineUI.code = "OP37";
			TryRestorePreviousGameMenuFocusOwner();
		}
	}

	private void OnAsanaFeedbackFormDidHide()
	{
		if (machineUI.code == "FE30")
		{
			machineUI.code = "OP37";
			TryRestorePreviousGameMenuFocusOwner();
		}
	}

	private void OnAlertViewDidHide()
	{
		if (machineUI.code == "QU17")
		{
			machineUI.code = "OP37";
			TryRestorePreviousGameMenuFocusOwner();
		}
	}

	private void OnCreditsDidHide()
	{
		if (machineUI.code == "CR30")
		{
			machineUI.code = "OP37";
			TryRestorePreviousGameMenuFocusOwner();
		}
	}

	public override void _UnhandledInput(InputEvent @event)
	{
		if (@event.IsActionPressed("ui_menu") || (gameMenuVisible && @event.IsActionPressed("ui_cancel")))
		{
			this.SetInputAsHandled(@event);
			if (gameMenuVisible)
			{
				HideGameMenu();
			}
			else
			{
				ShowGameMenuOrAlertMiniMenu();
			}
		}
		if (@event.IsActionPressed("intercom") && talkButton.Visible && !talkButton.Disabled)
		{
			this.SetInputAsHandled(@event);
			talkButton.PlayPressedSound();
			OnPressTalkButton();
		}
		else if (@event.IsActionPressed("skip") && voController.Skip())
		{
			this.SetInputAsHandled(@event);
		}
		if (@event.IsActionPressed("notebook") && notebookButton.Visible && !notebookButton.Disabled)
		{
			this.SetInputAsHandled(@event);
			notebookButton.PlayPressedSound();
			OnPressNotebookButton();
		}
		if (@event.IsActionPressed("set_title") && nameButton.Visible && !nameButton.Disabled)
		{
			this.SetInputAsHandled(@event);
			nameButton.PlayPressedSound();
			OnPressNameButton();
		}
	}

	public override void _Process(double delta)
	{
		if (!presentingUncuttableContent && !machineUI.isTransitioningBetweenCards)
		{
			PopupManager.instance.ShowPendingPopups();
		}
		bool flag = AlertView.instance.Visible || SettingsView.instance.Visible || Credits.instance.Visible || TitleSplashScreen.instance.Visible || gameMenuVisible || notebookView.Visible || AsanaFeedbackForm.instance.Visible;
		if (flag != timersPaused)
		{
			timersPaused = flag;
			delayTimer.Paused = timersPaused;
			intercomDelayTimer.Paused = timersPaused;
			machineCodeDelayBeforeSearchTimer.Paused = timersPaused;
		}
		bool paused = AlertView.instance.Visible || SettingsView.instance.Visible || Credits.instance.Visible || gameMenuVisible || AsanaFeedbackForm.instance.Visible;
		voController.SetPaused(paused);
		UpdateTutorialForCollectingTitles((float)delta);
	}

	private void UpdateTutorialForCollectingTitles(float delta)
	{
		int score = GetScore("title");
		if (!playerIsCollectingTitles || score >= 3 || machineUI.activeCardView == null || machineUI.isTransitioningBetweenCards || GlobalBackButton.instance.WantsVisible || timersPaused || (machineUI.codeEntryMode && PrimaryInputManager.isGamepad))
		{
			timerUntilTitleCollectionTooltipIsShown = -1f;
			Tooltips.instance.RemoveTooltip("tutorial_collect_titles");
			return;
		}
		LinkButton linkButton = machineUI.activeCardView.GetFirstOnScreenTitleLink();
		Control control = machineUI.activeCardView.GetViewport().GuiGetFocusOwner();
		if (control != null && control is LinkButton { isTitle: not false, collected: false } linkButton2 && machineUI.activeCardView != null && machineUI.activeCardView.IsOnScreen(linkButton2))
		{
			linkButton = linkButton2;
		}
		if (linkButton == null)
		{
			timerUntilTitleCollectionTooltipIsShown = -1f;
			Tooltips.instance.RemoveTooltip("tutorial_collect_titles");
			return;
		}
		if (timerUntilTitleCollectionTooltipIsShown < 0f)
		{
			switch (score)
			{
			case 0:
				timerUntilTitleCollectionTooltipIsShown = 5f;
				break;
			case 1:
				timerUntilTitleCollectionTooltipIsShown = 8f;
				break;
			case 2:
				timerUntilTitleCollectionTooltipIsShown = 10f;
				break;
			default:
				return;
			}
		}
		timerUntilTitleCollectionTooltipIsShown -= delta;
		if (!(timerUntilTitleCollectionTooltipIsShown > 0f))
		{
			if (timerUntilTitleCollectionTooltipIsShown < 0f)
			{
				timerUntilTitleCollectionTooltipIsShown = 0f;
			}
			Vector3 targetPosition3D = machineUI.Get3DPositionOfControl(linkButton);
			string text = "Click to collect";
			if (Platform.isMobile)
			{
				text = "Tap to collect";
			}
			else if (PrimaryInputManager.instance.CurrentInputType == PrimaryInputManager.PrimaryInputType.Gamepad)
			{
				text = "Press to collect";
			}
			Tooltips.instance.ShowTooltip(targetPosition3D, text, "tutorial_collect_titles", Tooltip.Direction.Down, 0f, -35f);
		}
	}

	private void ShowGameMenu()
	{
		if (!gameMenuVisible)
		{
			OnSearch("OP37");
		}
	}

	public void HideGameMenu()
	{
		if (!gameMenuVisible)
		{
			GD.PrintErr("Tried to hide game menu when it wasn't visible");
			return;
		}
		previousGameMenuFocusOwner = null;
		machineUI.SetPresentingGameMenuCard(presentingActive: false, currentCardCode);
		SetPresentingGameMenu(gameMenuPresentationMode: false);
	}

	private void ShowGameMenuOrAlertMiniMenu()
	{
		if (gameMenuVisible || AlertView.instance.Visible)
		{
			return;
		}
		if (machineUI.screenIsOn)
		{
			ShowGameMenu();
			return;
		}
		List<AlertOption> list = new List<AlertOption>();
		list.Add(new AlertOption
		{
			text = "Resume",
			isCancel = true,
			isPrimary = true
		});
		list.Add(AlertOption.Secondary("Settings", delegate
		{
			SettingsView.instance.ShowSettings();
		}));
		if (platformCanQuit)
		{
			list.Add(AlertOption.Secondary("Quit", delegate
			{
				GetTree().Quit();
			}));
		}
		AlertView.instance.ShowAlert("TR-49", list.ToArray());
	}

	public void OnGlobalBackButtonPressed()
	{
		if (gameMenuVisible)
		{
			HideGameMenu();
		}
	}

	private void SetPresentingGameMenu(bool gameMenuPresentationMode)
	{
		gameMenuVisible = gameMenuPresentationMode;
		if (gameMenuVisible)
		{
			GlobalBackButton.instance.Push(this, strict: false);
		}
		else
		{
			GlobalBackButton.instance.Pop(this, strict: false);
		}
		if (gameMenuPresentationMode)
		{
			gameCamera.ChangePosition(GameCamera.Who.Menu, GameCamera.CameraPosition.Menu);
			gameCamera.SetDesaturateMode(desaturate: true);
		}
		else
		{
			gameCamera.ResetPosition(GameCamera.Who.Menu);
			gameCamera.SetDesaturateMode(desaturate: false);
		}
		if (gameMenuPresentationMode)
		{
			GameHUD.instance.SetVisibility(GameHUD.Who.Menu, visible: false);
		}
		else
		{
			GameHUD.instance.ResetVisibility(GameHUD.Who.Menu);
		}
	}

	private void SetupStory()
	{
		BindExternals();
		inkRelationStore = new InkRelationStore(story.runtimeStory);
		SetupStoryGlobalVariables();
		EmitSignal("InkStoryReady");
	}

	private void SetupStoryGlobalVariables()
	{
		story.runtimeStory.variablesState["INKY"] = false;
		story.runtimeStory.variablesState["PLATFORM_CAN_FEEDBACK"] = platformCanFeedback;
		story.runtimeStory.variablesState["PLATFORM_CAN_LINK"] = platformCanLink;
		story.runtimeStory.variablesState["PLATFORM_CAN_QUIT"] = platformCanQuit;
		SyncReduceHintsOptionFromSettings();
	}

	private void SyncReduceHintsOptionFromSettings()
	{
		bool num = (bool)story.runtimeStory.variablesState["REDUCE_HINTS"];
		bool reduceHints = GameSettings.instance.reduceHints;
		if (num != reduceHints)
		{
			story.runtimeStory.variablesState["REDUCE_HINTS"] = reduceHints;
			GD.Print($"Set Ink REDUCE_HINTS to: {reduceHints}");
		}
	}

	public void BeginOrSetupFromLoadedState()
	{
		if (DebugOptions.instance.artMode)
		{
			SetUpForArtMode();
			return;
		}
		SetupStoryGlobalVariables();
		AmbientAudio.instance.Begin();
		LightsController.instance.SetTurnedOn(lightsAreUp, immediate: true);
		if (!lightsAreUp)
		{
			introFadeFromBlack.Visible = true;
			introFadeFromBlack.Modulate = new Color(1f, 1f, 1f);
			Tween tween = CreateTween();
			tween.TweenProperty(introFadeFromBlack, "modulate:a", 0f, slowIntroFadeDuration).SetDelay(10.0);
			tween.Finished += delegate
			{
				introFadeFromBlack.Visible = false;
			};
		}
		else
		{
			introFadeFromBlack.Visible = false;
			GameHUD.instance.MoveHUDButtonsToSide(isOnSide: true, immediate: true);
		}
		FadeToBlack.instance.HideBlack(0f, 2f);
		SetCameraPositionFromInk(immediate: true);
		story.EvaluateFunction("clearSessionCache");
		UpdateScoreLabel();
		Continue();
		LoadingIcon.instance.wantsVisible = false;
	}

	private void SetUpForArtMode()
	{
		GetNode<Button>("../ScreenSpaceUI/DebugButtons/DebugLightsToggleButton").Visible = true;
		GetNode<Control>("../ScreenSpaceUI/DebugButtons/DebugCameraPos").Visible = true;
		GetNode<Control>("../ScreenSpaceUI/Blackbars/Top").Visible = false;
		GetNode<Control>("../ScreenSpaceUI/Blackbars/Bottom").Visible = false;
		GetNode<Control>("../ScreenSpaceUI/IntroFadeFromBlack").Visible = false;
		GetNode<Control>("../ScreenSpaceUI/GameHUD").Visible = false;
		GetNode<Control>("../ScreenSpaceUI/VOController").Visible = false;
		LoadingIcon.instance.fadeDuration = 0f;
		LoadingIcon.instance.wantsVisible = false;
	}

	private void ContinueWithChoiceAtIndex(int index)
	{
		story.ChooseChoiceIndex(index);
		Continue();
	}

	private bool IsGameMenuCode(string code)
	{
		switch (code)
		{
		case "FE30":
			if (platformCanFeedback)
			{
				break;
			}
			goto default;
		default:
			if (!(code == "CR30") && (!(code == "NK13") || !platformCanLink || !gameMenuVisible))
			{
				if (code == "QU17")
				{
					return platformCanQuit;
				}
				return false;
			}
			break;
		case "OP37":
		case "PL47":
		case "RE80":
		case "SE77":
			break;
		}
		return true;
	}

	private void GenerateMenu()
	{
		story.runtimeStory.SwitchFlow("generate_game_menu");
		story.runtimeStory.ChoosePathString("game_menu", true, SaveLoadManager.instance.secondsSinceSave);
		while (story.CanContinue)
		{
			NextInkContent();
		}
		generatingCardContent = false;
		story.runtimeStory.RemoveFlow("generate_game_menu");
	}

	private void GenerateAndShowNotebook(NotebookMode mode)
	{
		generatingNotebookContent = true;
		targetNotebookMode = mode;
		notebookContent.Clear();
		ContinueWithChoiceAtIndex(notebookChoice.Index);
	}

	private void Continue()
	{
		ResetChoiceRecords();
		_generatedNewAudioThisTurn = false;
		bool flag = playerIsCollectingTitles;
		delayTimer.Stop();
		if (canSave)
		{
			SaveLoadManager.instance.TrySave();
		}
		while (story.CanContinue)
		{
			NextInkContent();
		}
		if (flag != playerIsCollectingTitles && !generatingCardContent)
		{
			machineUI.activeCardView.RefreshAllLinkButtons();
		}
		if (generatingCardContent)
		{
			generatingCardContent = false;
			machineUI.PresentCard(codeThatGeneratedCurrentCard, !coherenceIsCriticallyLow, coherenceUncached, coherenceIsCriticallyLow, currentCardIsRedacted);
		}
		else if (generatingNotebookContent)
		{
			NotebookMode notebookMode = targetNotebookMode;
			generatingNotebookContent = false;
			targetNotebookMode = NotebookMode.Normal;
			Ink.Runtime.InkList inner = story.FetchVariable<GodotInk.InkList>("currentCard").inner;
			string text = ((inner.Count > 0) ? inner.First().Key.itemName : "");
			notebookView.ShowNotebook(notebookContent, text, latestTitleCodeCollected, notebookMode);
		}
		UpdateChoiceButtons();
	}

	private void DebugInkLog(string log)
	{
		if (DebugOptions.instance.debugLogInk)
		{
			GD.Print(log);
		}
	}

	private void NextInkContent()
	{
		if (!story.CanContinue)
		{
			GD.PrintErr("Expected story.CanContinue to be true");
			return;
		}
		string text = story.Continue().Trim();
		DebugInkLog("INK LINE: " + text);
		playerIsCollectingTitles = ((Ink.Runtime.InkList)story.runtimeStory.variablesState["AllTruth"]).ContainsItemNamed("RECORD_TITLES");
		IReadOnlyList<string> currentTags = story.CurrentTags;
		if (currentTags.Count > 0)
		{
			DebugInkLog("TAGS: " + string.Join(", ", currentTags));
		}
		if (currentTags.Contains("LOG") || (text.StartsWith("[") && text.EndsWith("]")))
		{
			DebugInkLog("INK LOG: " + text);
			return;
		}
		IReadOnlyList<InkChoice> currentChoices = story.CurrentChoices;
		foreach (InkChoice item in currentChoices)
		{
			DebugInkLog("CHOICE: " + item.Text);
		}
		string text2 = null;
		bool flag = false;
		bool flag2 = false;
		bool cuttable = false;
		bool flag3 = false;
		bool subtitleCentre = false;
		string text3 = null;
		string namedPopup = null;
		foreach (string item2 in currentTags)
		{
			if (SplitPropertyTag(item2, out var splitTag))
			{
				if (splitTag.property == "SECTION")
				{
					string val = splitTag.val;
					machineUI.activeCardView.StartSection(val);
				}
				else if (splitTag.property == "AUDIO")
				{
					text2 = splitTag.val;
				}
				else if (splitTag.property == "QUOTE_AUDIO")
				{
					text2 = splitTag.val;
					flag3 = true;
				}
				else if (splitTag.property == "UNLOCK")
				{
					text3 = splitTag.val;
				}
				else if (splitTag.property == "POPUP")
				{
					flag = true;
					namedPopup = splitTag.val.ToLowerInvariant();
				}
				else
				{
					GD.PrintErr("Unhandled split tag type: " + item2);
				}
				continue;
			}
			switch (item2)
			{
			case "CARD":
				generatingCardContent = true;
				ClearCuttableTimedContent();
				machineUI.ClearCard();
				break;
			case "ROW":
				machineUI.activeCardView.StartRow();
				break;
			case "CARD_TITLE":
				machineUI.activeCardView.Append("title", text);
				text = null;
				break;
			case "GLYPH":
				machineUI.activeCardView.Append("glyph", text.Trim());
				text = null;
				break;
			case "IMAGE":
				machineUI.activeCardView.SetImageBackground(text.Trim(), (bool)story.EvaluateFunction("isFace"));
				text = null;
				break;
			case "SKIPPABLE":
				flag2 = true;
				break;
			case "CUTTABLE":
				cuttable = true;
				break;
			case "HIDE_INPUT":
				machineUI.StopCodeEntry();
				break;
			case "CLEAR_AND_TURN_OFF_MACHINE":
				machineUI.ClearAndTurnOffMachine();
				break;
			case "RESTART":
				Restart();
				return;
			case "SUBTITLE_CENTRE":
				subtitleCentre = true;
				break;
			}
		}
		if (!string.IsNullOrWhiteSpace(text))
		{
			if (text.StartsWith(">>>"))
			{
				string instructionName;
				string text4 = (instructionName = text.Substring(">>>".Length).Trim());
				string instructionValue = null;
				string[] array = text4.Split(":", 2);
				if (array.Length > 1)
				{
					instructionName = array[0].Trim();
					instructionValue = array[1].Trim();
				}
				ProcessInstruction(instructionName, instructionValue);
			}
			else if (flag)
			{
				PopupManager.instance.Prepare(InkStylingUtility.ProcessAndStyleText(text), namedPopup, Popup.Priority.ExplicitInk);
			}
			else if (text.StartsWith("AUDIO:"))
			{
				text2 = text.Substring("AUDIO:".Length).Trim();
				QueueTimedContent(new TimedContent
				{
					type = TimedContentType.SFX,
					content = "",
					choices = null,
					skippable = flag2,
					audioFile = text2,
					cuttable = false,
					subtitleCentre = subtitleCentre
				});
			}
			else if (text.StartsWith("MUSIC:"))
			{
				backgroundMusicPlayer.PlayFromInk(text.Substring("MUSIC:".Length).Trim());
			}
			else if (text.IndexOf(":") == 2)
			{
				string text5 = text.Substring(0, 2);
				if ((!_generatedNewAudioThisTurn & flag2) && presentingUncuttableContent)
				{
					GD.Print("Skipping optional dialogue VO line completely");
				}
				else if (!CharacterIsCurrentInterlocutor(text5))
				{
					GD.Print("Skipping dialogue line because " + text5 + " is not present.");
				}
				else
				{
					string content = InkStylingUtility.ProcessAndStyleText(text.Substring(3));
					QueueTimedContent(new TimedContent
					{
						type = TimedContentType.VO,
						speaker = text5,
						content = content,
						choices = null,
						skippable = flag2,
						audioFile = text2,
						cuttable = cuttable,
						subtitleCentre = subtitleCentre
					});
					EnableHUDButton(talkButton, enable: false);
					_generatedNewAudioThisTurn = true;
				}
			}
			else if (generatingCardContent)
			{
				machineUI.activeCardView.Append("text", text);
				EnableHUDButton(talkButton, enable: false);
			}
			else if (generatingNotebookContent)
			{
				notebookContent.Add(text);
			}
			else if (text.Length > 0)
			{
				GD.PrintErr("Unexpected line of ink content with no particular purpose: " + text);
			}
		}
		if (flag3 && text2 != null && text2 != _mostRecentQuotePlayed)
		{
			PlayQuote(text2);
		}
		if (text3 != null)
		{
			machineUI.activeCardView.SetCurrentSectionUnlockCode(text3);
		}
		ParseChoices(currentChoices);
	}

	private void ProcessInstruction(string instructionName, string instructionValue)
	{
		switch (instructionName)
		{
		case "SECTION":
			machineUI.activeCardView.StartSection(instructionValue);
			break;
		case "ROW":
			machineUI.activeCardView.StartRow();
			break;
		case "QUOTE":
			machineUI.activeCardView.StartQuote();
			break;
		case "END_SECTION":
			machineUI.activeCardView.EndSection();
			break;
		case "END_ROW":
			machineUI.activeCardView.EndRow();
			break;
		case "END_QUOTE":
			machineUI.activeCardView.EndQuote();
			break;
		case "CREDITS":
			delayTimer.Stop();
			intercomDelayTimer.Stop();
			machineCodeDelayBeforeSearchTimer.Stop();
			Credits.instance.ShowCredits(ShowCreditsContext.EndOfGame, instructionValue == "SHORT");
			break;
		case "REMOVE_ALL_BUTTONS":
			HideAllButtons();
			break;
		default:
			GD.PushError("Unhandled instruction: " + instructionName);
			break;
		}
	}

	private void ResetChoiceRecords()
	{
		notebookChoice = null;
		talkChoice = null;
		nameChoice = null;
		continueChoice = null;
		cuttingContinueChoice = false;
		talkButton.highlighted = false;
		notebookButton.highlighted = false;
		nameButton.highlighted = false;
		choiceTextIndex.Clear();
		searchChoices = new List<SearchChoice>();
	}

	private void ParseChoices(IReadOnlyList<InkChoice> choices)
	{
		foreach (InkChoice choice in choices)
		{
			bool flag = false;
			bool flag2 = false;
			bool flag3 = false;
			bool clickable = true;
			bool flag4 = false;
			bool flag5 = false;
			bool unsolved = false;
			if (choice.Tags != null)
			{
				foreach (string tag in choice.Tags)
				{
					switch (tag.ToUpper())
					{
					case "CLOSE":
						if (!notebookView.Visible)
						{
							machineUI.canCloseCard = true;
						}
						break;
					case "UNSOLVED":
						unsolved = true;
						break;
					case "CURRENT_CARD":
						clickable = false;
						break;
					}
				}
			}
			if (choice.Text.StartsWith("DELAY"))
			{
				flag5 = true;
			}
			else if (choice.Text.StartsWith("CONTINUE"))
			{
				flag = true;
			}
			else if (choice.Text.StartsWith("NAME"))
			{
				flag3 = true;
			}
			else if (choice.Text.StartsWith("TALK"))
			{
				flag4 = true;
			}
			else if (choice.Text.StartsWith("NOTE"))
			{
				flag2 = true;
			}
			string key = CodeInStandardFormat(choice.Text);
			if (!choiceTextIndex.ContainsKey(key))
			{
				choiceTextIndex[key] = choice.Index;
			}
			if (flag5)
			{
				continue;
			}
			if (flag)
			{
				continueChoice = choice;
				cuttingContinueChoice = choice.Text.EndsWith("CUT");
			}
			else if (flag2)
			{
				notebookChoice = choice;
				notebookButton.highlighted = choice.Text.Contains("!");
			}
			else if (flag3)
			{
				nameChoice = choice;
				nameButton.highlighted = choice.Text.Contains("!");
			}
			else if (flag4)
			{
				if (talkChoice == null)
				{
					talkChoice = choice;
					if (GameSettings.instance.reduceHints && playerIsCollectingTitles)
					{
						talkButton.highlighted = false;
					}
					else
					{
						talkButton.highlighted = choice.Text.Contains('!') || choice.inner.index == 0 || (!choice.Text.Contains('?') && talkReminderTimeoutComplete);
					}
				}
			}
			else
			{
				searchChoices.Add(new SearchChoice
				{
					choice = choice,
					clickable = clickable,
					unsolved = unsolved
				});
			}
		}
	}

	private void ClearSkippableTimedContent()
	{
		foreach (TimedContent item in timedContentQueue)
		{
			if (item.skippable)
			{
				timedElementsToSkip.Add(item);
			}
		}
	}

	private void ClearCuttableTimedContent()
	{
		voController.CutIfCuttable();
		foreach (TimedContent item in timedContentQueueIncludingCurrent)
		{
			if (item.cuttable)
			{
				timedElementsToSkip.Add(item);
			}
		}
	}

	private void QueueTimedContent(TimedContent content)
	{
		timedContentQueue.Enqueue(content);
		if (!presenting)
		{
			presenting = true;
			PresentTimedContentQueue();
		}
	}

	private async void PresentTimedContentQueue()
	{
		while (timedContentQueue.Count > 0)
		{
			_currentlyPresentingContent = timedContentQueue.Dequeue();
			UpdateChoiceButtons();
			while (_currentlyPresentingContent.type == TimedContentType.Quote && (generatingCardContent || machineUI.isTransitioningBetweenCards))
			{
				await ToSignal(GetTree(), "process_frame");
			}
			if (timedElementsToSkip.Contains(_currentlyPresentingContent))
			{
				timedElementsToSkip.Remove(_currentlyPresentingContent);
			}
			else if (_currentlyPresentingContent.type == TimedContentType.VO)
			{
				string subtitle = _currentlyPresentingContent.speaker + ": " + _currentlyPresentingContent.content;
				await voController.Present(_currentlyPresentingContent.audioFile, subtitle, _currentlyPresentingContent.cuttable, 1f, _currentlyPresentingContent.subtitleCentre);
			}
			else if (_currentlyPresentingContent.type == TimedContentType.Quote)
			{
				_mostRecentQuotePlayed = _currentlyPresentingContent.audioFile;
				await voController.Present(_currentlyPresentingContent.audioFile, "", _currentlyPresentingContent.cuttable, audioClarityForCurrentCardQuote);
			}
			else if (_currentlyPresentingContent.type == TimedContentType.SFX)
			{
				voController.PlaySFX(_currentlyPresentingContent.audioFile);
			}
		}
		presenting = false;
		UpdateChoiceButtons();
	}

	private void UpdateChoiceButtons()
	{
		if (continueChoice != null && (!presenting || (cuttingContinueChoice && !presentingUncuttableContent)) && !notebookView.Visible)
		{
			if (cuttingContinueChoice)
			{
				ClearCuttableTimedContent();
			}
			ContinueWithChoiceAtIndex(continueChoice.Index);
			return;
		}
		EnableHUDButton(notebookButton, notebookChoice != null && !notebookView.Visible);
		if (talkChoice != null && !presentingUncuttableContent)
		{
			if (intercomDelayTimer.IsStopped() && talkButton.Disabled)
			{
				intercomDelayTimer.WaitTime = GD.RandRange(0.5, 1.0) * (double)maxLengthOfIntercomDelay;
				intercomDelayTimer.Start();
			}
		}
		else
		{
			intercomDelayTimer.Stop();
			EnableHUDButton(talkButton, enable: false);
		}
		EnableHUDButton(nameButton, nameChoice != null && !notebookView.Visible);
		if (currentDelayChoiceIndex != -1 && !presenting)
		{
			if (delayTimer.IsStopped())
			{
				delayTimer.WaitTime = lengthOfDelay;
				delayTimer.Start();
			}
		}
		else
		{
			delayTimer.Stop();
		}
	}

	private void RefreshTitlePopup()
	{
		if (nameButton.Visible)
		{
			story.EvaluateFunction("getTitlePopupText", out string textOutput);
			if (!string.IsNullOrWhiteSpace(textOutput))
			{
				PopupManager.instance.Prepare(textOutput.Trim(), "title", Popup.Priority.Titling);
			}
			else
			{
				PopupManager.instance.ClearPopup("title");
			}
		}
	}

	private void SetEndGameUIState()
	{
		_inEndgame = true;
		HUDRoundButton hUDRoundButton = nameButton;
		bool visible = (notebookButton.Visible = false);
		hUDRoundButton.Visible = visible;
	}

	private void EnableHUDButton(HUDRoundButton button, bool enable = true)
	{
		if (enable)
		{
			button.Visible = true;
		}
		bool flag = !enable;
		if (button.Disabled != flag)
		{
			button.Disabled = !enable;
			if (button == talkButton && enable)
			{
				voController.PlayWalkieTalkieSFX();
			}
		}
	}

	private void Clear(bool immediate)
	{
		delayTimer.Stop();
		intercomDelayTimer.Stop();
		machineCodeDelayBeforeSearchTimer.Stop();
		story.ResetState();
		SaveLoadManager.instance.ResetSaveTimer();
		SetupStoryGlobalVariables();
		playerIsCollectingTitles = false;
		tutorialGamepadCharactersConfirmed = 0;
		tutorialGamepadThumbstickDegreesRolled = 0f;
		inkRelationStore.Clear();
		timedContentQueue.Clear();
		HUDRoundButton hUDRoundButton = nameButton;
		HUDRoundButton hUDRoundButton2 = talkButton;
		bool flag = (notebookButton.Visible = false);
		bool visible = (hUDRoundButton2.Visible = flag);
		hUDRoundButton.Visible = visible;
		gameCamera.Clear();
		machineUI.ClearAndTurnOffMachine();
		machineUI.InitCode();
		GameHUD.instance.Clear();
		scoresView.Clear(immediate);
		cachedScores.Clear();
		if (immediate)
		{
			Credits.instance.Clear();
		}
		else
		{
			Credits.instance.HideCredits();
		}
		notebookView.Clear();
		latestTitleCodeCollected = "";
		PopupManager.instance.HideAll();
	}

	private void Restart()
	{
		Clear(immediate: false);
		SaveLoadManager.instance.TrySave();
		BeginOrSetupFromLoadedState();
	}

	private void ReloadCurrentSave()
	{
		LoadSave();
	}

	public void LoadSave(string filePathOverride = null)
	{
		Clear(immediate: false);
		SaveLoadManager.instance.TryLoad(filePathOverride);
		BeginOrSetupFromLoadedState();
	}

	public string SaveState()
	{
		return story.SaveState();
	}

	public void LoadState(string stateJson, string initialCode, int uiUnlockState, string music)
	{
		story.LoadState(stateJson);
		_tutorialGamepadCharactersConfirmed = (int)story.runtimeStory.variablesState["TUTORIAL_GAMEPAD_CHARACTERS_CONFIRMED"];
		_tutorialGamepadThumbstickDegreesRolled = (float)story.runtimeStory.variablesState["TUTORIAL_GAMEPAD_THUMBSTICK_DEGREES_ROLLED"];
		gameCamera.Clear();
		SetCameraPositionFromInk(immediate: true);
		machineUI.screenIsOn = true;
		machineUI.code = initialCode;
		OnMachineCodeChanged(initialCode);
		talkButton.Visible = uiUnlockState >= 1;
		notebookButton.Visible = uiUnlockState >= 2;
		nameButton.Visible = uiUnlockState >= 3;
		machineUI.StopCodeEntry();
		backgroundMusicPlayer.PlayFromInk(music);
	}

	private void HideAllButtons()
	{
		HUDRoundButton hUDRoundButton = nameButton;
		HUDRoundButton hUDRoundButton2 = notebookButton;
		bool flag = (talkButton.Visible = false);
		bool visible = (hUDRoundButton2.Visible = flag);
		hUDRoundButton.Visible = visible;
	}

	private void SetCameraPositionFromInk(bool immediate = false)
	{
		GameCamera.CameraPosition positionFromInkName = GameCamera.GetPositionFromInkName(((Ink.Runtime.InkList)story.runtimeStory.variablesState["CameraPosition"]).singleItem.itemName);
		gameCamera.ChangePosition(GameCamera.Who.MainOrInk, positionFromInkName, immediate);
	}

	private int IndexTextToCodeInt(string searchFor)
	{
		if (!_codeIntCache.ContainsKey(searchFor))
		{
			if (!new Regex("^[A-Za-z]{2}-?\\d{2}$").IsMatch(searchFor))
			{
				return -1;
			}
			string text = searchFor.Substring(0, 2);
			string text2 = searchFor.Substring(2);
			int num = text[0].ToString().ToUpper()[0] - 65 + 1;
			int num2 = text[1].ToString().ToUpper()[0] - 65 + 1;
			string text3 = num.ToString().PadLeft(2, '0');
			string text4 = num2.ToString().PadLeft(2, '0');
			_codeIntCache[searchFor] = int.Parse(text3 + text4 + text2);
		}
		return _codeIntCache[searchFor];
	}

	private void PlayQuote(string audioFile)
	{
		QueueTimedContent(new TimedContent
		{
			type = TimedContentType.Quote,
			content = "",
			choices = null,
			skippable = true,
			audioFile = audioFile,
			cuttable = true
		});
	}

	private void SayBookName(string cardCode, BookNameContexts context)
	{
		if (presentingUncuttableContent)
		{
			return;
		}
		ClearCuttableTimedContent();
		ClearSkippableTimedContent();
		string text;
		string value;
		switch (context)
		{
		case BookNameContexts.OnWrongAssignment:
			text = "?";
			value = "qn";
			break;
		case BookNameContexts.OnCorrectAssignement:
			text = "!";
			value = "done";
			break;
		default:
			text = "...";
			value = "new";
			break;
		}
		if (context == BookNameContexts.OnPickUp)
		{
			story.EvaluateFunction("ME_TutorialiseTitlePickup", out string textOutput, cardCode);
			if (!string.IsNullOrWhiteSpace(textOutput))
			{
				string[] array = textOutput.Split("AUDIO:");
				ClearSkippableTimedContent();
				QueueTimedContent(new TimedContent
				{
					type = TimedContentType.VO,
					speaker = "ME",
					content = InkStylingUtility.ProcessAndStyleText(array[0]),
					choices = null,
					skippable = false,
					audioFile = array[1].Trim(),
					cuttable = (context == BookNameContexts.OnPickUp)
				});
			}
		}
		string content = "\"" + GetTitleForBook(cardCode, getFullTitle: true) + "\"" + text;
		QueueTimedContent(new TimedContent
		{
			type = TimedContentType.VO,
			speaker = "ME",
			content = content,
			choices = null,
			skippable = false,
			audioFile = $"Audio/Titles/{cardCode}_{value}.ogg",
			cuttable = (context == BookNameContexts.OnPickUp)
		});
	}

	public void TryCollectTitle(string titleCode)
	{
		GD.Print("Collected title: " + titleCode);
		if ((bool)story.runtimeStory.EvaluateFunction("pickUpTitle", titleCode))
		{
			if (!presentingUncuttableContent)
			{
				SayBookName(titleCode, BookNameContexts.OnPickUp);
			}
			machineUI.activeCardView.MarkTitleCollected(titleCode);
			latestTitleCodeCollected = titleCode;
			GenerateAndShowNotebook(NotebookMode.NewTitleRecorded);
		}
	}

	public string VerifyAdditionalWritingLink(string code)
	{
		return (string)story.EvaluateFunction("getLiveVersionOfHardCodedCode", code);
	}

	private void OnNotebookOpen()
	{
		PopupManager.instance.HideAll();
	}

	private void OnNotebookPressCodeLink(string link)
	{
		OnPressLink(link);
	}

	private void OnNotebookMainCodesPageAssignedCode(string titleRealCode, string assignedCode, bool isSilentSwap)
	{
		if (string.IsNullOrWhiteSpace(assignedCode))
		{
			GD.PushError("OnNotebookMainCodesPageAssignedCode: assignedCode should ALWAYS be set, even if titleRealCode is unassigned. assignedCode was: " + assignedCode);
			return;
		}
		Ink.Runtime.InkList inkList = Ink.Runtime.InkList.FromString(titleRealCode, story.runtimeStory);
		Ink.Runtime.InkList inkList2 = Ink.Runtime.InkList.FromString(assignedCode ?? "", story.runtimeStory);
		story.runtimeStory.EvaluateFunction("nameCardAs", out var _, inkList2, inkList);
		bool flag = assignedCode == titleRealCode;
		if (!string.IsNullOrWhiteSpace(titleRealCode))
		{
			SayBookName(titleRealCode, (!flag || GameSettings.instance.reduceHints) ? BookNameContexts.OnWrongAssignment : BookNameContexts.OnCorrectAssignement);
		}
		if (flag && assignedCode == currentCardCode)
		{
			notebookPerformedNewlyCorrectCodeAssignmentWhileOpen = assignedCode;
		}
	}

	public string GetDragTooltipText(string codeOfLabel)
	{
		story.EvaluateFunction("getTooltipTextForCode", out string textOutput, DepunctuateCode(codeOfLabel));
		return textOutput.Trim();
	}

	private void OnPressLink(string link)
	{
		if (link.StartsWith("TITLE:"))
		{
			if (playerIsCollectingTitles && notebookChoice != null)
			{
				TryCollectTitle(link.Substring("TITLE:".Length));
			}
			else
			{
				GD.Print("Player is not collecting titles, so cannot collect title: " + link);
			}
		}
		else if (machineUI.code != link)
		{
			string text;
			if (link.Length == 2)
			{
				text = ((!int.TryParse(link, out var _)) ? (link + machineUI.code.Substring(2, 2)) : (machineUI.code.Substring(0, 2) + link));
			}
			else
			{
				text = DepunctuateCode(link);
				machineUI.StopCodeEntry();
			}
			if (text != machineUI.code)
			{
				machineUI.code = text;
				OnMachineCodeChanged(text);
			}
		}
	}

	private void OnCardArrivedInView()
	{
		RefreshTitlePopup();
	}

	private void OnNotebookViewDidHide()
	{
		latestTitleCodeCollected = "";
		if (notebookPerformedNewlyCorrectCodeAssignmentWhileOpen == currentCardCode)
		{
			string codeCollected = notebookPerformedNewlyCorrectCodeAssignmentWhileOpen;
			notebookPerformedNewlyCorrectCodeAssignmentWhileOpen = "";
			machineUI.activeCardView.ScrollToTop();
			machineUI.RippleScreen();
			voController.PlaySFX("Audio/SFX/SoftCrackle.ogg", delegate
			{
				if (codeCollected == currentCardCode)
				{
					PlayQuote(_mostRecentQuotePlayed);
				}
			});
		}
		UpdateChoiceButtons();
		TryRefresh();
	}

	private void OnPressTalkButton()
	{
		PopupManager.instance.intercomPopup.Hide();
		if (talkChoice == null)
		{
			GD.Print("No talk choice found");
		}
		else if (!machineIsRunning)
		{
			if (story.runtimeStory.currentChoices.Contains(talkChoice.inner))
			{
				ClearCuttableTimedContent();
				EnableHUDButton(talkButton, enable: false);
				ContinueWithChoiceAtIndex(talkChoice.Index);
			}
			else
			{
				GD.Print("Current moment's talk choice " + talkChoice.Text + " not found in current choices. Is it out of date?");
				talkChoice = null;
			}
		}
	}

	private void OnPressNameButton()
	{
		if (nameChoice == null)
		{
			GD.Print("No naming choice found");
		}
		else if (!machineIsRunning)
		{
			if (story.runtimeStory.currentChoices.Contains(nameChoice.inner))
			{
				EnableHUDButton(nameButton, enable: false);
				GenerateAndShowNotebook(NotebookMode.CodeAssignment);
			}
			else
			{
				GD.Print("Current moment's Name choice " + nameChoice.Text + " not found in current choices. Is it out of date?");
				nameChoice = null;
			}
		}
	}

	private void OnPressNotebookButton()
	{
		if (notebookChoice == null)
		{
			GD.Print("No notebook choice found");
		}
		else if (!machineIsRunning)
		{
			if (story.runtimeStory.currentChoices.Contains(notebookChoice.inner))
			{
				GenerateAndShowNotebook(NotebookMode.Normal);
			}
			else
			{
				GD.Print("Current moment's notebook choice " + notebookChoice.Text + " not found in current choices. Is it out of date?");
				notebookChoice = null;
			}
			UpdateChoiceButtons();
		}
	}

	private void OnPressMenuButton()
	{
		ShowGameMenuOrAlertMiniMenu();
	}

	private void OnIntercomTimerTimeout()
	{
		EnableHUDButton(talkButton, !presentingUncuttableContent && talkChoice != null);
	}

	private void OnDelayTimerTimeout()
	{
		TryRefresh();
	}

	private float ParseTextAsFloat(string text, float fallbackValue)
	{
		text = text.Replace(',', '.');
		if (!float.TryParse(text, NumberStyles.Float, CultureInfo.InvariantCulture, out var result))
		{
			return fallbackValue;
		}
		return result;
	}

	private bool TryRefresh(bool calledFromMachine = false)
	{
		if (machineIsRunning && !calledFromMachine)
		{
			return false;
		}
		int num = currentDelayChoiceIndex;
		if (num == -1)
		{
			return false;
		}
		ContinueWithChoiceAtIndex(num);
		return true;
	}

	public void OnMachineCodeChanged(string code)
	{
		if (IsGameMenuCode(code))
		{
			machineCodeDelayBeforeSearchTimer.Stop();
			OnSearch(code);
			return;
		}
		if (code == "TR49" && !(bool)story.runtimeStory.variablesState["SHOWN_SPLASH"])
		{
			story.runtimeStory.variablesState["SHOWN_SPLASH"] = true;
			TitleSplashScreen.instance.ShowSplash();
		}
		machineCodeDelayBeforeSearchTimer.Start();
	}

	private void OnMachineCodeDelayBeforeSearchTimerTimeout()
	{
		OnSearch(machineUI.code);
	}

	private void OnSearch(string inputText)
	{
		inputText = CodeInStandardFormat(inputText);
		if (IsGameMenuCode(inputText) && inputText != "OP37" && inputText != "PL47")
		{
			if (!gameMenuVisible)
			{
				ShowGameMenu();
			}
			machineUI.code = inputText;
		}
		if (inputText == "OP37")
		{
			if (!gameMenuVisible)
			{
				SetPresentingGameMenu(gameMenuPresentationMode: true);
				GenerateMenu();
				machineUI.SetPresentingGameMenuCard(presentingActive: true);
				machineUI.code = "OP37";
				delayTimer.Paused = true;
			}
			return;
		}
		if (gameMenuVisible && inputText == "PL47")
		{
			HideGameMenu();
			return;
		}
		switch (inputText)
		{
		case "RE80":
			CaptureGameMenuFocusOwner();
			AlertView.instance.ShowAlert("Are you sure you want to completely reset the game?", AlertOption.Primary("Reset", delegate
			{
				HideGameMenu();
				Restart();
			}), AlertOption.Cancel(delegate
			{
				machineUI.code = "OP37";
				TryRestorePreviousGameMenuFocusOwner();
			}));
			return;
		case "SE77":
			CaptureGameMenuFocusOwner();
			SettingsView.instance.ShowSettings();
			return;
		case "FE30":
			if (platformCanFeedback)
			{
				CaptureGameMenuFocusOwner();
				AsanaFeedbackForm.instance.ShowFeedbackForm();
				return;
			}
			break;
		}
		if (inputText == "CR30")
		{
			CaptureGameMenuFocusOwner();
			Credits.instance.ShowCredits(ShowCreditsContext.GameMenu);
			return;
		}
		if (inputText == "NK13" && gameMenuVisible && platformCanLink)
		{
			CaptureGameMenuFocusOwner();
			OS.ShellOpen("https://www.inklestudios.com");
			machineUI.code = "OP37";
			return;
		}
		if (inputText == "QU17" && platformCanQuit)
		{
			CaptureGameMenuFocusOwner();
			AlertView.instance.ShowAlert("Are you sure you want to quit?", AlertOption.Primary("Quit", delegate
			{
				GetTree().Quit();
			}), AlertOption.Cancel(delegate
			{
				machineUI.code = "OP37";
				TryRestorePreviousGameMenuFocusOwner();
			}));
			return;
		}
		if (gameMenuVisible)
		{
			gameMenuVisible = false;
			SetPresentingGameMenu(gameMenuPresentationMode: false);
		}
		if (TryUseUnlockCodeForActiveCard(inputText))
		{
			return;
		}
		int num = IndexTextToCodeInt(inputText);
		if (choiceTextIndex.ContainsKey(inputText))
		{
			codeThatGeneratedCurrentCard = inputText;
			ContinueWithChoiceAtIndex(choiceTextIndex[inputText]);
			return;
		}
		if (choiceTextIndex.ContainsKey("CODE") && num > -1)
		{
			story.StoreVariable("inputCardInt", num);
			codeThatGeneratedCurrentCard = inputText;
			ContinueWithChoiceAtIndex(choiceTextIndex["CODE"]);
			return;
		}
		if (TryRefresh(calledFromMachine: true))
		{
			GD.Print("CODE choice not found; called DELAY fallback to refresh.");
		}
		else
		{
			GD.Print("CODE choice not found; no DELAY fallback either; this can happen safely inside enforced dialogue moments.");
		}
		if (lightsAreUp)
		{
			GD.Print("Restart machine timer so we can check in on the code when ready for it.");
			machineCodeDelayBeforeSearchTimer.Start();
		}
	}

	private bool TryUseUnlockCodeForActiveCard(string code)
	{
		CardView activeCardView = machineUI.activeCardView;
		if (activeCardView == null)
		{
			return false;
		}
		if (activeCardView.TryUnlockSectionWithCode(code))
		{
			machineAudio.CardSectionUnlocked();
			story.EvaluateFunction("usedUnlockCode", code);
			return true;
		}
		return false;
	}

	private string GetCodeFromInkCode(object x)
	{
		if (x is Ink.Runtime.InkList { Count: >0 } inkList)
		{
			return inkList.singleItem.itemName;
		}
		return x.ToString();
	}

	public static string HyphenateCode(string code)
	{
		if (code.Length == 4)
		{
			string text = code.Substring(0, 2);
			string text2 = code.Substring(2);
			return text + "-" + text2;
		}
		return code;
	}

	public static string DepunctuateCode(string input)
	{
		if (string.IsNullOrEmpty(input))
		{
			return input;
		}
		Span<char> span = stackalloc char[input.Length];
		int length = 0;
		foreach (char c in input)
		{
			if (!char.IsPunctuation(c))
			{
				span[length++] = c;
			}
		}
		return new string(span.Slice(0, length));
	}

	private bool InkListContainsElement(string element, string inkListVariableName)
	{
		Ink.Runtime.InkList otherList = Ink.Runtime.InkList.FromString(element, story.runtimeStory);
		return story.FetchVariable<GodotInk.InkList>(inkListVariableName).inner.Contains(otherList);
	}

	private bool CharacterIsCurrentInterlocutor(string characterCode)
	{
		return InkListContainsElement(characterCode, "Interlocutors");
	}

	public bool GotTitle(string code)
	{
		return InkListContainsElement(DepunctuateCode(code), "TitlesCollected");
	}

	public string GetTitleForBook(string code, bool getFullTitle = false)
	{
		story.EvaluateFunction("getTitleFromStringCode", out string textOutput, code, getFullTitle);
		return textOutput.Trim();
	}

	private void BindExternals()
	{
		story.runtimeStory.BindExternalFunction("alpha", (int n) => ((char)(65 + n - 1)).ToString(), lookaheadSafe: true);
		story.runtimeStory.BindExternalFunction("fuzz", (string sourceString) => CardTextContent.FuzzText(sourceString, 0.3f, coherenceIsCriticallyLow: true));
		story.runtimeStory.BindExternalFunction("NowPlaying", () => backgroundMusicPlayer.currentMusicFromInk ?? "");
		story.runtimeStory.BindExternalFunction("cardLinkCount", () => machineUI.activeCardView?.linkCount ?? 0);
		story.runtimeStory.BindExternalFunction("currentlyTalking", delegate
		{
			if (!presenting)
			{
				return false;
			}
			foreach (TimedContent item in timedContentQueueIncludingCurrent)
			{
				if (!item.skippable && item.type == TimedContentType.VO)
				{
					return true;
				}
				if (item.type == TimedContentType.Quote)
				{
					return true;
				}
			}
			return false;
		});
		story.runtimeStory.BindExternalFunction("getTitleForJunkBook", delegate(int keyInt)
		{
			if (!_cachedJunkTitles.ContainsKey(keyInt))
			{
				story.EvaluateFunction("_getTitleForJunkBook", out string textOutput, keyInt);
				_cachedJunkTitles[keyInt] = textOutput.Trim();
			}
			return _cachedJunkTitles[keyInt];
		}, lookaheadSafe: true);
		story.runtimeStory.BindExternalFunction("forceCode", delegate(string codeString)
		{
			machineUI.code = codeString;
		});
		story.runtimeStory.BindExternalFunction("formatCardCode", (object x) => HyphenateCode(GetCodeFromInkCode(x)), lookaheadSafe: true);
		story.runtimeStory.BindExternalFunction("nameCodeFrom", delegate(object x)
		{
			Ink.Runtime.InkList inkList = (Ink.Runtime.InkList)x;
			if (!_cacheCharacterCodeForCardCode.ContainsKey(inkList))
			{
				string codeFromInkCode = GetCodeFromInkCode(inkList);
				string stringName = ((codeFromInkCode.Length > 0) ? codeFromInkCode.Substr(0, 2) : "");
				_cacheCharacterCodeForCardCode[inkList] = StringToInkList(stringName);
			}
			return _cacheCharacterCodeForCardCode[inkList];
		}, lookaheadSafe: true);
		story.runtimeStory.BindExternalFunction("_getIntFromCode", delegate(object x)
		{
			string codeFromInkCode = GetCodeFromInkCode(x);
			return IndexTextToCodeInt(codeFromInkCode);
		}, lookaheadSafe: true);
		story.runtimeStory.BindExternalFunction("_getValueOfState", delegate(object x)
		{
			Ink.Runtime.InkList otherList = x as Ink.Runtime.InkList;
			if (!((Ink.Runtime.InkList)story.runtimeStory.variablesState["StatesInStorage"]).Contains(otherList))
			{
				return 0;
			}
			int num2 = 0;
			for (int num3 = 1; num3 <= 262144; num3 *= 2)
			{
				if (((Ink.Runtime.InkList)story.runtimeStory.variablesState["StatesBinary" + num3]).Contains(otherList))
				{
					num2 += num3;
				}
			}
			return num2 * ((!((Ink.Runtime.InkList)story.runtimeStory.variablesState["StatesNegative"]).Contains(otherList)) ? 1 : (-1));
		}, lookaheadSafe: true);
		story.runtimeStory.BindExternalFunction("STRING_TO_LIST", (string stringName) => StringToInkList(stringName), lookaheadSafe: true);
		story.runtimeStory.BindExternalFunction("tunnelDepth", () => story.runtimeStory.state.callstackDepth, lookaheadSafe: true);
		story.runtimeStory.BindExternalFunction("HAS_ANY", (Ink.Runtime.InkList listOne, Ink.Runtime.InkList listTwo) => listOne.HasIntersection(listTwo), lookaheadSafe: true);
		story.runtimeStory.BindExternalFunction("LIST_IS_MEMBER_OF", delegate(Ink.Runtime.InkList listForList, Ink.Runtime.InkList sourceList)
		{
			if (listForList.origins == null)
			{
				return false;
			}
			foreach (ListDefinition origin in listForList.origins)
			{
				if (!sourceList.origins.Contains(origin))
				{
					return false;
				}
			}
			return true;
		}, lookaheadSafe: true);
		story.runtimeStory.BindExternalFunction("STOP_LOOKAHEAD", delegate
		{
		});
		Story runtimeStory = story.runtimeStory;
		List<string> list = new List<string>();
		CollectionsMarshal.SetCount(list, 4);
		Span<string> span = CollectionsMarshal.AsSpan(list);
		int num = 0;
		span[num] = "TitlesCollected";
		num++;
		span[num] = "Cards";
		num++;
		span[num] = "mostRecentCardNamed";
		num++;
		span[num] = "LightsUp";
		num++;
		runtimeStory.ObserveVariables(list, delegate
		{
			if (!animatingDecoherence)
			{
				UpdateScoreLabel();
			}
		});
		story.runtimeStory.ObserveVariable("whatYouErased", delegate(string varName, object newValue)
		{
			if (((Ink.Runtime.InkList)newValue).Count > 0)
			{
				SetEndGameUIState();
			}
		});
		story.runtimeStory.ObserveVariable("CameraPosition", delegate
		{
			SetCameraPositionFromInk();
		});
		story.runtimeStory.ObserveVariable("LightsUp", delegate(string varName, object newValue)
		{
			LightsController.instance.SetTurnedOn((bool)newValue);
		});
		Story runtimeStory2 = story.runtimeStory;
		List<string> list2 = new List<string>();
		CollectionsMarshal.SetCount(list2, 2);
		span = CollectionsMarshal.AsSpan(list2);
		num = 0;
		span[num] = "coherence";
		num++;
		span[num] = "decoheringAnimatedStat";
		num++;
		runtimeStory2.ObserveVariables(list2, delegate
		{
			RefreshCardFuzzAndRedaction();
		});
		Story runtimeStory3 = story.runtimeStory;
		List<string> list3 = new List<string>();
		CollectionsMarshal.SetCount(list3, 1);
		span = CollectionsMarshal.AsSpan(list3);
		num = 0;
		span[num] = "Achievements";
		num++;
		runtimeStory3.ObserveVariables(list3, delegate(string varName, object newValue)
		{
			if (!steamWrapper.Get("steam_initialized").As<bool>())
			{
				GD.Print("Steam not (yet?) initialized, skipping achievement unlock checks");
			}
			else
			{
				Ink.Runtime.InkList inkList = newValue as Ink.Runtime.InkList;
				if (inkList != null)
				{
					Ink.Runtime.InkList inkList2 = inkList;
					if (lastObservedAchievements != null)
					{
						inkList2 = new Ink.Runtime.InkList(inkList);
						inkList2.Without(lastObservedAchievements);
					}
					foreach (InkListItem key in inkList2.Keys)
					{
						GD.Print("Unlocking achievement: " + key.itemName);
						steamWrapper.Call("unlock_achievement", key.itemName);
					}
				}
				else
				{
					GD.PrintErr("Achievements list is null, newValue was: " + newValue);
				}
				lastObservedAchievements = inkList;
			}
		});
	}

	private Ink.Runtime.InkList StringToInkList(string stringName)
	{
		if ((bool)story.runtimeStory.listDefinitions.FindSingleItemListWithName(stringName))
		{
			return Ink.Runtime.InkList.FromString(stringName, story.runtimeStory);
		}
		return new Ink.Runtime.InkList();
	}

	private void RefreshCardFuzzAndRedaction()
	{
		if (machineUI.activeCardView != null)
		{
			machineUI.activeCardView.Fuzz(coherenceUncached, coherenceIsCriticallyLow, currentCardIsRedacted);
		}
	}

	public void DebugUnredactCard()
	{
		if (machineUI.activeCardView != null)
		{
			machineUI.activeCardView.ScrollToTop();
			machineUI.RippleScreen();
			PlayQuote(_mostRecentQuotePlayed);
			machineUI.activeCardView.Fuzz(1f, coherenceIsCriticallyLow: false, redacted: false);
		}
	}

	private void UpdateScoreLabel()
	{
		story.EvaluateFunction("ScoreText", out string textOutput, true);
		string[] array = textOutput.Split("\n");
		List<Score> list = new List<Score>(3);
		string[] array2 = array;
		foreach (string input in array2)
		{
			Match match = ScoreRegex.Match(input);
			if (match.Success)
			{
				Score item = new Score
				{
					value = int.Parse(match.Groups[1].Value),
					label = match.Groups[3].Value
				};
				if (match.Groups[2].Success)
				{
					item.total = int.Parse(match.Groups[2].Value);
				}
				list.Add(item);
			}
		}
		scoresView.UpdateScores(list);
		cachedScores = list;
	}

	public int GetScore(string forLabel)
	{
		foreach (Score cachedScore in cachedScores)
		{
			if (cachedScore.label.ToLowerInvariant().Contains(forLabel.ToLowerInvariant().Trim()))
			{
				return cachedScore.value;
			}
		}
		return 0;
	}

	private bool SplitPropertyTag(string tag, out PropertyTag splitTag)
	{
		splitTag = new PropertyTag
		{
			property = "",
			val = ""
		};
		int num = tag.IndexOf(':');
		if (num != -1)
		{
			splitTag.property = tag.Substring(0, num).Trim().ToUpper();
			splitTag.val = tag.Substring(num + 1).Trim();
			return true;
		}
		return false;
	}
}
