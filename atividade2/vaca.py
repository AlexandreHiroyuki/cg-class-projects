"""Vaca minimalista de perfil: corpo oval, cabeca redonda, duas patas e
manchas circulares que trocam de cor juntas pela tecla 2."""

import moderngl
from geometrias import curva_circulo, curva_elipse, quad


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


class Vaca:
    BRANCO = (0.95, 0.95, 0.92, 1.0)  # corpo e patas
    BEGE = (0.93, 0.89, 0.80, 1.0)  # cabeca
    PALETA_MANCHAS = (
        (0.12, 0.10, 0.10, 1.0),  # preto
        (0.45, 0.28, 0.15, 1.0),  # marrom
        (0.55, 0.55, 0.55, 1.0),  # cinza
    )
    MANCHA = None  # marcador: desenhar() troca por self.cor_manchas
    CAIXA_COLISAO = (-0.16, 0.0, 0.25, 0.37)
    LIMITE_X = (-1.0 - CAIXA_COLISAO[0], 1.0 - CAIXA_COLISAO[2])

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
            (
                novo_vao(quad(-0.13, 0.0, -0.09, 0.10)),
                1.0,
                (0.0, 0.0),
                self.BRANCO,
                moderngl.TRIANGLE_FAN,
            ),  # pata traseira
            (
                novo_vao(quad(0.07, 0.0, 0.11, 0.10)),
                1.0,
                (0.0, 0.0),
                self.BRANCO,
                moderngl.TRIANGLE_FAN,
            ),  # pata dianteira
            (
                novo_vao(curva_elipse(0.16, 0.11)),
                1.0,
                (0.0, 0.18),
                self.BRANCO,
                moderngl.TRIANGLE_FAN,
            ),  # corpo
            (circulo, 0.045, (-0.06, 0.20), self.MANCHA, moderngl.TRIANGLE_FAN),
            (circulo, 0.035, (0.05, 0.15), self.MANCHA, moderngl.TRIANGLE_FAN),
            (circulo, 0.040, (0.10, 0.23), self.MANCHA, moderngl.TRIANGLE_FAN),
            (circulo, 0.07, (0.18, 0.30), self.BEGE, moderngl.TRIANGLE_FAN),  # cabeca
        )

    def desenhar(self):
        """Escreve uniforms por parte (posicao + offset local) e renderiza."""
        px, py = self.posicao
        for vao, escala, (ox, oy), cor, modo in self.partes:
            self.prog["u_escala"].value = escala
            self.prog["u_deslocamento"].value = (px + ox, py + oy)
            self.prog["u_cor"].value = cor if cor is not None else self.cor_manchas
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

    def ciclar_manchas(self):
        """Avanca a paleta; a mesma cor vale para todas as manchas juntas."""
        self.indice_manchas = (self.indice_manchas + 1) % len(self.PALETA_MANCHAS)
        self.cor_manchas = self.PALETA_MANCHAS[self.indice_manchas]

    def liberar(self):
        """Libera VAOs e VBOs."""
        for vao, vbo in self.recursos:
            vao.release()
            vbo.release()
