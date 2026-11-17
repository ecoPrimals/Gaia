using System.Collections.Generic;
using System.Linq;
using Godot;

public partial class ScoresView : Control
{
	[Export(PropertyHint.None, "")]
	private PackedScene singleScoreScene;

	[Export(PropertyHint.None, "")]
	private Control scoresContainer;

	[Export(PropertyHint.None, "")]
	private float positionYWhenMenuVisible = 130f;

	private List<SingleScore> scoreViews = new List<SingleScore>();

	private List<SingleScore> oldScoreViews = new List<SingleScore>();

	private Tween showHideTween;

	public override void _Ready()
	{
		base.Visible = false;
		base.Modulate = new Color(1f, 1f, 1f, 0f);
	}

	public void Clear(bool immediate)
	{
		if (!immediate)
		{
			FadeTo(0f, thenClear: true);
			return;
		}
		foreach (SingleScore scoreView in scoreViews)
		{
			scoreView.QueueFree();
		}
		scoreViews.Clear();
		base.Visible = false;
		base.Modulate = new Color(1f, 1f, 1f, 0f);
	}

	public void UpdateScores(List<Score> scores)
	{
		if (DebugOptions.instance.disableScoresView)
		{
			base.Visible = false;
			return;
		}
		GD.Print($"Updating scores: {scores.Count}: {string.Join(" // ", scores.Select((Score s) => s.ToString()))}");
		if (scores.Count == 0)
		{
			if (base.Visible)
			{
				FadeTo(0f);
			}
			return;
		}
		if (scores.Count > 0 && !base.Visible)
		{
			FadeTo(1f);
		}
		oldScoreViews.AddRange(scoreViews);
		scoreViews.Clear();
		foreach (Score score in scores)
		{
			int num = oldScoreViews.FindIndex((SingleScore view) => view.score.label == score.label);
			SingleScore singleScore;
			if (num != -1)
			{
				singleScore = oldScoreViews[num];
				scoreViews.Add(singleScore);
				oldScoreViews.RemoveAt(num);
			}
			else
			{
				singleScore = singleScoreScene.Instantiate<SingleScore>(PackedScene.GenEditState.Disabled);
				scoreViews.Add(singleScore);
				scoresContainer.AddChild(singleScore, forceReadableName: false, InternalMode.Disabled);
			}
			singleScore.score = score;
		}
		foreach (SingleScore oldScoreView in oldScoreViews)
		{
			oldScoreView.QueueFree();
		}
		oldScoreViews.Clear();
	}

	private void FadeTo(float alpha, bool thenClear = false)
	{
		if (showHideTween != null)
		{
			showHideTween.Kill();
			showHideTween = null;
		}
		if (!base.Visible)
		{
			base.Modulate = new Color(1f, 1f, 1f, 0f);
		}
		base.Visible = true;
		showHideTween = CreateTween();
		showHideTween.TweenProperty(this, "modulate:a", alpha, 0.5);
		showHideTween.Finished += delegate
		{
			if (alpha == 0f)
			{
				base.Visible = false;
			}
			showHideTween = null;
			if (thenClear)
			{
				Clear(immediate: true);
			}
		};
	}
}
