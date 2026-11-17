using System;
using System.Collections.Generic;
using System.Linq;
using Godot;

public partial class CardTextContent : Control
{
	[Signal]
	public delegate void LinkPressedEventHandler(string link, LinkButton linkButton);

	[Signal]
	public delegate void LinkButtonAppearedEventHandler(LinkButton linkButton);

	private struct Item
	{
		public Control control;

		public string originalText;

		public bool isSpace;

		public bool isRedactable;
	}

	private struct Paragraph
	{
		public List<Item> items;
	}

	public const string ContentGroupName = "card_text_contents";

	[Export(PropertyHint.None, "")]
	private float lineHeight = 50f;

	[Export(PropertyHint.None, "")]
	private bool isSingleLine;

	[Export(PropertyHint.None, "")]
	private float paragraphIndent = 30f;

	[Export(PropertyHint.None, "")]
	private float topMargin = 20f;

	[Export(PropertyHint.None, "")]
	private float bottomMargin = 20f;

	[Export(PropertyHint.None, "")]
	private float straightThreshold = 100f;

	[Export(PropertyHint.None, "")]
	private float lineScaleEffectStrength = 0.4f;

	[Export(PropertyHint.None, "")]
	private float buttonYOffset = -10f;

	[Export(PropertyHint.None, "")]
	private Control cardContainer;

	[Export(PropertyHint.None, "")]
	private bool invertedColors;

	[Export(PropertyHint.None, "")]
	private bool defaultBold;

	[Export(PropertyHint.None, "")]
	private FontVariation boldFont;

	[Export(PropertyHint.None, "")]
	private FontVariation italicFont;

	public static float lineHeightScaleFactor = 1f;

	private const float fadeInDelayPerItem = 0.15f;

	private const float fadeInDuration = 0.3f;

	private const float fadeOutDuration = 0.1f;

	private List<Paragraph> paragraphs = new List<Paragraph>();

	private List<Control> lineContainers = new List<Control>();

	private List<int> totalWordCountSoFarAtEndOfEachLine = new List<int>();

	private Tween wordsAnimTween;

	private int fuzzSessionCounter;

	private bool wordsShown;

	private int lineLimit = -1;

	private int layoutLines;

	private float layoutMaxLineWidth;

	public float scaledLineHeight => lineHeight * lineHeightScaleFactor;

	private Texture2D psiSmallImage => ResourceLoader.Load<Texture2D>("res://Glyphs/psi_small.png", null, ResourceLoader.CacheMode.Reuse);

	public async void SetText(string text, bool contentIsRedactable, int lineLimit)
	{
		Clear();
		this.lineLimit = lineLimit;
		List<string> lines = text.Split("\n").ToList();
		CreateParagraphs(lines, contentIsRedactable);
		await ToSignal(GetTree(), "process_frame");
		LayoutControlsLines();
	}

