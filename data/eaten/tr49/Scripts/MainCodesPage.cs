using System;
using System.Collections.Generic;
using Godot;

public partial class MainCodesPage : NotebookPage
{
	[Signal]
	public delegate void AssignedCodeEventHandler(string titleRealCode, string assignedCode, bool isSilentSwap);

	[Signal]
	public delegate void PickedUpPuzzlePieceEventHandler(PuzzlePiece puzzlePiece);

	private struct CodeEntryRow
	{
		public Control control;

		public RichTextLabel titleLabel;

		public RichTextLabel codeLabel;

		public Control dot;

		public Control clipContainer;

		public string realCode;

		public string assignedCode;

		public bool isBlank;

		public bool isConfirmed;

		public PuzzlePiece assignedPuzzlePiece;

		public Control selectionControl;

		public Control codeDropZoneHighlight;

		public void Clear()
		{
			titleLabel.Text = "";
			codeLabel.Text = "";
			dot.Visible = false;
			realCode = "";
			assignedCode = "";
		}
	}

	[Export(PropertyHint.None, "")]
	private PackedScene codeEntryScene;

	[Export(PropertyHint.None, "")]
	private Control codeEntryContainer;

	[Export(PropertyHint.None, "")]
	private ScrollContainer scrollContainer;

	[Export(PropertyHint.None, "")]
	private Control scrollableContentContainer;

	[Export(PropertyHint.None, "")]
	private Control printerPaper;

	[Export(PropertyHint.None, "")]
	private Texture2D printerMidSection;

	[Export(PropertyHint.None, "")]
	private Line2D verticalLine;

	[Export(PropertyHint.None, "")]
	private Theme confirmedEntryTheme;

	[Export(PropertyHint.None, "")]
	private PackedScene puzzlePieceScene;

	[Export(PropertyHint.None, "")]
	private Control puzzlePieceContainer;

	[Export(PropertyHint.None, "")]
	private Vector2 puzzlePieceOffset;

	[Export(PropertyHint.None, "")]
	private Control unplacedPiecesRect;

	[Export(PropertyHint.None, "")]
	private bool canAssignCodes;

	[Export(PropertyHint.None, "")]
	private int defaultMinimumRows = 10;

	[Export(PropertyHint.None, "")]
	private float gamepadVerticalScrollSpeed = 40f;

	[Export(PropertyHint.None, "")]
	private Color newlyDiscoveredTitleColor;

	[Export(PropertyHint.None, "")]
	private float newlyDiscoveredTitleWriteInTimePerChar = 0.1f;

	[Export(PropertyHint.None, "")]
	private string unknownCodeText = "(Don't know yet)";

	[Export(PropertyHint.None, "")]
	private float badAngleDistanceScalePenalty = 2f;

	public string codeBeingAssigned;

	public bool slideOverMode;

	private PuzzlePiece lastTouchedPuzzlePiece;

	private PuzzlePiece focusedPuzzlePiece;

	private int _selectedRowIdx = -1;

	private List<CodeEntryRow> rows = new List<CodeEntryRow>();

	private List<PuzzlePiece> puzzlePieces = new List<PuzzlePiece>();

	private List<PuzzlePiece> unassignedPuzzlePieces = new List<PuzzlePiece>();

	private List<PuzzlePiece> bottomRowOfUnassignedPieces = new List<PuzzlePiece>();

	private List<int> rowIndicesWithValidCodes = new List<int>();

	private List<int> rowIndicesWithValidCodesOrPuzzlePieces = new List<int>();

	private Tween puzzlePieceLayoutTween;

	private PuzzlePiece draggingPuzzlePiece;

	private int usedRows;

	private float defaultPaperLength;

	private float defaultPrinterMidSectionLength;

	private float timeLeftStickHoldTimer;

	private List<AudioStream> scribbleSounds;

	private AudioStreamPlayer scribbleAudioPlayer;

	private Tween scrollTween;

	private Tween titleWriteInTween;

	private float titleWriteInStartTime;

	private float codeAssignTutorialTimeout = -1f;

	private string dragTooltipTextCache;

	private string dragTooltipTextCacheCode;

	public PuzzlePiece goToPuzzlePiece
	{
		get
		{
			if (PrimaryInputManager.instance.CurrentInputType == PrimaryInputManager.PrimaryInputType.Gamepad)
			{
				return focusedPuzzlePiece;
			}
			return lastTouchedPuzzlePiece;
		}
	}

	public bool canScrollUp => scrollContainer.ScrollVertical > 0;

	public bool canScrollDown
	{
		get
		{
			if (rows.Count <= 10)
			{
				return false;
			}
			VScrollBar vScrollBar = scrollContainer.GetVScrollBar();
			return vScrollBar.Value < vScrollBar.MaxValue - vScrollBar.Page;
		}
	}

	public bool isDraggingPuzzlePiece => draggingPuzzlePiece != null;

	private int selectedRowIdx
	{
		get
		{
			return _selectedRowIdx;
		}
		set
		{
			if (_selectedRowIdx != value)
			{
				_selectedRowIdx = value;
				for (int i = 0; i < rows.Count; i++)
				{
					rows[i].selectionControl.Visible = i == _selectedRowIdx;
				}
			}
		}
	}

