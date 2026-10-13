"""Astro: generalizacao de sol.py — a mesma classe gera sol e lua,
com cor, posicao e escala recebidos por instancia."""

import moderngl

from geometrias import curva_circulo


class Astro:
    def __init__(self, ctx, prog, cor, posicao, escala):
        self.prog = prog
        self.cor = cor
        self.posicao = posicao
        self.escala = escala
        vertices = curva_circulo()
        self.vbo = ctx.buffer(vertices.tobytes())
        self.vao = ctx.vertex_array(prog, [(self.vbo, "4f", "vPosition")])

    def desenhar(self):
        self.prog["u_escala"].value = self.escala
        self.prog["u_deslocamento"].value = self.posicao
        self.prog["u_cor"].value = self.cor
        self.vao.render(moderngl.TRIANGLE_FAN)

    def liberar(self):
        self.vao.release()
        self.vbo.release()
