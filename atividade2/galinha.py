"""Galinha: corpo, cabeca, bico e rabo como partes com uniforms proprios."""

import moderngl
from geometrias import curva_circulo, curva_elipse, triangulo


def _invade(x, y, local, caixa):
    lx0, ly0, lx1, ly1 = local
    cx0, cy0, cx1, cy1 = caixa
    ax0, ay0 = x + lx0, y + ly0
    ax1, ay1 = x + lx1, y + ly1
    return ax0 < cx1 and ax1 > cx0 and ay0 < cy1 and ay1 > cy0


def _contornar(origem, novo, y, local, caixa):
    """Se o passo entra na caixa, encosta no lado de onde o animal veio."""
    if not _invade(novo, y, local, caixa):
        return novo
    lx0, _, lx1, _ = local
    cx0, _, cx1, _ = caixa
    if origem + (lx0 + lx1) / 2 < (cx0 + cx1) / 2:
        return cx0 - lx1
    return cx1 - lx0


class Galinha:
    BRANCO = (0.97, 0.97, 0.95, 1.0)
    LARANJA = (0.95, 0.55, 0.10, 1.0)  # bico
    VERMELHO = (0.80, 0.15, 0.12, 1.0)  # rabo
    CAIXA_COLISAO = (-0.12, 0.0, 0.125, 0.175)
    LIMITE_X = (-1.0 - CAIXA_COLISAO[0], 1.0 - CAIXA_COLISAO[2])

    def __init__(self, ctx, prog):
        self.prog = prog
        self.posicao = (-0.20, -0.55)  # pe apoiado no chao
        bico = triangulo((0.09, 0.145), (0.125, 0.13), (0.09, 0.115))
        rabo = triangulo((-0.07, 0.10), (-0.12, 0.16), (-0.05, 0.14))
        geometrias = (
            (
                curva_elipse(0.075, 0.06),
                1.0,
                (0.0, 0.07),
                self.BRANCO,
                moderngl.TRIANGLE_FAN,
            ),  # corpo
            (
                curva_circulo(),
                0.035,
                (0.07, 0.14),
                self.BRANCO,
                moderngl.TRIANGLE_FAN,
            ),  # cabeca
            (bico, 1.0, (0.0, 0.0), self.LARANJA, moderngl.TRIANGLES),
            (rabo, 1.0, (0.0, 0.0), self.VERMELHO, moderngl.TRIANGLES),
        )
        self.recursos = []
        self.partes = []
        for vertices, escala, offset, cor, modo in geometrias:
            vbo = ctx.buffer(vertices.tobytes())
            vao = ctx.vertex_array(prog, [(vbo, "4f", "vPosition")])
            self.recursos.append((vao, vbo))
            self.partes.append((vao, escala, offset, cor, modo))

    def desenhar(self):
        px, py = self.posicao
        for vao, escala, (ox, oy), cor, modo in self.partes:
            self.prog["u_escala"].value = escala
            self.prog["u_deslocamento"].value = (px + ox, py + oy)
            self.prog["u_cor"].value = cor
            vao.render(modo)

    def andar(self, dx, caixa=None):
        """Desloca no x, dentro da tela e sem entrar na caixa da casa."""
        x, y = self.posicao
        novo = min(max(x + dx, self.LIMITE_X[0]), self.LIMITE_X[1])
        if caixa is not None:
            novo = _contornar(x, novo, y, self.CAIXA_COLISAO, caixa)
            novo = min(max(novo, self.LIMITE_X[0]), self.LIMITE_X[1])
            if _invade(novo, y, self.CAIXA_COLISAO, caixa):
                return
        self.posicao = (novo, y)

    def liberar(self):
        for vao, vbo in self.recursos:
            vao.release()
            vbo.release()
