"""Estrelas: pontos fixos espalhados pelo ceu, desenhados numa unica
chamada POINTS (tamanho definido por gl_PointSize no vertex shader)."""

import moderngl
import numpy as np


class Estrelas:
    def __init__(self, ctx, prog):
        self.prog = prog
        vertices = np.array(
            [
                (-0.92, 0.80, 0.0, 1.0),
                (-0.78, 0.42, 0.0, 1.0),
                (-0.65, 0.90, 0.0, 1.0),
                (-0.55, 0.15, 0.0, 1.0),
                (-0.45, 0.62, 0.0, 1.0),
                (-0.33, 0.30, 0.0, 1.0),
                (-0.22, 0.88, 0.0, 1.0),
                (-0.12, 0.55, 0.0, 1.0),
                (-0.05, 0.10, 0.0, 1.0),
                (0.08, 0.72, 0.0, 1.0),
                (0.18, 0.38, 0.0, 1.0),
                (0.28, 0.93, 0.0, 1.0),
                (0.38, 0.20, 0.0, 1.0),
                (0.50, 0.60, 0.0, 1.0),
                (0.62, 0.82, 0.0, 1.0),
                (0.72, 0.12, 0.0, 1.0),
                (0.82, 0.48, 0.0, 1.0),
                (0.93, 0.70, 0.0, 1.0),
            ],
            dtype="f4",
        )
        self.vbo = ctx.buffer(vertices.tobytes())
        self.vao = ctx.vertex_array(prog, [(self.vbo, "4f", "vPosition")])

    def desenhar(self):
        self.prog["u_escala"].value = 1.0
        self.prog["u_deslocamento"].value = (0.0, 0.0)
        self.prog["u_cor"].value = (0.92, 0.94, 1.0, 1.0)
        self.vao.render(moderngl.POINTS)

    def liberar(self):
        self.vao.release()
        self.vbo.release()
