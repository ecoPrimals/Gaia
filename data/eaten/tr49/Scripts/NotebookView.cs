using System.Collections.Generic;
using Godot;

public partial class NotebookView : Control, IGlobalBackButtonHandler
{
	[Signal]
	public delegate void WillOpenEventHandler();

	[Signal]
	public delegate void CodeLinkPressedEventHandler(string link);

	[Signal]
	public delegate void DidHideEventHandler();

	private enum HorizontalPagesDragState
	{
		None,
		PressStarted,
		Dragging
	}

	public static NotebookView instance;

	[ExportGroup("Scene references", "")]
	[Export(PropertyHint.None, "")]
	private CoverPage coverPage;

	[Export(PropertyHint.None, "")]
	private MainCodesPage systemPage;

	[Export(PropertyHint.None, "")]
	public MainCodesPage mainCodesPage;

	[Export(PropertyHint.None, "")]
	private PackedScene authorPageScene;

	[Export(PropertyHint.None, "")]
	private Control codeAssignmentPageLayout;

	[Export(PropertyHint.None, "")]
	private Control newTitleRecordedPageLayout;

	[Export(PropertyHint.None, "")]
	private TextureButton backgroundButton;

	[Export(PropertyHint.None, "")]
	private GameCamera gameCamera;

	[Export(PropertyHint.None, "")]
	private Control scrollButtons;

	[Export(PropertyHint.None, "")]
	private Button scrollUpButton;

	[Export(PropertyHint.None, "")]
	private Button scrollDownButton;

	[Export(PropertyHint.None, "")]
	private Button previousPageButton;

	[Export(PropertyHint.None, "")]
	private Button nextPageButton;

	[Export(PropertyHint.None, "")]
	private ButtonWithPrompt gamepadSelectModeButton;

	[Export(PropertyHint.None, "")]
	private ButtonWithPrompt gamepadGoToCodeButton;

	[Export(PropertyHint.None, "")]
	private TextureRect torchLight;

	[Export(PropertyHint.None, "")]
	private ColorRect backgroundDarken;

	[Export(PropertyHint.None, "")]
	private Button debugToggleSlideOverButton;

	[ExportGroup("SFX", "")]
	[Export(PropertyHint.None, "")]
	private AudioStream[] openSFX;

	[Export(PropertyHint.None, "")]
	private AudioStream[] closeSFX;

	[Export(PropertyHint.None, "")]
	private AudioStream[] changePageSFX;

	[Export(PropertyHint.None, "")]
	private AudioStream continuousPageDragSFX;

	[Export(PropertyHint.None, "")]
	private float[] continuousPageDragSFXStartTimes;

	[ExportGroup("Show-hide transition", "")]
	[Export(PropertyHint.None, "")]
	private float pagesShowHideDuration = 0.6f;

	[Export(PropertyHint.None, "")]
	private float pagesShowHideFadeProportion = 0.3f;

	[Export(PropertyHint.None, "")]
	private float pagesHiddenScale = 0.5f;

	[Export(PropertyHint.None, "")]
	private float pagesHiddenSquash = 0.7f;

	[Export(PropertyHint.None, "")]
	private float pagesHiddenOffsetX = 100f;

	[Export(PropertyHint.None, "")]
	private float pagesHiddenOffsetY = 160f;

	[Export(PropertyHint.None, "")]
	private float pagesNewTitleHiddenScale = 0.05f;

	[ExportGroup("Page flow", "")]
	[Export(PropertyHint.None, "")]
	private float pageSlideDuration = 0.4f;

	[Export(PropertyHint.None, "")]
	private float pageFlowSmoothTime = 0.1f;

	[Export(PropertyHint.None, "")]
	private float pageFlowMaxSpeed = 10f;

	[Export(PropertyHint.None, "")]
	private float selectModeDuration = 0.4f;

	[ExportGroup("Page positioning", "")]
	[Export(PropertyHint.None, "")]
	private float leftOffsetFar = -600f;

	[Export(PropertyHint.None, "")]
	private float leftOffsetNear = -400f;

	[Export(PropertyHint.None, "")]
	private float rightOffsetNear = 1100f;

	[Export(PropertyHint.None, "")]
	private float rightOffsetFar = 2000f;

	[Export(PropertyHint.None, "")]
	private float leftRotationFar = -10f;

	[Export(PropertyHint.None, "")]
	private float leftRotationNear = -5f;

	[Export(PropertyHint.None, "")]
	private float rightRotationNear = 5f;

	[Export(PropertyHint.None, "")]
	private float rightRotationFar = 10f;

	[Export(PropertyHint.None, "")]
	private float darknessNear = 0.9f;

	[Export(PropertyHint.None, "")]
	private float darknessFar = 0.6f;

	[Export(PropertyHint.None, "")]
	private float slideOverLeftOffset = -500f;

	[Export(PropertyHint.None, "")]
	private float slideOverRightOffset = 500f;

	[Export(PropertyHint.None, "")]
	private float nearFarNormCurvePower = 0.5f;

	[Export(PropertyHint.None, "")]
	private Curve nearFarNormCurve;

	[ExportGroup("Debug", "")]
	[Export(PropertyHint.None, "")]
	private bool debugTestCodeAssignment;

	private NotebookContent content;

	private List<NotebookPage> pages;

	private Tween pagesShowHideTween;

	private float hideShowNorm;

