public interface IGlobalBackButtonHandler
{
	void OnGlobalBackButtonPressed();

	bool CanUseGlobalBackButton()
	{
		return true;
	}
}
