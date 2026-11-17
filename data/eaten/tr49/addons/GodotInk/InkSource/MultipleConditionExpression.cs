using System.Collections.Generic;
using System.Linq;
using Ink.Runtime;

namespace Ink.Parsed;

public class MultipleConditionExpression : Expression
{
	public List<Expression> subExpressions => base.content.Cast<Expression>().ToList();

	public MultipleConditionExpression(List<Expression> conditionExpressions)
	{
		AddContent(conditionExpressions);
	}

	public override void GenerateIntoContainer(Container container)
	{
		bool flag = true;
		foreach (Expression subExpression in subExpressions)
		{
			subExpression.GenerateIntoContainer(container);
			if (!flag)
			{
				container.AddContent(NativeFunctionCall.CallWithName("&&"));
			}
			flag = false;
		}
	}
}