	private float stickOrDpadHoldTime;

	private int stickOrDpadRepeatCount;

	private Vector2 mainCodePageDefaultPosition;

	private float mainCodePageDefaultRotation;

	private bool titleRecordingOnlyLayout;

	private Control[] fullscreenControls;

	private Vector2 lastKnownScreenResolution;

	private float _fractionalPageIdx;

	private float _pageIdxChangeSpeed;

	private int _targetPageIdx;

	private float _slideOverNorm;

	private bool selectMode;

	private float _gamepadSelectModeNorm;

	private int mainCodesPageIdx;

	private float continuousPageDragSFXVolume;

	private AudioStreamPlayer continuousPageDragSFXPlayer;

	private float scrollButtonsDefaultX;

	private bool _doingHide;

	private HorizontalPagesDragState horizontalPagesDragState;

	private float horizontalPagesDragStartMouseX;

	private float dragSpeed;

	private float lastDragDist = -1f;

	[ExportGroup("Pages Drag", "")]
	[Export(PropertyHint.None, "")]
	private float pagesDragSpeedScalar = 1f;

	[Export(PropertyHint.None, "")]
	private float pagesDragDecelleration = 4f;

	public bool fullyVisible
	{
		get
		{
			if (base.Visible)
			{
				return pagesShowHideTween == null;
			}
			return false;
		}
	}

	private int currentPageIdx => Mathf.Clamp(Mathf.RoundToInt(_fractionalPageIdx), 0, pages.Count - 1);

	public override void _EnterTree()
	{
		instance = this;
	}

	public override void _Ready()
	{
		coverPage.WasClicked += OnPageClicked;
		systemPage.CodeLinkPressed += OnCodeLinkPressed;
		systemPage.WasClicked += OnPageClicked;
		mainCodesPage.CodeLinkPressed += OnCodeLinkPressed;
		mainCodesPage.WasClicked += OnPageClicked;
		mainCodesPage.PickedUpPuzzlePiece += OnPickedUpPuzzlePiece;
		backgroundButton.Pressed += delegate
		{
			HideNotebook();
		};
		coverPage.Visible = true;
		systemPage.Visible = true;
		mainCodesPage.Visible = true;
		codeAssignmentPageLayout.Visible = false;
		newTitleRecordedPageLayout.Visible = false;
		mainCodePageDefaultPosition = mainCodesPage.Position;
		mainCodePageDefaultRotation = mainCodesPage.Rotation;
		previousPageButton.Pressed += delegate
		{
			ChangePage(-1);
		};
		nextPageButton.Pressed += delegate
		{
			ChangePage(1);
		};
		gamepadGoToCodeButton.Pressed += delegate
		{
			if (pages[currentPageIdx] is MainCodesPage mainCodesPage)
			{
				mainCodesPage.EmitSignal(SignalName.CodeLinkPressed, mainCodesPage.goToPuzzlePiece.code);
			}
		};
		PrimaryInputManager.instance.PrimaryInputTypeChanged += OnInputTypeChanged;
		gamepadSelectModeButton.Pressed += delegate
		{
			selectMode = true;
			pages[currentPageIdx].SetSelectMode(enabled: true);
		};
		pages = new List<NotebookPage> { coverPage, systemPage };
		scrollButtonsDefaultX = scrollButtons.Position.X;
		Control obj = coverPage.GetParent() as Control;
		obj.Position = new Vector2(y: HiddenOffsetYForHiddenScale(), x: pagesHiddenOffsetX);
		obj.Scale = new Vector2(pagesHiddenScale * pagesHiddenSquash, pagesHiddenScale);
		obj.Modulate = new Color(1f, 1f, 1f, 0f);
		torchLight.Modulate = new Color(1f, 1f, 1f, 0f);
		torchLight.Scale = new Vector2(1f, 3f);
		backgroundDarken.Modulate = new Color(0f, 0f, 0f, 0f);
		if (base.Owner == null)
		{
			ShowNotebook(new List<string>
			{
				"§Objective§", "I've got to figure out what the heck is going on with this notebook", "Sources: 5 of 25", "Titles: 3 of 10 (2 confirmed)", "§System Codes§", "TR49 -- System Boot Sequence -- REFCOUNT=1/10", "AB05 -- Emergency Override -- ", "ZZ99 -- Test Code Alpha -- REFCOUNT=3/7", "XY12 -- Placeholder Entry -- ", "LM34 -- Dummy Sequence -- REFCOUNT=2/5",
				"QR56 -- Sample Override -- ", "AA11 -- Filler Boot -- REFCOUNT=4/8", "BB22 -- Mock Emergency -- ", "§Main Codes§", "-- Main Reactor Control -- ", "-- The Genesis of the Wombles -- ", "-- Three Steps Down to Hell -- ", "-- The Story of Titch -- ", "-- Why cook when you can eat? -- ", "-- Thimbles Full of Thistles -- ",
				"-- The Malnourished Pigeon -- ", "-- The Boy Who Cried Fart -- ", "-- Twenty Thousand Leagues Later... -- ", "-- The First of the Midgets -- ", "-- The Last of the Midgets -- ", "-- Simple Approaches To Implementing Anarchy -- ", "CD99 -- CD player", "AB01 -- -- ", "AC01 -- -- ", "AZ01 -- -- ",
				"XE23 -- -- ", "DF49 -- -- ", "EG19 -- -- ", "FH20 -- -- ", "AI52 -- -- ", "YA01 -- -- ", "RT01 -- -- ", "TY01 -- -- ", "UV23 -- -- ", "AS49 -- -- ",
				"FF19 -- -- ", "KJ20 -- -- ", "QO52 -- -- ", "AH00 -- -- REFCOUNT=1/10", "JR99 -- Jolly Roger -- REFCOUNT=1/10", "SD13 -- Scooby Doo -- REFCOUNT=1/10", "SD12 -- Scooby Doo -- REFCOUNT=1/10 -- CONFIRMED=true", "§Journals§", "Academicalist's Journal -- AJ", "BLURB -- ",
				"The description of AJ", "More of it", "END_BLURB", "PUBLICATION -- AJ30 -- -- ?", "PUBLICATION -- AJ32 -- -- ?", "§People§", "Lemarchant -- QL -- Images/Characters/Photos/Aliz_Photo.png", "BLURB", "The description of QL", "and his moustache!",
				"END_BLURB", "PUBLICATION -- QL24 -- -- ?", "Pemberton -- DP -- Images/Characters/Photos/Aliz_Photo.png", "BLURB", "The description of DP", "END_BLURB", "PUBLICATION -- DP08 -- -- ?", "Kendrick -- PK", "PUBLICATION -- PK32 -- Dark Matter and the Veil of Perception --", "Silverton -- JS",
				"Reverend Alfonso -- RA", "PUBLICATION -- RA26 -- My God, He Dances --", "Pierre Letour -- PL -- Images/Characters/Photos/Aliz_Photo.png", "PUBLICATION -- PL72 -- -- ?"
			}, "AB05", null, debugTestCodeAssignment ? NotebookMode.CodeAssignment : NotebookMode.Normal);
			SetPageIdx(2, immediate: true);
			debugToggleSlideOverButton.Pressed += delegate
			{
				mainCodesPage.slideOverMode = !mainCodesPage.slideOverMode;
			};
		}
		else
		{
			debugToggleSlideOverButton.Visible = false;
		}
	}

