"""Chao: uma faixa de grama na base da tela, com VAO e uniforms proprios."""

import moderngl

from geometrias import quad


class Chao:
    COR = (0.35, 0.60, 0.25, 1.0)  # verde grama

    def __init__(self, ctx, prog):
        self.prog = prog
        vertices = quad(-1.0, -1.0, 1.0, -0.55)
        self.vbo = ctx.buffer(vertices.tobytes())
        self.vao = ctx.vertex_array(prog, [(self.vbo, "4f", "vPosition")])

    def desenhar(self):
        self.prog["u_escala"].value = 1.0
        self.prog["u_deslocamento"].value = (0.0, 0.0)
        self.prog["u_cor"].value = self.COR
        self.vao.render(moderngl.TRIANGLE_FAN)

    def liberar(self):
        self.vao.release()
        self.vbo.release()