	private PuzzlePiece mostSignificantPuzzlePiece
	{
		get
		{
			if (codeBeingAssigned != null)
			{
				PuzzlePiece puzzlePiece = puzzlePieces.Find((PuzzlePiece piece) => piece.code == codeBeingAssigned);
				if (puzzlePiece != null)
				{
					return puzzlePiece;
				}
			}
			if (unassignedPuzzlePieces.Count > 0)
			{
				PuzzlePiece puzzlePiece2 = unassignedPuzzlePieces[0];
				if (puzzlePiece2 != null)
				{
					return puzzlePiece2;
				}
			}
			if (puzzlePieces.Count > 0)
			{
				return puzzlePieces[0];
			}
			return null;
		}
	}

	public bool hasCodePuzzlePiecesToAssign
	{
		get
		{
			if (canAssignCodes)
			{
				return unassignedPuzzlePieces.Count > 0;
			}
			return false;
		}
	}

	private bool draggingFocusedPuzzlePiece
	{
		get
		{
			if (focusedPuzzlePiece != null)
			{
				return focusedPuzzlePiece.state == PuzzlePiece.State.Dragging;
			}
			return false;
		}
	}

	public override void _Ready()
	{
		base._Ready();
		if (canAssignCodes)
		{
			scribbleSounds = new List<AudioStream>
			{
				ResourceLoader.Load<AudioStream>("res://Audio/SFX/Scribble1.ogg", null, ResourceLoader.CacheMode.Reuse),
				ResourceLoader.Load<AudioStream>("res://Audio/SFX/Scribble2.ogg", null, ResourceLoader.CacheMode.Reuse),
				ResourceLoader.Load<AudioStream>("res://Audio/SFX/Scribble3.ogg", null, ResourceLoader.CacheMode.Reuse)
			};
			scribbleAudioPlayer = new AudioStreamPlayer();
			scribbleAudioPlayer.Bus = "SFX";
			AddChild(scribbleAudioPlayer, forceReadableName: false, InternalMode.Disabled);
		}
		defaultPaperLength = printerPaper.Size.Y;
		defaultPrinterMidSectionLength = printerMidSection.GetSize().Y;
		PrimaryInputManager.instance.PrimaryInputTypeChanged += OnInputTypeChanged;
	}

	public override void SetSelectMode(bool enabled)
	{
		base.SetSelectMode(enabled);
		if (enabled)
		{
			if (focusedPuzzlePiece == null)
			{
				PuzzlePiece puzzlePiece = mostSignificantPuzzlePiece;
				SetFocusedPuzzlePiece(puzzlePiece);
				if (puzzlePiece == null && rowIndicesWithValidCodes.Count > 0)
				{
					selectedRowIdx = rowIndicesWithValidCodes[0];
				}
			}
		}
		else
		{
			SetFocusedPuzzlePiece(null);
			selectedRowIdx = -1;
		}
	}

	public void PickUpCurrentPuzzlePiece()
	{
		if (focusedPuzzlePiece != null)
		{
			focusedPuzzlePiece.PickUp(withMouse: false);
		}
	}

	private void SetFocusedPuzzlePiece(PuzzlePiece puzzlePiece)
	{
		if (focusedPuzzlePiece != null && focusedPuzzlePiece != puzzlePiece)
		{
			focusedPuzzlePiece.LoseFocusAndCancelDragIfNecessary();
		}
		focusedPuzzlePiece = puzzlePiece;
		if (puzzlePiece != null)
		{
			puzzlePiece.focused = true;
			ScrollToPuzzlePiece(puzzlePiece);
		}
	}

	public void Scroll(float amount)
	{
		scrollContainer.ScrollVertical += Mathf.RoundToInt(gamepadVerticalScrollSpeed * amount);
	}

	private void ScrollToPuzzlePiece(PuzzlePiece puzzlePiece)
	{
		if (puzzlePiece == null)
		{
			GD.PushError("ScrollToPuzzlePiece: puzzlePiece is null");
			return;
		}
		Vector2 zero = Vector2.Zero;
		Control control = scrollContainer.GetChild(0) as Control;
		Control control2 = puzzlePiece;
		while (control2 != null && control2 != control)
		{
			zero += control2.Position;
			control2 = control2.GetParent() as Control;
		}
		float y = zero.Y;
		float y2 = puzzlePiece.Size.Y;
		float y3 = scrollContainer.Size.Y;
		float targetScroll = y + y2 / 2f - y3 / 2f;
		ScrollTo(targetScroll);
	}

	private void ScrollToRow(int rowIdx)
	{
		if (rowIdx < 0 || rowIdx >= rows.Count)
		{
			return;
		}
		CodeEntryRow codeEntryRow = rows[rowIdx];
		if (codeEntryRow.control != null)
		{
			Vector2 zero = Vector2.Zero;
			Control control = scrollContainer.GetChild(0) as Control;
			Control control2 = codeEntryRow.control;
			while (control2 != null && control2 != control)
			{
				zero += control2.Position;
				control2 = control2.GetParent() as Control;
			}
			float y = zero.Y;
			float y2 = codeEntryRow.control.Size.Y;
			float y3 = scrollContainer.Size.Y;
			float targetScroll = y + y2 / 2f - y3 / 2f;
			ScrollTo(targetScroll);
		}
	}

