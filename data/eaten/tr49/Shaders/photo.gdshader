// Simple shader for rendering images on the screen:
//  - applies a mask so that we can automatically make annie's art circular
//    with a feathering/vignette effect at the edges
//  - also multiplies by a colour so we can turn a black and white
//    thing into more of a green-screen effect
shader_type canvas_item;

uniform sampler2D alpha_mask;
uniform vec4 tint_color : source_color;
uniform float mask_scale : hint_range(0.0, 1.0) = 1.0;

void fragment() {
    vec4 main_col = texture(TEXTURE, UV);
    vec2 centered_uv = (UV - 0.5) / mask_scale + 0.5;
    float alpha = texture(alpha_mask, centered_uv).a;
    COLOR = vec4(main_col.rgb * tint_color.rgb, alpha * tint_color.a);
}