	public void PressedBack()
	{
		NotebookPage notebookPage = ((currentPageIdx >= 0 && currentPageIdx < pages.Count) ? pages[currentPageIdx] : null);
		if (notebookPage != null && (notebookPage.selectMode || selectMode))
		{
			selectMode = false;
			notebookPage.SetSelectMode(enabled: false);
		}
		else
		{
			HideNotebook();
		}
	}

	public override void _UnhandledInput(InputEvent @event)
	{
		if (!base.Visible)
		{
			return;
		}
		NotebookPage notebookPage = pages[currentPageIdx];
		if (@event.IsActionPressed("ui_accept") && notebookPage != coverPage && !selectMode)
		{
			this.SetInputAsHandled(@event);
			selectMode = true;
			notebookPage.SetSelectMode(enabled: true);
		}
		if (@event.IsActionPressed("ui_cancel") || @event.IsActionPressed("ui_menu") || @event.IsActionPressed("notebook") || @event.IsActionPressed("set_title"))
		{
			this.SetInputAsHandled(@event);
			PressedBack();
		}
		if (!selectMode && !titleRecordingOnlyLayout)
		{
			if (@event.IsActionPressed("ui_left", allowEcho: true) && !(@event is InputEventJoypadButton))
			{
				this.SetInputAsHandled(@event);
				ChangePage(-1);
			}
			else if (@event.IsActionPressed("ui_right", allowEcho: true) && !(@event is InputEventJoypadButton))
			{
				this.SetInputAsHandled(@event);
				ChangePage(1);
			}
		}
		this.SetInputAsHandled(@event);
	}

