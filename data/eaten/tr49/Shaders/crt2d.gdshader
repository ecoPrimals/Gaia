shader_type canvas_item;

uniform sampler2D screen_texture : source_color;
uniform sampler2D mask_texture : source_color;
uniform sampler2D radial_texture : source_color;
uniform float blur_effect : hint_range(0.0, 1.0);


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
	float shimmer = 0.0004 * sin(uv.y * 200.0 + TIME * 30.0);
	float wibble  = 0.001  * sin(uv.y * 12.0  + TIME * 2.0);
	float vWave   = 0.001  * sin(uv.x * 10.0  + TIME * 2.0);
	uv.x += wibble + shimmer;
	uv.y += vWave;

	// Sample screen texture with a subtle blur for glow
	vec4 tex_color = get_blurred_texture(screen_texture, uv);
	vec3 color = tex_color.rgb;

	// Radial scanline / vignette texture (rotating)
	vec2 centre = vec2(0.5);
	float angle = 0.5 * TIME;
	vec2 rotUV = uv - centre;
	rotUV = vec2(
		rotUV.x * cos(angle) - rotUV.y * sin(angle),
		rotUV.x * sin(angle) + rotUV.y * cos(angle)
	);
	rotUV += centre;
	float radialAlpha = texture(radial_texture, rotUV).r;
	color *= radialAlpha;

	COLOR = vec4(color, mask_alpha);
}

