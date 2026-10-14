"""
Senhor Coracao num sitio: uma geometria desenhada varias vezes, agora em
meio a uma cena de sitio (sol/lua, estrelas, chao, arvore, bangalo, vaca e
galinha), cada objeto em sua propria classe.

Duas curvas na VRAM (o coracao e um circulo) e varios desenhos por quadro. O que
muda de um desenho para o outro nao esta em nenhum VBO: esta em variaveis
uniformes. As teclas trocam o valor de uma uniforme.

A chuva é um retangulo que cobre a tela e o fragmento gera linhas verticais a partir de u_tempo.

MCCC007-23 - Computacao Grafica - UFABC

Executar: python 06_senhor_coracao.py
Teclas:   SETAS movem o olhar | ESQ/DIR andam vaca e galinha
          D alterna dia/noite | C alterna chuva | ESC sai
          1 cicla o telhado do bangalo | 2 cicla as manchas da vaca
          3 cicla a copa da arvore
"""

import sys
from pathlib import Path

import glfw
import moderngl
from arvore import Arvore
from astro import Astro
from bangalo import Bangalo
from chao import Chao
from estrelas import Estrelas
from galinha import Galinha
from geometrias import curva_circulo, curva_coracao, quad_tela
from vaca import Vaca

SHADERS = Path(__file__).parent / "shaders"

MAGENTA = (0.85, 0.10, 0.45, 1.0)
BRANCO_OLHO = (1.0, 1.0, 1.0, 1.0)
PRETO = (0.05, 0.05, 0.05, 1.0)
FUNDO_DIA = (0.53, 0.78, 0.95, 1.0)
FUNDO_NOITE = (0.10, 0.10, 0.17, 1.0)
FUNDO_DIA_CHUVA = (0.18, 0.30, 0.45, 1.0)
FUNDO_NOITE_CHUVA = (0.01, 0.01, 0.05, 1.0)

ESCALA_CORPO = 0.62
ESCALA_OLHO, ESCALA_PUPILA = 0.085, 0.040
CENTRO_OLHO = (0.17, 0.20)  # afastamento do eixo e altura de cada olho

# Ate onde a pupila pode sair do centro do olho, sem escapar do branco.
LIMITE_OLHAR = ESCALA_OLHO - ESCALA_PUPILA
PASSO_OLHAR = LIMITE_OLHAR / 2.0
PASSO_VACA = 0.04
PASSO_GALINHA = 0.07


def erro_glfw(codigo, descricao):
    """Substitui o aviso padrão do pyGLFW: imprime código
    e descrição de qualquer erro do GLFW em stderr"""
    print(f"GLFW [{codigo}]: {descricao}", file=sys.stderr)


glfw.set_error_callback(erro_glfw)  # antes de glfw.init(), de proposito

if not glfw.init():
    sys.exit("FALHA: glfw nao inicializou")

glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
# Sem a dica acima, o macOS recusa qualquer contexto 3.2+ e
# create_window devolve None. E inofensiva no Windows e no Linux.
glfw.window_hint(glfw.SAMPLES, 4)  # quatro amostras por pixel
glfw.window_hint(glfw.RESIZABLE, False)  # janela quadrada: ver a nota

janela = glfw.create_window(640, 640, "Senhor Coracao", None, None)
if not janela:
    glfw.terminate()
    sys.exit("FALHA: nao foi possivel criar a janela")

glfw.make_context_current(janela)
ctx = moderngl.create_context()

# SAMPLES e uma dica, nao uma garantia: o driver pode entregar menos amostras
# do que se pediu. Conferir e barato.
print(f"amostras por pixel obtidas: {ctx.screen.samples}")

prog = ctx.program(
    vertex_shader=(SHADERS / "senhor_coracao.vert").read_text(encoding="utf-8"),
    fragment_shader=(SHADERS / "senhor_coracao.frag").read_text(encoding="utf-8"),
)
prog_chuva = ctx.program(
    vertex_shader=(SHADERS / "chuva.vert").read_text(encoding="utf-8"),
    fragment_shader=(SHADERS / "chuva.frag").read_text(encoding="utf-8"),
)


def montar(vertices, programa=None):
    programa = prog if programa is None else programa
    vbo = ctx.buffer(vertices.tobytes())
    return vbo, ctx.vertex_array(programa, [(vbo, "4f", "vPosition")])


vbo_coracao, vao_coracao = montar(curva_coracao())
vbo_circulo, vao_circulo = montar(curva_circulo())
vbo_chuva, vao_chuva = montar(quad_tela(), prog_chuva)
sol = Astro(ctx, prog, cor=(0.98, 0.80, 0.10, 1.0), posicao=(0.70, 0.70), escala=0.18)
lua = Astro(ctx, prog, cor=(0.85, 0.87, 0.95, 1.0), posicao=(0.65, 0.68), escala=0.14)
estrelas = Estrelas(ctx, prog)
chao = Chao(ctx, prog)
arvore = Arvore(ctx, prog)
bangalo = Bangalo(ctx, prog)
vaca = Vaca(ctx, prog)
galinha = Galinha(ctx, prog)

