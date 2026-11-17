public struct NotebookCodeEntry
{
	public string text;

	public string code;

	public string realCode;

	public bool isConfirmed;

	public int refCount;

	public int refCountMax;

	public bool isUntitled
	{
		get
		{
			if (!string.IsNullOrWhiteSpace(text))
			{
				return text == "???";
			}
			return true;
		}
	}

	public string RichText()
	{
		string value = (string.IsNullOrEmpty(text) ? "" : (" - " + text));
		return $"[color=#744c00][url={code}]{code}[/url][/color]{value}";
	}

	public override string ToString()
	{
		return $"{code} - {text} {refCount}/{refCountMax}";
	}
}
