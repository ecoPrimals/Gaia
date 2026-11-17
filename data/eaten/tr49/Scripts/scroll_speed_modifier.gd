extends ScrollContainer

@export var scroll_multiplier: = 1.0

func _gui_input(event: InputEvent) -> void :
	if event is InputEventPanGesture:
		event.delta *= scroll_multiplier