	private void ScrollTo(float targetScroll)
	{
		float max = (float)scrollContainer.GetVScrollBar().MaxValue;
		float min = (float)scrollContainer.GetVScrollBar().MinValue;
		targetScroll = Mathf.Clamp(targetScroll, min, max);
		if (scrollTween != null)
		{
			scrollTween.Kill();
		}
		scrollTween = CreateTween();
		scrollTween.SetTrans(Tween.TransitionType.Sine);
		scrollTween.SetEase(Tween.EaseType.InOut);
		float num = Mathf.Clamp(Mathf.Abs((float)scrollContainer.ScrollVertical - targetScroll) / 1000f, 0.1f, 0.3f);
		scrollTween.TweenProperty(scrollContainer, "scroll_vertical", targetScroll, num);
		scrollTween.Finished += delegate
		{
			scrollTween = null;
		};
	}

	public override void _Input(InputEvent @event)
	{
		if (@event.IsActionPressed("go_to_code") && (goToPuzzlePiece != null || (selectedRowIdx != -1 && selectedRowIdx < rows.Count)))
		{
			this.SetInputAsHandled(@event);
			if (goToPuzzlePiece != null)
			{
				EmitSignal(NotebookPage.SignalName.CodeLinkPressed, goToPuzzlePiece.code);
			}
			else
			{
				EmitSignal(NotebookPage.SignalName.CodeLinkPressed, rows[selectedRowIdx].assignedCode);
			}
		}
		if (selectMode && !draggingFocusedPuzzlePiece)
		{
			if (@event.IsActionPressed("ui_up"))
			{
				this.SetInputAsHandled(@event);
				SelectInDirection(Vector2.Up, isContinuous: false);
			}
			else if (@event.IsActionPressed("ui_down"))
			{
				this.SetInputAsHandled(@event);
				SelectInDirection(Vector2.Down, isContinuous: false);
			}
			else if (@event.IsActionPressed("ui_left"))
			{
				this.SetInputAsHandled(@event);
				SelectInDirection(Vector2.Left, isContinuous: false);
			}
			else if (@event.IsActionPressed("ui_right"))
			{
				this.SetInputAsHandled(@event);
				SelectInDirection(Vector2.Right, isContinuous: false);
			}
			else if (@event.IsActionPressed("ui_accept") && selectedRowIdx != -1 && selectedRowIdx < rows.Count)
			{
				this.SetInputAsHandled(@event);
				EmitSignal(NotebookPage.SignalName.CodeLinkPressed, rows[selectedRowIdx].assignedCode);
			}
		}
	}

	public override void _Process(double delta)
	{
		if (selectMode && !draggingFocusedPuzzlePiece)
		{
			Vector2 leftStick = InputX.GetLeftStick();
			if (leftStick.Length() > 0.5f)
			{
				SelectInDirection(leftStick, isContinuous: true, (float)delta);
			}
			else
			{
				timeLeftStickHoldTimer = 0f;
			}
		}
		if (draggingPuzzlePiece != null && (!GodotObject.IsInstanceValid(draggingPuzzlePiece) || draggingPuzzlePiece.IsQueuedForDeletion()))
		{
			draggingPuzzlePiece = null;
		}
		if (draggingPuzzlePiece != null)
		{
			float num = draggingPuzzlePiece.GetGlobalPosition().Y + 0.5f * draggingPuzzlePiece.Size.Y;
			float value = 0f;
			float y = GetViewport().GetVisibleRect().Size.Y;
			if (num < 80f)
			{
				value = 0f - (1f - num / 80f);
			}
			else if (num > y - 80f)
			{
				value = 1f - (y - num) / 80f;
			}
			value = Mathf.Clamp(value, -1f, 1f);
			float num2 = Mathf.Lerp(100f, 1500f, Mathf.Abs(value)) * (float)MathF.Sign(value) * (float)delta;
			if (num2 != 0f)
			{
				int value2 = scrollContainer.ScrollVertical + (int)num2;
				int min = 0;
				int max = (int)scrollContainer.GetVScrollBar().MaxValue;
				scrollContainer.ScrollVertical = Mathf.Clamp(value2, min, max);
			}
		}
		if (canAssignCodes && titleWriteInTween != null && titleWriteInTween.IsValid() && titleWriteInTween.IsRunning() && (float)Time.GetTicksMsec() / 1000f - titleWriteInStartTime >= 0.5f && !scribbleAudioPlayer.IsPlaying())
		{
			scribbleAudioPlayer.Stream = scribbleSounds[GD.RandRange(0, scribbleSounds.Count - 1)];
			scribbleAudioPlayer.Play();
		}
		if (canAssignCodes && Tooltips.instance != null)
		{
			if (codeAssignTutorialTimeout >= 0f && base.isCurrentActivePage)
			{
				codeAssignTutorialTimeout -= (float)delta;
				if (codeAssignTutorialTimeout <= 0f)
				{
					codeAssignTutorialTimeout = 0f;
				}
				PuzzlePiece puzzlePiece = mostSignificantPuzzlePiece;
				if (puzzlePiece != null)
				{
					puzzlePiece.isTutorialPiece = true;
					if (codeAssignTutorialTimeout <= 0f)
					{
						if (dragTooltipTextCache == null || dragTooltipTextCacheCode != puzzlePiece.codeLabel.Text)
						{
							dragTooltipTextCache = StoryController.instance.GetDragTooltipText(puzzlePiece.codeLabel.Text);
							dragTooltipTextCacheCode = puzzlePiece.codeLabel.Text;
						}
						Tooltips.instance.ShowTooltip(puzzlePiece, dragTooltipTextCache, "tutorial_drag_to_title", Tooltip.Direction.Down, 0f, -10f);
					}
				}
			}
			else
			{
				Tooltips.instance.RemoveTooltip("tutorial_drag_to_title");
				dragTooltipTextCache = null;
				dragTooltipTextCacheCode = null;
			}
		}
		int nearestDroppableRowIndex = -1;
		if (draggingPuzzlePiece != null)
		{
			Vector2 localPuzzlePieceCentrePosition = draggingPuzzlePiece.Position + 0.5f * draggingPuzzlePiece.Size;
			TryGetNearestDroppableRowIndex(localPuzzlePieceCentrePosition, out nearestDroppableRowIndex);
		}
		bool flag = draggingPuzzlePiece != null;
		for (int i = 0; i < rows.Count; i++)
		{
			CodeEntryRow codeEntryRow = rows[i];
			bool flag2 = !codeEntryRow.isBlank && !codeEntryRow.isConfirmed;
			float to = ((flag && flag2) ? ((nearestDroppableRowIndex == i) ? 1f : 0.2f) : 0f);
			Color selfModulate = codeEntryRow.codeDropZoneHighlight.SelfModulate;
			selfModulate.A = Mathf.MoveToward(selfModulate.A, to, (float)delta / 0.3f);
			codeEntryRow.codeDropZoneHighlight.SelfModulate = selfModulate;
			codeEntryRow.codeDropZoneHighlight.Visible = selfModulate.A > 0f;
		}
	}

