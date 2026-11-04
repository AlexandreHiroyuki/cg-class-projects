#version 400 core

in vec4 v2fcolor;
uniform float u_brilho;
out vec4 outfragcolor;

void main() {
    outfragcolor = vec4(v2fcolor.rgb * u_brilho, v2fcolor.a);
}
