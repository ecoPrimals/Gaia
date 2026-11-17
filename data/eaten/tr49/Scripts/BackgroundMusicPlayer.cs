using Godot;

public partial class BackgroundMusicPlayer : Node
{
	[Export(PropertyHint.None, "")]
	private AudioStreamPlayer musicPlayer;

	[Export(PropertyHint.None, "")]
	private AudioStream creditsMusic;

	private string targetMusicFromInk;

	private bool loop = true;

	private bool playingCreditsMusic;

	public string currentMusicFromInk { get; private set; }

	public void PlayFromInk(string newMusicName)
	{
		if (newMusicName == "SILENCE")
		{
			targetMusicFromInk = null;
			PlayPendingMusic();
			return;
		}
		if (string.IsNullOrWhiteSpace(newMusicName))
		{
			loop = false;
			return;
		}
		string text = (newMusicName.Contains("res://") ? newMusicName : ("res://" + newMusicName));
		if (!ResourceLoader.Exists(text))
		{
			GD.PrintErr("Music file " + text + " not found.");
			return;
		}
		targetMusicFromInk = text;
		loop = true;
		if (!musicPlayer.Playing)
		{
			PlayPendingMusic();
		}
	}

	public void PlayCreditsMusic()
	{
		if (!playingCreditsMusic)
		{
			playingCreditsMusic = true;
			musicPlayer.Stop();
			musicPlayer.Stream = creditsMusic;
			musicPlayer.Play();
		}
	}

	public void StopCreditsMusic()
	{
		playingCreditsMusic = false;
		musicPlayer.Stop();
		PlayPendingMusic();
	}

	public override void _Ready()
	{
		musicPlayer.Finished += OnMusicFinished;
	}

	private void OnMusicFinished()
	{
		if (playingCreditsMusic)
		{
			musicPlayer.Play();
		}
		else
		{
			PlayPendingMusic();
		}
	}

	private void PlayPendingMusic()
	{
		musicPlayer.Stop();
		currentMusicFromInk = null;
		if (targetMusicFromInk != null)
		{
			AudioStream stream = ResourceLoader.Load<AudioStream>(targetMusicFromInk, null, ResourceLoader.CacheMode.Reuse);
			currentMusicFromInk = targetMusicFromInk;
			musicPlayer.Stream = stream;
			musicPlayer.Play();
			if (!loop)
			{
				targetMusicFromInk = null;
			}
		}
	}
}