	public void ShowNotebook(List<string> notebookContentLines, string currentCardCode, string newTitleCollectedCode, NotebookMode notebookMode)
	{
		EmitSignal(SignalName.WillOpen);
		GlobalBackButton.instance?.Push(this);
		if (DebugOptions.instance.debugLogNotebook)
		{
			GD.Print("notebook content lines: " + string.Join("\n", notebookContentLines));
		}
		content = NotebookContent.Parse(notebookContentLines);
		Control control = pages[0].GetParent() as Control;
		int targetPageIdx = _targetPageIdx;
		int num = 0;
		titleRecordingOnlyLayout = false;
		if (notebookMode == NotebookMode.NewTitleRecorded)
		{
			coverPage.Visible = false;
			mainCodesPage.Visible = true;
			systemPage.Visible = false;
			mainCodesPage.SetCurrentActivePage(isActivePage: true);
			pages.Add(mainCodesPage);
			previousPageButton.Visible = false;
			nextPageButton.Visible = false;
			Control control2 = newTitleRecordedPageLayout;
			mainCodesPage.Position = control2.Position;
			mainCodesPage.Rotation = control2.Rotation;
			titleRecordingOnlyLayout = true;
		}
		else
		{
			coverPage.Visible = true;
			systemPage.Visible = true;
			systemPage.SetCurrentActivePage(isActivePage: false);
			mainCodesPage.Visible = content.mainCodes.Count > 0 || notebookMode == NotebookMode.CodeAssignment;
			mainCodesPage.SetCurrentActivePage(isActivePage: false);
			if (mainCodesPage.Visible)
			{
				pages.Add(mainCodesPage);
			}
			if (content.authorPages != null)
			{
				content.authorPages.Sort((NotebookAuthorPage x, NotebookAuthorPage notebookAuthorPage) => x.prefixLetters.CompareTo(notebookAuthorPage.prefixLetters));
				foreach (NotebookAuthorPage authorPage2 in content.authorPages)
				{
					AuthorPage authorPage = authorPageScene.Instantiate<AuthorPage>(PackedScene.GenEditState.Disabled);
					control.AddChild(authorPage, forceReadableName: false, InternalMode.Disabled);
					authorPage.Setup(authorPage2);
					authorPage.CodeLinkPressed += OnCodeLinkPressed;
					authorPage.WasClicked += OnPageClicked;
					pages.Insert(pages.Count, authorPage);
				}
			}
			num = ((notebookMode != NotebookMode.CodeAssignment) ? Mathf.Clamp(targetPageIdx, 0, pages.Count - 1) : mainCodesPageIdx);
			SetPageIdx(num, immediate: true);
			mainCodesPage.Position = mainCodePageDefaultPosition;
			mainCodesPage.Rotation = mainCodePageDefaultRotation;
		}
		for (int num2 = pages.Count - 1; num2 >= 0; num2--)
		{
			control.MoveChild(pages[num2], pages.Count - 1 - num2);
		}
		coverPage.Clear();
		coverPage.Setup(content.objectivesText, content.sourcesText, content.titlesText);
		systemPage.Clear();
		systemPage.SetupWithCodes(content.systemCodes);
		mainCodesPage.Clear();
		mainCodesPage.SetupWithCodes(content.mainCodes, currentCardCode);
		mainCodesPageIdx = pages.FindIndex((NotebookPage page) => page == mainCodesPage);
		if (GameHUD.instance != null)
		{
			GameHUD.instance.SetVisibility(GameHUD.Who.Notebook, visible: false);
		}
		if (gameCamera != null)
		{
			gameCamera.ChangePosition(GameCamera.Who.Notebook, GameCamera.CameraPosition.Notebook);
		}
		bool visible = base.Visible;
		if (pagesShowHideTween != null)
		{
			pagesShowHideTween.Kill();
		}
		if (notebookMode == NotebookMode.NewTitleRecorded)
		{
			SetPageIdx(mainCodesPageIdx, immediate: true);
			mainCodesPage.WriteInNewTitle(newTitleCollectedCode);
			if (PrimaryInputManager.instance.CurrentInputType == PrimaryInputManager.PrimaryInputType.Gamepad && mainCodesPage.hasCodePuzzlePiecesToAssign)
			{
				mainCodesPage.SetSelectMode(enabled: true);
				selectMode = true;
				mainCodesPage.PickUpCurrentPuzzlePiece();
			}
		}
		base.Visible = true;
		if (!visible)
		{
			control.Scale = new Vector2(pagesHiddenScale * pagesHiddenSquash, pagesHiddenScale);
			float y = HiddenOffsetYForHiddenScale();
			control.Position = new Vector2(pagesHiddenOffsetX, y);
			control.Modulate = new Color(1f, 1f, 1f, 0f);
		}
		pagesShowHideTween = CreateTween().SetParallel();
		pagesShowHideTween.SetTrans(Tween.TransitionType.Cubic);
		pagesShowHideTween.SetEase(Tween.EaseType.InOut);
		pagesShowHideTween.TweenProperty(control, "position", new Vector2(0f, 0f), pagesShowHideDuration);
		pagesShowHideTween.TweenProperty(control, "scale:x", 1f, pagesShowHideDuration);
		pagesShowHideTween.TweenProperty(control, "scale:y", 1f, pagesShowHideDuration);
		pagesShowHideTween.TweenProperty(control, "modulate:a", 1f, pagesShowHideFadeProportion * pagesShowHideDuration);
		pagesShowHideTween.TweenProperty(torchLight, "modulate:a", 1f, pagesShowHideDuration);
		pagesShowHideTween.TweenProperty(torchLight, "scale:y", 1f, 1.5f * pagesShowHideDuration);
		pagesShowHideTween.TweenProperty(backgroundDarken, "modulate:a", 1f, pagesShowHideDuration);
		pagesShowHideTween.TweenProperty(this, "hideShowNorm", 1f, pagesShowHideDuration);
		pagesShowHideTween.Finished += delegate
		{
			pagesShowHideTween = null;
		};
		if (notebookMode == NotebookMode.CodeAssignment && gameCamera != null)
		{
			GetTree().CreateTimer(0.2f * pagesShowHideDuration).Timeout += delegate
			{
				gameCamera.ChangePosition(GameCamera.Who.Notebook, GameCamera.CameraPosition.SideCrossRef);
				mainCodesPage.slideOverMode = true;
				SetPageIdx(mainCodesPageIdx, immediate: false);
				if (PrimaryInputManager.instance.CurrentInputType == PrimaryInputManager.PrimaryInputType.Gamepad && mainCodesPage.hasCodePuzzlePiecesToAssign)
				{
					mainCodesPage.SetSelectMode(enabled: true);
					selectMode = true;
					mainCodesPage.PickUpCurrentPuzzlePiece();
				}
			};
		}
		PlayNotebookSFX(openSFX.Random());
		Haptic.instance.SubtleWhoosh();
	}

