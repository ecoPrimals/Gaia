using System.Collections.Generic;
using System.Text;

namespace Ink.Runtime;

public static class StringExt
{
	public static string Join<T>(string separator, List<T> objects)
	{
		StringBuilder stringBuilder = new StringBuilder();
		bool flag = true;
		foreach (T @object in objects)
		{
			if (!flag)
			{
				stringBuilder.Append(separator);
			}
			stringBuilder.Append(@object.ToString());
			flag = false;
		}
		return stringBuilder.ToString();
	}
}
