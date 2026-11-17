using System.Collections.Generic;
using Godot;

public partial class Credits : Control, IGlobalBackButtonHandler
{
	[Signal]
	public delegate void DidCompleteEventHandler();

	[Signal]
	public delegate void DidHideEventHandler();

	[Export(PropertyHint.None, "")]
	private float initialDelay = 1f;

	[Export(PropertyHint.None, "")]
	private float fadeInDuration = 4f;

	[Export(PropertyHint.None, "")]
	private float fadeInDurationGameMenu = 1f;

	[Export(PropertyHint.None, "")]
	private float fadeOutDuration = 1f;

	[Export(PropertyHint.None, "")]
	private float scrollSpeed = 50f;

	[Export(PropertyHint.None, "")]
	private CreditsLabel title;

	[Export(PropertyHint.None, "")]
	private CreditsLabel subtitleLine1;

	[Export(PropertyHint.None, "")]
	private CreditsLabel subtitleLine2;

	[Export(PropertyHint.None, "")]
	private Control scrollingContents;

	[Export(PropertyHint.None, "")]
	private PackedScene scrollingCreditTitleScene;

	[Export(PropertyHint.None, "")]
	private PackedScene actorCreditScene;

	[Export(PropertyHint.None, "")]
	private PackedScene simpleCreditScene;

	[Export(PropertyHint.None, "")]
	private BackgroundMusicPlayer backgroundMusicPlayer;

	[Export(PropertyHint.None, "")]
	private float frequencyOfFuzzing = 0.05f;

	[Export(PropertyHint.None, "")]
	private float probabilityOfFuzzVsFix = 0.2f;

	[Export(PropertyHint.None, "")]
	private float actorFuzzStrength = 0.3f;

	[Export(PropertyHint.None, "")]
	private float screenEdgeCharacterHideMargin = 100f;

	public static Credits instance;

	private Tween showHideTween;

	private Tween sequencerTween;

	private Tween completeTween;

	private List<CreditsLabel> scrollingCreditsLabels = new List<CreditsLabel>();

	private bool hasCalledComplete;

	public ShowCreditsContext context { get; private set; }

	private bool scrollIsComplete => scrollingContents.Position.Y <= 0f - scrollingContents.Size.Y;

	public override void _EnterTree()
	{
		instance = this;
	}

	public override void _Ready()
	{
		base.Visible = false;
		base.Modulate = new Color(1f, 1f, 1f, 0f);
		scrollingContents.Visible = false;
		if (base.Owner == null)
		{
			base.Modulate = new Color(1f, 1f, 1f);
			ShowCredits(ShowCreditsContext.Test);
		}
	}

	public override void _Input(InputEvent @event)
	{
		if (!base.Visible)
		{
			return;
		}
		AlertView alertView = AlertView.instance;
		if (alertView == null || !alertView.Visible)
		{
			if (@event.IsActionPressed("ui_cancel") && !hasCalledComplete)
			{
				Complete();
			}
			if (!(@event is InputEventMouseButton))
			{
				this.SetInputAsHandled(@event);
			}
		}
	}

	public void Complete()
	{
		backgroundMusicPlayer.StopCreditsMusic();
		AmbientAudio.instance.rampDownForCredits = false;
		if (!hasCalledComplete)
		{
			hasCalledComplete = true;
			if (sequencerTween != null)
			{
				sequencerTween.Kill();
				sequencerTween = null;
			}
			if (completeTween != null)
			{
				completeTween.Kill();
				completeTween = null;
			}
			completeTween = CreateTween().SetParallel();
			if (title.Visible)
			{
				completeTween.TweenProperty(title, "modulate:a", 0f, 0.20000000298023224);
			}
			if (subtitleLine1.Visible)
			{
				completeTween.TweenProperty(subtitleLine1, "modulate:a", 0f, 0.20000000298023224);
			}
			if (subtitleLine2.Visible)
			{
				completeTween.TweenProperty(subtitleLine2, "modulate:a", 0f, 0.20000000298023224);
			}
			if (scrollingContents.Visible && !scrollIsComplete)
			{
				completeTween.TweenProperty(scrollingContents, "modulate:a", 0f, 1.0);
			}
			completeTween.TweenInterval(0.10000000149011612);
			completeTween.Finished += delegate
			{
				completeTween = null;
				scrollingContents.Visible = false;
				EmitSignal(SignalName.DidComplete);
			};
		}
	}

