using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Godot;

public partial class CardView : Control
{
	[Signal]
	public delegate void CardLinkPressedEventHandler(string link);

	[Signal]
	public delegate void LinkButtonAppearedEventHandler(LinkButton linkButton);

	[Signal]
	public delegate void CardViewLayoutCompleteEventHandler();

	private abstract class Content
	{
		public Control control;

		public List<Content> children;

		public void Clear()
		{
			if (children != null)
			{
				foreach (Content child in children)
				{
					child.Clear();
				}
			}
			if (control != null)
			{
				control.QueueFree();
			}
		}

		public override string ToString()
		{
			return ToString(0).TrimEnd();
		}

		private string ToString(int indent)
		{
			string value = new string(' ', 4 * indent);
			StringBuilder stringBuilder = new StringBuilder();
			if (this is TextContent textContent)
			{
				StringBuilder stringBuilder2 = stringBuilder;
				StringBuilder stringBuilder3 = stringBuilder2;
				StringBuilder.AppendInterpolatedStringHandler handler = new StringBuilder.AppendInterpolatedStringHandler(7, 2, stringBuilder2);
				handler.AppendFormatted(value);
				handler.AppendLiteral("Text: ");
				handler.AppendFormatted(textContent.text);
				handler.AppendLiteral("\n");
				stringBuilder3.Append(ref handler);
			}
			else
			{
				StringBuilder stringBuilder2 = stringBuilder;
				StringBuilder stringBuilder4 = stringBuilder2;
				StringBuilder.AppendInterpolatedStringHandler handler = new StringBuilder.AppendInterpolatedStringHandler(1, 2, stringBuilder2);
				handler.AppendFormatted(value);
				handler.AppendFormatted(GetType().Name);
				handler.AppendLiteral("\n");
				stringBuilder4.Append(ref handler);
			}
			if (children != null)
			{
				foreach (Content child in children)
				{
					stringBuilder.Append(child.ToString(indent + 1));
				}
			}
			return stringBuilder.ToString();
		}
	}

	private class SectionContent : Content
	{
		public string type;

		public string unlockCode;

		public LockableSectionContent lockableSection;
	}

	private class LockableSectionContent : Content
	{
		public bool collapsed;

		public Control footerControl;
	}

	private class RowContent : Content
	{
	}

	private class QuoteContent : Content
	{
	}

	private class TextContent : Content
	{
		public string text;
	}

	private class GlyphContent : Content
	{
		public string imageName;
	}

	private class TitleContent : Content
	{
		public string text;
	}

	[Export(PropertyHint.None, "")]
	private Theme defaultCardTheme;

	[Export(PropertyHint.None, "")]
	private int largeFontSizeOverride = 32;

	[Export(PropertyHint.None, "")]
	private PackedScene titleContentScene;

	[Export(PropertyHint.None, "")]
	private PackedScene glyphContentScene;

	[Export(PropertyHint.None, "")]
	private PackedScene quoteContentScene;

	[Export(PropertyHint.None, "")]
	private PackedScene rowContentScene;

	[Export(PropertyHint.None, "")]
	private PackedScene rowItemContentScene;

	[Export(PropertyHint.None, "")]
	private PackedScene headerSectionContentScene;

	[Export(PropertyHint.None, "")]
	private PackedScene footerSectionContentScene;

	[Export(PropertyHint.None, "")]
	private PackedScene authorSectionContentScene;

	[Export(PropertyHint.None, "")]
	private PackedScene gameMenuSectionContentScene;

	[Export(PropertyHint.None, "")]
	private PackedScene lockableSectionContentScene;

	[Export(PropertyHint.None, "")]
	private PackedScene textContentScene;

	[Export(PropertyHint.None, "")]
	private PackedScene quoteTextContentScene;

	[Export(PropertyHint.None, "")]
	private PackedScene rowItemScene;

	[Export(PropertyHint.None, "")]
	private Control cardContentContainer;

	[Export(PropertyHint.None, "")]
	private ScrollContainer scrollContainer;

	[Export(PropertyHint.None, "")]
	private float pauseBeforeImageTransitionBegins = 4f;

	[Export(PropertyHint.None, "")]
	private float imageTransitionDuration = 9f;

	[Export(PropertyHint.None, "")]
	private float particleSpinSpeed = 1000f;

	[Export(PropertyHint.None, "")]
	private float particlesFadeInPeriod = 0.1f;

	[Export(PropertyHint.None, "")]
	private float particlesMaxAlpha = 0.6f;

	[Export(PropertyHint.None, "")]
	private float particlesMinScale = 0.2f;

	[Export(PropertyHint.None, "")]
	private float particlesMaxScale = 0.8f;

	[Export(PropertyHint.None, "")]
	private float blinkHalfClosedTime = 0.06f;

	[Export(PropertyHint.None, "")]
	private float blinkClosedTime = 0.1f;

	[Export(PropertyHint.None, "")]
	private float minTimeBetweenBlinks = 0.2f;

	[Export(PropertyHint.None, "")]
	private float maxTimeBetweenBlinks = 3f;

	[Export(PropertyHint.None, "")]
	private float faceScaleSpeed = 0.731f;

	[Export(PropertyHint.None, "")]
	private float faceScaleAmount = 0.1f;

	[Export(PropertyHint.None, "")]
	private float faceRotationSpeed = 0.6512f;

	[Export(PropertyHint.None, "")]
	private float faceRotationMaxDegrees = 5f;

	[Export(PropertyHint.None, "")]
	private float faceAlphaMin = 0.4f;

	[Export(PropertyHint.None, "")]
	private float missedTapMaxDistance = 36f;

	[Export(PropertyHint.None, "")]
	private float missedTapMovementAllowance = 14f;

	public string sectionThemeName;

	private float imageTransition;