	private void CreateParagraphs(List<string> lines, bool contentIsRedactable)
	{
		foreach (string line in lines)
		{
			List<Item> list = new List<Item>();
			foreach (LineParser.Word word in new LineParser(line).Parse())
			{
				if (word.isWhitespace)
				{
					list.Add(new Item
					{
						isSpace = true
					});
				}
				else if (word.link != null)
				{
					bool flag = word.link.StartsWith("TITLE:");
					string text = (flag ? word.link.Substring("TITLE:".Length) : word.link);
					LinkButton link = new LinkButton();
					link.MouseFilter = MouseFilterEnum.Pass;
					bool collected = flag && StoryController.instance.GotTitle(text);
					link.Setup(word.text, text, flag, collected, invertedColors);
					link.Pressed += delegate
					{
						EmitSignal(SignalName.LinkPressed, word.link, link);
					};
					link.Modulate = new Color(1f, 1f, 1f, 0f);
					AddChild(link, forceReadableName: false, InternalMode.Disabled);
					list.Add(new Item
					{
						control = link,
						isRedactable = contentIsRedactable
					});
				}
				else if (word.text == "PSICHAR")
				{
					TextureRect textureRect = new TextureRect();
					textureRect.Texture = psiSmallImage;
					textureRect.MouseFilter = MouseFilterEnum.Ignore;
					textureRect.ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize;
					textureRect.StretchMode = TextureRect.StretchModeEnum.KeepAspectCentered;
					textureRect.Size = new Vector2(26f, 26f);
					Color themeColor = GetThemeColor("font_color", "Label");
					themeColor.A = 0f;
					textureRect.Modulate = themeColor;
					AddChild(textureRect, forceReadableName: false, InternalMode.Disabled);
					list.Add(new Item
					{
						control = textureRect,
						isRedactable = false
					});
				}
				else
				{
					Label label = new Label();
					label.Text = word.text;
					label.MouseFilter = MouseFilterEnum.Ignore;
					if (word.isBold || defaultBold)
					{
						label.AddThemeFontOverride("font", boldFont);
					}
					else if (word.isItalic)
					{
						label.AddThemeFontOverride("font", italicFont);
					}
					label.Modulate = new Color(1f, 1f, 1f, 0f);
					AddChild(label, forceReadableName: false, InternalMode.Disabled);
					list.Add(new Item
					{
						control = label,
						originalText = word.text,
						isRedactable = (contentIsRedactable && word.isItalic)
					});
				}
			}
			paragraphs.Add(new Paragraph
			{
				items = list
			});
		}
	}

	public override void _Ready()
	{
		AddToGroup("card_text_contents");
	}

	private void LayoutControlsLines()
	{
		float num = paragraphIndent;
		float num2 = topMargin;
		float num3 = (isSingleLine ? float.MaxValue : base.Size.X);
		layoutMaxLineWidth = 0f;
		layoutLines = 0;
		totalWordCountSoFarAtEndOfEachLine.Clear();
		int num4 = 0;
		foreach (Paragraph paragraph in paragraphs)
		{
			Control control = CreateNewLineContainer(num2);
			foreach (Item item in paragraph.items)
			{
				if (item.isSpace)
				{
					num += 10f;
					continue;
				}
				float x = item.control.Size.X;
				if (num + x > num3)
				{
					totalWordCountSoFarAtEndOfEachLine.Add(num4);
					num = 0f;
					num2 += scaledLineHeight;
					layoutLines++;
					control = CreateNewLineContainer(num2);
				}
				bool flag = item.control is Button;
				item.control.Position = new Vector2(num, flag ? buttonYOffset : 0f);
				RemoveChild(item.control);
				control.AddChild(item.control, forceReadableName: false, InternalMode.Disabled);
				num += x;
				layoutMaxLineWidth = Mathf.Max(layoutMaxLineWidth, num);
				num4++;
			}
			num = paragraphIndent;
			num2 += scaledLineHeight;
			layoutLines++;
			totalWordCountSoFarAtEndOfEachLine.Add(num4);
		}
		RefreshMinimumSize(immediate: true);
	}

	private void RefreshMinimumSize(bool immediate)
	{
		Vector2 vector;
		if (isSingleLine)
		{
			vector = new Vector2(layoutMaxLineWidth, scaledLineHeight + bottomMargin);
		}
		else
		{
			int num = layoutLines;
			if (lineLimit > 0 && num > lineLimit)
			{
				num = lineLimit;
			}
			vector = new Vector2(layoutMaxLineWidth, (float)num * scaledLineHeight + bottomMargin);
		}
		if (immediate)
		{
			base.CustomMinimumSize = vector;
		}
		else
		{
			CreateTween().TweenProperty(this, "custom_minimum_size", vector, 0.20000000298023224);
		}
	}

	private Control CreateNewLineContainer(float y)
	{
		float x = base.Size.X;
		Control control = new Control();
		control.MouseFilter = MouseFilterEnum.Ignore;
		control.Position = new Vector2(0f, y);
		control.Size = new Vector2(x, scaledLineHeight);
		control.PivotOffset = new Vector2(x / 2f, scaledLineHeight / 2f);
		AddChild(control, forceReadableName: false, InternalMode.Disabled);
		lineContainers.Add(control);
		return control;
	}

