"""
Tetris simplificado: pecas caem, encaixam, completam linhas.

MCCC007-23 - Computacao Grafica - UFABC

Executar (na pasta atividade3):
    uv run python tetris.py

Teclas:
    ENTER     comeca na tela de inicio, ou reinicia depois do fim
    ESQUERDA  move a peca (segurando, o passo se repete)
    DIREITA   move a peca
    BAIXO     queda suave, enquanto a tecla estiver segurada
    CIMA      gira no sentido horario
    Z         gira no sentido anti-horario
    ESPACO    queda instantanea
    P         pausa e retoma
    R         reinicia a partida
    V         liga e desliga o vsync
    ESC       sai

O titulo da janela mostra o estado, a pontuacao, as linhas, o fps
e o cooldown (queda, trava da peca ou limpeza de linha). Os numeros
tambem sao desenhados na cena, com quadrados, sem biblioteca de texto.
"""

import math
import random
import sys
from pathlib import Path

import glfw
import moderngl
import numpy as np

SHADERS = Path(__file__).parent / "shaders"

LARGURA, ALTURA = 560, 640
COLS, ROWS = 10, 20
PX = 26
MARGEM_X, MARGEM_Y = 28, 48
LINHAS_PARA_VENCER = 10

# Velocidades em celulas por segundo. O avanco de cada quadro e velocidade * dt.
QUEDA_INICIAL = 1.35
QUEDA_POR_NIVEL = 0.40
QUEDA_MAXIMA = 8.0
QUEDA_SUAVE = 12.0
PASSO_MAXIMO = 0.05  # segundos; evita salto quando a janela e arrastada

ATRASO_REPETICAO = 0.17
INTERVALO_REPETICAO = 0.05
TEMPO_TRAVA = 0.50
MAX_DESLIZAMENTOS = 12
DURACAO_LIMPA = 0.30
GIRO = 1.15  # radianos por segundo do triangulo decorativo

PONTOS_LINHA = {1: 100, 2: 300, 3: 500, 4: 800}
SPAWN = (3, 16)

INICIO, JOGANDO, PAUSADO, FIM = "inicio", "jogando", "pausado", "fim"

FUNDO = (0.07, 0.08, 0.10, 1.0)
COR_POCO = (0.11, 0.12, 0.15, 1.0)
COR_PAINEL = (0.14, 0.15, 0.18, 1.0)
COR_GRADE = (0.22, 0.24, 0.28, 1.0)
COR_FANTASMA = (0.82, 0.88, 0.94, 0.45)
COR_DIGITO = (0.94, 0.96, 0.98, 1.0)
COR_DIGITO_OFF = (0.22, 0.24, 0.28, 1.0)
COR_ZERO = (0.38, 0.41, 0.46, 1.0)
COR_MARCA = (0.95, 0.78, 0.28, 1.0)
COR_MARCA_VAZIA = (0.40, 0.43, 0.48, 1.0)
COR_BARRA = (0.96, 0.72, 0.28, 1.0)
COR_TRILHO = (0.22, 0.24, 0.28, 1.0)

CORES = {
    "I": (0.35, 0.86, 0.95, 1.0),
    "O": (0.95, 0.82, 0.28, 1.0),
    "T": (0.70, 0.42, 0.90, 1.0),
    "S": (0.42, 0.84, 0.46, 1.0),
    "Z": (0.90, 0.34, 0.36, 1.0),
    "J": (0.32, 0.48, 0.95, 1.0),
    "L": (0.95, 0.58, 0.24, 1.0),
}
TIPOS = list(CORES)