	private bool imageTransitionActive;

	private TextureRect imageNode;

	private Texture2D backgroundImage;

	private Texture2D blinkHalfClosed;

	private Texture2D blinkClosed;

	private bool isFace;

	private float nextBlinkTimeout;

	private float lastScrollOffset = -1f;

	private bool currentAllowTitleLinks;

	public float currentCoherence = 1f;

	private bool currentCoherenceIsCriticallyLow;

	private bool currentRedacted;

	private const int quoteTruncatedLineLimit = 2;

	private List<CardTextContent> lineLimitedQuoteTexts = new List<CardTextContent>();

	private Dictionary<int, Vector2> pendingBgTouchTapPositions = new Dictionary<int, Vector2>();

	private Vector2? pendingBgMouseClickPosition;

	private List<Content> allCardContent = new List<Content>();

	private Stack<Content> containerStack = new Stack<Content>();

	private List<SectionContent> unlockableSections = new List<SectionContent>();

	private bool cardGenerationInProgress;

	private bool wordsShown;

	private static bool hasOverridenFontSize;

	private Tween scrollTween;

	private List<Tween> sectionCollapseTweens = new List<Tween>();

	public string title { get; private set; }

	public string code { get; private set; }

	public bool isComplete { get; set; }

	public bool arrivedInView { get; private set; }

	public bool canScrollUp => scrollContainer.ScrollVertical > 0;

	public bool canScrollDown
	{
		get
		{
			VScrollBar vScrollBar = scrollContainer.GetVScrollBar();
			return vScrollBar.Value < vScrollBar.MaxValue - vScrollBar.Page;
		}
	}

	public float currentScrollPosition => scrollContainer.ScrollVertical;

	public int linkCount { get; private set; }

	public LinkButton firstOnScreenTitleLink { get; private set; }

	public string debugContentSummary
	{
		get
		{
			StringBuilder stringBuilder = new StringBuilder();
			foreach (Content item in allCardContent)
			{
				stringBuilder.Append(item.ToString());
				if (stringBuilder.Length > 100)
				{
					break;
				}
			}
			string text = stringBuilder.ToString().Replace("\n", "//").Substring(0, Math.Min(100, stringBuilder.Length));
			if (text.Length == 0)
			{
				return "<EMPTY>";
			}
			return text;
		}
	}

	public override void _EnterTree()
	{
		if ((Platform.isiPhone || Platform.isSwitch || Platform.isSteamDeck) && !hasOverridenFontSize)
		{
			hasOverridenFontSize = true;
			defaultCardTheme.DefaultFontSize = largeFontSizeOverride;
			defaultCardTheme.SetFontSize("font_size", "Button", largeFontSizeOverride);
			CardTextContent.lineHeightScaleFactor = 1.1f;
		}
		imageNode = GetNode<TextureRect>("Image");
	}

	public override void _Ready()
	{
		Clear();
		if (base.Owner == null)
		{
			StartSection("header");
			Append("glyph", "PSI");
			Append("title", "AJ-26");
			StartRow();
			Append("Softback");
			Append("Joe's very awesome book");
			Append("2005");
			EndRow();
			StartQuote();
			Append("text", "The real treasure was the bureaucratic forms we filled out along the way, said nobody ever, yet here we are.");
			Append("text", "It's remarkable how a simple quote can pretend to be profound while actually saying nothing at all. Rather like this one, in fact.");
			EndQuote();
			EndSection();
			Append("(%AJ26%), from 1926. Notable articles include:");
			Append("- an account of the destruction of Professor [b]Quentin[/b] [b]Lemarchant[/b]’s 1918 work by an editor with links to the [b]Church[/b] [b]of[/b] [b]the[/b] [b]Rampaging[/b] [b]Christ[/b]. See (CR89) - but have a stiff drink to hand!");
			Append("- a brief mention of (%QL18%) ‘s deathbed publication.");
			Append("[color=#FFE473](IM46)[/color] [color=#FFE473]is[/color] [color=#FFE473]associated[/color]");
			Append("[color=#FFE473]with[/color] [color=#FFE473]this[/color] [color=#FFE473]entry.[/color]");
			Finalise("AJ26", allowTitleLinks: true, 1f, coherenceIsCriticallyLow: false, redacted: true, immediate: true);
		}
	}

	public void Clear()
	{
		foreach (Content item in allCardContent)
		{
			item.Clear();
		}
		containerStack.Clear();
		allCardContent.Clear();
		unlockableSections.Clear();
		lineLimitedQuoteTexts.Clear();
		foreach (Node child in cardContentContainer.GetChildren())
		{
			child.QueueFree();
		}
		SetImageBackground(null);
		imageTransition = 0f;
		imageTransitionActive = false;
		GetNode<TextureRect>("Image/ParticleSpin").Visible = false;
		scrollContainer.ScrollVertical = 0;
		if (scrollTween != null)
		{
			scrollTween.Kill();
			scrollTween = null;
		}
		foreach (Tween sectionCollapseTween in sectionCollapseTweens)
		{
			sectionCollapseTween.Kill();
		}
		sectionCollapseTweens.Clear();
		cardGenerationInProgress = true;
		wordsShown = false;
		pendingBgTouchTapPositions.Clear();
		pendingBgMouseClickPosition = null;
	}

	public void OnArrivedInView(MachineUI machineUI)
	{
		arrivedInView = true;
		if (wordsShown)
		{
			return;
		}
		wordsShown = true;
		float num = 0f;
		bool grabFocusOnFirstButton = true;
		foreach (CardTextContent item in AllTextContentEnumerator())
		{
			if (item.ShowWords(animated: true, num, grabFocusOnFirstButton))
			{
				grabFocusOnFirstButton = false;
			}
			num += 0.05f;
		}
	}

