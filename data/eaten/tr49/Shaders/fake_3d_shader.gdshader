shader_type canvas_item;

uniform float flip_amount : hint_range(-1.0, 1.0); // -1 = fully flipped left, 0 = front-facing, 1 = flipped right
uniform vec2 size = vec2(800.0, 800.0);

void vertex() {
    float angle = flip_amount * PI; // Convert to radians
    float scale_y = cos(angle); // compress the width
    float scale_x = 0.2 * sin(angle) + 1.0; // compress the width

    VERTEX -= 0.5 * size; // shift to center
    VERTEX.y *= scale_y;      // squash Y as we "rotate"
    VERTEX.x *= mix(1.0 - (scale_x - 1.0), scale_x, step(UV.y, 0.5));
    VERTEX += 0.5 * size; // shift back
}