# Quatro rotacoes de cada peca, em coordenadas locais (x, y), y para cima.
BLOCOS = {
    "I": (
        ((0, 1), (1, 1), (2, 1), (3, 1)),
        ((2, 0), (2, 1), (2, 2), (2, 3)),
        ((0, 2), (1, 2), (2, 2), (3, 2)),
        ((1, 0), (1, 1), (1, 2), (1, 3)),
    ),
    "O": (
        ((1, 0), (2, 0), (1, 1), (2, 1)),
        ((1, 0), (2, 0), (1, 1), (2, 1)),
        ((1, 0), (2, 0), (1, 1), (2, 1)),
        ((1, 0), (2, 0), (1, 1), (2, 1)),
    ),
    "T": (
        ((1, 0), (0, 1), (1, 1), (2, 1)),
        ((1, 0), (1, 1), (2, 1), (1, 2)),
        ((0, 1), (1, 1), (2, 1), (1, 2)),
        ((1, 0), (0, 1), (1, 1), (1, 2)),
    ),
    "S": (
        ((1, 0), (2, 0), (0, 1), (1, 1)),
        ((1, 0), (1, 1), (2, 1), (2, 2)),
        ((1, 1), (2, 1), (0, 2), (1, 2)),
        ((0, 0), (0, 1), (1, 1), (1, 2)),
    ),
    "Z": (
        ((0, 0), (1, 0), (1, 1), (2, 1)),
        ((2, 0), (1, 1), (2, 1), (1, 2)),
        ((0, 1), (1, 1), (1, 2), (2, 2)),
        ((1, 0), (0, 1), (1, 1), (0, 2)),
    ),
    "J": (
        ((0, 0), (0, 1), (1, 1), (2, 1)),
        ((1, 0), (2, 0), (1, 1), (1, 2)),
        ((0, 1), (1, 1), (2, 1), (2, 2)),
        ((1, 0), (1, 1), (0, 2), (1, 2)),
    ),
    "L": (
        ((2, 0), (0, 1), (1, 1), (2, 1)),
        ((1, 0), (1, 1), (1, 2), (2, 2)),
        ((0, 1), (1, 1), (2, 1), (0, 2)),
        ((0, 0), (1, 0), (1, 1), (1, 2)),
    ),
}

# top, sup. dir., inf. dir., base, inf. esq., sup. esq., meio
MASCARAS = {
    "0": (1, 1, 1, 1, 1, 1, 0),
    "1": (0, 1, 1, 0, 0, 0, 0),
    "2": (1, 1, 0, 1, 1, 0, 1),
    "3": (1, 1, 1, 1, 0, 0, 1),
    "4": (0, 1, 1, 0, 0, 1, 1),
    "5": (1, 0, 1, 1, 0, 1, 1),
    "6": (1, 0, 1, 1, 1, 1, 1),
    "7": (1, 1, 1, 0, 0, 0, 0),
    "8": (1, 1, 1, 1, 1, 1, 1),
    "9": (1, 1, 1, 1, 0, 1, 1),
}
CHUTES = ((0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0), (0, 1), (0, -1))


def px_ndc(x, y):
    """Pixel da janela (origem no canto inferior esquerdo) para NDC."""
    return (x / LARGURA) * 2.0 - 1.0, (y / ALTURA) * 2.0 - 1.0


def tam_ndc(w, h):
    return (w / LARGURA) * 2.0, (h / ALTURA) * 2.0


def malha_quadrado():
    return np.array(
        [
            [-0.5, -0.5, 0.0, 1.0],
            [0.5, -0.5, 0.0, 1.0],
            [0.5, 0.5, 0.0, 1.0],
            [-0.5, 0.5, 0.0, 1.0],
        ],
        dtype="f4",
    )


def malha_triangulo():
    return np.array(
        [
            [0.0, 0.50, 0.0, 1.0],
            [-0.46, -0.40, 0.0, 1.0],
            [0.46, -0.40, 0.0, 1.0],
        ],
        dtype="f4",
    )


def malha_circulo(n=40):
    ang = np.linspace(0.0, 2.0 * math.pi, n, endpoint=False)
    borda = np.column_stack(
        (0.5 * np.cos(ang), 0.5 * np.sin(ang), np.zeros(n), np.ones(n))
    ).astype("f4")
    centro = np.array([[0.0, 0.0, 0.0, 1.0]], dtype="f4")
    return np.concatenate((centro, borda, borda[:1]))


class Peca:
    def __init__(self, tipo, x, y, rot=0):
        self.tipo = tipo
        self.x = x
        self.y = y
        self.rot = rot

    def celulas(self):
        return [(self.x + dx, self.y + dy) for dx, dy in BLOCOS[self.tipo][self.rot]]