	private void SelectInDirection(Vector2 searchDirection, bool isContinuous, float delta = 0f)
	{
		float num = 0.2f;
		if (isContinuous && timeLeftStickHoldTimer > 0f)
		{
			if (timeLeftStickHoldTimer < num)
			{
				timeLeftStickHoldTimer += delta;
				return;
			}
			timeLeftStickHoldTimer = 0f;
		}
		if (focusedPuzzlePiece == null && selectedRowIdx == -1)
		{
			focusedPuzzlePiece = puzzlePieces.Find((PuzzlePiece piece) => piece.highlighted);
			if (focusedPuzzlePiece == null && puzzlePieces.Count > 0)
			{
				if (unassignedPuzzlePieces.Count > 0)
				{
					focusedPuzzlePiece = unassignedPuzzlePieces[0];
					focusedPuzzlePiece.focused = true;
				}
				else if (puzzlePieces.Count > 0)
				{
					focusedPuzzlePiece = puzzlePieces[0];
					focusedPuzzlePiece.focused = true;
				}
				else
				{
					if (rowIndicesWithValidCodes.Count <= 0)
					{
						return;
					}
					selectedRowIdx = rowIndicesWithValidCodes[0];
				}
			}
		}
		PuzzlePiece puzzlePiece = null;
		int num2 = -1;
		rowIndicesWithValidCodesOrPuzzlePieces.Clear();
		for (int num3 = 0; num3 < rows.Count && !rows[num3].isBlank; num3++)
		{
			if (rows[num3].assignedPuzzlePiece != null || !string.IsNullOrWhiteSpace(rows[num3].codeLabel.Text))
			{
				rowIndicesWithValidCodesOrPuzzlePieces.Add(num3);
			}
		}
		int num4 = selectedRowIdx;
		if (num4 == -1 && focusedPuzzlePiece != null)
		{
			num4 = rows.FindIndex((CodeEntryRow r) => r.assignedPuzzlePiece == focusedPuzzlePiece);
		}
		if (unassignedPuzzlePieces.Contains(focusedPuzzlePiece))
		{
			Vector2 center = focusedPuzzlePiece.GetRect().GetCenter();
			float num5 = float.MaxValue;
			foreach (PuzzlePiece unassignedPuzzlePiece in unassignedPuzzlePieces)
			{
				if (unassignedPuzzlePiece == focusedPuzzlePiece)
				{
					continue;
				}
				Vector2 center2 = unassignedPuzzlePiece.GetRect().GetCenter();
				float num6 = (center2 - center).Length();
				float num7 = Mathf.RadToDeg(Mathf.Acos(searchDirection.Dot((center2 - center).Normalized())));
				if (!(num7 > 45f))
				{
					float num8 = Mathf.Remap(num7, 10f, 45f, 1f, badAngleDistanceScalePenalty) * num6;
					if (num8 < num5)
					{
						num5 = num8;
						puzzlePiece = unassignedPuzzlePiece;
					}
				}
			}
			if (bottomRowOfUnassignedPieces.Contains(focusedPuzzlePiece) && searchDirection.Y > 0.5f && rowIndicesWithValidCodesOrPuzzlePieces.Count > 0)
			{
				num2 = rowIndicesWithValidCodesOrPuzzlePieces[0];
				puzzlePiece = null;
			}
		}
		else if (num4 != -1)
		{
			int num9 = rowIndicesWithValidCodesOrPuzzlePieces.IndexOf(num4);
			if (num9 == -1)
			{
				GD.PushError("Expected to find defacto selected row in rowIndicesWithValidCodesOrPuzzlePieces");
				return;
			}
			int num10 = num9;
			if (searchDirection.Y > 0.5f)
			{
				num10++;
			}
			else if (searchDirection.Y < -0.5f)
			{
				num10--;
			}
			num10 = Mathf.Clamp(num10, -1, rowIndicesWithValidCodesOrPuzzlePieces.Count - 1);
			if (num10 != num9)
			{
				if (num10 == -1)
				{
					if (bottomRowOfUnassignedPieces.Count == 0)
					{
						return;
					}
					puzzlePiece = bottomRowOfUnassignedPieces[bottomRowOfUnassignedPieces.Count - 1];
					num2 = -1;
				}
				else
				{
					num2 = rowIndicesWithValidCodesOrPuzzlePieces[num10];
					puzzlePiece = null;
				}
			}
		}
		int num11 = num2;
		if (num2 != -1)
		{
			PuzzlePiece assignedPuzzlePiece = rows[num2].assignedPuzzlePiece;
			if (assignedPuzzlePiece != null)
			{
				puzzlePiece = assignedPuzzlePiece;
				num11 = -1;
			}
		}
		if (puzzlePiece != null && puzzlePiece != focusedPuzzlePiece)
		{
			SetFocusedPuzzlePiece(puzzlePiece);
			selectedRowIdx = -1;
			timeLeftStickHoldTimer = delta;
		}
		else if (num11 != -1)
		{
			selectedRowIdx = num11;
			SetFocusedPuzzlePiece(null);
			ScrollToRow(num11);
			timeLeftStickHoldTimer = delta;
		}
	}

