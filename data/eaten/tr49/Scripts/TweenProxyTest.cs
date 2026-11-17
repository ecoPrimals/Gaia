using System.Linq;
using Godot;

public partial class TweenProxyTest : Control
{
	[Export(PropertyHint.None, "")]
	public ColorRect[] rects;

	private TweenProxy[] rectProxies;

	private TweenProxy proxy;

	public override void _Ready()
	{
		rectProxies = rects.Select((ColorRect r) => new TweenProxy(r)).ToArray();
		proxy = new TweenProxy(this);
	}

	public void TestTween()
	{
		if (true)
		{
			for (int i = 0; i < rectProxies.Length; i++)
			{
				TweenProxy rect = rectProxies[i];
				rect.CreateTween(1f, delegate
				{
					rect.AddDelay(0.1f + 0.1f * (float)i);
					rect.X += 400f;
					rect.AddDelay(1.3f);
					rect.X -= 400f;
				}, Tween.TransitionType.Sine, Tween.EaseType.InOut);
			}
			return;
		}
		proxy.CreateTween(1f, delegate
		{
			TweenProxy[] array = rectProxies;
			for (int j = 0; j < array.Length; j++)
			{
				array[j].X += 400f;
				proxy.AddDelay(0.1f);
			}
			proxy.AddDelay(1f);
			array = rectProxies;
			for (int j = 0; j < array.Length; j++)
			{
				array[j].X -= 400f;
				proxy.AddDelay(0.1f);
			}
		}, Tween.TransitionType.Sine, Tween.EaseType.InOut);
	}
}
