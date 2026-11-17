using System;
using Godot;
using Godot.Collections;

public partial class FlipperDigit : Node3D
{
	[Signal]
	public delegate void ClickedEventHandler(FlipperDigit digit);

	[Export(PropertyHint.None, "")]
	public bool useLetters;

	[Export(PropertyHint.None, "")]
	public float trimToWidth = 0.86f;

	[Export(PropertyHint.None, "")]
	public float smoothTime = 0.1f;

	[Export(PropertyHint.None, "")]
	public float maxSpeed = 10f;

	[Export(PropertyHint.None, "")]
	private Color selectedColor = Colors.Red;

	[Export(PropertyHint.None, "")]
	private Color litColor = Colors.White;

	[Export(PropertyHint.None, "")]
	private Color unlitColor = Colors.Black;

	[Export(PropertyHint.None, "")]
	public StandardMaterial3D material;

	[Export(PropertyHint.None, "")]
	public float flipperSeparation = 0.05f;

	[Export(PropertyHint.None, "")]
	public float transparentMeshSortingOffset = 3f;

	[Export(PropertyHint.None, "")]
	public int lightingGroup = 1;

	[Export(PropertyHint.None, "")]
	public MachineAudio machineAudio;

	public bool canInteract = true;

	public int digitIndex;

	private float fractionalCharacterIndex;

	private float currentVelocity;

	private int targetCharacterIndex;

	private bool isLit;

	public bool isSelected;

	private Sprite3D glow;

	private Area3D area;

	private MeshInstance3D upperTopMeshInst;

	private MeshInstance3D upperBottomMeshInst;

	private MeshInstance3D lowerTopMeshInst;

	private MeshInstance3D lowerBottomMeshInst;

	private StandardMaterial3D upperMaterial;

	private StandardMaterial3D lowerMaterial;

	private static ArrayMesh topHalfMesh;

	private static ArrayMesh bottomHalfMesh;

	private static Texture2D[] numberTextures;

	private static Texture2D[] letterTextures;

	public override void _Ready()
	{
		Node3D node = GetNode<Node3D>("3DFlipper");
		glow = GetNode<Sprite3D>("Glow");
		area = GetNode<Area3D>("Area3D");
		area.InputEvent += delegate(Node camera, InputEvent @event, Vector3 eventPosition, Vector3 normal, long shapeIdx)
		{
			OnAreaInputEvent(@event);
		};
		glow.Visible = false;
		if (topHalfMesh == null)
		{
			GenerateMeshes();
		}
		if (numberTextures == null)
		{
			numberTextures = new Texture2D[10];
			for (int num = 0; num < 10; num++)
			{
				numberTextures[num] = GD.Load<Texture2D>($"res://Images/Flipper_Characters/{num}.png");
			}
			letterTextures = new Texture2D[26];
			for (int num2 = 0; num2 < 26; num2++)
			{
				letterTextures[num2] = GD.Load<Texture2D>("res://Images/Flipper_Characters/" + (char)(65 + num2) + ".png");
			}
		}
		upperTopMeshInst = new MeshInstance3D();
		upperTopMeshInst.Mesh = topHalfMesh;
		node.AddChild(upperTopMeshInst, forceReadableName: false, InternalMode.Disabled);
		upperBottomMeshInst = new MeshInstance3D();
		upperBottomMeshInst.Mesh = bottomHalfMesh;
		node.AddChild(upperBottomMeshInst, forceReadableName: false, InternalMode.Disabled);
		lowerTopMeshInst = new MeshInstance3D();
		lowerTopMeshInst.Mesh = topHalfMesh;
		node.AddChild(lowerTopMeshInst, forceReadableName: false, InternalMode.Disabled);
		lowerBottomMeshInst = new MeshInstance3D();
		lowerBottomMeshInst.Mesh = bottomHalfMesh;
		node.AddChild(lowerBottomMeshInst, forceReadableName: false, InternalMode.Disabled);
		RotateForFractionalProgressNorm(0f);
		lowerTopMeshInst.Position = new Vector3(0f, (0f - flipperSeparation) / 2f, 0f);
		lowerBottomMeshInst.Position = new Vector3(0f, (0f - flipperSeparation) / 2f, 0f);
		upperMaterial = (StandardMaterial3D)material.Duplicate();
		lowerMaterial = (StandardMaterial3D)material.Duplicate();
		upperTopMeshInst.MaterialOverride = upperMaterial;
		upperBottomMeshInst.MaterialOverride = upperMaterial;
		lowerTopMeshInst.MaterialOverride = lowerMaterial;
		lowerBottomMeshInst.MaterialOverride = lowerMaterial;
		upperTopMeshInst.SortingOffset = transparentMeshSortingOffset;
		upperBottomMeshInst.SortingOffset = transparentMeshSortingOffset;
		lowerTopMeshInst.SortingOffset = transparentMeshSortingOffset;
		lowerBottomMeshInst.SortingOffset = transparentMeshSortingOffset;
		isSelected = false;
		isLit = false;
		RefreshColors();
		if (LightsController.instance != null)
		{
			LightsController.instance.RegisterFlipperDigit(this);
		}
	}

	public void SetIsLit(bool isLit)
	{
		this.isLit = isLit;
		RefreshColors();
	}