	public void SetupWithCodes(List<NotebookCodeEntry> entries, string codeBeingAssigned = null)
	{
		this.codeBeingAssigned = codeBeingAssigned;
		selectMode = false;
		lastTouchedPuzzlePiece = null;
		focusedPuzzlePiece = null;
		puzzlePieces.Clear();
		unassignedPuzzlePieces.Clear();
		rowIndicesWithValidCodes.Clear();
		codeAssignTutorialTimeout = -1f;
		scrollContainer.ScrollVertical = 0;
		if (canAssignCodes)
		{
			entries.Sort(delegate(NotebookCodeEntry a, NotebookCodeEntry b)
			{
				if (a.isConfirmed != b.isConfirmed)
				{
					if (!a.isConfirmed)
					{
						return -1;
					}
					return 1;
				}
				string strA = ((a.text.Length >= 8) ? a.text.Substr(0, 6) : ((object)a))?.ToString() + a.realCode;
				string strB = ((b.text.Length >= 8) ? b.text.Substr(0, 6) : ((object)b))?.ToString() + b.realCode;
				return string.Compare(strA, strB);
			});
			if (StoryController.instance != null)
			{
				switch (StoryController.instance.GetScore("named"))
				{
				case 0:
					codeAssignTutorialTimeout = 0f;
					break;
				case 1:
					codeAssignTutorialTimeout = 5f;
					break;
				}
			}
		}
		foreach (NotebookCodeEntry entry in entries)
		{
			if (!canAssignCodes || !entry.isUntitled)
			{
				AddRowWithEntry(entry);
			}
		}
		if (canAssignCodes)
		{
			foreach (NotebookCodeEntry entry2 in entries)
			{
				if (entry2.isUntitled && !string.IsNullOrWhiteSpace(entry2.code))
				{
					PuzzlePiece item = CreatePuzzlePieceWithCode(entry2.code);
					unassignedPuzzlePieces.Add(item);
				}
			}
		}
		if (canAssignCodes)
		{
			LayoutPuzzlePieces(animated: false);
		}
		while (rows.Count < defaultMinimumRows)
		{
			CreateNewCodeEntryRow(blank: true);
		}
		float num = 100f;
		Control control = rows[rows.Count - 1].control;
		float num2 = codeEntryContainer.Position.Y + control.Position.Y + control.Size.Y;
		scrollableContentContainer.CustomMinimumSize = new Vector2(0f, num2 + num);
		float y = control.Position.Y + control.Size.Y;
		verticalLine.Points = new Vector2[2]
		{
			new Vector2(0f, 0f),
			new Vector2(0f, y)
		};
		float num3 = 100f;
		float y2 = printerPaper.Scale.Y;
		float num4 = num2 + num3;
		int num5 = Mathf.CeilToInt((num4 / y2 - defaultPaperLength) / defaultPrinterMidSectionLength);
		float y3 = defaultPaperLength + (float)num5 * defaultPrinterMidSectionLength;
		printerPaper.Size = new Vector2(printerPaper.Size.X, y3);
		fullPageButton.Size = new Vector2(fullPageButton.Size.X, num4);
	}

	public void WriteInNewTitle(string newTitleCollectedCode)
	{
		int num = rows.FindIndex((CodeEntryRow row) => row.realCode == newTitleCollectedCode);
		if (num == -1)
		{
			GD.PushError("Could not find row for newly collected title with code: " + newTitleCollectedCode);
			return;
		}
		CodeEntryRow codeEntryRow = rows[num];
		Control clipContainer = codeEntryRow.clipContainer;
		float x = clipContainer.Size.X;
		clipContainer.Size = new Vector2(0f, clipContainer.Size.Y);
		codeEntryRow.titleLabel.AddThemeColorOverride("default_color", newlyDiscoveredTitleColor);
		float num2 = codeEntryRow.control.Position.Y + codeEntryContainer.Position.Y;
		bool num3 = num2 > scrollContainer.Size.Y * 0.7f;
		if (titleWriteInTween != null)
		{
			titleWriteInTween.Kill();
		}
		titleWriteInTween = CreateTween().SetParallel();
		float num4 = 0f;
		if (num3)
		{
			int num5 = Mathf.RoundToInt(num2 - scrollContainer.Size.Y * 0.5f);
			titleWriteInTween.TweenProperty(scrollContainer, "scroll_vertical", num5, 0.4000000059604645).SetEase(Tween.EaseType.InOut).SetTrans(Tween.TransitionType.Sine)
				.SetDelay(0.4000000059604645);
			num4 = 0.2f;
		}
		float num6 = newlyDiscoveredTitleWriteInTimePerChar * (float)codeEntryRow.titleLabel.Text.Length;
		titleWriteInTween.TweenProperty(clipContainer, "size:x", x, num6).SetDelay(0.5f + num4);
		titleWriteInTween.Finished += delegate
		{
			titleWriteInTween = null;
		};
		titleWriteInStartTime = (float)Time.GetTicksMsec() / 1000f;
	}

