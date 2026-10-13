# Atividade 2

## Setup do Ambiente

```bash
uv sync
```

## Execução

```bash
uv run 06_senhor_coracao.py
```

## Relatório

1. Código base do senhor coração copiado e inalterado.
2. Adicionada flag de chuva.
3. Tema original da NOITE alterada.
4. Adicionado temas de chuva para combinação com DIA e NOITE originais.
  - A intenção é criar 4 estados combinando a flag original de noite com a flag de chuva criada.
    - DIA, NOITE, DIA_CHUVA, NOITE_CHUVA.
5. Cria animação de chuva. Um retangulo cobre a tela e o fragmento gera linhas verticais a partir de u_tempo.
6. Adicionado sol reutilizando a geometria de círculo dos olhos (TRIANGLE_FAN), mudando apenas uniformes de escala, posição e cor.
7. Refatoração POO — cada objeto de cena em sua classe, formas compartilhadas em geometrias.py.
8. Cena de sítio: sol/lua, estrelas noturnas, chão, árvore, bangalô, vaca e galinha.
9. Teclas 1/2/3 ciclam cores do telhado, das manchas da vaca e da copa.
