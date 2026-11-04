#version 400 core
// Um unico buffer (quadrado, circulo ou triangulo) desenhado varias vezes.
// Posicao, escala, rotacao e cor vem de uniforms: o VBO nao muda.

layout(location = 0) in vec4 vPosition;

uniform vec2 u_escala;
uniform vec2 u_deslocamento;
uniform float u_rotacao;
uniform vec4 u_cor;

out vec4 v2fcolor;

void main() {
    vec2 p = vPosition.xy * u_escala;
    float c = cos(u_rotacao);
    float s = sin(u_rotacao);
    vec2 girado = vec2(c * p.x - s * p.y, s * p.x + c * p.y);
    gl_Position = vec4(girado + u_deslocamento, 0.0, 1.0);
    v2fcolor = u_cor;
}