	public void Clear()
	{
		foreach (CodeEntryRow row in rows)
		{
			row.control.QueueFree();
			if (row.assignedPuzzlePiece != null)
			{
				row.assignedPuzzlePiece.QueueFree();
			}
		}
		rows.Clear();
		usedRows = 0;
		selectMode = false;
		codeBeingAssigned = null;
		lastTouchedPuzzlePiece = null;
		slideOverMode = false;
		if (scrollTween != null)
		{
			scrollTween.Kill();
			scrollTween = null;
		}
		if (titleWriteInTween != null)
		{
			titleWriteInTween.Kill();
			titleWriteInTween = null;
		}
		foreach (PuzzlePiece puzzlePiece in puzzlePieces)
		{
			puzzlePiece.mainCodesPage = null;
			puzzlePiece.QueueFree();
		}
		puzzlePieces.Clear();
		unassignedPuzzlePieces.Clear();
		focusedPuzzlePiece = null;
	}

	public override void ClearForPageChange()
	{
		base.ClearForPageChange();
		focusedPuzzlePiece = null;
		lastTouchedPuzzlePiece = null;
		slideOverMode = false;
	}

	private void CreateNewCodeEntryRow(bool blank)
	{
		Control control = codeEntryScene.Instantiate<Control>(PackedScene.GenEditState.Disabled);
		CodeEntryRow item = new CodeEntryRow
		{
			control = control,
			titleLabel = control.GetNode<RichTextLabel>("TitleClipContainer/TitleLabel"),
			codeLabel = control.GetNode<RichTextLabel>("CodeLabel"),
			dot = control.GetNode<Control>("Dot"),
			clipContainer = control.GetNode<Control>("TitleClipContainer"),
			selectionControl = control.GetNode<Control>("Selection"),
			codeDropZoneHighlight = control.GetNode<Control>("CodeDropZoneHighlight"),
			isBlank = blank
		};
		float y = 0f;
		if (rows.Count > 0)
		{
			Control control2 = rows[rows.Count - 1].control;
			y = control2.Position.Y + control2.Size.Y;
		}
		item.control.Position = new Vector2(0f, y);
		item.dot.Position += new Vector2((float)GD.RandRange(-2.0, 2.0), (float)GD.RandRange(-2.0, 2.0));
		item.selectionControl.Visible = false;
		item.codeDropZoneHighlight.Visible = false;
		Color selfModulate = item.codeDropZoneHighlight.SelfModulate;
		selfModulate.A = 0f;
		item.codeDropZoneHighlight.SelfModulate = selfModulate;
		if (!item.isBlank)
		{
			MakeLabelsClickable(item.codeLabel);
		}
		codeEntryContainer.AddChild(item.control, forceReadableName: false, InternalMode.Disabled);
		rows.Add(item);
		item.Clear();
	}

	public void AddRowWithEntry(NotebookCodeEntry entry)
	{
		int num = usedRows;
		while (num >= rows.Count)
		{
			CreateNewCodeEntryRow(blank: false);
		}
		CodeEntryRow value = rows[num];
		value.titleLabel.Text = entry.text ?? "";
		value.assignedCode = StoryController.DepunctuateCode(entry.code);
		if (!canAssignCodes || (!string.IsNullOrWhiteSpace(entry.code) && entry.isConfirmed))
		{
			value.codeLabel.Text = CardLinks.ClickableCode(entry.code ?? "");
			rowIndicesWithValidCodes.Add(num);
		}
		else if (canAssignCodes && !string.IsNullOrWhiteSpace(entry.code) && !entry.isConfirmed)
		{
			PuzzlePiece assignedPuzzlePiece = CreatePuzzlePieceWithCode(entry.code);
			value.assignedPuzzlePiece = assignedPuzzlePiece;
		}
		if (entry.isUntitled)
		{
			value.titleLabel.Text = unknownCodeText;
			value.titleLabel.HorizontalAlignment = HorizontalAlignment.Center;
			value.control.GetNode<Line2D>("Horizontal line").Width = 3f;
		}
		value.dot.Visible = entry.refCountMax - entry.refCount > 0 && (entry.realCode == null || entry.isConfirmed);
		value.realCode = entry.realCode;
		value.isConfirmed = entry.isConfirmed;
		if (entry.isConfirmed)
		{
			value.control.Theme = confirmedEntryTheme;
		}
		rows[num] = value;
		usedRows++;
	}

