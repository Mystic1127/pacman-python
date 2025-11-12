# Pac-Man en Python

Este proyecto contiene una recreación completa de PAC-MAN construida exclusivamente con la biblioteca estándar de Python y la interfaz gráfica Tkinter. Incluye un menú de inicio, laberinto clásico, pellets, fantasmas con movimiento autónomo, detección de colisiones, puntuación en pantalla y progresión de niveles.

## Requisitos

- Python 3.10 o superior (probado con Python 3.14.0).
- Tkinter (incluida por defecto en la mayoría de las distribuciones oficiales de Python).

No se necesitan dependencias externas; el archivo `requirements.txt` se mantiene únicamente como referencia.

## Ejecución

```bash
python main.py
```

Al ejecutar el juego aparecerá el menú de inicio. Presiona **Enter** para comenzar y utiliza las flechas del teclado para guiar a Pac-Man. Recolecta todos los puntos para avanzar al siguiente nivel mientras evitas a los fantasmas.

## Estructura del código

- `main.py`: punto de entrada de la aplicación.
- `game/constants.py`: constantes y definición del laberinto.
- `game/vector.py`: utilidades matemáticas simples para manejar posiciones y distancias.
- `game/maze.py`: lógica del laberinto y de los pellets, junto con el renderizado en el lienzo.
- `game/actors.py`: clases para Pac-Man y los fantasmas, incluyendo animaciones básicas.
- `game/game.py`: bucle principal, gestión de estados, niveles, puntuación y colisiones.

¡Disfruta jugando y modificando el código!
