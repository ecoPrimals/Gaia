using System;
using System.Collections.Generic;
using Godot;

[GlobalClass]
[Tool]
public partial class CreditsLabel : Control
{
	[Export(PropertyHint.None, "")]
	private AudioStream[] characterWriteInSFX;

	[Export(PropertyHint.None, "")]
	private AudioStream[] deconstructSFX;

	private string _text = "";

	private Font _font;

	private int _fontSize = 32;

	private float _characterSpacing = 1f;

	private float _writeInProportion = 1f;

	private float _randomVisibleProportion = 1f;

	private float _fuzzStrength;

	private List<bool> charactersVisible = new List<bool>();

	[Export(PropertyHint.None, "")]
	public string text
	{
		get
		{
			return _text;
		}
		set
		{
			_text = value;
			QueueRedraw();
			SetToMinimumSize();
		}
	}

	[Export(PropertyHint.None, "")]
	public Font font
	{
		get
		{
			return _font;
		}
		set
		{
			_font = value;
			QueueRedraw();
			SetToMinimumSize();
		}
	}

	[Export(PropertyHint.Range, "1, 500, 1")]
	public int fontSize
	{
		get
		{
			return _fontSize;
		}
		set
		{
			_fontSize = value;
			QueueRedraw();
			SetToMinimumSize();
		}
	}

	[Export(PropertyHint.None, "")]
	public float characterSpacing
	{
		get
		{
			return _characterSpacing;
		}
		set
		{
			_characterSpacing = value;
			QueueRedraw();
			SetToMinimumSize();
		}
	}

	[Export(PropertyHint.Range, "0, 1, 0.01")]
	public float writeInProportion
	{
		get
		{
			return _writeInProportion;
		}
		set
		{
			int num = writtenInCharacterCount;
			_writeInProportion = Math.Clamp(value, 0f, 1f);
			QueueRedraw();
			int num2 = writtenInCharacterCount;
			if (num2 != num && num2 > 0 && characterWriteInSFX != null && characterWriteInSFX.Length != 0)
			{
				AudioStreamPlayer audioStreamPlayer = new AudioStreamPlayer();
				audioStreamPlayer.Bus = "SFX";
				audioStreamPlayer.Stream = characterWriteInSFX.Random();
				AddChild(audioStreamPlayer, forceReadableName: false, InternalMode.Disabled);
				audioStreamPlayer.Play();
			}
		}
	}

	private int writtenInCharacterCount => Mathf.CeilToInt((float)_text.Length * _writeInProportion);

	[Export(PropertyHint.Range, "0, 1, 0.01")]
	public float randomVisibleProportion
	{
		get
		{
			return _randomVisibleProportion;
		}
		set
		{
			_randomVisibleProportion = Math.Clamp(value, 0f, 1f);
			QueueRedraw();
		}
	}

	[Export(PropertyHint.Range, "0, 1, 0.01")]
	public float fuzzStrength
	{
		get
		{
			return _fuzzStrength;
		}
		set
		{
			_fuzzStrength = Math.Clamp(value, 0f, 1f);
			QueueRedraw();
		}
	}

	public void PlayDeconstructSFX()
	{
		if (deconstructSFX != null)
		{
			AudioStreamPlayer audioStreamPlayer = new AudioStreamPlayer();
			audioStreamPlayer.Bus = "SFX";
			audioStreamPlayer.Stream = deconstructSFX.Random();
			AddChild(audioStreamPlayer, forceReadableName: false, InternalMode.Disabled);
			audioStreamPlayer.Play();
		}
	}

	public override Vector2 _GetMinimumSize()
	{
		if (_font == null || string.IsNullOrEmpty(_text))
		{
			return Vector2.Zero;
		}
		float x = _font.GetCharSize(77L, _fontSize).X;
		float x2 = (float)_text.Length * _characterSpacing * x;
		float y = (float)_fontSize + _font.GetAscent(_fontSize);
		return new Vector2(x2, y);
	}

	private void SetToMinimumSize()
	{
		if (IsInsideTree())
		{
			base.Size = _GetMinimumSize();
		}
	}

	public override void _Ready()
	{
		SetToMinimumSize();
	}

	public override void _Notification(int what)
	{
		if ((long)what == 40)
		{
			SetToMinimumSize();
		}
	}

	public override void _Draw()
	{
		if (_font == null)
		{
			return;
		}
		Color themeColor = GetThemeColor("font_color", "Label");
		RefreshRandomCharactersVisible();
		int num = Mathf.RoundToInt(fuzzStrength * (float)_text.Length);
		float coherence = 1f - fuzzStrength;
		string text = CardTextContent.FuzzText(_text, coherence, coherenceIsCriticallyLow: false, _text.GetHashCode() + num);
		float x = _font.GetCharSize(77L, _fontSize).X;
		float num2 = 0f;
		for (int i = 0; i < _text.Length; i++)
		{
			char c = text[i];
			if (charactersVisible[i] && _writeInProportion > 0f && i < Mathf.CeilToInt((float)_text.Length * _writeInProportion))
			{
				float x2 = _font.GetCharSize(c, _fontSize).X;
				float num3 = 0.5f * _characterSpacing - 0.5f * x2;
				_font.DrawChar(GetCanvasItem(), new Vector2(num2 + num3, _fontSize), c, _fontSize, themeColor);
			}
			num2 += _characterSpacing * x;
		}
	}

	private void RefreshRandomCharactersVisible()
	{
		charactersVisible.Clear();
		for (int i = 0; i < _text.Length; i++)
		{
			charactersVisible.Add(item: true);
		}
		if (charactersVisible.Count != _text.Length)
		{
			charactersVisible.Clear();
			for (int j = 0; j < _text.Length; j++)
			{
				charactersVisible.Add(item: true);
			}
		}
		else
		{
			for (int k = 0; k < _text.Length; k++)
			{
				charactersVisible[k] = true;
			}
		}
		Random random = new Random(_text.GetHashCode());
		int num = (int)Math.Round((float)_text.Length * (1f - _randomVisibleProportion));
		List<int> list = new List<int>();
		for (int l = 0; l < _text.Length; l++)
		{
			list.Add(l);
		}
		for (int num2 = list.Count - 1; num2 > 0; num2--)
		{
			int index = random.Next(num2 + 1);
			int value = list[num2];
			list[num2] = list[index];
			list[index] = value;
		}
		for (int m = 0; m < num; m++)
		{
			charactersVisible[list[m]] = false;
		}
	}
}