	private PuzzlePiece CreatePuzzlePieceWithCode(string code)
	{
		PuzzlePiece puzzlePiece = puzzlePieceScene.Instantiate<PuzzlePiece>(PackedScene.GenEditState.Disabled);
		puzzlePiece.codeLabel.Text = code;
		puzzlePiece.mainCodesPage = this;
		puzzlePiece.Dropped += OnPuzzlePieceDropped;
		puzzlePiece.PickedUp += OnPuzzlePiecePickedUp;
		puzzlePiece.Moved += OnPuzzlePieceMoved;
		puzzlePiece.CancelledDrag += OnPuzzlePieceCancelledDrag;
		float num = Mathf.DegToRad(8f);
		puzzlePiece.Rotation = (float)GD.RandRange(0f - num, num);
		puzzlePieces.Add(puzzlePiece);
		puzzlePieceContainer.AddChild(puzzlePiece, forceReadableName: false, InternalMode.Disabled);
		puzzlePiece.code = StoryController.DepunctuateCode(code);
		if (puzzlePiece.code == codeBeingAssigned)
		{
			puzzlePiece.highlighted = true;
		}
		if (Platform.isiPhone || Platform.isSwitch)
		{
			puzzlePiece.Scale = new Vector2(1.15f, 1.15f);
		}
		return puzzlePiece;
	}

	private void LayoutPuzzlePieces(bool animated)
	{
		if (puzzlePieceLayoutTween != null)
		{
			puzzlePieceLayoutTween.Kill();
			puzzlePieceLayoutTween = null;
		}
		if (animated && puzzlePieces.Count > 0)
		{
			puzzlePieceLayoutTween = CreateTween().SetParallel();
			puzzlePieceLayoutTween.SetTrans(Tween.TransitionType.Cubic);
			puzzlePieceLayoutTween.SetEase(Tween.EaseType.InOut);
			puzzlePieceLayoutTween.Finished += delegate
			{
				puzzlePieceLayoutTween = null;
			};
		}
		bottomRowOfUnassignedPieces.Clear();
		if (unassignedPuzzlePieces.Count > 0)
		{
			int num = Mathf.CeilToInt((float)unassignedPuzzlePieces.Count / 4f);
			if (num > 3)
			{
				num = 3;
			}
			float num2 = unplacedPiecesRect.Size.X / (float)unassignedPuzzlePieces.Count;
			float num3 = unplacedPiecesRect.Position.X - puzzlePieceContainer.Position.X;
			float num4 = unplacedPiecesRect.Position.Y - puzzlePieceContainer.Position.Y;
			float num5 = unplacedPiecesRect.Size.Y / (float)num;
			for (int num6 = 0; num6 < unassignedPuzzlePieces.Count; num6++)
			{
				int num7 = num6 % num;
				if (num7 == num - 1)
				{
					bottomRowOfUnassignedPieces.Add(unassignedPuzzlePieces[num6]);
				}
				PuzzlePiece puzzlePiece = unassignedPuzzlePieces[num6];
				float num8 = 1f;
				Vector2 vector = new Vector2(num3 + ((float)num6 - 0.5f * (float)num7 + 0.5f) * num2 - 0.5f * puzzlePiece.Size.X, num4 + ((float)num7 + num8) * num5 - 0.5f * puzzlePiece.Size.Y);
				if (animated)
				{
					float num9 = Mathf.Clamp((puzzlePiece.Position - vector).Length() / 1000f, 0.1f, 0.5f);
					puzzlePieceLayoutTween.TweenProperty(puzzlePiece, "position", vector, num9);
				}
				else
				{
					puzzlePiece.Position = vector;
				}
			}
		}
		for (int num10 = 0; num10 < rows.Count; num10++)
		{
			CodeEntryRow codeEntryRow = rows[num10];
			if (codeEntryRow.assignedPuzzlePiece != null)
			{
				Vector2 vector2 = TargetLocalTopLeftPuzzlePositionForRow(num10);
				if (animated)
				{
					float num11 = Mathf.Clamp((codeEntryRow.assignedPuzzlePiece.Position - vector2).Length() / 1000f, 0.1f, 0.5f);
					puzzlePieceLayoutTween.TweenProperty(codeEntryRow.assignedPuzzlePiece, "position", vector2, num11);
				}
				else
				{
					codeEntryRow.assignedPuzzlePiece.Position = vector2;
				}
			}
		}
	}

	private Vector2 TargetLocalTopLeftPuzzlePositionForRow(int rowIdx)
	{
		CodeEntryRow codeEntryRow = rows[rowIdx];
		return codeEntryRow.control.Position + new Vector2(codeEntryRow.control.Size.X, 0f) + puzzlePieceOffset + codeEntryContainer.Position - puzzlePieceContainer.Position;
	}

	private bool TryGetNearestDroppableRowIndex(Vector2 localPuzzlePieceCentrePosition, out int nearestDroppableRowIndex)
	{
		Vector2 point = localPuzzlePieceCentrePosition + puzzlePieceContainer.Position;
		for (int i = 0; i < rows.Count; i++)
		{
			CodeEntryRow codeEntryRow = rows[i];
			if (!codeEntryRow.isBlank && !codeEntryRow.isConfirmed)
			{
				Rect2 rect = codeEntryRow.control.GetRect();
				rect.Position += codeEntryContainer.Position;
				if (rect.HasPoint(point))
				{
					nearestDroppableRowIndex = i;
					return true;
				}
			}
		}
		nearestDroppableRowIndex = -1;
		return false;
	}

