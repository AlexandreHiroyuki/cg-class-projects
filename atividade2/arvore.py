"""Arvore do sitio: tronco de quad marrom e copa circular com paleta ciclica."""

import moderngl

from geometrias import curva_circulo, quad


class Arvore:
    PALETA_COPA = (
        (0.22, 0.50, 0.20, 1.0),  # verde
        (0.10, 0.32, 0.10, 1.0),  # verde-escuro
        (0.85, 0.45, 0.10, 1.0),  # outono alaranjado
    )
    ESCALA_COPA = 0.22
    OFFSET_COPA = (0.0, 0.42)

    def __init__(self, ctx, prog):
        """Monta os VAOs das partes em coords locais ao redor da origem."""
        self.prog = prog
        self.posicao = (0.55, -0.55)  # base do tronco no chao
        self.indice_copa = 0

        # cor None = cor ciclica da copa, resolvida na paleta a cada frame
        dados = (
            (quad(-0.03, 0.0, 0.03, 0.30), 1.0, (0.0, 0.0), (0.40, 0.25, 0.12, 1.0)),
            (curva_circulo(), self.ESCALA_COPA, self.OFFSET_COPA, None),
        )
        self.vbos = []
        self.partes = []
        for vertices, escala, offset, cor in dados:
            vbo = ctx.buffer(vertices.tobytes())
            vao = ctx.vertex_array(prog, [(vbo, "4f", "vPosition")])
            self.vbos.append(vbo)
            self.partes.append((vao, escala, offset, cor, moderngl.TRIANGLE_FAN))

    def desenhar(self):
        """Escreve uniforms por parte (posicao + offset local) e renderiza."""
        px, py = self.posicao
        for vao, escala, (ox, oy), cor, modo in self.partes:
            self.prog["u_escala"].value = escala
            self.prog["u_deslocamento"].value = (px + ox, py + oy)
            self.prog["u_cor"].value = cor if cor is not None else self.PALETA_COPA[self.indice_copa]
            vao.render(modo)

    def ciclar_copa(self):
        """Avanca a cor da copa na paleta, voltando ao inicio no fim."""
        self.indice_copa = (self.indice_copa + 1) % len(self.PALETA_COPA)

    def liberar(self):
        """Libera VAOs e VBOs."""
        for vao, *_resto in self.partes:
            vao.release()
        for vbo in self.vbos:
            vbo.release()