	public void Clear()
	{
		base.Visible = false;
		if (GlobalBackButton.instance.HasPushed(this))
		{
			GlobalBackButton.instance.Pop(this);
		}
		foreach (Node child in scrollingContents.GetChildren())
		{
			child.QueueFree();
		}
		scrollingCreditsLabels.Clear();
		SetAlpha(scrollingContents, 1f);
		scrollingContents.Visible = false;
		SetAlpha(title, 1f);
		title.Visible = false;
		title.writeInProportion = 0f;
		SetAlpha(subtitleLine1, 1f);
		subtitleLine1.Visible = false;
		subtitleLine1.writeInProportion = 0f;
		SetAlpha(subtitleLine2, 1f);
		subtitleLine2.Visible = false;
		subtitleLine2.writeInProportion = 0f;
		if (showHideTween != null)
		{
			showHideTween.Kill();
			showHideTween = null;
		}
		if (sequencerTween != null)
		{
			sequencerTween.Kill();
			sequencerTween = null;
		}
		if (completeTween != null)
		{
			completeTween.Kill();
			completeTween = null;
		}
		backgroundMusicPlayer.StopCreditsMusic();
		AmbientAudio.instance.rampDownForCredits = false;
		hasCalledComplete = false;
	}

	public void HideCredits()
	{
		if (base.Visible)
		{
			if (GlobalBackButton.instance.HasPushed(this))
			{
				GlobalBackButton.instance.Pop(this);
			}
			if (showHideTween != null)
			{
				showHideTween.Kill();
				showHideTween = null;
			}
			showHideTween = CreateTween();
			showHideTween.TweenProperty(this, "modulate:a", 0f, fadeOutDuration);
			showHideTween.Finished += delegate
			{
				Clear();
				EmitSignal(SignalName.DidHide);
			};
		}
		else
		{
			Clear();
			EmitSignal(SignalName.DidHide);
		}
	}

	private void SetAlpha(Control control, float alpha)
	{
		Color modulate = control.Modulate;
		modulate.A = alpha;
		control.Modulate = modulate;
	}

	public void DebugShowCredits()
	{
		ShowCredits(ShowCreditsContext.Test);
	}