	public override void _Process(double delta)
	{
		if (imageTransitionActive)
		{
			float num = ((imageTransition < 0f) ? (imageTransition + (float)delta) : (imageTransition + (float)delta / imageTransitionDuration));
			if (num >= 1f)
			{
				imageTransitionActive = false;
			}
			SetImageTransition(num);
			if (num <= 0f)
			{
				return;
			}
			TextureRect node = GetNode<TextureRect>("Image/ParticleSpin");
			node.Visible = true;
			node.RotationDegrees = num * particleSpinSpeed;
			float num2 = Mathf.Lerp(particlesMinScale, particlesMaxScale, num);
			node.Scale = new Vector2(num2, num2);
			float num3 = ((!(num < particlesFadeInPeriod)) ? (1f - (num - particlesFadeInPeriod) / (1f - particlesFadeInPeriod)) : (num / particlesFadeInPeriod));
			node.Modulate = new Color(1f, 1f, 1f, particlesMaxAlpha * num3);
		}
		if (scrollTween == null && lastScrollOffset != (float)scrollContainer.ScrollVertical && !cardGenerationInProgress && StoryController.instance.canLinkButtonGrabFocus)
		{
			float num4 = scrollContainer.Size.Y * 0.35f;
			Control control = GetViewport().GuiGetFocusOwner();
			float num5 = 100f;
			foreach (LinkButton item in AllButtonEnumerator())
			{
				if ((!item.isTitle || StoryController.instance.playerIsCollectingTitles) && !item.collected)
				{
					float num6 = Mathf.Abs(item.GetGlobalPosition().Y - scrollContainer.GetGlobalPosition().Y - num4);
					if (num6 < num5)
					{
						control = item;
						num5 = num6;
					}
				}
			}
			control?.GrabFocus();
		}
		lastScrollOffset = scrollContainer.ScrollVertical;
		if (backgroundImage != null && blinkClosed != null && blinkHalfClosed != null && imageNode != null)
		{
			nextBlinkTimeout -= (float)delta;
			if (nextBlinkTimeout <= 0f)
			{
				float num7 = 0f - nextBlinkTimeout;
				if (num7 > 2f * blinkHalfClosedTime + blinkClosedTime)
				{
					imageNode.Texture = backgroundImage;
					nextBlinkTimeout = ((GD.Randf() < 0.2f) ? ((float)GD.RandRange(0.10000000149011612, 0.20000000298023224)) : ((float)GD.RandRange(minTimeBetweenBlinks, maxTimeBetweenBlinks)));
				}
				else if (num7 < blinkHalfClosedTime || num7 > blinkHalfClosedTime + blinkClosedTime)
				{
					imageNode.Texture = blinkHalfClosed;
				}
				else
				{
					imageNode.Texture = blinkClosed;
				}
			}
		}
		if (backgroundImage != null && isFace)
		{
			float weight = 0.5f * Mathf.Sin(faceScaleSpeed * (float)Time.GetTicksMsec() * 0.001f) + 0.5f;
			float num8 = Mathf.Lerp(1f - faceScaleAmount, 1f + faceScaleAmount, weight);
			float rotationDegrees = Mathf.Lerp(0f - faceRotationMaxDegrees, faceRotationMaxDegrees, 0.5f * Mathf.Sin(faceRotationSpeed * (float)Time.GetTicksMsec() * 0.001f) + 0.5f);
			float a = Mathf.Lerp(faceAlphaMin, 1f, weight);
			imageNode.Scale = new Vector2(num8, num8);
			imageNode.RotationDegrees = rotationDegrees;
			imageNode.Modulate = new Color(1f, 1f, 1f, a);
		}
	}

	private bool IsWithinScrollBounds(Vector2 globalPosition)
	{
		if (scrollContainer == null)
		{
			return false;
		}
		return scrollContainer.GetGlobalRect().HasPoint(globalPosition);
	}

	private bool PositionHitsAnyLinkButton(Vector2 position)
	{
		foreach (LinkButton item in AllButtonEnumerator())
		{
			if (item != null && GodotObject.IsInstanceValid(item) && item.Visible && item.IsVisibleInTree() && item.GetGlobalRect().HasPoint(position))
			{
				return true;
			}
		}
		return false;
	}

	private void HandleBackgroundTapRelease(Vector2 startPosition, Vector2 position)
	{
		if (IsWithinScrollBounds(position) && !((position - startPosition).Length() > missedTapMovementAllowance) && !PositionHitsAnyLinkButton(position) && TryFindNearestLinkButton(position, out var nearestButton, out var bestDistance) && !(bestDistance > missedTapMaxDistance))
		{
			nearestButton.GrabFocus();
			nearestButton.EmitSignal(BaseButton.SignalName.Pressed);
		}
	}

	private bool TryFindNearestLinkButton(Vector2 position, out LinkButton nearestButton, out float bestDistance)
	{
		nearestButton = null;
		bestDistance = float.MaxValue;
		foreach (LinkButton item in AllButtonEnumerator())
		{
			if (item != null && GodotObject.IsInstanceValid(item) && item.Visible && item.IsVisibleInTree() && !item.Disabled && (!item.isTitle || StoryController.instance.playerIsCollectingTitles) && !item.collected && IsOnScreen(item))
			{
				Rect2 globalRect = item.GetGlobalRect();
				Vector2 to = new Vector2(Mathf.Clamp(position.X, globalRect.Position.X, globalRect.Position.X + globalRect.Size.X), Mathf.Clamp(position.Y, globalRect.Position.Y, globalRect.Position.Y + globalRect.Size.Y));
				float num = position.DistanceTo(to);
				if (num < bestDistance)
				{
					bestDistance = num;
					nearestButton = item;
				}
			}
		}
		return nearestButton != null;
	}

