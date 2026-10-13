"""Vaca minimalista de perfil: corpo oval, cabeca redonda, duas patas e
manchas circulares que trocam de cor juntas pela tecla 2."""

import moderngl

from geometrias import curva_circulo, curva_elipse, quad


class Vaca:
    BRANCO = (0.95, 0.95, 0.92, 1.0)  # corpo e patas
    BEGE = (0.93, 0.89, 0.80, 1.0)  # cabeca
    PALETA_MANCHAS = (
        (0.12, 0.10, 0.10, 1.0),  # preto
        (0.45, 0.28, 0.15, 1.0),  # marrom
        (0.55, 0.55, 0.55, 1.0),  # cinza
    )
    MANCHA = None  # marcador: desenhar() troca por self.cor_manchas

    def __init__(self, ctx, prog):
        """Monta os VAOs das partes em coords locais; cabeca e manchas
        dividem o mesmo VAO de circulo."""
        self.prog = prog
        self.posicao = (0.30, -0.55)  # patas apoiadas no chao
        self.indice_manchas = 0
        self.cor_manchas = self.PALETA_MANCHAS[0]
        self.recursos = []

        def novo_vao(vertices):
            vbo = ctx.buffer(vertices.tobytes())
            vao = ctx.vertex_array(prog, [(vbo, "4f", "vPosition")])
            self.recursos.append((vao, vbo))
            return vao

        circulo = novo_vao(curva_circulo())
        self.partes = (
            (novo_vao(quad(-0.13, 0.0, -0.09, 0.10)), 1.0, (0.0, 0.0),
             self.BRANCO, moderngl.TRIANGLE_FAN),  # pata traseira
            (novo_vao(quad(0.07, 0.0, 0.11, 0.10)), 1.0, (0.0, 0.0),
             self.BRANCO, moderngl.TRIANGLE_FAN),  # pata dianteira
            (novo_vao(curva_elipse(0.16, 0.11)), 1.0, (0.0, 0.18),
             self.BRANCO, moderngl.TRIANGLE_FAN),  # corpo
            (circulo, 0.045, (-0.06, 0.20), self.MANCHA, moderngl.TRIANGLE_FAN),
            (circulo, 0.035, (0.05, 0.15), self.MANCHA, moderngl.TRIANGLE_FAN),
            (circulo, 0.040, (0.10, 0.23), self.MANCHA, moderngl.TRIANGLE_FAN),
            (circulo, 0.07, (0.18, 0.30),
             self.BEGE, moderngl.TRIANGLE_FAN),  # cabeca
        )

    def desenhar(self):
        """Escreve uniforms por parte (posicao + offset local) e renderiza."""
        px, py = self.posicao
        for vao, escala, (ox, oy), cor, modo in self.partes:
            self.prog["u_escala"].value = escala
            self.prog["u_deslocamento"].value = (px + ox, py + oy)
            self.prog["u_cor"].value = cor if cor is not None else self.cor_manchas
            vao.render(modo)

    def ciclar_manchas(self):
        """Avanca a paleta; a mesma cor vale para todas as manchas juntas."""
        self.indice_manchas = (self.indice_manchas + 1) % len(self.PALETA_MANCHAS)
        self.cor_manchas = self.PALETA_MANCHAS[self.indice_manchas]

    def liberar(self):
        """Libera VAOs e VBOs."""
        for vao, vbo in self.recursos:
            vao.release()
            vbo.release()