	public void ShowCredits(ShowCreditsContext context, bool truncatedToTitleOnly = false)
	{
		base.Visible = true;
		hasCalledComplete = false;
		this.context = context;
		if (context == ShowCreditsContext.EndOfGame || context == ShowCreditsContext.Test)
		{
			if (backgroundMusicPlayer != null)
			{
				backgroundMusicPlayer.PlayCreditsMusic();
			}
			if (AmbientAudio.instance != null)
			{
				AmbientAudio.instance.rampDownForCredits = true;
			}
		}
		Vector2 position = scrollingContents.Position;
		position.Y = scrollingContents.GetParent<Control>().Size.Y;
		scrollingContents.Position = position;
		SetAlpha(scrollingContents, 1f);
		scrollingContents.Visible = false;
		if (showHideTween != null)
		{
			showHideTween.Kill();
			showHideTween = null;
			sequencerTween.Kill();
			sequencerTween = null;
		}
		showHideTween = CreateTween();
		if (context == ShowCreditsContext.EndOfGame)
		{
			showHideTween.TweenInterval(initialDelay);
		}
		showHideTween.TweenProperty(this, "modulate:a", 1f, (context == ShowCreditsContext.EndOfGame) ? fadeInDuration : fadeInDurationGameMenu);
		showHideTween.Finished += delegate
		{
			showHideTween = null;
		};
		title.Visible = false;
		title.writeInProportion = 0f;
		SetAlpha(title, 1f);
		subtitleLine1.Visible = false;
		subtitleLine1.writeInProportion = 0f;
		SetAlpha(subtitleLine1, 1f);
		subtitleLine2.Visible = false;
		subtitleLine2.writeInProportion = 0f;
		SetAlpha(subtitleLine2, 1f);
		sequencerTween = CreateTween();
		if (context == ShowCreditsContext.EndOfGame)
		{
			sequencerTween.TweenInterval(4.0);
		}
		sequencerTween.TweenInterval(1.0);
		sequencerTween.TweenSubtween(CreateLabelWriteInTween(title, "TR-49"));
		sequencerTween.TweenInterval(1.0);
		if (truncatedToTitleOnly)
		{
			sequencerTween.TweenCallback(Callable.From(delegate
			{
				if (!hasCalledComplete)
				{
					Complete();
				}
			}));
			return;
		}
		foreach (var item in new List<(string, string)>
		{
			("an inkle game", null),
			("Written and directed by", "Jon Ingold"),
			("Development and graphic design", "Joseph Humfrey"),
			("Art", "Anastasia Wyatt"),
			("Music", "Laurence Chapman"),
			("Marketing and PR", "Emily Morganti")
		})
		{
			Tween tween = CreateTween().SetParallel();
			tween.TweenSubtween(CreateLabelWriteInTween(subtitleLine1, item.Item1)).SetDelay(0.20000000298023224);
			if (item.Item2 != null)
			{
				tween.TweenSubtween(CreateLabelWriteInTween(subtitleLine2, item.Item2)).SetDelay(1.0);
			}
			sequencerTween.TweenSubtween(tween);
			sequencerTween.TweenInterval(0.5);
		}
		AddScrollingCreditTitle("CAST");
		AddScrollingCreditSpacer(30f);
		List<(string, string)> obj = new List<(string, string)>
		{
			("Abbi", "Rebekah McLoughlin"),
			("Liam", "Paul Warren"),
			("The Soldier", "Phillipe Bosher"),
			("Aliz", "Rachel Raphaely Ingold"),
			("Beatrice", "Doctor Holly Nielsen"),
			("Cecil", "Jon Ingold")
		};
		new List<Control>();
		foreach (var item2 in obj)
		{
			AddScrollingActorCredit(item2.Item1, item2.Item2);
		}
		AddScrollingCreditSpacer(100f);
		AddScrollingCreditTitle("THE LIBRARY CHORUS");
		AddScrollingCreditSpacer(30f);
		foreach (string item3 in new List<string> { "Sally Beaumont", "Phillipe Bosher", "Phil Cheesman", "Nick Colston", "Tom Granger", "Joseph Humfrey", "Professor Tim Ingold", "Jon, Francesca, Leo & Rachel Raphaely Ingold", "Victor Ojuel", "Professor Hans Steinmüller" })
		{
			AddScrollingSimpleCredit(item3);
		}
		AddScrollingCreditSpacer(100f);
		AddScrollingCreditTitle("PLAYTESTING");
		AddScrollingCreditSpacer(30f);
		foreach (string item4 in new List<string>
		{
			"Ambrolen", "Brooke Abbey", "Jem Alexander", "Allan Anderson", "Nick Bush", "Phil Cheesman", "Joseph Dewar", "Andrey Dineev", "Sam Drysdale", "Zach Durtschi",
			"Adam Evans", "Diana Flindt", "Damiano Gerli", "Felix Grünewald", "Sean Hannan", "Sunder Iyer", "Steve Morton", "Ada Null", "Federico Odorizzi", "James Patton",
			"Deloria Patton", "Nikita Radostev", "Sonia Sulaiman", "Claudia Tröger", "Kevin Wickenden", "Stefan Winter", "Brandon Wolff"
		})
		{
			AddScrollingSimpleCredit(item4);
		}
		AddScrollingCreditSpacer(100f);
		AddScrollingSimpleCredit("Polyhedron logo adapted from");
		AddScrollingSimpleCredit("\"Perspectiva Corporum Regularium\", Wentzel Jamnitzer (1568)");
		AddScrollingSimpleCredit("via the Public Domain Image Archive");
		AddScrollingCreditSpacer(30f);
		AddScrollingCreditSpacer(100f);
		AddScrollingCreditTitle("ADDITIONAL WRITING");
		AddScrollingCreditSpacer(30f);
		List<string> list = ((!Platform.isSwitch) ? new List<string>
		{
			"@eyeznteef.com (ET16)", "@sallybeaumont.bsky.social (SB45)", "@thetickms.bsky.social (TM33)", "@ranja72.bsky.social (RJ72)", "@lyndac.bsky.social (LD98)", "@n0seblunt.bsky.social (NB16)", "@thislop.bsky.social (TH50)", "@papayachemist.bsky.social (PC82)", "@magsthepirate.bsky.social (MP38)", "@berlineditorgal.bsky.social (EM87)",
			"@tximista.bsky.social (JD68)", "@dubsington.bsky.social (DT97)", "@pacodiago.bsky.social (PD13)", "@sahilbajaj.dev (SB21)", "@ptrtlrwrts.bsky.social (PT08)", "@vividfax.bsky.social (VF11)", "@matronboy.bsky.social (MB14)", "@potatocubed.bsky.social (PC22)", "@eblong.com (AP04)", "@leighloveday.bsky.social (LL14)",
			"@cliftonb.bsky.social (CB01)", "@cerandor.com (CM06)", "@ramiismail.com (RI17)", "@stephanebura.com (SB13)", "@jigu.com.br (PG09)", "@nattgoo.bsky.social (NG08)", "@sc.mt (SC11)", "@kittydorkling.bsky.social (KD38)", "@scrivscriv.bsky.social (SS50)", "@brendanmcleod.com (BM30)",
			"@finnjc.bsky.social (FC36)", "@gstrachan.bsky.social (GS32)", "@zusty.bsky.social (KZ36)", "@mikediamond.bsky.social (MD35)", "@vinicius-marino.bsky.social (VM40)", "@letominor.bsky.social (LM40)", "@qixotl.bsky.social (CP37)", "@jamespatton.bsky.social (JP26)", "@benjymous.bsky.social (RB35)", "@positivelaser.bsky.social (PL46)",
			"@shadesogrey.bsky.social (SG47)", "@christikerr.bsky.social (CK27)", "@inepthope.bsky.social (IH26)", "@herecomestroble.bsky.social (TR26)", "@isakcoffee.bsky.social (IC74)", "@lionhartjulian.bsky.social (LJ52)", "@twinkle-shine.bsky.social (TS72)", "@funambulism.com (DG55)", "@pseudavid.bsky.social (PD61)", "@stmilo.bsky.social (SM66)",
			"@infininoodle.bsky.social (IN62)", "@jfg.land (JG65)", "@nick.aetheric-games.com (NB68)", "@kithara.bsky.social (CK72)", "@krisrf.bsky.social (KF72)", "@sarahsunfire.bsky.social (SS54)", "@coil.bsky.social (DJ65)", "@hedgefield.bsky.social (HF75)", "@tanatb.housefuckinggame.com (TB53)", "@abdoubouam.bsky.social (AB72)",
			"@hthrflwrs.bsky.social (HF56)", "@writingstudio.bsky.social (DV75)", "@berlineditorgal.bsky.social (MM67)", "@amityblamity.bsky.social (AB57)", "@comradechloe.bsky.social (CH65)", "@jawalker.bsky.social (JW80)", "@iachbodb.bsky.social (IB80)", "@thepoetofcuisine.bsky.social (PC78)", "@adamburt.com (AB82)", "@ericnewsom.bsky.social (EN85)",
			"@damonreece.com (DR79)", "@lmicharlie.bsky.social (CB83)", "@depressionwizard.bsky.social (DW80)", "@astrobolism.bsky.social (CW85)", "@johnayliff.bsky.social (JA06)", "@jaxyacks.bsky.social (JY83)", "@rettisawesome.com (RA77)", "@acampwriting.com (AC82)", "@v21.bsky.social (VB78)", "@pvbuk.bsky.social (SM78)",
			"@rebeccamwrites.bsky.social (RM76)", "@danielvella.bsky.social (DV80)", "@natahq.bsky.social (NP79)", "@alanau.bsky.social (AU81)"
		} : new List<string>
		{
			"Mani (ET16)", "Sally Beaumont (SB45)", "thetickms (TM33)", "Arjan Terpstra (RJ72)", "Lynda Clark (LD98)", "Alex (NB16)", "Thomas Hislop (TH50)", "papayachemist (PC82)", "Mags D. (MP38)", "berlineditorgal (EM87)",
			"Jill (JD68)", "Dubs (DT97)", "Paco Diago (PD13)", "Sahil Bajaj (SB21)", "Peter Taylor (PT08)", "Rianna (VF11)", "Jamie Brittain (MB14)", "Chris Longhurst (PC22)", "Andrew Plotkin (AP04)", "Leigh Loveday (LL14)",
			"Clifton B (CB01)", "Ciaran McGrath (CM06)", "Rami Ismail (RI17)", "Stephane Bura (SB13)", "Pedro Giglio (PG09)", "Nataliya Gorbina (NG08)", "Simon Cutajar (SC11)", "Kitty Dorkling (KD38)", "scrivscriv (SS50)", "Brendan Mordheim (BM30)",
			"Finn Carney (FC36)", "Graeme Strachan (GS32)", "Karla (KZ36)", "Mike Diamond (MD35)", "Vinicius Marino Carvalho (VM40)", "Andrei Filote (LM40)", "Chris Payne (CP37)", "James Patton (JP26)", "Richard (RB35)", "Dave Proctor (PL46)",
			"Anne Stickney (SG47)", "Christi Kerr (CK27)", "inepthope (IH26)", "Thomas Robinson (TR26)", "coffee (IC74)", "lionhartjulian (LJ52)", "twinkle-shine (TS72)", "gril (DG55)", "pseudavid (PD61)", "Milo Minderbinder (SM66)",
			"infininoodle (IN62)", "Jason Grinblat (JG65)", "nickbell (NB68)", "kithara (CK72)", "Kris (KF72)", "Sarah Sunfire (SS54)", "Dan Johnson (DJ65)", "Tim Hengeveld (HF75)", "Tanat Boozayaangool (TB53)", "Abdou Bouam (AB72)",
			"Heather Flowers (HF56)", "David Varela (DV75)", "Berlin Editor Gal (MM67)", "Amity G. (AB57)", "Chlo (CH65)", "jawalker (JW80)", "Bodb (IB80)", "thepoetofcuisine (PC78)", "Adam Burt (AB82)", "ericnewsom (EN85)",
			"Damon (DR79)", "Charlie Ball (CB83)", "depressionwizard (DW80)", "Caleb Wilson (CW85)", "johnayliff (JA06)", "Jackie aka Jax (JY83)", "Rett (RA77)", "Alice Camp (AC82)", "V Buckenham (VB78)", "Steve Morton (SM78)",
			"Rebecca McCarthy (RM76)", "Daniel Vella (DV80)", "Nata Pokrovskaya (NP79)", "Alan Au (AU81)"
		});
		foreach (string item5 in list)
		{
			int num = item5.IndexOf("(");
			if (num < 0)
			{
				GD.Print("No ( found in " + item5);
			}
			string code = item5.Substring(num + 1, 4);
			AddScrollingSimpleCredit(string.Concat(str2: (StoryController.instance == null) ? StoryController.HyphenateCode(code) : StoryController.instance.VerifyAdditionalWritingLink(code), str0: item5.Substr(0, num - 1), str1: " (", str3: ")"));
		}
		AddScrollingCreditSpacer(30f);
		AddScrollingCreditTitle("WITH");
		AddScrollingCreditSpacer(30f);
		foreach (string item6 in new List<string>
		{
			"Victor Hugo (VH-31)", "James Joyce (JJ-20)", "Raymond Chandler (RC-39)", "Joseph Conrad (JC-99)", "Graham Greene (GG-55)", "William Golding (WG-54)", "Joseph Heller (JH-61)", "J.R.R. Tolkien (JT-54)", "Herman Melville (HM-51)", "F. Scott Fitzgerald (FF-25)",
			"Mary Shelley (MS-18)", "Oscar Wilde (OW-90)", "Jack London (JL-03)", "George Orwell (GO-49)", "Emily Brontë (EB-47)", "Bram Stoker (BS-97)", "John Steinbeck (JS-39)", "Fyodor Dostoevsky (FD-66)", "Nathaniel Hawthorne (NH-50)", "Franz Kafka (FK-15)",
			"J.D. Salinger (JS-51)", "Leo Tolstoy (LT-78)", "Charlotte Brontë (CB-47)", "Charles Dickens (CD-61)", "Thomas Hardy (TH-91)", "H.G. Wells (HW-98)", "Arthur Conan Doyle (AD-02)", "George Eliot (GE-71)", "Agatha Christie (AC-20)", "P.G. Wodehouse(PW-34)",
			"Lewis Carroll (LC-65)", "Alfred Lord Tennyson (AT-35, AT-59)", "Robert Louis Stevenson (RS-83)", "Alexander Dumas (AD-45)", "Antoine Galland (AG-04)", "God (GA-00)", "and", "Jane Austen (JA-13)"
		})
		{
			AddScrollingSimpleCredit(item6);
		}
		AddScrollingCreditSpacer(100f);
		AddScrollingCreditTitle("Written in INK");
		AddScrollingCreditSpacer(30f);
		if (!Platform.isSwitch)
		{
			AddScrollingCreditSpacer(100f);
			AddScrollingSimpleCredit("For more games by inkle visit");
			AddScrollingCreditSpacer(30f);
			AddScrollingCreditTitle("inklestudios.com");
		}
		sequencerTween.TweenCallback(Callable.From(delegate
		{
			scrollingContents.Visible = true;
		}));
	}

