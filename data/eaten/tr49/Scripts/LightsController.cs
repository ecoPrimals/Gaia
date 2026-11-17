using System;
using System.Collections.Generic;
using Godot;

public partial class LightsController : Node
{
	[Export(PropertyHint.None, "")]
	private float[] groupSwitchOnDelays = new float[0];

	[Export(PropertyHint.None, "")]
	private Texture2D[] floorLightingTextures = new Texture2D[0];

	[Export(PropertyHint.None, "")]
	private Curve flickerCurve;

	[Export(PropertyHint.None, "")]
	private MeshInstance3D screenReflection;

	[Export(PropertyHint.None, "")]
	private ParticleProcessMaterial fogParticleProcessMaterial;

	[Export(PropertyHint.None, "")]
	private Color fogParticlesUnlitColor = new Color(0f, 0f, 0f);

	public static LightsController instance;

	private List<LitSprite3D> litSprite3Ds = new List<LitSprite3D>();

	private List<FloorWires> floorWires = new List<FloorWires>();

	private List<FlipperDigit> flipperDigits = new List<FlipperDigit>();

	private List<LightVisibilityNode> lightVisibilityNodes = new List<LightVisibilityNode>();

	public bool isTurnedOn;

	private Tween switchTween;

	private ShaderMaterial floorMaterial;

	private Color fogParticleDefaultColor;

	public override void _EnterTree()
	{
		instance = this;
	}

	public override void _Ready()
	{
		MeshInstance3D node = GetNode<MeshInstance3D>("../Room/Floor");
		floorMaterial = node.GetActiveMaterial(0) as ShaderMaterial;
		fogParticleDefaultColor = fogParticleProcessMaterial.Color;
		SetTurnedOn(turnedOn: false, immediate: true);
	}

	public void DebugToggleLights()
	{
		SetTurnedOn(!isTurnedOn);
	}