	private void PlayNotebookSFX(AudioStream stream)
	{
		AudioStreamPlayer audioStreamPlayer = new AudioStreamPlayer();
		audioStreamPlayer.Bus = "SFX";
		audioStreamPlayer.Stream = stream;
		AddChild(audioStreamPlayer, forceReadableName: false, InternalMode.Disabled);
		audioStreamPlayer.Play();
	}

	private void UpdateContinuousPageDragSFX(float dt, float dragSpeed)
	{
		if (dragSpeed > 0f && continuousPageDragSFXPlayer == null)
		{
			continuousPageDragSFXPlayer = new AudioStreamPlayer();
			continuousPageDragSFXPlayer.Bus = "SFX";
			continuousPageDragSFXPlayer.Stream = continuousPageDragSFX;
			AddChild(continuousPageDragSFXPlayer, forceReadableName: false, InternalMode.Disabled);
			continuousPageDragSFXVolume = 1f;
			continuousPageDragSFXPlayer.Play(continuousPageDragSFXStartTimes.Random());
		}
		else if (dragSpeed > 0f && continuousPageDragSFXPlayer != null)
		{
			float to = Mathf.InverseLerp(0f, 10f, dragSpeed);
			continuousPageDragSFXVolume = Mathf.MoveToward(continuousPageDragSFXVolume, to, dt / 0.1f);
			continuousPageDragSFXVolume = Mathf.Clamp(continuousPageDragSFXVolume, 0f, 1f);
			continuousPageDragSFXPlayer.VolumeDb = AudioX.VolumeDbFromNormalized(continuousPageDragSFXVolume);
		}
		else if (dragSpeed == 0f && continuousPageDragSFXPlayer != null)
		{
			continuousPageDragSFXVolume = Mathf.MoveToward(continuousPageDragSFXVolume, 0f, dt / 0.3f);
			continuousPageDragSFXVolume = Mathf.Clamp(continuousPageDragSFXVolume, 0f, 1f);
			continuousPageDragSFXPlayer.VolumeDb = AudioX.VolumeDbFromNormalized(continuousPageDragSFXVolume);
			if (continuousPageDragSFXVolume == 0f)
			{
				continuousPageDragSFXPlayer.QueueFree();
				continuousPageDragSFXPlayer = null;
			}
		}
	}

	private float HiddenOffsetYForHiddenScale()
	{
		float y = (pages[0].GetParent() as Control).Size.Y;
		float num = 0.5f * (y * (1f - pagesHiddenScale));
		return y - num - pagesHiddenOffsetY;
	}

	public void HideNotebook()
	{
		if (!_doingHide && base.Visible && base.Owner != null)
		{
			_doingHide = true;
			GlobalBackButton.instance?.Pop(this);
			mainCodesPage.slideOverMode = false;
			if (pagesShowHideTween != null)
			{
				pagesShowHideTween.Kill();
			}
			Control control = pages[0].GetParent() as Control;
			pagesShowHideTween = CreateTween().SetParallel();
			pagesShowHideTween.SetTrans(Tween.TransitionType.Cubic);
			pagesShowHideTween.SetEase(Tween.EaseType.InOut);
			float y = HiddenOffsetYForHiddenScale();
			pagesShowHideTween.TweenProperty(control, "position", new Vector2(pagesHiddenOffsetX, y), pagesShowHideDuration);
			pagesShowHideTween.TweenProperty(control, "scale:x", pagesHiddenScale * pagesHiddenSquash, pagesShowHideDuration);
			pagesShowHideTween.TweenProperty(control, "scale:y", pagesHiddenScale, pagesShowHideDuration);
			pagesShowHideTween.TweenProperty(control, "modulate:a", 0f, pagesShowHideFadeProportion * pagesShowHideDuration).SetDelay((1f - pagesShowHideFadeProportion) * pagesShowHideDuration);
			pagesShowHideTween.TweenProperty(torchLight, "modulate:a", 0f, pagesShowHideDuration);
			pagesShowHideTween.TweenProperty(torchLight, "scale:y", 3f, pagesShowHideDuration);
			pagesShowHideTween.TweenProperty(backgroundDarken, "modulate:a", 0f, 2f * pagesShowHideDuration);
			pagesShowHideTween.TweenProperty(this, "hideShowNorm", 0f, pagesShowHideDuration);
			pagesShowHideTween.Finished += delegate
			{
				pagesShowHideTween = null;
				Clear();
				_doingHide = false;
				base.Visible = false;
				EmitSignal(SignalName.DidHide);
			};
			if (GameHUD.instance != null)
			{
				GameHUD.instance.ResetVisibility(GameHUD.Who.Notebook);
			}
			if (gameCamera != null)
			{
				gameCamera.ResetPosition(GameCamera.Who.Notebook);
			}
			PlayNotebookSFX(closeSFX.Random());
			Haptic.instance.SubtleWhoosh();
		}
	}

	private void SetPageIdx(int pageIdx, bool immediate)
	{
		if (pageIdx < 0 || pageIdx >= pages.Count)
		{
			GD.PushError("SetPageIdx: pageIdx out of bounds: " + pageIdx);
			return;
		}
		if (selectMode)
		{
			selectMode = false;
		}
		bool num = _targetPageIdx != pageIdx;
		if (num)
		{
			pages[currentPageIdx].ClearForPageChange();
		}
		_targetPageIdx = pageIdx;
		if (immediate)
		{
			_fractionalPageIdx = _targetPageIdx;
			_pageIdxChangeSpeed = 0f;
		}
		if (num)
		{
			PlayNotebookSFX(changePageSFX.Random());
			Haptic.instance.LightStep();
		}
	}