	private void AddScrollingCreditTitle(string title)
	{
		Label label = scrollingCreditTitleScene.Instantiate<Label>(PackedScene.GenEditState.Disabled);
		label.Text = title;
		scrollingContents.AddChild(label, forceReadableName: false, InternalMode.Disabled);
	}

	private void AddScrollingCreditSpacer(float height)
	{
		Control control = new Control();
		control.Name = "Spacer";
		control.CustomMinimumSize = new Vector2(0f, height);
		scrollingContents.AddChild(control, forceReadableName: false, InternalMode.Disabled);
	}

	private void AddScrollingActorCredit(string characterName, string actorName)
	{
		Control control = actorCreditScene.Instantiate<Control>(PackedScene.GenEditState.Disabled);
		CreditsLabel node = control.GetNode<CreditsLabel>("CharacterName");
		CreditsLabel node2 = control.GetNode<CreditsLabel>("ActorName");
		node.text = characterName;
		node2.text = actorName;
		float x = node2.Position.X;
		float x2 = node._GetMinimumSize().X;
		node2._GetMinimumSize();
		node.Position = new Vector2(0f - x - x2, node.Position.Y);
		scrollingCreditsLabels.Add(node);
		scrollingCreditsLabels.Add(node2);
		scrollingContents.AddChild(control, forceReadableName: false, InternalMode.Disabled);
	}

