shader_type spatial;

uniform sampler2D albedo_texture : source_color;
uniform float mipmap_bias : hint_range(-3.0, 3.0) = -1.0;

// Lighting texture (same as floor.gdshader)
uniform sampler2D lighting_texture : hint_default_white;
uniform float lighting_intensity : hint_range(0.0, 10.0) = 1.0;

// Hardcoded floor plane parameters
const vec3 floor_center = vec3(-0.039, 0.0, -3.61);
const vec2 floor_size = vec2(10.958, 11.254);

// Varying variable to pass floor UVs from vertex to fragment shader
varying vec2 floor_uv;

void vertex() {
    // Calculate world position of this vertex
    vec3 world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
    
    // Map world position to floor lighting texture coordinates
    floor_uv = (world_pos.xz - floor_center.xz) / floor_size + 0.5;
}

void fragment() {
    // Sample the wire texture
    vec4 albedo_tex = texture(albedo_texture, UV, mipmap_bias);
    vec3 wire_color = albedo_tex.rgb;
    
    // Sample the lighting texture using pre-calculated UVs
    vec4 lighting_color = texture(lighting_texture, floor_uv);
    
    // Apply lighting to the wire color
    vec3 final_color = wire_color * lighting_color.rgb * lighting_intensity;
    
    ALBEDO = final_color;
    ALPHA = albedo_tex.a;
}