class Partida:
    """Regras do tetris, sem OpenGL. Cada celula do poco e um retangulo."""

    def __init__(self):
        self.reiniciar()

    def reiniciar(self):
        self.grade = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.pontos = 0
        self.linhas = 0
        self.saco = []
        self.seguinte = self._puxar()
        self.atual = None
        self.fracao = 0.0
        self.repouso = 0.0
        self.deslizamentos = 0
        self.limpando = []
        self.tempo_limpa = 0.0
        self.resultado = None
        self._spawn()

    def controlar(self):
        return self.atual is not None and not self.limpando and self.resultado is None

    def velocidade_queda(self):
        nivel = self.linhas // 2
        return min(QUEDA_MAXIMA, QUEDA_INICIAL + nivel * QUEDA_POR_NIVEL)

    def restante_trava(self):
        if not self.controlar() or not self._no_chao():
            return None
        return max(0.0, TEMPO_TRAVA - self.repouso)

    def restante_limpa(self):
        if not self.limpando:
            return None
        return max(0.0, self.tempo_limpa)

    def atualizar(self, dt, suave):
        if self.resultado:
            return
        if self.limpando:
            self.tempo_limpa -= dt
            if self.tempo_limpa <= 0.0:
                self._concluir_limpeza()
            return
        if self.atual is None:
            return

        vel = QUEDA_SUAVE if suave else self.velocidade_queda()
        self.fracao += vel * dt
        passos = 0
        # Um celula por iteracao: dt grande nao atravessa um bloco ocupado.
        while self.fracao >= 1.0 and self.controlar():
            self.fracao -= 1.0
            if not self._descer():
                self.fracao = 0.0
                break
            passos += 1
        if suave:
            self.pontos += passos

        if not self.controlar():
            return
        # O dt desta queda nao entra na trava: o cooldown comeca no quadro seguinte,
        # quando a peca ja esta parada. Um pico de tempo nao fixa a peca na hora.
        if passos == 0 and self._no_chao():
            self.repouso += dt
            if self.repouso >= TEMPO_TRAVA:
                self._fixar()
        else:
            self.repouso = 0.0

    def mover(self, dx):
        if not self.controlar():
            return False
        if self._colide(self.atual.x + dx, self.atual.y, self.atual.rot):
            return False
        self.atual.x += dx
        self._adiar_trava()
        return True

    def girar(self, sentido):
        if not self.controlar():
            return False
        nova = (self.atual.rot + sentido) % 4
        for dx, dy in CHUTES:
            if not self._colide(self.atual.x + dx, self.atual.y + dy, nova):
                self.atual.x += dx
                self.atual.y += dy
                self.atual.rot = nova
                self._adiar_trava()
                return True
        return False

    def derrubar(self):
        if not self.controlar():
            return
        n = 0
        while self._descer():
            n += 1
        self.pontos += 2 * n
        self.fracao = 0.0
        self._fixar()

    def fantasma(self):
        if not self.controlar():
            return None
        y = self.atual.y
        while not self._colide(self.atual.x, y - 1, self.atual.rot):
            y -= 1
        if y == self.atual.y:
            return None
        return y

    def _puxar(self):
        if not self.saco:
            self.saco = TIPOS[:]
            random.shuffle(self.saco)
        return self.saco.pop()

    def _spawn(self):
        tipo = self.seguinte
        self.seguinte = self._puxar()
        self.atual = Peca(tipo, SPAWN[0], SPAWN[1])
        self.fracao = 0.0
        self.repouso = 0.0
        self.deslizamentos = 0
        if self._colide(self.atual.x, self.atual.y, self.atual.rot):
            self.atual = None
            self.resultado = "derrota"

    def _colide(self, x, y, rot):
        for dx, dy in BLOCOS[self.atual.tipo][rot]:
            cx, cy = x + dx, y + dy
            if cx < 0 or cx >= COLS or cy < 0 or cy >= ROWS:
                return True
            if self.grade[cy][cx]:
                return True
        return False

    def _no_chao(self):
        return self._colide(self.atual.x, self.atual.y - 1, self.atual.rot)

    def _descer(self):
        if self._colide(self.atual.x, self.atual.y - 1, self.atual.rot):
            return False
        self.atual.y -= 1
        self.repouso = 0.0
        self.deslizamentos = 0
        return True

    def _adiar_trava(self):
        if not self._no_chao():
            return
        if self.deslizamentos >= MAX_DESLIZAMENTOS:
            return
        self.repouso = 0.0
        self.deslizamentos += 1

    def _fixar(self):
        for x, y in self.atual.celulas():
            if 0 <= x < COLS and 0 <= y < ROWS:
                self.grade[y][x] = self.atual.tipo
        self.atual = None
        self.fracao = 0.0
        cheias = [y for y in range(ROWS) if all(self.grade[y])]
        if cheias:
            self.limpando = cheias
            self.tempo_limpa = DURACAO_LIMPA
            return
        self._spawn()

    def _concluir_limpeza(self):
        cheias = set(self.limpando)
        n = len(cheias)
        self.grade = [linha for i, linha in enumerate(self.grade) if i not in cheias]
        for _ in range(n):
            self.grade.append([0 for _ in range(COLS)])
        self.linhas += n
        self.pontos += PONTOS_LINHA.get(n, 100 * n)
        self.limpando = []
        self.tempo_limpa = 0.0
        if self.linhas >= LINHAS_PARA_VENCER:
            self.resultado = "vitoria"
            return
        self._spawn()


