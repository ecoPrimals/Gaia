using System;

namespace Ink.Parsed;

[Flags]
public enum SequenceType
{
	Stopping = 1,
	Cycle = 2,
	Shuffle = 4,
	Once = 8
}
