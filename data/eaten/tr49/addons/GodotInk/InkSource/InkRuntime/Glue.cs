using Ink.Runtime;

namespace Ink.Runtime
{
	public class Glue : Object
	{
		public override string ToString()
		{
			return "Glue";
		}
	}
}
namespace Ink.Parsed
{
	public class Glue : Wrap<Ink.Runtime.Glue>
	{
		public Glue(Ink.Runtime.Glue glue)
			: base(glue)
		{
		}
	}
}