class Desenhista:
    """Tres malhas criadas uma vez. O quadro so troca uniforms."""

    def __init__(self, ctx, prog):
        self.ctx = ctx
        self.prog = prog
        self.recursos = []
        self.quad = self._vao(malha_quadrado())
        self.triangulo = self._vao(malha_triangulo())
        self.circulo = self._vao(malha_circulo())

    def _vao(self, vertices):
        vbo = self.ctx.buffer(vertices.tobytes())
        vao = self.ctx.vertex_array(self.prog, [(vbo, "4f", "vPosition")])
        self.recursos.extend((vbo, vao))
        return vao

    def malha(self, vao, modo, cx, cy, w, h, cor, brilho=1.0, rotacao=0.0):
        self.prog["u_deslocamento"].value = px_ndc(cx, cy)
        self.prog["u_escala"].value = tam_ndc(w, h)
        self.prog["u_rotacao"].value = rotacao
        self.prog["u_cor"].value = cor
        self.prog["u_brilho"].value = brilho
        vao.render(modo)

    def quadrado(self, cx, cy, lado, cor, brilho=1.0):
        self.malha(self.quad, moderngl.TRIANGLE_FAN, cx, cy, lado, lado, cor, brilho)

    def retangulo(self, cx, cy, w, h, cor, brilho=1.0):
        self.malha(self.quad, moderngl.TRIANGLE_FAN, cx, cy, w, h, cor, brilho)

    def contorno(self, cx, cy, w, h, cor, brilho=1.0):
        self.malha(self.quad, moderngl.LINE_LOOP, cx, cy, w, h, cor, brilho)

    def liberar(self):
        for recurso in self.recursos:
            recurso.release()
        self.prog.release()


