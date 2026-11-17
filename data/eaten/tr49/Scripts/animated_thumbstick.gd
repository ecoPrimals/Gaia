extends Control

@export var min_rotation = -260.0
@export var max_rotation = 260.0
@export var pulse_speed = 1.0

func _process(_delta):
	var pulse = 0.5 * sin(Time.get_ticks_msec() * 0.001 * pulse_speed) + 0.5
	rotation_degrees = lerp(min_rotation, max_rotation, pulse)