	public void SetLineLimitAnimated(int lineLimit)
	{
		this.lineLimit = lineLimit;
		RefreshMinimumSize(immediate: false);
		SetWordsVisibility_Internal(wordsShown, animated: true, 0f, grabFocusOnFirstButton: false);
	}

	public bool ShowWords(bool animated, float delay = 0f, bool grabFocusOnFirstButton = false)
	{
		if (wordsShown)
		{
			return false;
		}
		wordsShown = true;
		return SetWordsVisibility_Internal(visible: true, animated, delay, grabFocusOnFirstButton);
	}

	public void HideWords(bool animated, float delay = 0f)
	{
		if (wordsShown)
		{
			wordsShown = false;
			SetWordsVisibility_Internal(visible: false, animated, delay, grabFocusOnFirstButton: false);
		}
	}

	private bool SetWordsVisibility_Internal(bool visible, bool animated, float delay, bool grabFocusOnFirstButton)
	{
		if (wordsAnimTween != null)
		{
			wordsAnimTween.Kill();
			wordsAnimTween = null;
		}
		int num = int.MaxValue;
		if (visible && lineLimit > 0 && lineLimit <= totalWordCountSoFarAtEndOfEachLine.Count)
		{
			num = totalWordCountSoFarAtEndOfEachLine[lineLimit - 1];
		}
		bool flag = false;
		int num2 = 0;
		foreach (Paragraph paragraph in paragraphs)
		{
			foreach (Item item in paragraph.items)
			{
				if (item.control == null)
				{
					continue;
				}
				float num3 = (visible ? 1f : 0f);
				if (visible && num2 >= num)
				{
					num3 = 0f;
				}
				bool flag2 = item.control.Modulate.A == num3;
				float num4 = delay;
				if (!animated)
				{
					item.control.Modulate = new Color(1f, 1f, 1f, num3);
				}
				else
				{
					float num5 = delay;
					if (!visible)
					{
						float num6 = (float)GD.RandRange(0.0, 0.30000001192092896);
						num5 += num6;
					}
					if (!flag2)
					{
						if (wordsAnimTween == null)
						{
							wordsAnimTween = CreateTween().SetParallel();
						}
						wordsAnimTween.TweenProperty(item.control, "modulate:a", num3, 0.30000001192092896).SetDelay(num5);
						wordsAnimTween.TweenCallback(Callable.From(delegate
						{
							if (item.control is LinkButton)
							{
								EmitSignal(SignalName.LinkButtonAppeared, item.control as LinkButton);
							}
						})).SetDelay(num5 + 0.15f);
						if (visible)
						{
							delay += 0.15f * ((float)GD.RandRange(0, 3) * 0.5f);
						}
					}
				}
				if (!flag & grabFocusOnFirstButton)
				{
					Control control = item.control;
					Button button = control as Button;
					if (button != null && StoryController.instance.canLinkButtonGrabFocus)
					{
						flag = true;
						if ((!animated | flag2) || wordsAnimTween == null)
						{
							button.GrabFocus();
						}
						else
						{
							wordsAnimTween.TweenCallback(Callable.From(delegate
							{
								if (button.IsVisibleInTree() && StoryController.instance.canLinkButtonGrabFocus)
								{
									button.GrabFocus();
								}
							})).SetDelay(num4 + 0.1f);
						}
					}
				}
				num2++;
			}
		}
		return flag;
	}

	public IEnumerable<Control> AllButtonEnumerator()
	{
		foreach (Paragraph paragraph in paragraphs)
		{
			foreach (Item item in paragraph.items)
			{
				if (item.control is Button button)
				{
					yield return button;
				}
			}
		}
	}

	public void Clear()
	{
		foreach (Control lineContainer in lineContainers)
		{
			lineContainer.QueueFree();
		}
		paragraphs.Clear();
		lineContainers.Clear();
		totalWordCountSoFarAtEndOfEachLine.Clear();
		wordsShown = false;
		fuzzSessionCounter++;
		lineLimit = -1;
	}