class Jogo:
    def __init__(self, janela, ctx, des):
        self.janela = janela
        self.ctx = ctx
        self.des = des
        self.estado = INICIO
        self.partida = None
        self.vsync = True
        self.eixo = 0
        self.espera_eixo = 0.0
        self.tempo_cena = 0.0
        self.fps = 0.0
        self._quadros = 0
        self._marco = glfw.get_time()
        self._anterior = self._marco

    def comecar(self):
        self.partida = Partida()
        self.estado = JOGANDO
        self.eixo = 0
        self.espera_eixo = 0.0

    def ao_teclar(self, key):
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(self.janela, True)
        elif key == glfw.KEY_V:
            self.vsync = not self.vsync
            glfw.swap_interval(1 if self.vsync else 0)
        elif key in (glfw.KEY_ENTER, glfw.KEY_KP_ENTER):
            if self.estado in (INICIO, FIM):
                self.comecar()
        elif key == glfw.KEY_R:
            self.comecar()
        elif key == glfw.KEY_P:
            if self.estado == JOGANDO:
                self.estado = PAUSADO
            elif self.estado == PAUSADO:
                self.estado = JOGANDO
        elif self.estado == JOGANDO and self.partida:
            if key == glfw.KEY_UP:
                self.partida.girar(1)
            elif key == glfw.KEY_Z:
                self.partida.girar(-1)
            elif key == glfw.KEY_SPACE:
                self.partida.derrubar()
                self._fechar_se_acabou()

    def rodar(self):
        while not glfw.window_should_close(self.janela):
            agora = glfw.get_time()
            dt = agora - self._anterior
            self._anterior = agora
            if dt > PASSO_MAXIMO:
                dt = PASSO_MAXIMO
            # Na pausa o relogio da cena nao anda, entao o dt parado nao entra no jogo.
            if self.estado != PAUSADO:
                self.tempo_cena += dt
            if self.estado == JOGANDO:
                self._mover_continuo(dt)
                suave = glfw.get_key(self.janela, glfw.KEY_DOWN) == glfw.PRESS
                self.partida.atualizar(dt, suave)
                self._fechar_se_acabou()

            self._desenhar()
            glfw.swap_buffers(self.janela)
            glfw.poll_events()
            self._medir_fps(agora)

    def _fechar_se_acabou(self):
        if self.partida and self.partida.resultado:
            self.estado = FIM

    def _mover_continuo(self, dt):
        esq = glfw.get_key(self.janela, glfw.KEY_LEFT) == glfw.PRESS
        dire = glfw.get_key(self.janela, glfw.KEY_RIGHT) == glfw.PRESS
        eixo = (-1 if esq else 0) + (1 if dire else 0)
        if eixo == 0 or (esq and dire):
            self.eixo = 0
            self.espera_eixo = 0.0
            return
        if eixo != self.eixo:
            self.eixo = eixo
            self.espera_eixo = ATRASO_REPETICAO
            self.partida.mover(eixo)
            return
        self.espera_eixo -= dt
        if self.espera_eixo <= 0.0:
            self.partida.mover(eixo)
            self.espera_eixo = INTERVALO_REPETICAO

    def _medir_fps(self, agora):
        self._quadros += 1
        decorrido = agora - self._marco
        if decorrido >= 0.5:
            self.fps = self._quadros / decorrido
            self._quadros = 0
            self._marco = agora
        glfw.set_window_title(self.janela, self._titulo())

    def _titulo(self):
        vs = "on" if self.vsync else "OFF"
        fps = f"{self.fps:5.1f} fps"
        if self.estado == INICIO:
            return f"Tetris | inicio | ENTER comeca | vsync {vs} | {fps}"
        pontos = self.partida.pontos
        linhas = self.partida.linhas
        nucleo = f"pontos {pontos} | linhas {linhas}/{LINHAS_PARA_VENCER}"
        if self.estado == PAUSADO:
            return f"Tetris | pausa | {nucleo} | P retoma | vsync {vs} | {fps}"
        if self.estado == FIM:
            return (
                f"Tetris | {self.partida.resultado} | {nucleo} "
                f"| R reinicia | vsync {vs} | {fps}"
            )
        limpa = self.partida.restante_limpa()
        trava = self.partida.restante_trava()
        if limpa is not None:
            ritmo = f"limpa {limpa:.2f}s"
        elif trava is not None:
            ritmo = f"trava {trava:.2f}s"
        elif glfw.get_key(self.janela, glfw.KEY_DOWN) == glfw.PRESS:
            ritmo = f"suave {1.0 / QUEDA_SUAVE:.2f}s"
        else:
            ritmo = f"queda {1.0 / self.partida.velocidade_queda():.2f}s"
        return f"Tetris | jogando | {nucleo} | {ritmo} | vsync {vs} | {fps}"

    def _desenhar(self):
        self.ctx.clear(*FUNDO)
        self._poco()
        self._painel()

    def _poco(self):
        d = self.des
        x0 = MARGEM_X + COLS * PX / 2
        y0 = MARGEM_Y + ROWS * PX / 2
        d.retangulo(x0, y0, COLS * PX + 12, ROWS * PX + 12, self._cor_moldura(), self._brilho_moldura())
        d.retangulo(x0, y0, COLS * PX, ROWS * PX, COR_POCO)
        for row in range(ROWS):
            for col in range(COLS):
                cx, cy = self._centro(col, row)
                d.contorno(cx, cy, PX, PX, COR_GRADE)
        grade = self.partida.grade if self.partida else None
        if grade:
            for row in range(ROWS):
                for col in range(COLS):
                    tipo = grade[row][col]
                    if not tipo:
                        continue
                    brilho = 1.0
                    if row in self.partida.limpando:
                        brilho = 0.35 + 0.65 * abs(math.sin(self.tempo_cena * 22.0))
                    d.quadrado(*self._centro(col, row), PX - 3, CORES[tipo], brilho)
        if self.estado == INICIO:
            self._peca_de_abertura()
        elif self.partida and self.partida.atual:
            self._peca_atual()

    def _peca_atual(self):
        d = self.des
        peca = self.partida.atual
        gy = self.partida.fantasma()
        if gy is not None:
            ativas = set(peca.celulas())
            for dx, dy in BLOCOS[peca.tipo][peca.rot]:
                pos = (peca.x + dx, gy + dy)
                if pos not in ativas:
                    d.quadrado(*self._centro(*pos), PX - 3, COR_FANTASMA)
        pulso = 0.88 + 0.12 * math.sin(self.tempo_cena * 6.0)
        for x, y in peca.celulas():
            d.quadrado(*self._centro(x, y), PX - 3, CORES[peca.tipo], pulso)

    def _peca_de_abertura(self):
        tipo = TIPOS[int(self.tempo_cena / 2.4) % len(TIPOS)]
        rot = int(self.tempo_cena / 0.7) % 4
        blocos = BLOCOS[tipo][rot]
        xs = [b[0] for b in blocos]
        ys = [b[1] for b in blocos]
        meio_x = (min(xs) + max(xs) + 1) * 0.5
        meio_y = (min(ys) + max(ys) + 1) * 0.5
        cx = MARGEM_X + COLS * PX / 2
        cy = MARGEM_Y + ROWS * PX / 2 + math.sin(self.tempo_cena * 1.7) * 22.0
        brilho = 0.75 + 0.25 * math.sin(self.tempo_cena * 3.0)
        for x, y in blocos:
            px = cx + (x + 0.5 - meio_x) * PX
            py = cy + (y + 0.5 - meio_y) * PX
            self.des.quadrado(px, py, PX - 3, CORES[tipo], brilho)

    def _painel(self):
        d = self.des
        painel_x = MARGEM_X + COLS * PX + 20
        painel_w = LARGURA - painel_x - 20
        cx = painel_x + painel_w / 2
        cy = MARGEM_Y + ROWS * PX / 2
        d.retangulo(cx, cy, painel_w, ROWS * PX, COR_PAINEL)

        caixa = 112
        topo = MARGEM_Y + ROWS * PX - 24 - caixa / 2
        d.contorno(cx, topo, caixa, caixa, COR_GRADE)
        if self.partida and self.estado != INICIO:
            self._preview(cx, topo)

        pontos = self.partida.pontos if self.partida else 0
        base_numero = topo - caixa / 2 - 52
        self._numero(pontos, cx, base_numero)

        linhas = self.partida.linhas if self.partida else 0
        base_marcas = base_numero - 48
        self._marcas(linhas, cx, base_marcas)
        self._barra(cx, base_marcas - 32, painel_w - 36)
        self._ornamentos(cx, base_marcas - 96)

    def _preview(self, cx, cy):
        tipo = self.partida.seguinte
        blocos = BLOCOS[tipo][0]
        xs = [b[0] for b in blocos]
        ys = [b[1] for b in blocos]
        meio_x = (min(xs) + max(xs) + 1) * 0.5
        meio_y = (min(ys) + max(ys) + 1) * 0.5
        tam = 22.0 * (1.0 + 0.07 * math.sin(self.tempo_cena * 3.2))
        for x, y in blocos:
            px = cx + (x + 0.5 - meio_x) * tam
            py = cy + (y + 0.5 - meio_y) * tam
            self.des.quadrado(px, py, tam - 3, CORES[tipo])

    def _numero(self, valor, cx, base):
        digitos = f"{min(valor, 999999):06d}"
        w, h, t = 16.0, 32.0, 4.0
        gap = 5.0
        total = len(digitos) * w + (len(digitos) - 1) * gap
        x = cx - total / 2
        significativo = False
        for i, ch in enumerate(digitos):
            if ch != "0":
                significativo = True
            lider = not significativo and i < len(digitos) - 1
            self._digito(ch, x, base, w, h, t, lider)
            x += w + gap

    def _digito(self, ch, x, y, w, h, t, lider):
        metade = h / 2
        segmentos = (
            (w / 2, h - t / 2, w - t, t),
            (w - t / 2, h - metade / 2, t, metade),
            (w - t / 2, metade / 2, t, metade),
            (w / 2, t / 2, w - t, t),
            (t / 2, metade / 2, t, metade),
            (t / 2, h - metade / 2, t, metade),
            (w / 2, h / 2, w - t, t),
        )
        for ligado, (sx, sy, sw, sh) in zip(MASCARAS[ch], segmentos):
            if lider:
                cor = COR_ZERO if ligado else COR_DIGITO_OFF
            else:
                cor = COR_DIGITO if ligado else COR_DIGITO_OFF
            self.des.retangulo(x + sx, y + sy, sw, sh, cor)

    def _marcas(self, linhas, cx, cy):
        lado, gap = 16.0, 6.0
        n = LINHAS_PARA_VENCER
        total = n * lado + (n - 1) * gap
        x = cx - total / 2 + lado / 2
        feitas = min(linhas, n)
        for i in range(n):
            if i < feitas:
                self.des.quadrado(x, cy, lado, COR_MARCA)
            else:
                self.des.contorno(x, cy, lado, lado, COR_MARCA_VAZIA)
            x += lado + gap

    def _barra(self, cx, cy, largura):
        partida = self.partida
        if not partida or self.estado not in (JOGANDO, PAUSADO):
            return
        limpa = partida.restante_limpa()
        trava = partida.restante_trava()
        if limpa is not None:
            fracao, cor = limpa / DURACAO_LIMPA, (0.92, 0.95, 0.98, 1.0)
        elif trava is not None:
            fracao, cor = trava / TEMPO_TRAVA, COR_BARRA
        else:
            return
        self.des.retangulo(cx, cy, largura, 8, COR_TRILHO)
        if fracao > 0.0:
            cheia = largura * fracao
            self.des.retangulo(cx - largura / 2 + cheia / 2, cy, cheia, 8, cor)

    def _ornamentos(self, cx, cy):
        t = self.tempo_cena
        cor = (
            0.45 + 0.40 * math.sin(t * 1.6),
            0.42 + 0.38 * math.sin(t * 1.6 + 2.1),
            0.55 + 0.35 * math.sin(t * 1.6 + 4.0),
            1.0,
        )
        diametro = 34.0 + 8.0 * math.sin(t * 2.4)
        self.des.malha(
            self.des.circulo,
            moderngl.TRIANGLE_FAN,
            cx - 42,
            cy,
            diametro,
            diametro,
            cor,
        )
        self.des.malha(
            self.des.triangulo,
            moderngl.TRIANGLES,
            cx + 42,
            cy,
            30,
            30,
            (0.95, 0.55, 0.35, 1.0),
            rotacao=GIRO * t,
        )

    def _cor_moldura(self):
        if self.estado == INICIO:
            return (0.28, 0.62, 0.74, 1.0)
        if self.estado == PAUSADO:
            return (0.86, 0.64, 0.22, 1.0)
        if self.estado == FIM and self.partida.resultado == "vitoria":
            return (0.95, 0.78, 0.28, 1.0)
        if self.estado == FIM:
            return (0.82, 0.24, 0.28, 1.0)
        return (0.20, 0.24, 0.32, 1.0)

    def _brilho_moldura(self):
        if self.estado == INICIO:
            return 0.75 + 0.25 * math.sin(self.tempo_cena * 2.2)
        if self.estado == FIM:
            return 0.70 + 0.30 * math.sin(self.tempo_cena * 3.0)
        return 1.0

    def _centro(self, col, row):
        return MARGEM_X + (col + 0.5) * PX, MARGEM_Y + (row + 0.5) * PX