	private void AddScrollingSimpleCredit(string credit)
	{
		CreditsLabel creditsLabel = simpleCreditScene.Instantiate<CreditsLabel>(PackedScene.GenEditState.Disabled);
		creditsLabel.text = credit;
		scrollingCreditsLabels.Add(creditsLabel);
		scrollingContents.AddChild(creditsLabel, forceReadableName: false, InternalMode.Disabled);
	}

	private Tween CreateLabelWriteInTween(CreditsLabel label, string text)
	{
		return CreateLabelWriteInTween(this, label, text);
	}

	public static Tween CreateLabelWriteInTween(Node node, CreditsLabel label, string text, float pauseWhileVisibleDuration = 0.6f)
	{
		Tween tween = node.CreateTween();
		tween.TweenCallback(Callable.From(delegate
		{
			label.Visible = true;
			if (text != null)
			{
				label.text = text;
				Vector2 vector = label._GetMinimumSize();
				float x = label.GetParent<Control>().Size.X;
				label.Position = new Vector2(0.5f * x - 0.5f * vector.X, label.Position.Y);
			}
			label.writeInProportion = 0f;
			label.fuzzStrength = 0f;
			label.randomVisibleProportion = 1f;
		}));
		float num = ((text == "TR-49") ? 1f : 0.05f);
		float num2 = 1f;
		float num3 = (float)text.Length * num;
		if (num2 > num3)
		{
			num2 = num3;
		}
		tween.TweenProperty(label, "writeInProportion", 1f, num2);
		tween.TweenInterval(pauseWhileVisibleDuration);
		tween.TweenCallback(Callable.From(delegate
		{
			label.PlayDeconstructSFX();
		}));
		for (int num4 = 0; num4 < 6; num4++)
		{
			float fuzzStrength = (float)num4 * 0.2f;
			tween.TweenCallback(Callable.From(delegate
			{
				label.fuzzStrength = fuzzStrength;
			})).SetDelay(0.1666666716337204);
		}
		for (int num5 = 0; num5 < 6; num5++)
		{
			float visibilityProportion = (float)num5 * 0.2f;
			tween.TweenCallback(Callable.From(delegate
			{
				label.randomVisibleProportion = 1f - visibilityProportion;
			})).SetDelay(0.1666666716337204);
		}
		tween.TweenCallback(Callable.From(delegate
		{
			label.Visible = false;
		}));
		return tween;
	}

