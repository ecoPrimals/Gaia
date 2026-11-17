public struct Score
{
	public int value;

	public int total;

	public string label;

	public override string ToString()
	{
		if (total <= 0)
		{
			return $"{value} {label}";
		}
		return $"{value}/{total} {label}";
	}
}
