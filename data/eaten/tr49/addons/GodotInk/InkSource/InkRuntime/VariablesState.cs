using System;
using System.Collections;
using System.Collections.Generic;

namespace Ink.Runtime;

public class VariablesState : IEnumerable<string>, IEnumerable
{
	public delegate void VariableChanged(string variableName, Object newValue);

	public StatePatch patch;

	public static bool dontSaveDefaultValues = true;

	private Dictionary<string, Object> _globalVariables;

	private Dictionary<string, Object> _defaultGlobalVariables;

	private CallStack _callStack;

	private HashSet<string> _changedVariablesForBatchObs;

	private ListDefinitionsOrigin _listDefsOrigin;

	private bool _batchObservingVariableChanges;

	public CallStack callStack
	{
		get
		{
			return _callStack;
		}
		set
		{
			_callStack = value;
		}
	}

	public object this[string variableName]
	{
		get
		{
			if (patch != null && patch.TryGetGlobal(variableName, out var value))
			{
				return (value as Value).valueObject;
			}
			if (_globalVariables.TryGetValue(variableName, out value) || _defaultGlobalVariables.TryGetValue(variableName, out value))
			{
				return (value as Value).valueObject;
			}
			return null;
		}
		set
		{
			if (!_defaultGlobalVariables.ContainsKey(variableName))
			{
				throw new StoryException("Cannot assign to a variable (" + variableName + ") that hasn't been declared in the story");
			}
			Value value2 = Value.Create(value);
			if (value2 == null)
			{
				if (value == null)
				{
					throw new Exception("Cannot pass null to VariableState");
				}
				throw new Exception("Invalid value passed to VariableState: " + value.ToString());
			}
			SetGlobal(variableName, value2);
		}
	}

	public event VariableChanged variableChangedEvent;

	public void StartVariableObservation()
	{
		_batchObservingVariableChanges = true;
		_changedVariablesForBatchObs = new HashSet<string>();
	}

	public Dictionary<string, Object> CompleteVariableObservation()
	{
		_batchObservingVariableChanges = false;
		Dictionary<string, Object> dictionary = new Dictionary<string, Object>();
		if (_changedVariablesForBatchObs != null)
		{
			foreach (string changedVariablesForBatchOb in _changedVariablesForBatchObs)
			{
				Object value = _globalVariables[changedVariablesForBatchOb];
				dictionary[changedVariablesForBatchOb] = value;
			}
		}
		if (patch != null)
		{
			foreach (string changedVariable in patch.changedVariables)
			{
				if (patch.TryGetGlobal(changedVariable, out var value2))
				{
					dictionary[changedVariable] = value2;
				}
			}
		}
		_changedVariablesForBatchObs = null;
		return dictionary;
	}

	public void NotifyObservers(Dictionary<string, Object> changedVars)
	{
		foreach (KeyValuePair<string, Object> changedVar in changedVars)
		{
			variableChangedEvent(changedVar.Key, changedVar.Value);
		}
	}

	IEnumerator IEnumerable.GetEnumerator()
	{
		return GetEnumerator();
	}

	public IEnumerator<string> GetEnumerator()
	{
		return _globalVariables.Keys.GetEnumerator();
	}

	public VariablesState(CallStack callStack, ListDefinitionsOrigin listDefsOrigin)
	{
		_globalVariables = new Dictionary<string, Object>();
		_callStack = callStack;
		_listDefsOrigin = listDefsOrigin;
	}

	public void ApplyPatch()
	{
		foreach (KeyValuePair<string, Object> global in patch.globals)
		{
			_globalVariables[global.Key] = global.Value;
		}
		if (_changedVariablesForBatchObs != null)
		{
			foreach (string changedVariable in patch.changedVariables)
			{
				_changedVariablesForBatchObs.Add(changedVariable);
			}
		}
		patch = null;
	}

	public void SetJsonToken(Dictionary<string, object> jToken)
	{
		_globalVariables.Clear();
		foreach (KeyValuePair<string, Object> defaultGlobalVariable in _defaultGlobalVariables)
		{
			if (jToken.TryGetValue(defaultGlobalVariable.Key, out var value))
			{
				_globalVariables[defaultGlobalVariable.Key] = Json.JTokenToRuntimeObject(value);
			}
			else
			{
				_globalVariables[defaultGlobalVariable.Key] = defaultGlobalVariable.Value;
			}
		}
	}

	public void WriteJson(SimpleJson.Writer writer)
	{
		writer.WriteObjectStart();
		foreach (KeyValuePair<string, Object> globalVariable in _globalVariables)
		{
			string key = globalVariable.Key;
			Object value = globalVariable.Value;
			if (!dontSaveDefaultValues || _defaultGlobalVariables == null || !_defaultGlobalVariables.TryGetValue(key, out var value2) || !RuntimeObjectsEqual(value, value2))
			{
				writer.WritePropertyStart(key);
				Json.WriteRuntimeObject(writer, value);
				writer.WritePropertyEnd();
			}
		}
		writer.WriteObjectEnd();
	}

