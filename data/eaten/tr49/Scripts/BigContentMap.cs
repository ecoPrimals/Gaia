using System;
using Godot;

public partial class BigContentMap : Control
{
	[Signal]
	public delegate void SlotsReadyEventHandler();

	private class CardSlot
	{
		public TextureRect placeholderTextureRect;

		public CardView cardView;
	}

	[Export(PropertyHint.None, "")]
	public CardView cardView1;

	[Export(PropertyHint.None, "")]
	public CardView cardView2;

	[Export(PropertyHint.None, "")]
	public CardSlotRenderer cardSlotRenderer;

	[Export(PropertyHint.None, "")]
	public int xSlots = 25;

	[Export(PropertyHint.None, "")]
	public int ySlots = 25;

	private CardSlot[,] cardSlots;

	private Control cardSlotContainer;

	private CardSlot card1Slot;

	private CardSlot card2Slot;

	private const int slotSize = 1024;

	public override async void _Ready()
	{
		await ToSignal(cardSlotRenderer, CardSlotRenderer.SignalName.SlotsRendered);
		cardSlotContainer = new Control();
		cardSlotContainer.Name = "CardSlotContainer";
		cardSlotContainer.Size = new Vector2(xSlots * 1024, ySlots * 1024);
		cardSlotContainer.MouseFilter = MouseFilterEnum.Ignore;
		cardSlotContainer.FocusMode = FocusModeEnum.None;
		AddChild(cardSlotContainer, forceReadableName: false, InternalMode.Disabled);
		base.Size = cardSlotContainer.Size;
		cardSlots = new CardSlot[xSlots, ySlots];
		for (int i = 0; i < xSlots; i++)
		{
			for (int j = 0; j < ySlots; j++)
			{
				CardSlot cardSlot = new CardSlot();
				int index = (i + j * xSlots) % cardSlotRenderer.textures.Count;
				cardSlot.placeholderTextureRect = new TextureRect();
				cardSlot.placeholderTextureRect.Texture = cardSlotRenderer.textures[index];
				cardSlot.placeholderTextureRect.ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize;
				cardSlot.placeholderTextureRect.StretchMode = TextureRect.StretchModeEnum.KeepAspectCentered;
				cardSlot.placeholderTextureRect.Position = new Vector2(i * 1024, j * 1024);
				cardSlot.placeholderTextureRect.Size = new Vector2(1024f, 1024f);
				cardSlotContainer.AddChild(cardSlot.placeholderTextureRect, forceReadableName: false, InternalMode.Disabled);
				cardSlots[i, j] = cardSlot;
			}
		}
		EmitSignal(SignalName.SlotsReady);
	}

	public void ResetSlotForCard(CardView cardView)
	{
		CardSlot cardSlot = ((cardView == cardView1) ? card1Slot : card2Slot);
		if (cardSlot != null && cardSlot.cardView != null)
		{
			if (cardSlot.cardView != cardView)
			{
				GD.PushError($"Expected card slot to contain {cardView.Name}, but it had {cardSlot.cardView.Name}");
			}
			cardSlot.cardView = null;
			cardSlot.placeholderTextureRect.Visible = true;
		}
	}

	public void ClearAllSlots()
	{
		CardSlot[,] array = cardSlots;
		foreach (CardSlot cardSlot in array)
		{
			if (cardSlot.cardView != null)
			{
				cardSlot.cardView = null;
				cardSlot.placeholderTextureRect.Visible = true;
			}
		}
	}

	public Vector2I SlotForCode(string str)
	{
		new Vector2I(GD.RandRange(0, xSlots - 1), GD.RandRange(0, ySlots - 1));
		if (string.IsNullOrWhiteSpace(str))
		{
			str = "NU11";
		}
		string text = StoryController.DepunctuateCode(str);
		if (text.Length != 4 || !char.IsLetter(text[0]) || !char.IsLetter(text[1]) || !char.IsDigit(text[2]) || !char.IsDigit(text[3]))
		{
			text = "NU11";
		}
		string text2 = text.Substring(0, 2);
		int num = int.Parse(text.Substring(2, 2));
		int num2 = Array.IndexOf(new string[13]
		{
			"CC11", "BE47", "AL12", "AB81", "NU11", "TR49", "HO77", "XX00", "LA57", "ED17",
			"WI93", "MA43", "HE47"
		}, text);
		if (num2 != -1)
		{
			return new Vector2I(20, num2 % ySlots);
		}
		int num3 = Array.IndexOf(new string[11]
		{
			"MA23", "EX17", "PA74", "NT41", "AK37", "RO40", "PA55", "LO57", "DI43", "TR19",
			"HE19"
		}, text);
		if (num3 != -1)
		{
			return new Vector2I(num3, 22 % ySlots);
		}
		int num4 = Mathf.FloorToInt(num / 5) % xSlots;
		int y = (text2[0] - 65 + (text2[1] - 65) / 4) % ySlots;
		if (num4 >= 20)
		{
			num4 = (num4 + 1) % xSlots;
		}
		return new Vector2I(num4, y);
	}

	public void PlaceCardInSlotXY(CardView cardView, Vector2I slotXY)
	{
		if (slotXY.X < 0 || slotXY.X >= xSlots || slotXY.Y < 0 || slotXY.Y >= ySlots)
		{
			GD.PushError($"Slot coordinates ({slotXY.X}, {slotXY.Y}) are out of bounds. Valid range is (0-{xSlots - 1}, 0-{ySlots - 1})");
			return;
		}
		CardSlot cardSlot = cardSlots[slotXY.X, slotXY.Y];
		CardSlot cardSlot2 = ((cardView == cardView1) ? card2Slot : card1Slot);
		if (cardSlot2 != null && cardSlot2 == cardSlot)
		{
			slotXY.Y = (slotXY.Y + 1) % ySlots;
			cardSlot = cardSlots[slotXY.X, slotXY.Y];
		}
		if (cardSlot.cardView != null && cardSlot.cardView != cardView)
		{
			GD.PushError($"Expected card slot to be empty, but it had {cardSlot.cardView.Name}, with content: {cardSlot.cardView.debugContentSummary}");
		}
		cardSlot.cardView = cardView;
		cardSlot.placeholderTextureRect.Visible = false;
		cardView.Position = new Vector2(slotXY.X * 1024, slotXY.Y * 1024);
		if (cardView == cardView1)
		{
			card1Slot = cardSlot;
		}
		else
		{
			card2Slot = cardSlot;
		}
	}
}
