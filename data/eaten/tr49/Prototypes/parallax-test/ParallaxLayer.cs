using Godot;

public partial class ParallaxLayer : Node2D
{
	[Export(PropertyHint.None, "")]
	public float parallax = 0.5f;

	private Camera2D _camera;

	private Vector2 _originalPosition;

	private Vector2 _originalCameraPosition;

	private Camera2D camera
	{
		get
		{
			if (_camera == null)
			{
				_camera = GetViewport().GetCamera2D();
			}
			return _camera;
		}
	}

	public override void _Ready()
	{
		_originalPosition = base.Position;
		_originalCameraPosition = camera.Position;
	}

	public override void _Process(double delta)
	{
		Vector2 vector = camera.Position - _originalCameraPosition;
		Vector2 position = base.Position;
		position.X = _originalPosition.X + parallax * vector.X;
		base.Position = position;
	}
}