	private void HandleBackgroundTapInput(InputEvent @event)
	{
		if (scrollContainer == null)
		{
			return;
		}
		if (@event is InputEventScreenTouch inputEventScreenTouch)
		{
			Vector2 value;
			if (inputEventScreenTouch.Pressed)
			{
				if (IsWithinScrollBounds(inputEventScreenTouch.Position) && !PositionHitsAnyLinkButton(inputEventScreenTouch.Position))
				{
					pendingBgTouchTapPositions[inputEventScreenTouch.Index] = inputEventScreenTouch.Position;
				}
			}
			else if (pendingBgTouchTapPositions.TryGetValue(inputEventScreenTouch.Index, out value))
			{
				pendingBgTouchTapPositions.Remove(inputEventScreenTouch.Index);
				HandleBackgroundTapRelease(value, inputEventScreenTouch.Position);
			}
		}
		else if (@event is InputEventScreenDrag inputEventScreenDrag)
		{
			if (pendingBgTouchTapPositions.TryGetValue(inputEventScreenDrag.Index, out var value2) && (inputEventScreenDrag.Position - value2).Length() > missedTapMovementAllowance)
			{
				pendingBgTouchTapPositions.Remove(inputEventScreenDrag.Index);
			}
		}
		else if (@event is InputEventMouseButton inputEventMouseButton && inputEventMouseButton.ButtonIndex == MouseButton.Left)
		{
			if (inputEventMouseButton.Pressed)
			{
				if (!IsWithinScrollBounds(inputEventMouseButton.Position))
				{
					pendingBgMouseClickPosition = null;
				}
				else if (PositionHitsAnyLinkButton(inputEventMouseButton.Position))
				{
					pendingBgMouseClickPosition = null;
				}
				else
				{
					pendingBgMouseClickPosition = inputEventMouseButton.Position;
				}
			}
			else if (pendingBgMouseClickPosition.HasValue)
			{
				Vector2 value3 = pendingBgMouseClickPosition.Value;
				pendingBgMouseClickPosition = null;
				HandleBackgroundTapRelease(value3, inputEventMouseButton.Position);
			}
		}
		else if (@event is InputEventMouseMotion inputEventMouseMotion && pendingBgMouseClickPosition.HasValue && (inputEventMouseMotion.ButtonMask & MouseButtonMask.Left) != (MouseButtonMask)0L)
		{
			Vector2 value4 = pendingBgMouseClickPosition.Value;
			if ((inputEventMouseMotion.Position - value4).Length() > missedTapMovementAllowance)
			{
				pendingBgMouseClickPosition = null;
			}
		}
	}

	public override void _Input(InputEvent @event)
	{
		base._Input(@event);
		if (Platform.isMobile || Platform.isSteamDeck || Platform.isSwitch)
		{
			HandleBackgroundTapInput(@event);
		}
	}

	public bool IsOnScreen(Control control)
	{
		Rect2 globalRect = control.GetGlobalRect();
		float num = globalRect.Position.Y + globalRect.Size.Y * 0.5f;
		if (num >= 0f)
		{
			return num <= scrollContainer.Size.Y;
		}
		return false;
	}

	public LinkButton GetFirstOnScreenTitleLink()
	{
		LinkButton result = null;
		if (!cardGenerationInProgress)
		{
			foreach (LinkButton item in AllButtonEnumerator())
			{
				if (item.isTitle && !item.collected && IsOnScreen(item))
				{
					result = item;
					break;
				}
			}
		}
		return result;
	}

	public void Scroll(float directionAndStrength)
	{
		scrollContainer.ScrollVertical += (int)(directionAndStrength * 20f);
	}

	public void ScrollToTop()
	{
		ScrollTo(0f, immediate: false);
	}

	public void FocusPrevNextLink(int direction)
	{
		Control control = null;
		Control control2 = null;
		Control control3 = null;
		foreach (Control item in AllButtonEnumerator())
		{
			if (item.HasFocus() && direction < 0)
			{
				control3 = control;
				break;
			}
			if (direction > 0 && control2 != null)
			{
				control3 = item;
				break;
			}
			if (item.HasFocus())
			{
				control2 = item;
			}
			control = item;
		}
		if (control3 != null)
		{
			control3.GrabFocus();
			ScrollToControl(control3);
		}
	}

	public void FocusLeftRightLink(int direction)
	{
		Control control = AllButtonEnumerator().FirstOrDefault((Control l) => l.HasFocus());
		if (control == null)
		{
			return;
		}
		Vector2 vector = control.GetGlobalPosition() + control.Size * 0.5f;
		Vector2 with = new Vector2(direction, 0f).Normalized();
		Control control2 = null;
		float num = float.MaxValue;
		foreach (Control item in AllButtonEnumerator())
		{
			if (item != control)
			{
				Vector2 vector2 = item.GetGlobalPosition() + item.Size * 0.5f - vector;
				float num2 = vector2.Length();
				if (vector2.Normalized().Dot(with) > 0.5f && num2 < num)
				{
					num = num2;
					control2 = item;
				}
			}
		}
		if (control2 != null)
		{
			control2.GrabFocus();
			ScrollToControl(control2);
		}
	}

	private IEnumerable<Control> AllButtonEnumerator()
	{
		foreach (CardTextContent item in AllTextContentEnumerator())
		{
			foreach (Control item2 in item.AllButtonEnumerator())
			{
				yield return item2;
			}
		}
	}

	private IEnumerable<CardTextContent> AllTextContentEnumerator(List<Content> contentList = null)
	{
		List<Content> list = contentList ?? allCardContent;
		foreach (Content item in list)
		{
			if (item is TextContent textContent)
			{
				if (textContent.control is CardTextContent cardTextContent)
				{
					yield return cardTextContent;
				}
			}
			else
			{
				if (item.children == null || item is LockableSectionContent { collapsed: not false })
				{
					continue;
				}
				foreach (CardTextContent item2 in AllTextContentEnumerator(item.children))
				{
					yield return item2;
				}
			}
		}
	}

