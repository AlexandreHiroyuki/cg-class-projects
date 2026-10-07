#version 400 core

// Linhas verticais. Cada camada tem um comprimento e uma velocidade.
// u_tempo empurra a linha para baixo; ao sair da tela, ela volta em cima.

in vec2 vUv;
uniform float u_tempo;
out vec4 outfragcolor;

float camada(vec2 uv, float colunas, float comprimento, float velocidade) {
    float i = floor(uv.x * colunas);
    float linha = step(fract(uv.x * colunas), 0.08);
    float y = fract(uv.y + i * 0.37 + u_tempo * velocidade);
    return linha * step(y, comprimento);
}

void main() {
    float r = camada(vUv, 28.0, 0.12, 0.45);
    r += camada(vUv + vec2(0.2, 0.0), 16.0, 0.24, 0.70);
    r += camada(vUv + vec2(0.5, 0.0), 9.0, 0.40, 1.00);
    outfragcolor = vec4(0.75, 0.82, 0.92, clamp(r, 0.0, 0.85));
}
