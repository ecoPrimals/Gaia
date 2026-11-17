shader_type spatial;

uniform sampler2D viewport_tex;
uniform sampler2D mask_tex;

void fragment() {
    vec4 albedo_tex = texture(viewport_tex, UV);
    vec4 viewport_col = texture(viewport_tex, UV);
    vec4 mask_col = texture(mask_tex, UV);

    ALBEDO = albedo_tex.rgb;
    EMISSION = viewport_col.rgb * mask_col.rgb;
	ALPHA = albedo_tex.a;
}