	public void MarkTitleCollected(string titleLinkWithoutPrefix)
	{
		Button button = null;
		Button button2 = null;
		Button button3 = null;
		foreach (CardTextContent item in AllTextContentEnumerator())
		{
			foreach (LinkButton item2 in item.AllButtonEnumerator())
			{
				if (button2 != null && button3 == null)
				{
					button3 = item2;
				}
				if (button2 == null && item2.isTitle && item2.linkWithoutPrefix == titleLinkWithoutPrefix)
				{
					item2.SetAsCollected(collected: true);
					GD.Print("Found button with focus: " + item2.Name);
					button2 = item2;
				}
				button = item2;
			}
		}
		if (button2 == null)
		{
			button = null;
		}
		if (button != null)
		{
			button.GrabFocus();
		}
		else if (button3 != null)
		{
			button3.GrabFocus();
		}
		else
		{
			button2?.ReleaseFocus();
		}
	}

	public void RefreshAllLinkButtons()
	{
		foreach (LinkButton item in AllButtonEnumerator())
		{
			item.RefreshState();
		}
	}

	public void GrabFocusOnFirstButton()
	{
		AllButtonEnumerator().FirstOrDefault()?.GrabFocus();
	}

	private void SetImageTransition(float transition)
	{
		imageTransition = transition;
		if (transition < 0f)
		{
			imageNode.Visible = false;
			return;
		}
		imageNode.Visible = true;
		(imageNode.Material as ShaderMaterial).SetShaderParameter("mask_scale", imageTransition);
	}

	public void StartSection(string sectionType)
	{
		SectionContent sectionContent = new SectionContent
		{
			type = sectionType
		};
		sectionContent.children = new List<Content>();
		allCardContent.Add(sectionContent);
		containerStack.Push(sectionContent);
	}

	public void SetCurrentSectionUnlockCode(string unlockCode)
	{
		if (containerStack.Count > 0)
		{
			if (containerStack.Peek() is SectionContent sectionContent)
			{
				sectionContent.unlockCode = unlockCode;
				unlockableSections.Add(sectionContent);
			}
			else
			{
				DebugPrintAllContent();
				GD.PushError("SetCurrentSectionUnlockCode(" + unlockCode + ") added when not in a section. See main output log for full content.");
			}
		}
	}

	public void EndSection()
	{
		EndContainer<SectionContent>();
	}

	private void EndContainer<T>() where T : Content
	{
		while (containerStack.Count > 0)
		{
			Content content = containerStack.Pop();
			if (content is T)
			{
				break;
			}
			DebugPrintAllContent();
			GD.PushError($"Expected to end a {typeof(T).Name}, but found a container of type {content.GetType().Name}. See main output log for full content.");
		}
	}

	private void ExpectContainerOrRoot<T>() where T : Content
	{
		while (containerStack.Count > 0 && !(containerStack.Peek() is T))
		{
			DebugPrintAllContent();
			Content content = containerStack.Pop();
			GD.PushError($"Expected to be in a {typeof(T).Name} (or at root), but found a container of type {content.GetType().Name}. See main output log for full content.");
		}
	}

	public void StartRow()
	{
		RowContent item = new RowContent
		{
			children = new List<Content>()
		};
		ExpectContainerOrRoot<SectionContent>();
		Content content = containerStack.Peek();
		if (content is SectionContent sectionContent)
		{
			sectionContent.children.Add(item);
		}
		else if (content != null)
		{
			allCardContent.Add(item);
		}
		containerStack.Push(item);
	}

	public void EndRow()
	{
		EndContainer<RowContent>();
	}

	public void StartQuote()
	{
		QuoteContent item = new QuoteContent
		{
			children = new List<Content>()
		};
		ExpectContainerOrRoot<SectionContent>();
		if (((containerStack.Count > 0) ? containerStack.Peek() : null) is SectionContent sectionContent)
		{
			sectionContent.children.Add(item);
		}
		else
		{
			allCardContent.Add(item);
		}
		containerStack.Push(item);
	}

	public void EndQuote()
	{
		EndContainer<QuoteContent>();
	}

	public void Append(string text)
	{
		Append("text", text);
	}

	public void Append(string type, string text)
	{
		List<Content> children = allCardContent;
		Content content = ((containerStack.Count > 0) ? containerStack.Peek() : null);
		if (content != null)
		{
			children = content.children;
		}
		switch (type)
		{
		case "title":
			title = text;
			children.Add(new TitleContent
			{
				text = text
			});
			break;
		case "glyph":
			children.Add(new GlyphContent
			{
				imageName = text
			});
			break;
		default:
			children.Add(new TextContent
			{
				text = text
			});
			break;
		}
	}

	public void SetImageBackground(string image, bool isFace = false)
	{
		imageTransition = 0f;
		imageTransitionActive = false;
		this.isFace = isFace;
		backgroundImage = null;
		blinkHalfClosed = null;
		blinkClosed = null;
		nextBlinkTimeout = 0f;
		if (string.IsNullOrEmpty(image))
		{
			imageNode.Texture = null;
			imageNode.Visible = false;
			return;
		}
		string text = "res://" + image;
		if (ResourceLoader.Exists(text))
		{
			backgroundImage = ResourceLoader.Load<Texture2D>(text, null, ResourceLoader.CacheMode.Reuse);
			imageNode.Texture = backgroundImage;
			string directoryName = Path.GetDirectoryName(image);
			string fileNameWithoutExtension = Path.GetFileNameWithoutExtension(image);
			string extension = Path.GetExtension(image);
			string path = $"res://{directoryName}/{fileNameWithoutExtension}_HalfClosed{extension}";
			string path2 = $"res://{directoryName}/{fileNameWithoutExtension}_Closed{extension}";
			if (ResourceLoader.Exists(path))
			{
				blinkHalfClosed = ResourceLoader.Load<Texture2D>(path, null, ResourceLoader.CacheMode.Reuse);
			}
			if (ResourceLoader.Exists(path2))
			{
				blinkClosed = ResourceLoader.Load<Texture2D>(path2, null, ResourceLoader.CacheMode.Reuse);
			}
			if (blinkClosed != null)
			{
				nextBlinkTimeout = (float)GD.RandRange(minTimeBetweenBlinks, maxTimeBetweenBlinks);
			}
		}
		else
		{
			GD.PrintErr("ink image for #IMAGE tag not found: " + text);
		}
		imageTransitionActive = true;
		SetImageTransition(-1f * pauseBeforeImageTransitionBegins);
	}

