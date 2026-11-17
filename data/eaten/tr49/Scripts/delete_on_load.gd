extends Node

@export var delete_parent: bool = false

func _ready():
	if delete_parent:
		get_parent().queue_free()
	else:
		queue_free()
