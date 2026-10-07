#version 400 core

layout(location = 0) in vec4 vPosition;

out vec2 vUv;

void main() {
    gl_Position = vPosition;
    vUv = vPosition.xy * 0.5 + 0.5;
}