	public async void Finalise(string code, bool allowTitleLinks, float coherence, bool coherenceIsCriticallyLow, bool redacted, bool immediate)
	{
		this.code = code;
		arrivedInView = false;
		currentAllowTitleLinks = allowTitleLinks;
		currentCoherence = coherence;
		currentCoherenceIsCriticallyLow = coherenceIsCriticallyLow;
		currentRedacted = redacted;
		if (DebugOptions.instance.perfectCoherence)
		{
			currentCoherence = 1f;
			currentCoherenceIsCriticallyLow = false;
			currentRedacted = false;
		}
		FinaliseContentList_InternalRecursive(null, cardContentContainer, allCardContent, immediate, inHeader: false);
		EmbedLockableChildren();
		if (immediate)
		{
			wordsShown = true;
		}
		cardGenerationInProgress = false;
		foreach (SectionContent unlockableSection in unlockableSections)
		{
			SetSectionCollapsed(unlockableSection, targetCollapsed: true, immediate: true);
		}
		if (!immediate)
		{
			await ToSignal(GetTree(), "process_frame");
		}
		Fuzz(coherence, coherenceIsCriticallyLow, redacted);
	}

	private void FinaliseContentList_InternalRecursive(Content parentContent, Control parentControl, List<Content> contentList, bool immediate, bool inHeader, SectionContent lockingParent = null)
	{
		bool flag = false;
		for (int i = 0; i < contentList.Count; i++)
		{
			Content content = contentList[i];
			flag = false;
			if (!(content is TitleContent titleContent))
			{
				if (!(content is TextContent textContent))
				{
					if (!(content is GlyphContent glyphContent))
					{
						if (!(content is SectionContent sectionContent))
						{
							if (!(content is RowContent rowContent))
							{
								if (content is QuoteContent quoteContent)
								{
									CardContainer cardContainer = quoteContentScene.Instantiate<CardContainer>(PackedScene.GenEditState.Disabled);
									cardContainer.Name = "quote " + parentControl.GetChildCount();
									quoteContent.control = cardContainer.contentContainer;
									parentControl.AddChild(cardContainer, forceReadableName: false, InternalMode.Disabled);
								}
								else
								{
									GD.PrintErr("Unhandled content type: " + content.GetType().Name);
								}
							}
							else
							{
								CardContainer cardContainer2 = rowContentScene.Instantiate<CardContainer>(PackedScene.GenEditState.Disabled);
								cardContainer2.Name = "row " + parentControl.GetChildCount();
								rowContent.control = cardContainer2.contentContainer;
								parentControl.AddChild(cardContainer2, forceReadableName: false, InternalMode.Disabled);
							}
						}
						else
						{
							object obj = sectionContent.type switch
							{
								"header" => headerSectionContentScene, 
								"footer" => footerSectionContentScene, 
								"game_menu" => gameMenuSectionContentScene, 
								_ => authorSectionContentScene, 
							};
							if (sectionContent.type == "header")
							{
								flag = true;
							}
							CardContainer cardContainer3 = ((PackedScene)obj).Instantiate<CardContainer>(PackedScene.GenEditState.Disabled);
							parentControl.AddChild(cardContainer3, forceReadableName: false, InternalMode.Disabled);
							cardContainer3.Name = sectionContent.type;
							sectionContent.control = cardContainer3.contentContainer;
							lockingParent = null;
						}
					}
					else
					{
						TextureRect textureRect = (TextureRect)(glyphContent.control = glyphContentScene.Instantiate<TextureRect>(PackedScene.GenEditState.Disabled));
						string text = "res://Glyphs/" + glyphContent.imageName.ToLower() + ".png";
						if (ResourceLoader.Exists(text))
						{
							textureRect.Texture = ResourceLoader.Load<Texture2D>(text, null, ResourceLoader.CacheMode.Reuse);
						}
						else
						{
							GD.PrintErr("Glyph texture not found: " + text);
						}
						parentControl.AddChild(textureRect, forceReadableName: false, InternalMode.Disabled);
					}
				}
				else
				{
					string text2;
					CardTextContent cardTextContent;
					if (parentContent is RowContent)
					{
						text2 = textContent.text.Trim();
						text2 = text2.Replace("\n", " ");
						text2 = InkStylingUtility.ProcessAndStyleText(text2, terminatingPunctuation: false, "#000000");
						Control control = rowItemScene.Instantiate<Control>(PackedScene.GenEditState.Disabled);
						control.Name = "rowItem " + parentControl.GetChildCount();
						parentControl.AddChild(control, forceReadableName: false, InternalMode.Disabled);
						cardTextContent = control.GetNode<CardTextContent>("MarginContainer/CardTextContent");
					}
					else
					{
						StringBuilder stringBuilder = new StringBuilder();
						for (int j = i; j < contentList.Count && contentList[j] is TextContent textContent2; j++)
						{
							string value = InkStylingUtility.ProcessAndStyleText(textContent2.text);
							if (stringBuilder.Length > 0)
							{
								stringBuilder.Append("\n");
							}
							stringBuilder.Append(value);
							i = j;
						}
						text2 = stringBuilder.ToString();
						cardTextContent = ((parentContent is QuoteContent) ? quoteTextContentScene : textContentScene).Instantiate<CardTextContent>(PackedScene.GenEditState.Disabled);
						parentControl.AddChild(cardTextContent, forceReadableName: false, InternalMode.Disabled);
					}
					string text3 = CardLinks.ConvertToBBCode(text2, currentAllowTitleLinks);
					int lineLimit = -1;
					if (parentContent is QuoteContent && currentRedacted)
					{
						lineLimit = 2;
						lineLimitedQuoteTexts.Add(cardTextContent);
					}
					cardTextContent.SetText(text3, inHeader, lineLimit);
					if (immediate)
					{
						cardTextContent.ShowWords(animated: false);
					}
					cardTextContent.LinkPressed += delegate(string link, LinkButton linkButton)
					{
						OnCardLinkPressed(link, linkButton, lockingParent);
					};
					cardTextContent.LinkButtonAppeared += OnLinkButtonAppeared;
					textContent.control = cardTextContent;
				}
			}
			else
			{
				RichTextLabel richTextLabel = (RichTextLabel)(titleContent.control = titleContentScene.Instantiate<RichTextLabel>(PackedScene.GenEditState.Disabled));
				richTextLabel.Text = titleContent.text;
				parentControl.AddChild(richTextLabel, forceReadableName: false, InternalMode.Disabled);
			}
			if (content.children != null)
			{
				if (content is SectionContent && ((SectionContent)content).unlockCode != null)
				{
					lockingParent = (SectionContent)content;
				}
				FinaliseContentList_InternalRecursive(content, content.control, content.children, immediate, inHeader | flag, lockingParent);
			}
		}
	}