	public bool RuntimeObjectsEqual(Object obj1, Object obj2)
	{
		if (obj1.GetType() != obj2.GetType())
		{
			return false;
		}
		BoolValue boolValue = obj1 as BoolValue;
		if (boolValue != null)
		{
			return boolValue.value == ((BoolValue)obj2).value;
		}
		IntValue intValue = obj1 as IntValue;
		if (intValue != null)
		{
			return intValue.value == ((IntValue)obj2).value;
		}
		FloatValue floatValue = obj1 as FloatValue;
		if (floatValue != null)
		{
			return floatValue.value == ((FloatValue)obj2).value;
		}
		Value value = obj1 as Value;
		Value value2 = obj2 as Value;
		if (value != null)
		{
			return value.valueObject.Equals(value2.valueObject);
		}
		throw new Exception("FastRoughDefinitelyEquals: Unsupported runtime object type: " + obj1.GetType());
	}

	public Object GetVariableWithName(string name)
	{
		return GetVariableWithName(name, -1);
	}

	public Object TryGetDefaultVariableValue(string name)
	{
		Object value = null;
		_defaultGlobalVariables.TryGetValue(name, out value);
		return value;
	}

	public bool GlobalVariableExistsWithName(string name)
	{
		if (!_globalVariables.ContainsKey(name))
		{
			if (_defaultGlobalVariables != null)
			{
				return _defaultGlobalVariables.ContainsKey(name);
			}
			return false;
		}
		return true;
	}

	private Object GetVariableWithName(string name, int contextIndex)
	{
		Object obj = GetRawVariableWithName(name, contextIndex);
		VariablePointerValue variablePointerValue = obj as VariablePointerValue;
		if ((bool)variablePointerValue)
		{
			obj = ValueAtVariablePointer(variablePointerValue);
		}
		return obj;
	}

	private Object GetRawVariableWithName(string name, int contextIndex)
	{
		Object value = null;
		if (contextIndex == 0 || contextIndex == -1)
		{
			if (patch != null && patch.TryGetGlobal(name, out value))
			{
				return value;
			}
			if (_globalVariables.TryGetValue(name, out value))
			{
				return value;
			}
			if (_defaultGlobalVariables != null && _defaultGlobalVariables.TryGetValue(name, out value))
			{
				return value;
			}
			ListValue listValue = _listDefsOrigin.FindSingleItemListWithName(name);
			if ((bool)listValue)
			{
				return listValue;
			}
		}
		return _callStack.GetTemporaryVariableWithName(name, contextIndex);
	}

	public Object ValueAtVariablePointer(VariablePointerValue pointer)
	{
		return GetVariableWithName(pointer.variableName, pointer.contextIndex);
	}

	public void Assign(VariableAssignment varAss, Object value)
	{
		string variableName = varAss.variableName;
		int num = -1;
		bool flag = false;
		flag = ((!varAss.isNewDeclaration) ? GlobalVariableExistsWithName(variableName) : varAss.isGlobal);
		if (varAss.isNewDeclaration)
		{
			VariablePointerValue variablePointerValue = value as VariablePointerValue;
			if ((bool)variablePointerValue)
			{
				value = ResolveVariablePointer(variablePointerValue);
			}
		}
		else
		{
			VariablePointerValue variablePointerValue2 = null;
			do
			{
				variablePointerValue2 = GetRawVariableWithName(variableName, num) as VariablePointerValue;
				if ((bool)variablePointerValue2)
				{
					variableName = variablePointerValue2.variableName;
					num = variablePointerValue2.contextIndex;
					flag = num == 0;
				}
			}
			while ((bool)variablePointerValue2);
		}
		if (flag)
		{
			SetGlobal(variableName, value);
		}
		else
		{
			_callStack.SetTemporaryVariable(variableName, value, varAss.isNewDeclaration, num);
		}
	}

	public void SnapshotDefaultGlobals()
	{
		_defaultGlobalVariables = new Dictionary<string, Object>(_globalVariables);
	}

	private void RetainListOriginsForAssignment(Object oldValue, Object newValue)
	{
		ListValue listValue = oldValue as ListValue;
		ListValue listValue2 = newValue as ListValue;
		if ((bool)listValue && (bool)listValue2 && listValue2.value.Count == 0)
		{
			listValue2.value.SetInitialOriginNames(listValue.value.originNames);
		}
	}

	public void SetGlobal(string variableName, Object value)
	{
		Object value2 = null;
		if (patch == null || !patch.TryGetGlobal(variableName, out value2))
		{
			_globalVariables.TryGetValue(variableName, out value2);
		}
		ListValue.RetainListOriginsForAssignment(value2, value);
		if (patch != null)
		{
			patch.SetGlobal(variableName, value);
		}
		else
		{
			_globalVariables[variableName] = value;
		}
		if (variableChangedEvent == null || value.Equals(value2))
		{
			return;
		}
		if (_batchObservingVariableChanges)
		{
			if (patch != null)
			{
				patch.AddChangedVariable(variableName);
			}
			else if (_changedVariablesForBatchObs != null)
			{
				_changedVariablesForBatchObs.Add(variableName);
			}
		}
		else
		{
			variableChangedEvent(variableName, value);
		}
	}

	private VariablePointerValue ResolveVariablePointer(VariablePointerValue varPointer)
	{
		int num = varPointer.contextIndex;
		if (num == -1)
		{
			num = GetContextIndexOfVariableNamed(varPointer.variableName);
		}
		VariablePointerValue variablePointerValue = GetRawVariableWithName(varPointer.variableName, num) as VariablePointerValue;
		if ((bool)variablePointerValue)
		{
			return variablePointerValue;
		}
		return new VariablePointerValue(varPointer.variableName, num);
	}

	private int GetContextIndexOfVariableNamed(string varName)
	{
		if (GlobalVariableExistsWithName(varName))
		{
			return 0;
		}
		return _callStack.currentElementIndex;
	}
}
