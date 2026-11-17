shader_type canvas_item;

uniform sampler2D screen_texture : source_color;
uniform sampler2D radial_texture : source_color;

varying vec4 modulate;
void vertex()
{
    modulate = COLOR;
}

vec4 get_blurred_texture(sampler2D tex, vec2 uv) {
	vec4 tex_color = texture(tex, uv);

	// Sample neighboring pixels for blur
	vec4 blur = vec4(0.0);
	float blur_strength = 0.7;
	float blur_radius = 0.5;
	float blur_final_mix = 0.1;
	float offset = blur_radius / 256.0;

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
	return mix(original_tex_color + blur * blur_strength, blur, blur_final_mix);
}

void fragment() {
	
    // Apply a pincushion effect to UV to create a new UV coordinate
    // Pincushion: push pixels outward from center, opposite of barrel distortion
    // Apply barrel distortion and compensate so the effect reaches the top/bottom edges
    vec2 barrel_uv = UV;
    vec2 from_center = UV - vec2(0.5);
    float dist = dot(from_center, from_center);
    float barrel_strength = 0.4; // positive for barrel
    barrel_uv += from_center * dist * barrel_strength;

    // Compensate for the shrinking caused by barrel distortion
    // Find the maximum distance from center to a corner after distortion
    // For a square, the farthest point is (0.5, 0.5)
    float max_dist = dot(vec2(0.5, 0.5), vec2(0.5, 0.5));
    float max_barrel = 1.0 + barrel_strength * max_dist;
    barrel_uv = (barrel_uv - vec2(0.5)) / max_barrel + vec2(0.5);
	
	vec4 color = get_blurred_texture(screen_texture, barrel_uv);
	
    // Aspect-fit the square radial texture to the current viewport
    // Get the aspect ratio of the screen
    float aspect = float(SCREEN_PIXEL_SIZE.x) / float(SCREEN_PIXEL_SIZE.y);

    // Centered UV
    vec2 centered_uv = barrel_uv - vec2(0.5);

    // Scale UV so the largest axis fits [-0.5, 0.5] (aspect fit)
    vec2 fit_uv;
    if (aspect > 1.0) {
        // Wider than tall: scale x
        fit_uv = vec2(centered_uv.x / aspect, centered_uv.y);
    } else {
        // Taller than wide: scale y
        fit_uv = vec2(centered_uv.x, centered_uv.y * aspect);
    }
    // Map back to [0,1]
    vec2 radial_uv = fit_uv + vec2(0.5);

    // Rotate radial_uv around its center (0.5, 0.5) according to TIME
    float angle = TIME * 0.5;
    vec2 uv_from_center = radial_uv - vec2(0.5);
    float cos_a = cos(angle);
    float sin_a = sin(angle);
    vec2 rotated_uv = vec2(
        uv_from_center.x * cos_a - uv_from_center.y * sin_a,
        uv_from_center.x * sin_a + uv_from_center.y * cos_a
    );
    radial_uv = rotated_uv + vec2(0.5);

    float radialAlpha = texture(radial_texture, radial_uv).g * 0.8;
    if (length(fit_uv) > 0.5) {
        radialAlpha = 0.0;
    }
    // Photoshop "Overlay" blend mode for radialAlpha
    // Overlay formula: if base < 0.5: 2*base*blend, else: 1 - 2*(1-base)*(1-blend)
    color.rgb = mix(
        2.0 * color.rgb * radialAlpha,
        1.0 - 2.0 * (1.0 - color.rgb) * (1.0 - radialAlpha),
        step(0.5, color.rgb)
    );
    color.rgb = color.rgb * vec3(radialAlpha);

	COLOR = color * modulate;
}