	private void ScrollToContent(Content targetContent, bool immediate)
	{
		if (!allCardContent.Contains(targetContent))
		{
			GD.PushError("ScrollToContent: Can only scroll to root level content");
			return;
		}
		float num = 0f;
		foreach (Content item in allCardContent)
		{
			if (item == targetContent)
			{
				break;
			}
			if (item is SectionContent { lockableSection: not null } sectionContent)
			{
				num += 80f;
				if (!sectionContent.lockableSection.collapsed && sectionContent.lockableSection.control is CardContainer cardContainer)
				{
					num += cardContainer.contentContainer.Size.Y;
				}
			}
			else
			{
				num += item.control.Size.Y;
			}
		}
		ScrollToPositionIfNecessary(num, immediate);
	}

	private void ScrollToPositionIfNecessary(float y, bool immediate)
	{
		int num = (int)y - 100;
		int num2 = scrollContainer.ScrollVertical + 80;
		float num3 = (float)scrollContainer.ScrollVertical + scrollContainer.Size.Y - 300f;
		if (num <= num2 || !((float)num < num3))
		{
			ScrollTo(num, immediate);
		}
	}

	private void ScrollTo(float targetY, bool immediate)
	{
		if (immediate)
		{
			scrollContainer.ScrollVertical = (int)targetY;
			return;
		}
		if (scrollTween != null)
		{
			scrollTween.Kill();
		}
		scrollTween = CreateTween();
		scrollTween.SetTrans(Tween.TransitionType.Sine);
		scrollTween.SetEase(Tween.EaseType.InOut);
		scrollTween.TweenProperty(scrollContainer, "scroll_vertical", targetY, 0.5);
		scrollTween.Finished += delegate
		{
			scrollTween = null;
		};
	}

	private void ScrollToControl(Control control)
	{
		float y = control.GetGlobalPosition().Y - scrollContainer.GetGlobalPosition().Y + (float)scrollContainer.ScrollVertical;
		ScrollToPositionIfNecessary(y, immediate: false);
	}

	public bool TryUnlockSectionWithCode(string code)
	{
		if (!unlockableSections.Any((SectionContent section) => section.unlockCode == code))
		{
			return false;
		}
		foreach (Tween sectionCollapseTween in sectionCollapseTweens)
		{
			sectionCollapseTween.Kill();
		}
		sectionCollapseTweens.Clear();
		foreach (SectionContent unlockableSection in unlockableSections)
		{
			SetSectionCollapsed(unlockableSection, unlockableSection.unlockCode != code, immediate: false);
		}
		SectionContent sectionContent = unlockableSections.First((SectionContent section) => section.unlockCode == code);
		if (sectionContent != null)
		{
			ScrollToContent(sectionContent, immediate: false);
		}
		return true;
	}