	public void SetTurnedOn(bool turnedOn, bool immediate = false)
	{
		if (switchTween != null)
		{
			switchTween.Kill();
			switchTween = null;
		}
		isTurnedOn = turnedOn;
		(screenReflection.GetActiveMaterial(0) as StandardMaterial3D).AlbedoColor = (turnedOn ? Colors.White : Colors.White.WithAlpha(0f));
		fogParticleProcessMaterial.Color = (turnedOn ? fogParticleDefaultColor : fogParticlesUnlitColor);
		if (turnedOn && !immediate)
		{
			switchTween = CreateTween().SetParallel();
			foreach (LitSprite3D litSprite3D in litSprite3Ds)
			{
				int num = litSprite3D.lightingGroup;
				if (num >= groupSwitchOnDelays.Length)
				{
					GD.PrintErr($"LitSprite3D {litSprite3D.Name} has lighting group {num} which doesn't have a a defined delay in LightsController");
					num = groupSwitchOnDelays.Length - 1;
				}
				float num2 = groupSwitchOnDelays[num];
				switchTween.TweenSubtween(CreateFlickerTween(delegate(bool turnedOn2)
				{
					litSprite3D.SetTurnedOn(turnedOn2);
				})).SetDelay(num2);
			}
			foreach (FlipperDigit flipperDigit in flipperDigits)
			{
				int num3 = flipperDigit.lightingGroup;
				if (num3 >= groupSwitchOnDelays.Length)
				{
					GD.PrintErr($"FlipperDigit {flipperDigit.Name} has lighting group {num3} which doesn't have a a defined delay in LightsController");
					num3 = groupSwitchOnDelays.Length - 1;
				}
				float num4 = groupSwitchOnDelays[num3];
				switchTween.TweenSubtween(CreateFlickerTween(delegate(bool isLit)
				{
					flipperDigit.SetIsLit(isLit);
				})).SetDelay(num4);
			}
			foreach (LightVisibilityNode lightVisibilityNode in lightVisibilityNodes)
			{
				int num5 = lightVisibilityNode.lightingGroup;
				if (num5 >= groupSwitchOnDelays.Length)
				{
					GD.PrintErr($"LightVisibilityNode {lightVisibilityNode.Name} has lighting group {num5} which doesn't have a a defined delay in LightsController");
					num5 = groupSwitchOnDelays.Length - 1;
				}
				float num6 = groupSwitchOnDelays[num5];
				switchTween.TweenSubtween(CreateFlickerTween(delegate(bool turnedOn2)
				{
					lightVisibilityNode.SetTurnedOn(turnedOn2);
				})).SetDelay(num6);
			}
			Texture2D texture2D = floorLightingTextures[0];
			for (int num7 = 0; num7 < floorLightingTextures.Length; num7++)
			{
				if (num7 >= groupSwitchOnDelays.Length)
				{
					GD.PrintErr("More floor lighting textures than delays defined in LightsController");
					continue;
				}
				float num8 = groupSwitchOnDelays[num7];
				if (floorLightingTextures[num7] != null)
				{
					Texture2D tex1 = texture2D;
					Texture2D tex2 = floorLightingTextures[num7];
					switchTween.TweenSubtween(CreateFlickerTween(delegate(bool flag)
					{
						Texture2D floorLightingTexture = (flag ? tex2 : tex1);
						SetFloorLightingTexture(floorLightingTexture);
					})).SetDelay(num8);
					texture2D = tex2;
				}
			}
			switchTween.Finished += delegate
			{
				switchTween = null;
			};
			return;
		}
		foreach (LitSprite3D litSprite3D2 in litSprite3Ds)
		{
			litSprite3D2.SetTurnedOn(isTurnedOn);
		}
		foreach (FlipperDigit flipperDigit2 in flipperDigits)
		{
			flipperDigit2.SetIsLit(isTurnedOn);
		}
		foreach (LightVisibilityNode lightVisibilityNode2 in lightVisibilityNodes)
		{
			lightVisibilityNode2.SetTurnedOn(isTurnedOn);
		}
		if (turnedOn)
		{
			int num9 = floorLightingTextures.Length - 1;
			while (num9 >= 0 && floorLightingTextures[num9] == null)
			{
				num9--;
			}
			SetFloorLightingTexture(floorLightingTextures[num9]);
		}
		else
		{
			SetFloorLightingTexture(floorLightingTextures[0]);
		}
	}

	private void SetFloorLightingTexture(Texture2D texture)
	{
		floorMaterial.SetShaderParameter("lighting_texture", texture);
		foreach (FloorWires floorWire in floorWires)
		{
			floorWire.lightingTexture = texture;
		}
	}

	private Tween CreateFlickerTween(Action<bool> setTurnedOn)
	{
		Tween tween = CreateTween();
		tween.TweenMethod(Callable.From(delegate(float tweenVal)
		{
			float num = flickerCurve.Sample(tweenVal);
			setTurnedOn(num > 0.5f);
		}), 0f, 1f, 0.30000001192092896);
		tween.Finished += delegate
		{
			setTurnedOn(obj: true);
		};
		return tween;
	}

	public override void _Process(double delta)
	{
		if (DebugOptions.instance.artMode && switchTween == null)
		{
			SetTurnedOn(isTurnedOn, immediate: true);
		}
	}

	public void RegisterLitSprite3D(LitSprite3D litSprite3D)
	{
		if (!litSprite3Ds.Contains(litSprite3D))
		{
			litSprite3Ds.Add(litSprite3D);
		}
	}

	public void RegisterFloorWires(FloorWires floorWiresInstance)
	{
		floorWires.Add(floorWiresInstance);
	}

	public void RegisterFlipperDigit(FlipperDigit flipperDigit)
	{
		flipperDigits.Add(flipperDigit);
	}

	public void RegisterLightVisibilityNode(LightVisibilityNode lightVisibilityNode)
	{
		lightVisibilityNodes.Add(lightVisibilityNode);
	}
}