	public override void _Process(double delta)
	{
		if (!base.Visible)
		{
			UpdateContinuousPageDragSFX((float)delta, 0f);
			return;
		}
		if (!selectMode && pagesShowHideTween == null)
		{
			UpdateStickAndDpadInputForPageTurnsAndScroll((float)delta);
		}
		if (!titleRecordingOnlyLayout)
		{
			UpdateHorizontalPagesDrag((float)delta);
		}
		UpdatePageFlow((float)delta);
		bool flag = _targetPageIdx == currentPageIdx;
		bool num = PrimaryInputManager.instance.CurrentInputType == PrimaryInputManager.PrimaryInputType.Gamepad;
		NotebookPage notebookPage = pages[currentPageIdx];
		float num2 = Mathf.MoveToward(to: ((num && !selectMode && notebookPage != coverPage && pagesShowHideTween == null) & flag) ? 1f : 0f, from: gamepadSelectModeButton.Modulate.A, delta: (float)delta / 0.2f);
		if (!num)
		{
			num2 = 0f;
		}
		gamepadSelectModeButton.Modulate = new Color(1f, 1f, 1f, num2);
		gamepadSelectModeButton.Visible = num2 > 0f;
		gamepadSelectModeButton.text = ((notebookPage == this.mainCodesPage) ? "Select and Assign Codes" : "Select Codes");
		MainCodesPage mainCodesPage = notebookPage as MainCodesPage;
		if (mainCodesPage != null && mainCodesPage.goToPuzzlePiece != null && pagesShowHideTween == null)
		{
			gamepadGoToCodeButton.text = "Go to " + StoryController.HyphenateCode(mainCodesPage.goToPuzzlePiece.code);
			gamepadGoToCodeButton.Visible = true;
		}
		else
		{
			gamepadGoToCodeButton.Visible = false;
		}
		float to;
		if ((mainCodesPage != null && !Platform.isMobile) & flag)
		{
			to = (((mainCodesPage.canScrollUp || mainCodesPage.canScrollDown) && pagesShowHideTween == null) ? 1f : 0f);
			scrollUpButton.Disabled = !mainCodesPage.canScrollUp;
			scrollDownButton.Disabled = !mainCodesPage.canScrollDown;
		}
		else
		{
			to = 0f;
			scrollUpButton.Disabled = true;
			scrollDownButton.Disabled = true;
		}
		float num3 = Mathf.MoveToward(scrollButtons.Modulate.A, to, (float)delta / 0.2f);
		scrollButtons.Modulate = new Color(1f, 1f, 1f, num3);
		scrollButtons.Visible = num3 > 0f;
		float num4 = Mathf.Ease(_slideOverNorm, -3f);
		scrollButtons.Position = new Vector2(scrollButtonsDefaultX + num4 * slideOverLeftOffset, scrollButtons.Position.Y);
		if (scrollButtons.Visible && mainCodesPage != null)
		{
			if (scrollUpButton.IsPressed())
			{
				mainCodesPage.Scroll(-0.5f);
			}
			if (scrollDownButton.IsPressed())
			{
				mainCodesPage.Scroll(0.5f);
			}
		}
		Vector2 size = GetViewport().GetVisibleRect().Size;
		if (size != lastKnownScreenResolution)
		{
			lastKnownScreenResolution = size;
			float anchorLeft = 0f;
			float anchorRight = 1f;
			float anchorTop = 0f;
			float anchorBottom = 1f;
			float num5 = base.Size.X / base.Size.Y;
			float num6 = size.X / size.Y;
			if (num6 <= num5)
			{
				float num7 = (num5 / num6 - 1f) / 2f;
				anchorTop = 0f - num7;
				anchorBottom = 1f + num7;
			}
			else
			{
				float num8 = (num6 / num5 - 1f) / 2f;
				anchorLeft = 0f - num8;
				anchorRight = 1f + num8;
			}
			if (fullscreenControls == null)
			{
				fullscreenControls = new Control[3] { torchLight, backgroundDarken, backgroundButton };
			}
			Control[] array = fullscreenControls;
			foreach (Control obj in array)
			{
				obj.AnchorLeft = anchorLeft;
				obj.AnchorRight = anchorRight;
				obj.AnchorTop = anchorTop;
				obj.AnchorBottom = anchorBottom;
			}
		}
	}