def erro_glfw(codigo, descricao):
    print(f"GLFW [{codigo}]: {descricao}", file=sys.stderr)


def main():
    glfw.set_error_callback(erro_glfw)
    if not glfw.init():
        sys.exit("FALHA: glfw nao inicializou")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
    glfw.window_hint(glfw.SAMPLES, 4)
    glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)

    janela = glfw.create_window(LARGURA, ALTURA, "Tetris", None, None)
    if not janela:
        glfw.terminate()
        sys.exit("FALHA: nao foi possivel criar a janela")

    glfw.make_context_current(janela)
    glfw.swap_interval(1)
    ctx = moderngl.create_context()
    fb = glfw.get_framebuffer_size(janela)
    ctx.viewport = (0, 0, fb[0], fb[1])
    ctx.enable(moderngl.BLEND)
    ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

    prog = ctx.program(
        vertex_shader=(SHADERS / "tetris.vert").read_text(encoding="utf-8"),
        fragment_shader=(SHADERS / "tetris.frag").read_text(encoding="utf-8"),
    )
    des = Desenhista(ctx, prog)
    jogo = Jogo(janela, ctx, des)

    def tecla(window, key, scancode, action, mods):
        if action == glfw.PRESS:
            jogo.ao_teclar(key)

    glfw.set_key_callback(janela, tecla)
    jogo.rodar()
    des.liberar()
    glfw.terminate()
    print("Execucao finalizada.")


if __name__ == "__main__":
    main()