	public async void Fuzz(float coherence, bool coherenceIsCriticallyLow, bool redacted, bool immediate)
	{
		fuzzSessionCounter++;
		int thisFuzzSession = fuzzSessionCounter;
		if (paragraphs.Count == 0)
		{
			await ToSignal(GetTree(), "process_frame");
		}
		List<Item> list = new List<Item>();
		List<Item> list2 = new List<Item>();
		foreach (Paragraph paragraph in paragraphs)
		{
			foreach (Item item2 in paragraph.items)
			{
				if (item2.control is Label)
				{
					list.Add(item2);
				}
				else if (item2.control is Button)
				{
					list2.Add(item2);
				}
			}
		}
		foreach (Item item3 in list2)
		{
			LinkButton linkButton = (LinkButton)item3.control;
			if (item3.isRedactable & redacted)
			{
				linkButton.Visible = false;
				linkButton.Disabled = true;
			}
			else
			{
				linkButton.Visible = true;
				linkButton.RefreshState();
			}
		}
		if (!immediate)
		{
			for (int num = list.Count - 1; num > 0; num--)
			{
				int index = GD.RandRange(0, num);
				Item value = list[num];
				list[num] = list[index];
				list[index] = value;
			}
		}
		foreach (Item item in list)
		{
			int singleWordFuzzCount = 1;
			if (GD.RandRange(0, 100) < 10)
			{
				singleWordFuzzCount = GD.RandRange(4, 10);
			}
			Label label = item.control as Label;
			for (int i = 0; i < singleWordFuzzCount; i++)
			{
				float coherence2 = coherence;
				bool coherenceIsCriticallyLow2 = coherenceIsCriticallyLow;
				if (item.isRedactable & redacted)
				{
					coherence2 = 0.3f;
					coherenceIsCriticallyLow2 = true;
				}
				label.Text = FuzzText(item.originalText, coherence2, coherenceIsCriticallyLow2);
				if (!immediate)
				{
					await ToSignal(GetTree().CreateTimer(0.009999999776482582), "timeout");
					if (thisFuzzSession != fuzzSessionCounter)
					{
						return;
					}
				}
			}
		}
	}

	public static string FuzzText(string text, float coherence, bool coherenceIsCriticallyLow, int seed = 0)
	{
		if (text == null || text.Length == 0)
		{
			return text;
		}
		if (coherence >= 1f)
		{
			return text;
		}
		char[] array = text.ToCharArray();
		int num = 0;
		bool flag = false;
		bool flag2 = false;
		Random random = ((seed != 0) ? new Random(seed) : new Random());
		for (int i = 0; i < array.Length; i++)
		{
			char c = array[i];
			if (char.IsHighSurrogate(c) || char.IsLowSurrogate(c))
			{
				continue;
			}
			if (i + 2 < array.Length && num > 0 && c == 'u' && array[i + 1] == 'r' && array[i + 2] == 'l')
			{
				flag2 = !flag2;
			}
			flag = (flag ? (c != '"' && c != '"') : (c == '"' || c == '"'));
			bool flag3 = !flag2 && !flag && (float)random.NextDouble() > coherence;
			if (c == '[')
			{
				num++;
			}
			else if (num > 0 && c == ']')
			{
				num--;
			}
			else
			{
				if (!((num == 0) & flag3))
				{
					continue;
				}
				if (!flag && char.IsPunctuation(c))
				{
					string text2 = "!\"#$%&'*+,-./:;<=>?@\\^_`{|}~";
					array[i] = text2[random.Next(text2.Length)];
				}
				else
				{
					if (c == '\n')
					{
						continue;
					}
					if (coherenceIsCriticallyLow && (float)random.NextDouble() > coherence)
					{
						array[i] = ' ';
					}
					else if (char.IsLetter(c))
					{
						if (char.IsUpper(c))
						{
							array[i] = (char)(65 + random.Next(26));
						}
						else
						{
							array[i] = (char)(97 + random.Next(26));
						}
					}
					else if (char.IsDigit(c))
					{
						array[i] = (char)(48 + random.Next(10));
					}
				}
			}
		}
		return new string(array);
	}
}