	private void UpdateHorizontalPagesDrag(float dt)
	{
		float num = 0.001f * pagesDragSpeedScalar;
		float x = GetViewport().GetMousePosition().X;
		if (horizontalPagesDragState == HorizontalPagesDragState.None && Input.IsMouseButtonPressed(MouseButton.Left))
		{
			horizontalPagesDragState = HorizontalPagesDragState.PressStarted;
			horizontalPagesDragStartMouseX = x;
		}
		else if (horizontalPagesDragState == HorizontalPagesDragState.PressStarted)
		{
			bool flag = pages[currentPageIdx] is MainCodesPage mainCodesPage && mainCodesPage.isDraggingPuzzlePiece;
			if (!Input.IsMouseButtonPressed(MouseButton.Left) | flag)
			{
				horizontalPagesDragState = HorizontalPagesDragState.None;
			}
			else if (Mathf.Abs(x - horizontalPagesDragStartMouseX) > 5f)
			{
				horizontalPagesDragStartMouseX = x;
				horizontalPagesDragState = HorizontalPagesDragState.Dragging;
				lastDragDist = -1f;
				_pageIdxChangeSpeed = 0f;
			}
		}
		else if (horizontalPagesDragState == HorizontalPagesDragState.Dragging)
		{
			if (!Input.IsMouseButtonPressed(MouseButton.Left))
			{
				float num2 = _pageIdxChangeSpeed * _pageIdxChangeSpeed / (2f * pagesDragDecelleration) * (float)Mathf.Sign(_pageIdxChangeSpeed);
				_targetPageIdx = Mathf.Clamp(Mathf.RoundToInt(_fractionalPageIdx + num2), 0, pages.Count - 1);
				horizontalPagesDragState = HorizontalPagesDragState.None;
				UpdateContinuousPageDragSFX(dt, 0f);
				return;
			}
			float num3 = x - horizontalPagesDragStartMouseX;
			if (lastDragDist != -1f)
			{
				float num4 = num3 - lastDragDist;
				float to = ((dt > 0f) ? ((0f - num4) / dt) : 0f);
				dragSpeed = Mathf.Lerp(dragSpeed, to, TimeX.Lerping(0.5f, dt));
				_pageIdxChangeSpeed = dragSpeed * num;
				UpdateContinuousPageDragSFX(dt, Mathf.Abs(dragSpeed));
			}
			lastDragDist = num3;
			_fractionalPageIdx += dragSpeed * num * dt;
			_fractionalPageIdx = Mathf.Clamp(_fractionalPageIdx, 0f, pages.Count - 1);
		}
		else if (horizontalPagesDragState == HorizontalPagesDragState.None)
		{
			UpdateContinuousPageDragSFX(dt, 0f);
		}
	}

	private void UpdatePageFlow(float dt)
	{
		if (horizontalPagesDragState != HorizontalPagesDragState.Dragging)
		{
			_fractionalPageIdx = MathX.SmoothDamp(_fractionalPageIdx, _targetPageIdx, ref _pageIdxChangeSpeed, pageFlowSmoothTime, pageFlowMaxSpeed, dt);
		}
		_slideOverNorm = Mathf.MoveToward(_slideOverNorm, mainCodesPage.slideOverMode ? 1f : 0f, dt / pageSlideDuration);
		float num = Mathf.Ease(_slideOverNorm, -3f);
		_gamepadSelectModeNorm = Mathf.MoveToward(_gamepadSelectModeNorm, selectMode ? 1f : 0f, dt / selectModeDuration);
		float num2 = Mathf.Ease(_gamepadSelectModeNorm, -3f);
		int value = currentPageIdx;
		value = Mathf.Clamp(value, 0, pages.Count - 1);
		_ = pages[value];
		Vector2 vector = (pages[0].GetParent() as Control).Size / 2f;
		for (int i = 0; i < pages.Count; i++)
		{
			pages[i].SetCurrentActivePage(i == value && _targetPageIdx == value && pagesShowHideTween == null);
		}
		previousPageButton.Disabled = value == 0;
		nextPageButton.Disabled = value == pages.Count - 1;
		RandomNumberGenerator randomNumberGenerator = new RandomNumberGenerator();
		for (int j = 0; j < pages.Count; j++)
		{
			NotebookPage notebookPage = pages[j];
			Vector2 position = vector - notebookPage.Size / 2f;
			float num3 = (float)j - _fractionalPageIdx;
			float num4;
			float num5;
			if (num3 < -5f)
			{
				num4 = leftOffsetFar;
				num5 = leftRotationFar;
			}
			else if (num3 < -1f)
			{
				float offset = Mathf.Clamp(1f - Mathf.InverseLerp(-5f, -1f, num3), 0f, 1f);
				float weight = nearFarNormCurve.Sample(offset);
				num4 = Mathf.Lerp(leftOffsetNear, leftOffsetFar, weight);
				num5 = Mathf.Lerp(leftRotationNear, leftRotationFar, weight);
			}
			else if (num3 < 0f)
			{
				num4 = Mathf.Remap(num3, 0f, -1f, 0f, leftOffsetNear);
				num5 = Mathf.Remap(num3, 0f, -1f, 0f, leftRotationNear);
			}
			else if (num3 < 1f)
			{
				float weight2 = Mathf.InverseLerp(0f, 1f, num3);
				num4 = Mathf.Lerp(0f, rightOffsetNear, weight2);
				num5 = Mathf.Lerp(0f, rightRotationNear, weight2);
			}
			else if (num3 < 5f)
			{
				float offset2 = Mathf.Clamp(Mathf.InverseLerp(1f, 5f, num3), 0f, 1f);
				float weight3 = nearFarNormCurve.Sample(offset2);
				num4 = Mathf.Lerp(rightOffsetNear, rightOffsetFar, weight3);
				num5 = Mathf.Lerp(rightRotationNear, rightRotationFar, weight3);
			}
			else
			{
				num4 = rightOffsetFar;
				num5 = rightRotationFar;
			}
			num4 *= hideShowNorm;
			float weight4 = Mathf.Clamp(Mathf.InverseLerp(0f, 1f, num3), 0f, 1f);
			float num6 = Mathf.Lerp(slideOverLeftOffset, slideOverRightOffset, weight4);
			position.X += num4 + num * num6;
			float num7 = Mathf.Abs(num3);
			float a = Mathf.Clamp(Mathf.InverseLerp(6f, 4f, num7), 0f, 1f);
			float num8 = 1f;
			if (num7 < 1f)
			{
				float weight5 = Mathf.InverseLerp(0f, 1f, num7);
				num8 = Mathf.Lerp(1f, darknessNear, weight5);
			}
			else if (Mathf.Abs(num3) < 6f)
			{
				float weight6 = Mathf.InverseLerp(1f, 6f, num7);
				num8 = Mathf.Lerp(darknessNear, darknessFar, weight6);
			}
			else
			{
				num8 = darknessFar;
			}
			float num9 = 1f;
			if (j == value)
			{
				num9 = Mathf.Lerp(1f, 1.05f, num2);
			}
			else
			{
				num9 = Mathf.Lerp(1f, 0.9f, num2);
				num8 *= Mathf.Lerp(1f, 0.8f, num2);
			}
			notebookPage.Scale = new Vector2(num9, num9);
			notebookPage.ZIndex = ((num2 > 0.5f && j == value) ? 100 : 0);
			randomNumberGenerator.Seed = (ulong)(j + 12345);
			Vector2 vector2 = new Vector2(randomNumberGenerator.RandfRange(-1f, 1f), randomNumberGenerator.RandfRange(-1f, 1f)).Normalized();
			randomNumberGenerator.Seed = (ulong)(j + 54321);
			float num10 = randomNumberGenerator.RandfRange(-2f, 2f);
			position += 20f * vector2;
			num5 += (1f - num2) * num10;
			notebookPage.Position = position;
			notebookPage.RotationDegrees = num5;
			notebookPage.Modulate = new Color(num8, num8, num8, a);
		}
	}