# Todo o estado do programa cabe em dois numeros e dois booleanos.
olhar_x, olhar_y = 0.0, 0.0
noite = False
chuva = False
atenuacao = 1.0


def tecla(window, key, scancode, action, mods):
    global olhar_x, olhar_y, noite, chuva
    if action != glfw.PRESS and action != glfw.REPEAT:
        return
    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)
    elif key == glfw.KEY_D:
        noite = not noite
    elif key == glfw.KEY_C:
        chuva = not chuva
    elif key == glfw.KEY_1:
        bangalo.ciclar_telhado()
    elif key == glfw.KEY_2:
        vaca.ciclar_manchas()
    elif key == glfw.KEY_3:
        arvore.ciclar_copa()
    elif key in (glfw.KEY_LEFT, glfw.KEY_RIGHT, glfw.KEY_UP, glfw.KEY_DOWN):
        dx = {glfw.KEY_LEFT: -1.0, glfw.KEY_RIGHT: 1.0}.get(key, 0.0)
        dy = {glfw.KEY_DOWN: -1.0, glfw.KEY_UP: 1.0}.get(key, 0.0)
        if dx != 0.0:
            vaca.andar(dx * PASSO_VACA, bangalo.caixa())
            galinha.andar(dx * PASSO_GALINHA, bangalo.caixa())
        olhar_x += dx * PASSO_OLHAR
        olhar_y += dy * PASSO_OLHAR
        # O branco do olho e um CIRCULO, entao o limite tem de ser no vetor.
        # Limitar cada eixo em separado prende a pupila num quadrado, e na
        # diagonal ela escapa: o centro chega a 0.064 do centro do olho e a
        # borda da pupila a 0.104, contra um raio de 0.085.
        distancia = (olhar_x**2 + olhar_y**2) ** 0.5
        if distancia > LIMITE_OLHAR:
            olhar_x *= LIMITE_OLHAR / distancia
            olhar_y *= LIMITE_OLHAR / distancia


glfw.set_key_callback(janela, tecla)


def ajustar(nome, valor):
    """Escreve num uniforme, se ele existir.

    Um uniforme que o shader deixa de usar e descartado pelo ligador do
    GLSL, e prog[nome] levantaria KeyError. Os experimentos do capitulo
    fazem exatamente isso -- ignorar u_cor, ignorar u_atenuacao -- entao
    o acesso passa todo por aqui.
    """
    uniforme = prog.get(nome, None)
    if uniforme is not None:
        uniforme.value = valor


def desenhar(vao, escala, deslocamento, cor):
    """Carrega os tres uniformes daquele desenho e dispara a chamada."""
    ajustar("u_escala", escala)
    ajustar("u_deslocamento", deslocamento)
    ajustar("u_cor", cor)
    vao.render(moderngl.TRIANGLE_FAN)


def desenhar_chuva():
    """Cobre a cena com as linhas verticais do shader de chuva."""
    prog_chuva["u_tempo"].value = glfw.get_time()
    prog_chuva["u_atenuacao"].value = atenuacao
    ctx.enable(moderngl.BLEND)
    ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
    vao_chuva.render(moderngl.TRIANGLES)
    ctx.disable(moderngl.BLEND)


while not glfw.window_should_close(janela):
    if noite and chuva:
        atenuacao = 0.25
    elif noite and not chuva:
        atenuacao = 0.35
    elif chuva:
        atenuacao = 0.50
    else:
        atenuacao = 1.0
    # Uma escrita por quadro: os cinco desenhos abaixo leem este mesmo valor.
    ajustar("u_atenuacao", atenuacao)

    fundo = FUNDO_DIA
    if noite and chuva:
        fundo = FUNDO_NOITE_CHUVA
    elif noite and not chuva:
        fundo = FUNDO_NOITE
    elif chuva:
        fundo = FUNDO_DIA_CHUVA

    ctx.clear(*fundo)

    # Fundo vivo: estrelas e lua so de noite; sol de dia.
    if noite:
        estrelas.desenhar()
        lua.desenhar()
    else:
        sol.desenhar()

    chao.desenhar()
    arvore.desenhar()
    bangalo.desenhar()
    vaca.desenhar()
    galinha.desenhar()

    desenhar(vao_coracao, ESCALA_CORPO, (0.0, 0.0), MAGENTA)

    # A mesma geometria de circulo, quatro vezes, so mudando os uniformes.
    for lado in (-1.0, 1.0):
        centro = (lado * CENTRO_OLHO[0], CENTRO_OLHO[1])
        desenhar(vao_circulo, ESCALA_OLHO, centro, BRANCO_OLHO)
        desenhar(
            vao_circulo,
            ESCALA_PUPILA,
            (centro[0] + olhar_x, centro[1] + olhar_y),
            PRETO,
        )

    if chuva:
        desenhar_chuva()

    glfw.swap_buffers(janela)
    glfw.poll_events()

for objeto in (sol, lua, estrelas, chao, arvore, bangalo, vaca, galinha):
    objeto.liberar()
for recurso in (
    vao_coracao,
    vao_circulo,
    vao_chuva,
    vbo_coracao,
    vbo_circulo,
    vbo_chuva,
    prog,
    prog_chuva,
):
    recurso.release()
glfw.terminate()
print("Execucao finalizada.")
