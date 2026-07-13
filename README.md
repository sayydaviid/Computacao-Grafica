
# Rasterizador CG — Trabalho Prático

Aplicação desktop em Python/Tkinter.

## O que foi implementado

- Bresenham para retas em todos os octantes;
- círculo pelo algoritmo do ponto médio;
- elipse pelo algoritmo do ponto médio;
- Bézier grau 2 e grau 3, com rasterização dos segmentos por Bresenham;
- polilinha;
- preenchimento recursivo/4-conexo;
- preenchimento por varredura;
- recorte de linha por Cohen–Sutherland;
- recorte de polígono por Sutherland–Hodgman;
- translação;
- escala em relação a ponto fixo;
- rotação em relação a pivô;
- projeção ortográfica;
- projeção oblíqua;
- projeção perspectiva.

## Regra da interface

A grade cobre todos os quadrantes e usa coordenadas inteiras de `-10` a `10`.

O usuário **não pinta livremente**. Os cliques servem apenas para selecionar entradas
(pontos, vértices, centro, controles etc.). Somente os quadrados calculados pelo algoritmo
selecionado são pintados.

## Como executar

É necessário Python 3.10 ou superior.

No terminal, dentro da pasta do projeto:

```bash
python app.py
```

No Windows, também pode funcionar com:

```bash
py app.py
```

Não há dependências externas. O Tkinter já acompanha a instalação padrão do Python.

## Como usar

1. Selecione um algoritmo na lista.
2. Leia a instrução exibida.
3. Clique na grade para informar os pontos.
4. Preencha os parâmetros necessários.
5. Clique em **Executar algoritmo**.

Para algoritmos de quantidade fixa de pontos, a execução acontece automaticamente
quando o último ponto é selecionado.

## Convenção visual

- Azul: pixels produzidos pelo algoritmo;
- Laranja: pontos de entrada;
- Roxo tracejado: janela de recorte;
- Cinza: grade.