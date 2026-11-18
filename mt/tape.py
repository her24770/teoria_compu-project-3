"""Cinta infinita en ambas direcciones."""
from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

from .models import BLANK, DIRECTIONS, Symbol


class Tape:
    """Cinta representada como un diccionario posición -> símbolo.

    Solo se guardan las celdas que no son blank, así la cinta puede crecer
    sin límite hacia la izquierda o la derecha sin copiar listas.
    """

    def __init__(self, symbols: Iterable[str] = ()):
        self.cells: Dict[int, str] = {
            i: s for i, s in enumerate(symbols) if s is not BLANK
        }
        self.head = 0

    def read(self) -> Symbol:
        return self.cells.get(self.head, BLANK)

    def write(self, symbol: Symbol) -> None:
        if symbol is BLANK:
            self.cells.pop(self.head, None)
        else:
            self.cells[self.head] = symbol

    def move(self, direction: str) -> None:
        self.head += DIRECTIONS[direction]

    def _range(self) -> Tuple[int, int]:
        """Rango [inicio, fin] de celdas no blank (vacío si fin < inicio)."""
        if not self.cells:
            return (0, -1)
        return (min(self.cells), max(self.cells))

    def snapshot(self) -> Tuple[List[Symbol], List[Symbol]]:
        """Devuelve (izquierda, derecha) respecto al cabezal, como en una ID.

        - izquierda: desde el primer símbolo no blank hasta la celda anterior
          al cabezal.
        - derecha: desde la celda bajo el cabezal hasta el último símbolo no
          blank (siempre contiene al menos la celda bajo el cabezal).
        """
        start, end = self._range()
        left_start = min(start, self.head) if self.cells else self.head
        right_end = max(end, self.head)
        left = [self.cells.get(i, BLANK) for i in range(left_start, self.head)]
        right = [self.cells.get(i, BLANK) for i in range(self.head, right_end + 1)]
        return left, right

    def content(self) -> List[str]:
        """Contenido de la cinta entre el primer y el último símbolo no blank."""
        start, end = self._range()
        return [self.cells.get(i, BLANK) for i in range(start, end + 1)]

    def is_blank(self) -> bool:
        return not self.cells
