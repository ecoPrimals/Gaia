using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using Ink.Parsed;
using Ink.Runtime;

namespace Ink;

public class PluginManager
{
	private List<IPlugin> _plugins;

	public PluginManager(List<string> pluginDirectories)
	{
		_plugins = new List<IPlugin>();
		foreach (string pluginDirectory in pluginDirectories)
		{
			string[] files = Directory.GetFiles(pluginDirectory, "*.dll");
			for (int i = 0; i < files.Length; i++)
			{
				Type[] exportedTypes = Assembly.LoadFile(System.IO.Path.GetFullPath(files[i])).GetExportedTypes();
				foreach (Type type in exportedTypes)
				{
					if (typeof(IPlugin).IsAssignableFrom(type))
					{
						_plugins.Add((IPlugin)Activator.CreateInstance(type));
					}
				}
			}
		}
	}

	public string PreParse(string storyContent)
	{
		object[] array = new object[1] { storyContent };
		foreach (IPlugin plugin in _plugins)
		{
			typeof(IPlugin).InvokeMember("PreParse", BindingFlags.InvokeMethod, null, plugin, array);
		}
		return (string)array[0];
	}

	public Ink.Parsed.Story PostParse(Ink.Parsed.Story parsedStory)
	{
		object[] array = new object[1] { parsedStory };
		foreach (IPlugin plugin in _plugins)
		{
			typeof(IPlugin).InvokeMember("PostParse", BindingFlags.InvokeMethod, null, plugin, array);
		}
		return (Ink.Parsed.Story)array[0];
	}

	public Ink.Runtime.Story PostExport(Ink.Parsed.Story parsedStory, Ink.Runtime.Story runtimeStory)
	{
		object[] array = new object[2] { parsedStory, runtimeStory };
		foreach (IPlugin plugin in _plugins)
		{
			typeof(IPlugin).InvokeMember("PostExport", BindingFlags.InvokeMethod, null, plugin, array);
		}
		return (Ink.Runtime.Story)array[1];
	}
}
