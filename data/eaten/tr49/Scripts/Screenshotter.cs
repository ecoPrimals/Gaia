using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using Godot;

public partial class Screenshotter : Node
{
	[Export(PropertyHint.None, "")]
	public Vector2I targetSize = new Vector2I(3840, 2160);

	[Export(PropertyHint.None, "")]
	public string screenshotPrefix = "Screenshots/TR-49-screenshot-";

	[Export(PropertyHint.None, "")]
	public string requiredOSFeature = "editor";

	[Export(PropertyHint.None, "")]
	public Control[] controlsToHide;

	private bool isCapturing;

	public override void _Process(double delta)
	{
		if (string.IsNullOrWhiteSpace(requiredOSFeature) || OS.HasFeature(requiredOSFeature))
		{
			Key keycode = (Key)(Platform.isMac ? 4194327 : 4194326);
			if (!isCapturing && Input.IsKeyPressed(keycode) && Input.IsKeyPressed(Key.T))
			{
				TakeScreenshot();
			}
		}
	}

	public async Task TakeScreenshot()
	{
		if (isCapturing)
		{
			return;
		}
		isCapturing = true;
		Dictionary<Control, bool> controlVisibilityStates = null;
		try
		{
			SceneTree tree = GetTree();
			if (tree == null)
			{
				GD.PrintErr("Cannot take screenshot: no scene tree available.");
				return;
			}
			Node currentScene = tree.CurrentScene;
			if (currentScene == null)
			{
				GD.PrintErr("Cannot take screenshot: no current scene.");
				return;
			}
			Node originalParent = currentScene.GetParent();
			if (originalParent == null)
			{
				GD.PrintErr("Cannot take screenshot: current scene has no parent.");
				return;
			}
			int originalIndex = currentScene.GetIndex();
			Viewport viewport = GetViewport();
			int b = (int)(ProjectSettings.HasSetting("display/window/size/viewport_width") ? ((long)ProjectSettings.GetSetting("display/window/size/viewport_width")) : targetSize.X);
			int b2 = (int)(ProjectSettings.HasSetting("display/window/size/viewport_height") ? ((long)ProjectSettings.GetSetting("display/window/size/viewport_height")) : targetSize.Y);
			Vector2I vector2I = new Vector2I(Mathf.Max(1, b), Mathf.Max(1, b2));
			controlVisibilityStates = new Dictionary<Control, bool>();
			if (controlsToHide != null)
			{
				Control[] array = controlsToHide;
				foreach (Control control in array)
				{
					if (control != null && GodotObject.IsInstanceValid(control))
					{
						controlVisibilityStates[control] = control.Visible;
						control.Visible = false;
					}
				}
			}
			float num = (float)targetSize.X / (float)targetSize.Y;
			float num2 = (float)vector2I.X / (float)vector2I.Y;
			Vector2I size2DOverride;
			if (num < num2)
			{
				int y = Mathf.RoundToInt((float)vector2I.X / num);
				size2DOverride = new Vector2I(vector2I.X, y);
			}
			else
			{
				int x = Mathf.RoundToInt((float)vector2I.Y * num);
				size2DOverride = new Vector2I(x, vector2I.Y);
			}
			SubViewport screenshotViewport = new SubViewport
			{
				Name = "ScreenshotViewport",
				Size = targetSize,
				RenderTargetUpdateMode = SubViewport.UpdateMode.Always,
				RenderTargetClearMode = SubViewport.ClearMode.Always
			};
			screenshotViewport.Size2DOverride = size2DOverride;
			screenshotViewport.Size2DOverrideStretch = true;
			if (viewport != null)
			{
				screenshotViewport.CanvasItemDefaultTextureFilter = viewport.CanvasItemDefaultTextureFilter;
				screenshotViewport.CanvasItemDefaultTextureRepeat = viewport.CanvasItemDefaultTextureRepeat;
				screenshotViewport.Snap2DTransformsToPixel = viewport.Snap2DTransformsToPixel;
			}
			screenshotViewport.GuiDisableInput = true;
			tree.Root.AddChild(screenshotViewport, forceReadableName: false, InternalMode.Disabled);
			bool sceneReparented = false;
			try
			{
				originalParent.RemoveChild(currentScene);
				screenshotViewport.AddChild(currentScene, forceReadableName: false, InternalMode.Disabled);
				sceneReparented = true;
				await ToSignal(tree, SceneTree.SignalName.ProcessFrame);
				await ToSignal(RenderingServer.Singleton, RenderingServerInstance.SignalName.FramePostDraw);
				screenshotViewport.RenderTargetUpdateMode = SubViewport.UpdateMode.Disabled;
				Image image = screenshotViewport.GetTexture()?.GetImage();
				if (image == null)
				{
					GD.PrintErr("Failed to capture screenshot image.");
				}
				else
				{
					string text = $"user://{screenshotPrefix}{DateTime.Now:yyyyMMdd_HHmmss}.png";
					string baseDir = text.GetBaseDir();
					if (!string.IsNullOrEmpty(baseDir))
					{
						string path = ProjectSettings.GlobalizePath(baseDir);
						try
						{
							Directory.CreateDirectory(path);
						}
						catch (Exception ex)
						{
							GD.PrintErr("Failed to create directory " + baseDir + ": " + ex.Message);
						}
					}
					Error error = image.SavePng(text);
					if (error != Error.Ok)
					{
						GD.PrintErr($"Failed to save screenshot to {text}: {error}");
					}
					else
					{
						GD.Print("Saved screenshot to " + text);
					}
				}
			}
			finally
			{
				if (sceneReparented)
				{
					if (currentScene.GetParent() == screenshotViewport)
					{
						screenshotViewport.RemoveChild(currentScene);
					}
					originalParent.AddChild(currentScene, forceReadableName: false, InternalMode.Disabled);
					if (currentScene.GetIndex() != originalIndex)
					{
						originalParent.MoveChild(currentScene, originalIndex);
					}
					if (tree.CurrentScene != currentScene)
					{
						tree.CurrentScene = currentScene;
					}
				}
				screenshotViewport.QueueFree();
			}
			await ToSignal(RenderingServer.Singleton, RenderingServerInstance.SignalName.FramePostDraw);
		}
		catch (Exception value)
		{
			GD.PrintErr($"Screenshot capture failed: {value}");
		}
		finally
		{
			if (controlVisibilityStates != null)
			{
				foreach (KeyValuePair<Control, bool> item in controlVisibilityStates)
				{
					Control key = item.Key;
					if (GodotObject.IsInstanceValid(key))
					{
						key.Visible = item.Value;
					}
				}
			}
			isCapturing = false;
		}
	}
}