	private void SetSectionCollapsed(SectionContent section, bool targetCollapsed, bool immediate)
	{
		if (section.lockableSection == null)
		{
			GD.PushError("SetSectionCollapsed: No lockable section found in section");
			return;
		}
		if (!(section.lockableSection.control is CardContainer cardContainer))
		{
			GD.PushError("SetSectionCollapsed: Lockable section has no control or is not a CardContainer");
			return;
		}
		section.lockableSection.collapsed = targetCollapsed;
		float y = cardContainer.contentContainer.Size.Y;
		float num = (targetCollapsed ? 80f : y);
		if (immediate)
		{
			cardContainer.CustomMinimumSize = new Vector2(cardContainer.CustomMinimumSize.X, num);
			section.lockableSection.footerControl.Visible = targetCollapsed;
			section.lockableSection.footerControl.Modulate = new Color(1f, 1f, 1f, targetCollapsed ? 1f : 0f);
			foreach (CardTextContent item in AllTextContentEnumerator(section.lockableSection.children))
			{
				if (targetCollapsed)
				{
					item.HideWords(animated: false);
				}
				else
				{
					item.ShowWords(animated: false);
				}
			}
			{
				foreach (Content child in section.lockableSection.children)
				{
					if (child.control != null)
					{
						child.control.Modulate = new Color(1f, 1f, 1f, targetCollapsed ? 0f : 1f);
					}
				}
				return;
			}
		}
		Tween tween = CreateTween().SetParallel();
		tween.SetTrans(Tween.TransitionType.Sine);
		tween.SetEase(Tween.EaseType.InOut);
		tween.TweenProperty(cardContainer, "custom_minimum_size:y", num, 0.5);
		section.lockableSection.footerControl.Visible = true;
		tween.TweenProperty(section.lockableSection.footerControl, "modulate:a", targetCollapsed ? 1f : 0f, 0.5).SetDelay(targetCollapsed ? 0f : 0.5f);
		sectionCollapseTweens.Add(tween);
		tween.Finished += delegate
		{
			sectionCollapseTweens.Remove(tween);
			if (!targetCollapsed)
			{
				section.lockableSection.footerControl.Visible = false;
			}
		};
		foreach (Content child2 in section.lockableSection.children)
		{
			if (child2.control != null)
			{
				tween.TweenProperty(child2.control, "modulate:a", targetCollapsed ? 0f : 1f, 0.30000001192092896);
			}
		}
		float num2 = 0.3f;
		foreach (CardTextContent item2 in AllTextContentEnumerator(section.lockableSection.children))
		{
			if (targetCollapsed)
			{
				item2.HideWords(animated: true);
			}
			else
			{
				item2.ShowWords(animated: true, num2);
			}
			num2 += 0.05f;
		}
	}

	private void EmbedLockableChildren()
	{
		foreach (SectionContent unlockableSection in unlockableSections)
		{
			if (unlockableSection.children.FindIndex((Content child) => child is LockableSectionContent) != -1)
			{
				continue;
			}
			int num = unlockableSection.children.FindIndex((Content child) => child is RowContent);
			if (num == -1)
			{
				GD.PrintErr("Lockable section: No header row found");
				continue;
			}
			int num2 = num + 1;
			int num3 = unlockableSection.children.Count - 1;
			if (num3 < num2)
			{
				continue;
			}
			List<Content> range = unlockableSection.children.GetRange(num2, num3 - num2 + 1);
			unlockableSection.children.RemoveRange(num2, num3 - num2 + 1);
			LockableSectionContent lockableSectionContent = new LockableSectionContent
			{
				children = range,
				collapsed = true
			};
			CardContainer cardContainer = (CardContainer)(lockableSectionContent.control = lockableSectionContentScene.Instantiate<CardContainer>(PackedScene.GenEditState.Disabled));
			lockableSectionContent.footerControl = cardContainer.GetNode<Control>("Footer");
			cardContainer.Name = "lockable section";
			foreach (Content item in range)
			{
				if (item.control != null)
				{
					item.control.GetParent().RemoveChild(item.control);
					cardContainer.contentContainer.AddChild(item.control, forceReadableName: false, InternalMode.Disabled);
				}
			}
			unlockableSection.control.AddChild(cardContainer, forceReadableName: false, InternalMode.Disabled);
			unlockableSection.lockableSection = lockableSectionContent;
			unlockableSection.children.Add(lockableSectionContent);
		}
	}

	public void Fuzz(float coherence, bool coherenceIsCriticallyLow, bool redacted)
	{
		bool flag = currentRedacted;
		currentCoherence = coherence;
		currentCoherenceIsCriticallyLow = coherenceIsCriticallyLow;
		currentRedacted = redacted;
		if (DebugOptions.instance.perfectCoherence)
		{
			currentCoherence = 1f;
			currentCoherenceIsCriticallyLow = false;
			currentRedacted = false;
		}
		foreach (Content item in allCardContent)
		{
			ApplyFuzzToContent_Recurse(item, null);
		}
		if (flag == currentRedacted)
		{
			return;
		}
		foreach (CardTextContent lineLimitedQuoteText in lineLimitedQuoteTexts)
		{
			lineLimitedQuoteText.SetLineLimitAnimated(currentRedacted ? 2 : (-1));
		}
	}

	private void ApplyFuzzToContent_Recurse(Content content, Content parentContent)
	{
		if (content.control is CardTextContent cardTextContent)
		{
			float coherence = currentCoherence;
			if (parentContent is RowContent && !currentCoherenceIsCriticallyLow)
			{
				coherence = Mathf.Clamp(currentCoherence + 0.4f, 0f, 0.99f);
			}
			cardTextContent.Fuzz(coherence, currentCoherenceIsCriticallyLow, currentRedacted, immediate: false);
		}
		if (content.children == null)
		{
			return;
		}
		foreach (Content child in content.children)
		{
			ApplyFuzzToContent_Recurse(child, content);
		}
	}

	private void OnCardLinkPressed(string link, LinkButton linkButton, SectionContent lockingParent)
	{
		if (lockingParent != null && lockingParent.lockableSection.collapsed && lockingParent.unlockCode != link)
		{
			GD.Print("Link button with link " + link + " is in a collapsed section, skipping");
		}
		else if (IsOnScreen(linkButton))
		{
			EmitSignal(SignalName.CardLinkPressed, link);
		}
		else
		{
			GD.Print("Link button with link " + link + " is not on screen, skipping");
		}
	}

	private void OnLinkButtonAppeared(LinkButton linkButton)
	{
		if (IsOnScreen(linkButton))
		{
			EmitSignal(SignalName.LinkButtonAppeared, linkButton);
		}
	}

	private void DebugPrintAllContent()
	{
		GD.Print("=====All card content=====");
		foreach (Content item in allCardContent)
		{
			GD.Print(item.ToString());
		}
		GD.Print("=====End of all card content=====");
	}
}
