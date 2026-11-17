shader_type canvas_item;
render_mode unshaded;               // we’re doing the blending

uniform float strength : hint_range(0,1) = 1.0;   // 0-1 fade
uniform sampler2D SCREEN : hint_screen_texture;   // what’s already drawn

vec3 overlay(vec3 base, vec3 top) {
    vec3 low  = 2.0 * base * top;
    vec3 high = 1.0 - 2.0 * (1.0 - base) * (1.0 - top);
    return mix(low, high, step(0.5, base));
}

void fragment() {
    vec4 top   = texture(TEXTURE,  UV)   * COLOR;        // your image
    vec3 base  = texture(SCREEN,   SCREEN_UV).rgb;       // scene behind
    vec3 blend = overlay(base, top.rgb);
    vec3 result = mix(base, blend, top.a * strength);    // respect alpha
    COLOR = vec4(result, 1.0);
}