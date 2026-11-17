using Godot;

namespace GodotInk;

public partial class StubInkStory : InkStory
{
	protected override string RawStory
	{
		get
		{
			return base.RawStory;
		}
		set
		{
			throw new InvalidInkException("To load this story directly, please import it with 'is_main_file' set to true.");
		}
	}
}
