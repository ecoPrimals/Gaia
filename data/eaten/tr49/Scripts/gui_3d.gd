extends Node3D


var is_mouse_inside: = false


var last_event_pos2D: = Vector2()


var last_event_time: = -1.0

@export var node_viewport: SubViewport
@export var node_quad: MeshInstance3D
@export var node_area: Area3D

func _ready() -> void :
	node_area.mouse_entered.connect(_mouse_entered_area)
	node_area.mouse_exited.connect(_mouse_exited_area)
	node_area.input_event.connect(_mouse_input_event)











func _mouse_entered_area() -> void :
	is_mouse_inside = true

	node_viewport.notification(NOTIFICATION_VP_MOUSE_ENTER)


func _mouse_exited_area() -> void :

	node_viewport.notification(NOTIFICATION_VP_MOUSE_EXIT)
	is_mouse_inside = false


func _unhandled_input(event: InputEvent) -> void :

	for mouse_event in [InputEventMouseButton, InputEventMouseMotion, InputEventScreenDrag, InputEventScreenTouch]:
		if is_instance_of(event, mouse_event):


			return
	node_viewport.push_input(event)


func _mouse_input_event(_camera: Camera3D, event: InputEvent, event_position: Vector3, _normal: Vector3, _shape_idx: int) -> void :

	var quad_mesh_size: Vector2 = node_quad.mesh.size


	var event_pos3D: = event_position


	var now: = Time.get_ticks_msec() / 1000.0



	event_pos3D = node_quad.global_transform.affine_inverse() * event_pos3D



	var event_pos2D: = Vector2()

	if is_mouse_inside:

		event_pos2D = Vector2(event_pos3D.x, - event_pos3D.y)



		event_pos2D.x = event_pos2D.x / quad_mesh_size.x
		event_pos2D.y = event_pos2D.y / quad_mesh_size.y

		event_pos2D.x += 0.5
		event_pos2D.y += 0.5


		event_pos2D.x *= node_viewport.size.x
		event_pos2D.y *= node_viewport.size.y


	elif last_event_pos2D != null:

		event_pos2D = last_event_pos2D


	event.position = event_pos2D
	if event is InputEventMouse:
		event.global_position = event_pos2D


	if event is InputEventMouseMotion or event is InputEventScreenDrag:

		if last_event_pos2D == null:
			event.relative = Vector2(0, 0)


		else:
			event.relative = event_pos2D - last_event_pos2D
			event.velocity = event.relative / (now - last_event_time)


	last_event_pos2D = event_pos2D


	last_event_time = now


	node_viewport.push_input(event)
