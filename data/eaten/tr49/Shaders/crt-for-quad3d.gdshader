shader_type spatial;
render_mode unshaded;

uniform sampler2D screen_texture : source_color;
uniform sampler2D mask_texture : source_color;
uniform sampler2D radial_texture : source_color;
uniform float blur_effect : hint_range(0.0, 1.0);
uniform float turn_off_effect : hint_range(0.0, 1.0);
uniform float ripple_progress : hint_range(0.0, 1.0);
uniform float extra_brightness : hint_range(0.0, 3.0) = 1.0;
uniform float reduce_glitch_effects : hint_range(0.0, 1.0) = 0.0;


vec4 get_blurred_texture(sampler2D tex, vec2 uv) {
	vec4 tex_color = texture(tex, uv);

	// Sample neighboring pixels for blur
	vec4 blur = vec4(0.0);
	float blur_strength = 0.50;
	float offset = (0.8+(0.4*blur_effect)) / 256.0;

	blur += texture(tex, uv + vec2(-offset,  0.0));
	blur += texture(tex, uv + vec2( offset,  0.0));
	blur += texture(tex, uv + vec2( 0.0, -offset));
	blur += texture(tex, uv + vec2( 0.0,  offset));
	blur += texture(tex, uv + vec2(-offset, -offset));
	blur += texture(tex, uv + vec2( offset, -offset));
	blur += texture(tex, uv + vec2(-offset,  offset));
	blur += texture(tex, uv + vec2( offset,  offset));
	blur /= 8.0;

    vec4 original_tex_color = texture(tex, uv);
	return mix(original_tex_color + blur * blur_strength, blur, blur_effect);
}

void fragment() {
	
	vec2 uv = UV;

	// Barrel distortion
	const float barrel_effect_strength = 0.25;
	const float barrel_effect_compensate_scale = 1.06;
	vec2 center = uv - 0.5;
	float dist = dot(center, center);
	uv += center * dist * barrel_effect_strength;
	uv = ((uv - 0.5) / barrel_effect_compensate_scale) + 0.5;

	// Ripple effect (like ripples on a pond)
	float ripple_brightness = 1.0;
	if (ripple_progress < 1.0) {
		vec2 ripple_center = vec2(0.5);
		vec2 ripple_offset = uv - ripple_center;
		float ripple_distance = length(ripple_offset);
		
		float fade_in_duration = 0.08;
		float fade_in_progress = 1.0;
		if (ripple_progress < fade_in_duration) {
			fade_in_progress = ripple_progress / fade_in_duration;
		}
		
		// Create expanding ripple waves
		float ripple_wave = ripple_distance * 8.0 - ripple_progress * 4.0;
		float ripple_strength = sin(ripple_wave * PI * 2.0) * 0.5 + 0.5;
		
		// Fade out as ripple expands and as effect ends
		float ripple_fade = 1.0 - smoothstep(0.0, 0.8, ripple_progress);
		ripple_strength *= ripple_fade * fade_in_progress;
		
		// Fade out towards screen edges (circular mask)
		float edge_distance = ripple_distance;
		float edge_fade_start = 0.3;
		float edge_fade_end = 0.45;
		float edge_fade = 1.0 - smoothstep(edge_fade_start, edge_fade_end, edge_distance);
		ripple_strength *= edge_fade;
		
		// Apply ripple distortion (push outward from center)
		vec2 ripple_direction = normalize(ripple_offset);
		// Use (1.0 - ripple_progress) to maintain stronger effect at start
		float ripple_amount = ripple_strength * 0.045 * (1.0 - ripple_progress);
		uv += ripple_direction * ripple_amount;
		
		// Calculate brightness boost for ripple effect
		ripple_brightness = 1.0 + 20.0 * ripple_strength * 0.3 * fade_in_progress;
	}

	// Discard outside visible area after distortion
	if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
		discard;
	}

	// Circular mask
	float mask_alpha = texture(mask_texture, uv).a;
	if (mask_alpha < 0.01) {
		discard;
	}

	// CRT shimmer & wibble
	if (reduce_glitch_effects < 0.5) {
		float shimmer = 0.0004 * sin(uv.y * 200.0 + TIME * 30.0);
		float wibble  = 0.001  * sin(uv.y * 12.0  + TIME * 2.0);
		float vWave   = 0.001  * sin(uv.x * 10.0  + TIME * 2.0);
		uv.x += wibble + shimmer;
		uv.y += vWave;
	}

    float fade_out_scale = turn_off_effect;
    vec2 screen_center = vec2(0.5);
    vec2 from_center = uv - screen_center;
    vec2 screen_texture_uv = from_center / fade_out_scale + screen_center;

	// Clamp UV coordinates to prevent texture repetition
	vec2 screen_texture_uv_clamped = clamp(screen_texture_uv, vec2(0.0), vec2(1.0));

	// Spin the screen a bit when turning on and off
	if( turn_off_effect < 1.0 ) {
		float rotation_angle = (1.0-turn_off_effect) * 0.5 * PI;
		vec2 to_center = screen_texture_uv_clamped - vec2(0.5);
		float cos_a = cos(rotation_angle);
		float sin_a = sin(rotation_angle);
		vec2 rotated = vec2(
			to_center.x * cos_a - to_center.y * sin_a,
			to_center.x * sin_a + to_center.y * cos_a
		);
		screen_texture_uv_clamped = rotated + vec2(0.5);
	}
	vec4 tex_color;
	if (reduce_glitch_effects >= 0.5) {
		tex_color = texture(screen_texture, screen_texture_uv_clamped);
	} else {
		tex_color = get_blurred_texture(screen_texture, screen_texture_uv_clamped);
	}
	vec3 color = tex_color.rgb;

	// Radial scanline / vignette texture (rotating)
	vec2 centre = vec2(0.5);
	float angle = 0.5 * TIME * (1.0 - reduce_glitch_effects);
	vec2 rotUV = screen_texture_uv - centre;
	rotUV = vec2(
		rotUV.x * cos(angle) - rotUV.y * sin(angle),
		rotUV.x * sin(angle) + rotUV.y * cos(angle)
	);
	rotUV += centre;
    
	float radialAlpha = texture(radial_texture, rotUV).r;
	if (length(rotUV - screen_center) > 0.5) {
		radialAlpha = 0.0;
	}
	color *= radialAlpha;
	
	// Apply ripple brightness boost
	color *= ripple_brightness;
	
	// Fade in during the first 10% of the turn-off effect (when turning on)
	float fade_alpha = 1.0;
    float final_fade_distance = 0.05;
	if (turn_off_effect < final_fade_distance) {
		float fade_progress = turn_off_effect / 0.05; // 0.0 to 1.0 in first 10%
		fade_alpha = fade_progress;
	}

	// Brighten central screen dot when turning on and off
    vec2 offset_from_center = UV - screen_center;
    color *= mix(10.0, 1.0, turn_off_effect);
    
    // Fade out screen edges
    float screen_edge_fade = 1.0;
    float radius = length(offset_from_center);
    float ramp_center = turn_off_effect;
    float ramp_width = 0.2;
    float ramp_start = ramp_center - ramp_width * 0.5;
    float ramp_end = ramp_center + ramp_width * 0.5;
    screen_edge_fade = 1.0 - smoothstep(ramp_start, ramp_end, 2.0 * radius);
	
	ALBEDO = extra_brightness * (color * screen_edge_fade * fade_alpha);
	ALPHA = mask_alpha;
	EMISSION = color * screen_edge_fade * fade_alpha * extra_brightness;
}

