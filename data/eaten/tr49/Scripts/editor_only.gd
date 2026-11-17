extends Node

func _enter_tree():
	if get_parent():
		get_parent().queue_free()
