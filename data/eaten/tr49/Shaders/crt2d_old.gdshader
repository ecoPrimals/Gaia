shader_type canvas_item;

uniform sampler2D card_texture_1 : source_color;
uniform sampler2D intermediate_texture : source_color;
uniform sampler2D card_texture_2 : source_color;
uniform sampler2D mask_texture : source_color;
uniform sampler2D radial_texture : source_color;

uniform float card_lerp : hint_range(-0.5, 1.5);
uniform float hidden_image_alpha : hint_range(0.0, 1.0);

// ── Twist parameters you can tweak ───────────────────────────────
const float TWIST_INNER_MAX = 2.0;          // radians at centre (when card_lerp==0.5)
const float TWIST_OUTER_MAX = -2.5;   // radians at edge   (≈180°)
const float TWIST_CURVE     = 1.0;          // >1 ⇒ twist grows faster near edge
// ----------------------------------------------------------------

const float hidden_image_drift_speed = 3.0;

void vertex() {
	// Called for every vertex the material is visible on.
}

vec4 get_blurred_texture(sampler2D tex, vec2 uv) {
	vec4 tex_color = texture(tex, uv);

	// Sample neighboring pixels for blur
	vec4 blur = vec4(0.0);
	float blur_strength = 0.50;
	float offset = 1.0 / 256.0;

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
	return original_tex_color + blur * blur_strength;
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

	// Trim to post-barrel-distortion 0-1 range
	if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
		discard;
	}

	// Circle mask
	float mask_alpha = texture(mask_texture, uv).a;
	if( mask_alpha < 0.01 ) {
		discard;
	}

	// CRT wibble: horizontal sine wave, vertical scanlines, and slight barrel distortion
	float shimmer = 0.0004 * sin(uv.y * 200.0 + TIME * 30.0); // small scale horizontal wave
	float wibble = 0.001 * sin(uv.y * 12.0 + TIME * 2.0);    // large scale horizontal wave
	float verticalWave = 0.001 * sin(uv.x * 10.0 + TIME * 2.0); // large scale vertical wave
	uv.x += wibble + shimmer;
	uv.y += verticalWave;

	// ── Radial "twist" that comes & goes with the wipe ────────────
	vec2 uv_twisted = uv;                              // default (no twist)
	vec2 uv_twisted_opposite = uv;                     // default (no twist)

	// Texture 1: untwisted at card_lerp=0 (when visible), twisted at card_lerp=1 (when fading out)
	float twist_env_1 = card_lerp;      // can overshoot <0 or >1

	// Texture 3: twisted at card_lerp=0 (when fading out), untwisted at card_lerp=1 (when visible)
	float twist_env_3 = 1.0 - card_lerp; // can overshoot <0 or >1

	// Apply twist to texture 1
	if (abs(twist_env_1) > 0.0001) {
		vec2  diff        = uv - vec2(0.5);
		float r           = length(diff);
		float radial_wt   = pow(clamp(r * 2.0, 0.0, 1.0), TWIST_CURVE);
		float twist_angle = mix(TWIST_INNER_MAX, TWIST_OUTER_MAX, radial_wt) * twist_env_1;

		float base_angle  = atan(diff.y, diff.x) + twist_angle;
		uv_twisted        = vec2(cos(base_angle), sin(base_angle)) * r + vec2(0.5);
	}

	// Apply opposite twist to texture 3
	if (abs(twist_env_3) > 0.0001) {
		vec2  diff        = uv - vec2(0.5);
		float r           = length(diff);
		float radial_wt   = pow(clamp(r * 2.0, 0.0, 1.0), TWIST_CURVE);
		float twist_angle = mix(TWIST_INNER_MAX, TWIST_OUTER_MAX, radial_wt) * twist_env_3;

		// Negate the twist angle for opposite rotation
		float base_angle  = atan(diff.y, diff.x) - twist_angle;
		uv_twisted_opposite = vec2(cos(base_angle), sin(base_angle)) * r + vec2(0.5);
	}
	// ──────────────────────────────────────────────────────────────


    vec2 midPicUV = uv;
    midPicUV.x += 0.002 * sin(TIME * 3.27 * hidden_image_drift_speed);
	midPicUV.y += 0.016 * sin(TIME * 1.13 * hidden_image_drift_speed);

	float midScale = 0.2 * sin(TIME * hidden_image_drift_speed) + 0.9;
	midPicUV = (midPicUV - 0.5) / midScale + 0.5;

	// Simple additive blur for glow effect
	float fromMid = smoothstep(0.0, 1.0, 1.0 - (2.0 * abs(card_lerp-0.5)));

	vec4 tex_color_1 = get_blurred_texture(card_texture_1,
		(uv_twisted-0.5) * vec2(1.0 + 0.1*fromMid, 1.0 + 0.1*fromMid) + 0.5);
	vec4 intermediate_color = get_blurred_texture(intermediate_texture, midPicUV);
	vec4 tex_color_2 = get_blurred_texture(card_texture_2,
		(uv_twisted_opposite-0.5) * vec2(1.0 + 0.1*fromMid, 1.0 + 0.1*fromMid) + 0.5);

	// Radial wipe: use distance from center instead of diagonal
	const float wipe_thickness = 0.8;
	vec2 center_uv = uv - 0.5;
	float distance_from_center = length(center_uv);
	float radial = clamp(distance_from_center * 2.0, 0.0, 1.0); // Scale to 0-1 range

	// Single wipe: mostly from tex_color_1 to tex_color_2, but intermediate_color is revealed in the center of the wipe
	// DO NOT clamp card_lerp here, allow overshoot for elastic effect!
    float inner_card_lerp = mix(-wipe_thickness, 1.0+wipe_thickness, card_lerp);
	float t = inner_card_lerp; // 0.0 to 1.0 controls the wipe position
	float wipe = smoothstep(t - wipe_thickness, t + wipe_thickness, radial);

	// Blend 1 and 2, then add intermediate in the center
	vec3 color = mix(tex_color_2.rgb, tex_color_1.rgb, wipe);

	// Optionally, add a mid-wipe glow as before
	float mid_wipe_strength = 2.0 * (1.0 - abs((radial - t) / wipe_thickness));
	mid_wipe_strength = clamp(mid_wipe_strength, 0.0, 1.0);
	color += mid_wipe_strength * (tex_color_1.rgb + intermediate_color.rgb + tex_color_2.rgb) * 0.33;

    color = color + hidden_image_alpha * intermediate_color.rgb;

	//// Procedural radial scanline effect: darken concentric circles emanating from the center
	//float scanline_strength = 0.6; // how much to darken the scanline
	//float scanline_count = 1600.0;
//
	//// Create radial scanlines based on distance from center
	//float scanline = 0.5 + 0.5 * sin(distance_from_center * scanline_count);
	//float scanline_mask = mix(1.0 - scanline_strength, 1.0, pow(scanline, 0.8));
	//color *= scanline_mask;

    // Radial scanline texture, rotating over time
	vec2 center2 = vec2(0.5, 0.5);
	float angle = 0.5 * TIME;
	vec2 rotatedUV = uv - center2;
	rotatedUV = vec2(
		rotatedUV.x * cos(angle) - rotatedUV.y * sin(angle),
		rotatedUV.x * sin(angle) + rotatedUV.y * cos(angle)
	);
	rotatedUV += center2;
	float radialAlpha = texture(radial_texture, rotatedUV).r;
	color.rgb *= radialAlpha;

	COLOR = vec4(color, mask_alpha);
}
