"""Curvas fechadas da cena: coracao, circulo e o retangulo da chuva."""

import numpy as np


def leque(x, y):
    """Empacota uma curva fechada como TRIANGLE_FAN: primeiro o centro, depois
    a curva, e o primeiro ponto repetido no fim para fechar a volta."""
    x = np.concatenate(([0.0], x, [x[0]]))
    y = np.concatenate(([0.0], y, [y[0]]))
    return np.column_stack((x, y, np.zeros_like(x), np.ones_like(x))).astype("f4")


def curva_coracao(n=180):
    t = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    x = 16.0 * np.sin(t) ** 3
    y = 13.0 * np.cos(t) - 5.0 * np.cos(2 * t) - 2.0 * np.cos(3 * t) - np.cos(4 * t)
    y = y - 0.5 * (y.max() + y.min())  # centra a curva na origem
    return leque(x / 17.0, y / 17.0)  # normaliza para caber em [-1, 1]


def curva_circulo(n=48):
    t = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    return leque(np.cos(t), np.sin(t))


def curva_elipse(rx, ry, n=48):
    """Elipse fechada como TRIANGLE_FAN: rx e o raio horizontal, ry o vertical."""
    t = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    return leque(rx * np.cos(t), ry * np.sin(t))


def quad(x0, y0, x1, y1):
    """Retangulo alinhado aos eixos: 4 cantos em ordem (TRIANGLE_FAN cobre a
    area, LINE_LOOP desenha so o contorno do mesmo VBO)."""
    cantos = ((x0, y0), (x1, y0), (x1, y1), (x0, y1))
    return np.array([(x, y, 0.0, 1.0) for x, y in cantos], dtype="f4")


def triangulo(p1, p2, p3):
    """Triangulo simples a partir de tres pontos 2D."""
    return np.array([(x, y, 0.0, 1.0) for x, y in (p1, p2, p3)], dtype="f4")


def quad_tela():
    """Dois triangulos em NDC. A gota nao esta nestes vertices."""
    cantos = (
        (-1.0, -1.0),
        (1.0, -1.0),
        (1.0, 1.0),
        (-1.0, -1.0),
        (1.0, 1.0),
        (-1.0, 1.0),
    )
    return np.array([(x, y, 0.0, 1.0) for x, y in cantos], dtype="f4")
