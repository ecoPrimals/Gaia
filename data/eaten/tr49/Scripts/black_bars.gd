extends Control

@onready var top: Control = $Top
@onready var bottom: Control = $Bottom

@export var hud_buttons: HUDButtons = null

func _process(_delta):
	var black_bar_height = 0.0
	var screen_size = get_viewport_rect().size
	var aspect_ratio = screen_size.x / screen_size.y
	const letterbox_aspect_ratio = 19.0 / 9.0


	if aspect_ratio < letterbox_aspect_ratio:
		var standard_height = screen_size.x / letterbox_aspect_ratio
		black_bar_height = (screen_size.y - standard_height) / 2.0
		black_bar_height *= 1.0 - hud_buttons.currentOffsetNorm

	if black_bar_height > 0.0:
		visible = true
		top.size = Vector2(screen_size.x, black_bar_height)
		bottom.size = Vector2(screen_size.x, black_bar_height)
		top.position = Vector2(0.0, 0.0)
		bottom.position = Vector2(0.0, screen_size.y - black_bar_height)
	else:
		visible = false
