shader_type spatial;
render_mode blend_add, unshaded;

uniform sampler2D texture_albedo : source_color, hint_default_white;
uniform float alpha_multiplier : hint_range(0.0, 1.0) = 1.0;

void fragment() {
	vec4 tex_color = texture(texture_albedo, UV);
	ALBEDO = tex_color.rgb;
	ALPHA = alpha_multiplier * tex_color.a;
}