	private void UpdateStickAndDpadInputForPageTurnsAndScroll(float dt)
	{
		int num = 0;
		float x = InputX.GetLeftStick().X;
		if (x > 0.3f)
		{
			num = 1;
		}
		else if (x < -0.3f)
		{
			num = -1;
		}
		Vector2I dPad = InputX.GetDPad();
		if (dPad.X != 0)
		{
			num = dPad.X;
		}
		if (num == 0)
		{
			stickOrDpadHoldTime = 0f;
			stickOrDpadRepeatCount = 0;
		}
		if (num != 0)
		{
			stickOrDpadHoldTime += dt;
			float num2 = ((stickOrDpadRepeatCount == 0) ? 0f : ((stickOrDpadRepeatCount == 1) ? 0.3f : ((stickOrDpadRepeatCount != 2) ? 0.1f : 0.2f)));
			if (stickOrDpadHoldTime >= num2)
			{
				ChangePage(num);
				stickOrDpadRepeatCount++;
				stickOrDpadHoldTime = 0f;
			}
		}
		float num3 = 0f;
		float y = InputX.GetLeftStick().Y;
		if (Mathf.Abs(y) > 0.3f)
		{
			num3 = y;
		}
		if (dPad.Y != 0)
		{
			num3 = dPad.Y;
		}
		if (num3 != 0f && pages[currentPageIdx] is MainCodesPage mainCodesPage)
		{
			mainCodesPage.Scroll(num3);
		}
	}

	private void ChangePage(int delta)
	{
		SetPageIdx(Mathf.Clamp(_targetPageIdx + delta, 0, pages.Count - 1), immediate: false);
	}

	public void Clear()
	{
		content = default(NotebookContent);
		coverPage.Clear();
		systemPage.Clear();
		mainCodesPage.Clear();
		for (int num = pages.Count - 1; num >= 0; num--)
		{
			NotebookPage notebookPage = pages[num];
			if (notebookPage is AuthorPage)
			{
				notebookPage.QueueFree();
				pages.RemoveAt(num);
			}
		}
		pages.Remove(mainCodesPage);
		horizontalPagesDragState = HorizontalPagesDragState.None;
		dragSpeed = 0f;
		lastDragDist = -1f;
		UpdateContinuousPageDragSFX(1f, 0f);
	}

	private void OnCodeLinkPressed(string link)
	{
		if (base.Owner == null)
		{
			GD.Print("OnCodeLinkPressed: " + link);
		}
		else
		{
			HideNotebook();
		}
		EmitSignal(SignalName.CodeLinkPressed, link);
	}

	private void OnPageClicked(NotebookPage page)
	{
		int num = pages.IndexOf(page);
		if (num != _targetPageIdx)
		{
			SetPageIdx(num, immediate: false);
		}
	}

	private void OnPickedUpPuzzlePiece(PuzzlePiece puzzlePiece)
	{
		if (PrimaryInputManager.instance.CurrentInputType == PrimaryInputManager.PrimaryInputType.Gamepad)
		{
			selectMode = true;
			mainCodesPage.SetSelectMode(enabled: true);
		}
	}

	private void OnInputTypeChanged()
	{
		if (PrimaryInputManager.instance.CurrentInputType != PrimaryInputManager.PrimaryInputType.Gamepad)
		{
			selectMode = false;
			if (currentPageIdx != -1 && currentPageIdx < pages.Count)
			{
				pages[currentPageIdx].SetSelectMode(enabled: false);
			}
		}
	}

	public void OnGlobalBackButtonPressed()
	{
		PressedBack();
	}
}
