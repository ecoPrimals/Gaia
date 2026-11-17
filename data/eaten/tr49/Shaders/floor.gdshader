shader_type spatial;
render_mode blend_mix;

// Floor tile texture (repeating)
uniform sampler2D floor_texture : source_color;
uniform float tile_scale_x : hint_range(0.1, 10.0) = 1.0;
uniform float tile_scale_y : hint_range(0.1, 10.0) = 1.0;

// Lighting texture (non-repeating, covers whole plane)
uniform sampler2D lighting_texture : hint_default_white;
uniform float lighting_power_curve : hint_range(0.01, 10.0) = 1.0;
uniform float lighting_intensity : hint_range(0.0, 10.0) = 1.0;

void vertex() {
	// No vertex modifications needed
}

void fragment() {
	// Calculate UV coordinates for floor tiles (repeating, scaled from center)
	vec2 centered_uv = UV - 0.5; // Center the UV coordinates
	vec2 tile_uv = centered_uv * vec2(tile_scale_x, tile_scale_y) + 0.5; // Scale from center and offset back
	
	// Sample the floor texture with repeating UVs
	vec4 floor_color = texture(floor_texture, tile_uv);
	
	// Sample the lighting texture with non-repeating UVs (UV coordinates stay as-is)
	vec4 lighting_color = pow(texture(lighting_texture, UV), vec4(lighting_power_curve));
	
	// Multiply the floor color by the lighting texture
	vec4 final_color = floor_color * lighting_color * lighting_intensity;
	
	// Output the final color
	ALBEDO = final_color.rgb;
	
	// Fade out at left/right and far edges (but not near edge)
    float edge_start = 0.32;
    float edge_end = 0.5;
    vec2 centered = UV - 0.5;
    float distX = abs(centered.x);
    float distY = max(0.0, -centered.y);
    float dist = max(distX, distY); // box-ish fade
    float alpha = 1.0 - smoothstep(edge_start, edge_end, dist);
    ALPHA = clamp(alpha, 0.0, 1.0);
}