	public bool TryGetNearestDroppableCentrePosition(PuzzlePiece puzzlePiece, out Vector2 nearestDroppableCentrePosition)
	{
		Vector2 localPuzzlePieceCentrePosition = puzzlePiece.Position + 0.5f * puzzlePiece.Size;
		if (TryGetNearestDroppableRowIndex(localPuzzlePieceCentrePosition, out var nearestDroppableRowIndex) && nearestDroppableRowIndex != -1)
		{
			Vector2 vector = TargetLocalTopLeftPuzzlePositionForRow(nearestDroppableRowIndex);
			nearestDroppableCentrePosition = vector + 0.5f * puzzlePiece.Size;
			return true;
		}
		nearestDroppableCentrePosition = Vector2.Zero;
		return false;
	}

	private void OnPuzzlePiecePickedUp(PuzzlePiece puzzlePiece)
	{
		if (puzzlePiece == null)
		{
			GD.PushError("OnPuzzlePiecePickedUp called but puzzlePiece is null");
			return;
		}
		draggingPuzzlePiece = puzzlePiece;
		lastTouchedPuzzlePiece = puzzlePiece;
		foreach (PuzzlePiece puzzlePiece2 in puzzlePieces)
		{
			puzzlePiece2.isTutorialPiece = false;
		}
		SetFocusedPuzzlePiece(puzzlePiece);
		EmitSignal(SignalName.PickedUpPuzzlePiece, puzzlePiece);
	}

	private void OnPuzzlePieceMoved(PuzzlePiece puzzlePiece)
	{
		codeAssignTutorialTimeout = -1f;
	}

	private void OnPuzzlePieceCancelledDrag(PuzzlePiece puzzlePiece)
	{
		if (draggingPuzzlePiece == puzzlePiece)
		{
			draggingPuzzlePiece = null;
			LayoutPuzzlePieces(animated: true);
		}
	}

	private void OnPuzzlePieceDropped(PuzzlePiece puzzlePiece)
	{
		if (puzzlePiece == null)
		{
			GD.PushError("OnPuzzlePieceDropped called but puzzlePiece is null");
			return;
		}
		lastTouchedPuzzlePiece = puzzlePiece;
		draggingPuzzlePiece = null;
		Assignment assignment = new Assignment
		{
			titleRealCode = null,
			assignedCode = null
		};
		Assignment assignment2 = new Assignment
		{
			titleRealCode = null,
			assignedCode = null
		};
		Vector2 point = puzzlePiece.GetRect().GetCenter() + puzzlePieceContainer.Position;
		bool flag = false;
		for (int i = 0; i < rows.Count; i++)
		{
			CodeEntryRow value = rows[i];
			if (value.isBlank || value.isConfirmed)
			{
				continue;
			}
			Rect2 rect = value.control.GetRect();
			rect.Position += codeEntryContainer.Position;
			if (!rect.HasPoint(point))
			{
				continue;
			}
			if (value.assignedPuzzlePiece != puzzlePiece)
			{
				int num = rows.FindIndex((CodeEntryRow r) => r.assignedPuzzlePiece == puzzlePiece);
				if (num != -1)
				{
					CodeEntryRow value2 = rows[num];
					value2.assignedPuzzlePiece = null;
					rows[num] = value2;
				}
				unassignedPuzzlePieces.Remove(puzzlePiece);
				PuzzlePiece assignedPuzzlePiece = value.assignedPuzzlePiece;
				if (assignedPuzzlePiece != null)
				{
					if (num != -1)
					{
						CodeEntryRow value3 = rows[num];
						assignment2 = new Assignment
						{
							titleRealCode = value3.realCode,
							assignedCode = assignedPuzzlePiece.code
						};
						value3.assignedPuzzlePiece = assignedPuzzlePiece;
						rows[num] = value3;
					}
					else
					{
						assignment2 = new Assignment
						{
							titleRealCode = null,
							assignedCode = assignedPuzzlePiece.code
						};
						unassignedPuzzlePieces.Add(assignedPuzzlePiece);
					}
				}
				assignment = new Assignment
				{
					titleRealCode = value.realCode,
					assignedCode = puzzlePiece.code
				};
				value.assignedPuzzlePiece = puzzlePiece;
				rows[i] = value;
			}
			flag = true;
			break;
		}
		if (!flag)
		{
			int num2 = rows.FindIndex((CodeEntryRow r) => r.assignedPuzzlePiece == puzzlePiece);
			if (num2 != -1)
			{
				CodeEntryRow value4 = rows[num2];
				value4.assignedPuzzlePiece = null;
				rows[num2] = value4;
			}
			assignment = new Assignment
			{
				titleRealCode = null,
				assignedCode = puzzlePiece.code
			};
			if (!unassignedPuzzlePieces.Contains(puzzlePiece))
			{
				unassignedPuzzlePieces.Add(puzzlePiece);
			}
		}
		if (assignment2.assignedCode != null)
		{
			EmitSignal(SignalName.AssignedCode, assignment2.titleRealCode, assignment2.assignedCode, true);
		}
		if (assignment.assignedCode != null)
		{
			EmitSignal(SignalName.AssignedCode, assignment.titleRealCode, assignment.assignedCode, false);
		}
		unassignedPuzzlePieces.Sort((PuzzlePiece a, PuzzlePiece b) => a.Position.X.CompareTo(b.Position.X));
		LayoutPuzzlePieces(animated: true);
	}

	private void OnInputTypeChanged()
	{
		if (PrimaryInputManager.instance.CurrentInputType != PrimaryInputManager.PrimaryInputType.Gamepad)
		{
			selectMode = false;
		}
	}
}