	public override void _Process(double delta)
	{
		if (base.Visible && scrollingContents.Visible)
		{
			Vector2 position = scrollingContents.Position;
			position.Y -= (float)delta * scrollSpeed;
			scrollingContents.Position = position;
			foreach (CreditsLabel scrollingCreditsLabel in scrollingCreditsLabels)
			{
				if (GD.RandRange(0.0, 1.0) < (double)frequencyOfFuzzing)
				{
					if (GD.RandRange(0.0, 1.0) < (double)probabilityOfFuzzVsFix)
					{
						scrollingCreditsLabel.fuzzStrength = (float)GD.RandRange(0.0, actorFuzzStrength);
					}
					else
					{
						scrollingCreditsLabel.fuzzStrength = 0f;
					}
				}
			}
			float y = GetViewport().GetVisibleRect().Size.Y;
			foreach (CreditsLabel scrollingCreditsLabel2 in scrollingCreditsLabels)
			{
				float y2 = scrollingCreditsLabel2.GetGlobalPosition().Y;
				float a = Mathf.Clamp(y2 / screenEdgeCharacterHideMargin, 0f, 1f);
				float b = Mathf.Clamp((y - y2) / screenEdgeCharacterHideMargin, 0f, 1f);
				float randomVisibleProportion = Mathf.Min(a, b);
				scrollingCreditsLabel2.randomVisibleProportion = randomVisibleProportion;
			}
			if (!hasCalledComplete && scrollIsComplete)
			{
				Complete();
			}
		}
		if (base.Visible && GlobalBackButton.instance != null && !GlobalBackButton.instance.HasPushed(this) && (context == ShowCreditsContext.GameMenu || (context == ShowCreditsContext.EndOfGame && scrollingContents.Visible) || (context == ShowCreditsContext.Test && scrollingContents.Visible)))
		{
			GlobalBackButton.instance.Push(this);
		}
	}

	public void OnGlobalBackButtonPressed()
	{
		GD.Print($"OnGlobalBackButtonPressed: {context}");
		HideCredits();
	}
}
