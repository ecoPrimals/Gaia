class_name SteamWrapper extends Node

const APP_ID: = 3838370

signal achievements_received_from_steam


var _steam: Object = null


var steam_initialized: = false


var is_steam_deck: = false


var _stats_received: = false


var _achievements: = {}


var _achievement_ids: Array[String] = []

func _enter_tree():
	OS.set_environment("SteamAppId", str(APP_ID))
	OS.set_environment("SteamGameId", str(APP_ID))

	if not OS.has_feature("steam") and not OS.has_feature("editor"):
		print("Steam feature flag not enabled. Skipping Steam initialization.")
		return

	if not Engine.has_singleton("Steam"):
		print("Steam singleton not available.")
		return

	_steam = Engine.get_singleton("Steam")
	if _steam == null:
		print("Steam singleton not found.")
		return

	var init_result = _steam.steamInitEx(APP_ID, true)
	if init_result["status"] != 0:
		print("Steam initialization failed: ", init_result["verbal"])
		return

	if not _steam.isSteamRunning():
		print("Steam is not running.")
		return

	print("Steam initialized successfully.")
	steam_initialized = true



	is_steam_deck = _steam.isSteamRunningOnSteamDeck()
	print("steam_wrapper: Running on Steam Deck: ", is_steam_deck)

func _ready():
	if not steam_initialized:
		return



	_steam.user_stats_received.connect(_on_user_stats_received)
	_steam.user_achievement_stored.connect(_on_user_achievement_stored)



	_connect_to_story_controller()



func _process(_delta: float) -> void :
	if steam_initialized:
		_steam.run_callbacks()


func _connect_to_story_controller() -> void :
	var story_controller = get_tree().root.find_child("StoryController", true, false)
	if story_controller:

		story_controller.InkStoryReady.connect(_on_ink_story_ready.bind(story_controller))


		var achievement_names = story_controller.GetAchievementNames()
		if achievement_names.size() > 0:
			_on_ink_story_ready(story_controller)
	else:
		push_error("StoryController not found in scene tree. Achievement IDs won't be loaded.")



func _on_ink_story_ready(story_controller: Node) -> void :
	_achievement_ids.assign(story_controller.GetAchievementNames())
	print("Loaded %d achievement IDs from ink" % _achievement_ids.size())


	_request_stats()




func _request_stats() -> void :
	_steam.requestUserStats(_steam.getSteamID())



func _on_user_stats_received(game_id: int, result: int, _user_id: int) -> void :
	if game_id != APP_ID:
		print("Received stats from wrong game. Expected: %d, Got: %d" % [APP_ID, game_id])
		return


	if result != 1:
		print("Failed to receive Steam stats. Result code: ", result)
		return

	_stats_received = true


	var unlocked_count: = 0

	for achievement_id in _achievement_ids:
		var achievement_data = _steam.getAchievement(achievement_id)


		if achievement_data["ret"]:
			var is_unlocked = achievement_data["achieved"]
			_achievements[achievement_id] = is_unlocked
			if is_unlocked:
				unlocked_count += 1

	print("Achievements unlocked: %d / %d" % [unlocked_count, _achievement_ids.size()])

	achievements_received_from_steam.emit()








func unlock_achievement(achievement_id: String) -> bool:
	if not _stats_received:
		print("Cannot unlock achievement - stats not yet received from Steam.")
		return false


	if _achievements.get(achievement_id, false):
		return true


	if not _steam.setAchievement(achievement_id):
		print("Failed to set achievement: ", achievement_id)
		return false


	if not _steam.storeStats():
		print("Failed to store stats after setting achievement: ", achievement_id)
		return false

	print("Achievement '%s' set and stored. Waiting for confirmation..." % achievement_id)
	return true



func _on_user_achievement_stored(game_id: int, _group_achieve: bool, achievement_name: String, _current_progress: int, _max_progress: int) -> void :
	if game_id != APP_ID:
		return

	print("Achievement stored: ", achievement_name)
	_achievements[achievement_name] = true







func clear_all_achievements() -> void :
	if not _stats_received:
		print("Cannot clear achievement - stats not yet received from Steam.")
		return

	for achievement_id in _achievement_ids:
		if not _steam.clearAchievement(achievement_id):
			print("Failed to clear achievement: ", achievement_id)
			continue

		_achievements[achievement_id] = false

	if not _steam.storeStats():
		print("Failed to store stats after clearing achievements")

	print("Achievements cleared")
