"""Bangalo de madeira: corpo, telhado com cor ciclica e contornos em LINE_LOOP."""

import moderngl
from geometrias import quad, triangulo


class Bangalo:
    """Pecas em coordenadas locais; self.posicao desloca o conjunto inteiro."""

    PALETA_TELHADO = (
        (0.62, 0.22, 0.15, 1.0),  # vermelho-telha
        (0.30, 0.45, 0.20, 1.0),  # verde-musgo
        (0.20, 0.30, 0.55, 1.0),  # azul-ardosia
    )
    COR_MADEIRA = (0.62, 0.42, 0.25, 1.0)
    COR_CONTORNO = (0.15, 0.08, 0.04, 1.0)
    CAIXA_COLISAO = (-0.25, 0.0, 0.25, 0.38)

    def __init__(self, ctx, prog):
        self.prog = prog
        self.posicao = (-0.60, -0.55)  # base do corpo apoiada no chao
        self.i_telhado = 0

        # cor None = cor ciclica do telhado, resolvida na paleta a cada frame
        pecas = (
            (quad(-0.25, 0.0, 0.25, 0.38), self.COR_MADEIRA, moderngl.TRIANGLE_FAN),
            (
                triangulo((-0.30, 0.38), (0.30, 0.38), (0.0, 0.62)),
                None,
                moderngl.TRIANGLES,
            ),
            (quad(-0.06, 0.0, 0.06, 0.22), self.COR_CONTORNO, moderngl.LINE_LOOP),
            (quad(0.08, 0.15, 0.18, 0.28), self.COR_CONTORNO, moderngl.LINE_LOOP),
        )
        self.vaos = []
        self.vbos = []
        self.partes = []
        for vertices, cor, modo in pecas:
            vbo = ctx.buffer(vertices.tobytes())
            vao = ctx.vertex_array(prog, [(vbo, "4f", "vPosition")])
            self.vbos.append(vbo)
            self.vaos.append(vao)
            self.partes.append((vao, 1.0, (0.0, 0.0), cor, modo))

    def caixa(self):
        """Retangulo solido do corpo, em coordenadas da tela."""
        px, py = self.posicao
        x0, y0, x1, y1 = self.CAIXA_COLISAO
        return (px + x0, py + y0, px + x1, py + y1)

    def ciclar_telhado(self):
        """Avanca o telhado para a proxima cor da paleta (tecla 1)."""
        self.i_telhado = (self.i_telhado + 1) % len(self.PALETA_TELHADO)

    def desenhar(self):
        px, py = self.posicao
        for vao, escala, (ox, oy), cor, modo in self.partes:
            self.prog["u_escala"].value = escala
            self.prog["u_deslocamento"].value = (px + ox, py + oy)
            self.prog["u_cor"].value = (
                cor if cor else self.PALETA_TELHADO[self.i_telhado]
            )
            vao.render(modo)

    def liberar(self):
        for vao in self.vaos:
            vao.release()
        for vbo in self.vbos:
            vbo.release()
