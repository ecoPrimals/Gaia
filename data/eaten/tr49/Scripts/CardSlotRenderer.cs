using System.Collections.Generic;
using Godot;

public partial class CardSlotRenderer : Node
{
	[Signal]
	public delegate void SlotsRenderedEventHandler();

	private struct TestCardContent
	{
		public string title;

		public string writer;

		public string date;

		public string label;

		public string[] content;
	}

	public List<Texture2D> textures = new List<Texture2D>();

	[Export(PropertyHint.None, "")]
	private PackedScene cardPackedScene;

	[Export(PropertyHint.None, "")]
	private int renderResolution = 512;

	[Export(PropertyHint.None, "")]
	private int contentSize = 1024;

	private List<TestCardContent> testCardContents = new List<TestCardContent>
	{
		new TestCardContent
		{
			title = "AJ-26",
			writer = "Alice",
			date = "--1974",
			label = "Hardcover book. 256pp",
			content = new string[5] { "(%AJ26%), from 1926. Notable articles include:", "- an account of the destruction of Professor [b]Quentin[/b] [b]Lemarchant[/b]’s 1918 work by an editor with links to the [b]Church[/b] [b]of[/b] [b]the[/b] [b]Rampaging[/b] [b]Christ[/b]. See (CR89) - but have a stiff drink to hand!", "- a brief mention of (%QL18%) ‘s deathbed publication.", "[color=#FFE473](IM46)[/color] [color=#FFE473]is[/color] [color=#FFE473]associated[/color]", "[color=#FFE473]with[/color] [color=#FFE473]this[/color] [color=#FFE473]entry.[/color]" }
		},
		new TestCardContent
		{
			title = "BJ-69",
			writer = "Cecil",
			date = "--1974",
			label = "Hardcover book. 256pp",
			content = new string[5] { "(%AJ26%), from 1926. Notable articles include:", "- an account of the destruction of Professor [b]Quentin[/b] [b]Lemarchant[/b]’s 1918 work by an editor with links to the [b]Church[/b] [b]of[/b] [b]the[/b] [b]Rampaging[/b] [b]Christ[/b]. See (CR89) - but have a stiff drink to hand!", "- a brief mention of (%QL18%) ‘s deathbed publication.", "[color=#FFE473](IM46)[/color] [color=#FFE473]is[/color] [color=#FFE473]associated[/color]", "[color=#FFE473]with[/color] [color=#FFE473]this[/color] [color=#FFE473]entry.[/color]" }
		},
		new TestCardContent
		{
			title = "TR-49",
			writer = "Machine",
			date = "--1974",
			label = "Hardcover book. 256pp",
			content = new string[5] { "(%AJ26%), from 1926. Notable articles include:", "- an account of the destruction of Professor [b]Quentin[/b] [b]Lemarchant[/b]’s 1918 work by an editor with links to the [b]Church[/b] [b]of[/b] [b]the[/b] [b]Rampaging[/b] [b]Christ[/b]. See (CR89) - but have a stiff drink to hand!", "- a brief mention of (%QL18%) ‘s deathbed publication.", "[color=#FFE473](IM46)[/color] [color=#FFE473]is[/color] [color=#FFE473]associated[/color]", "[color=#FFE473]with[/color] [color=#FFE473]this[/color] [color=#FFE473]entry.[/color]" }
		}
	};

	public override async void _Ready()
	{
		List<SubViewport> viewports = new List<SubViewport>();
		for (int i = 0; i < testCardContents.Count; i++)
		{
			TestCardContent testCardContent = testCardContents[i];
			SubViewport subViewport = new SubViewport();
			subViewport.Size = new Vector2I(renderResolution, renderResolution);
			subViewport.Size2DOverride = new Vector2I(contentSize, contentSize);
			subViewport.Size2DOverrideStretch = true;
			subViewport.RenderTargetUpdateMode = SubViewport.UpdateMode.Once;
			subViewport.RenderTargetClearMode = SubViewport.ClearMode.Always;
			subViewport.TransparentBg = true;
			AddChild(subViewport, forceReadableName: false, InternalMode.Disabled);
			CardView cardView = cardPackedScene.Instantiate<CardView>(PackedScene.GenEditState.Disabled);
			subViewport.AddChild(cardView, forceReadableName: false, InternalMode.Disabled);
			cardView.Clear();
			viewports.Add(subViewport);
			cardView.StartSection("header");
			cardView.Append("title", testCardContent.title);
			cardView.StartRow();
			cardView.Append("Softback");
			cardView.Append("Joe's awesome book");
			cardView.Append("2005");
			cardView.EndRow();
			cardView.EndSection();
			cardView.StartSection("alice");
			string[] content = testCardContent.content;
			foreach (string text in content)
			{
				cardView.Append(text);
			}
			cardView.EndSection();
			cardView.StartSection("footer");
			cardView.StartRow();
			cardView.Append("Card made in 2025");
			cardView.Append("By Joe");
			cardView.EndRow();
			cardView.Finalise("JO33", allowTitleLinks: true, 1f, coherenceIsCriticallyLow: false, redacted: true, immediate: true);
		}
		await ToSignal(RenderingServer.Singleton, RenderingServerInstance.SignalName.FramePostDraw);
		for (int k = 0; k < viewports.Count; k++)
		{
			SubViewport subViewport2 = viewports[k];
			Image image = subViewport2.GetTexture().GetImage();
			ImageTexture imageTexture = new ImageTexture();
			imageTexture.SetImage(image);
			textures.Add(imageTexture);
			subViewport2.QueueFree();
		}
		EmitSignal(SignalName.SlotsRendered);
	}
}