	public override void _Process(double delta)
	{
		int num = (useLetters ? 26 : 10);
		fractionalCharacterIndex = Mathf.Wrap(fractionalCharacterIndex, 0f, num);
		float num2 = (float)targetCharacterIndex - fractionalCharacterIndex;
		if (num2 > (float)num * 0.5f)
		{
			num2 -= (float)num;
		}
		else if (num2 < (float)(-num) * 0.5f)
		{
			num2 += (float)num;
		}
		float target = fractionalCharacterIndex + num2;
		int num3 = Mathf.RoundToInt(fractionalCharacterIndex);
		fractionalCharacterIndex = MathX.SmoothDamp(fractionalCharacterIndex, target, ref currentVelocity, smoothTime, maxSpeed, (float)delta);
		if (Mathf.RoundToInt(fractionalCharacterIndex) != num3)
		{
			machineAudio.FlipperDigitFlipped(currentVelocity);
		}
		RefreshFromFractionalCharacterIndex();
	}

	private void RefreshFromFractionalCharacterIndex()
	{
		int num = (int)MathF.Floor(fractionalCharacterIndex);
		float num2 = fractionalCharacterIndex - (float)num;
		Texture2D[] array = (useLetters ? letterTextures : numberTextures);
		int num3 = (num % array.Length + array.Length) % array.Length;
		int num4 = ((num + 1) % array.Length + array.Length) % array.Length;
		if (num2 < 0.05f)
		{
			upperTopMeshInst.Visible = true;
			upperBottomMeshInst.Visible = true;
			lowerTopMeshInst.Visible = false;
			lowerBottomMeshInst.Visible = false;
			RotateForFractionalProgressNorm(0f);
		}
		else if (num2 > 0.95f)
		{
			upperTopMeshInst.Visible = false;
			upperBottomMeshInst.Visible = false;
			lowerTopMeshInst.Visible = true;
			lowerBottomMeshInst.Visible = true;
			RotateForFractionalProgressNorm(1f);
		}
		else
		{
			upperTopMeshInst.Visible = true;
			upperBottomMeshInst.Visible = true;
			lowerTopMeshInst.Visible = true;
			lowerBottomMeshInst.Visible = true;
			RotateForFractionalProgressNorm(num2);
		}
		upperMaterial.AlbedoTexture = array[num3];
		lowerMaterial.AlbedoTexture = array[num4];
	}

	private void RotateForFractionalProgressNorm(float progressNorm)
	{
		upperBottomMeshInst.Rotation = new Vector3(Mathf.DegToRad(-180f * progressNorm), 0f, 0f);
		lowerTopMeshInst.Rotation = new Vector3(Mathf.DegToRad(180f * (1f - progressNorm)), 0f, 0f);
	}

	private void OnAreaInputEvent(InputEvent @event)
	{
		if (canInteract && @event is InputEventMouseButton inputEventMouseButton && inputEventMouseButton.ButtonIndex == MouseButton.Left && inputEventMouseButton.Pressed)
		{
			this.SetInputAsHandled(@event);
			EmitSignal(SignalName.Clicked, this);
		}
	}

	public void SetValue(int value)
	{
		targetCharacterIndex = value;
	}

	public void SetSelected(bool selected)
	{
		isSelected = selected;
		RefreshColors();
		glow.Visible = selected;
	}

	private void RefreshColors()
	{
		Color albedoColor = (isLit ? litColor : unlitColor);
		if (isSelected)
		{
			albedoColor *= selectedColor;
		}
		upperMaterial.AlbedoColor = albedoColor;
		lowerMaterial.AlbedoColor = albedoColor;
	}

	private void GenerateMeshes()
	{
		topHalfMesh = GenerateHalfQuadMesh(0f, 0.5f);
		bottomHalfMesh = GenerateHalfQuadMesh(-0.5f, 0f);
	}

	private ArrayMesh GenerateHalfQuadMesh(float bottomY, float topY)
	{
		ArrayMesh arrayMesh = new ArrayMesh();
		Vector3[] array = new Vector3[4]
		{
			new Vector3((0f - trimToWidth) / 2f, topY, 0f),
			new Vector3(trimToWidth / 2f, topY, 0f),
			new Vector3(trimToWidth / 2f, bottomY, 0f),
			new Vector3((0f - trimToWidth) / 2f, bottomY, 0f)
		};
		float num = 0.5f * (1f - trimToWidth);
		Vector2[] array2 = new Vector2[4]
		{
			new Vector2(num, 0f - topY + 0.5f),
			new Vector2(1f - num, 0f - topY + 0.5f),
			new Vector2(1f - num, 0f - bottomY + 0.5f),
			new Vector2(num, 0f - bottomY + 0.5f)
		};
		int[] array3 = new int[6] { 0, 1, 2, 2, 3, 0 };
		Godot.Collections.Array array4 = new Godot.Collections.Array();
		array4.Resize(13);
		array4[0] = array;
		array4[4] = array2;
		array4[12] = array3;
		arrayMesh.AddSurfaceFromArrays(Mesh.PrimitiveType.Triangles, array4, null, null, (Mesh.ArrayFormat)0L);
		return arrayMesh;
	}
}
