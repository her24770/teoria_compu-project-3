"""Estructuras de datos que representan una Máquina de Turing de una cinta.

El estado de la MT es un par [q, caché]: además del estado q, el control
finito guarda un símbolo en memoria (mem_cache_value). Por eso una transición
tiene la forma:

    δ([q, c], x) = ([q', c'], y, D)

donde x es el símbolo leído, y el símbolo escrito y D el desplazamiento.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

# El símbolo blank se representa internamente con None
# (en el YAML se escribe como una entrada vacía).
BLANK = None

Symbol = Optional[str]
TransitionKey = Tuple[str, Symbol, Symbol]  # (estado, caché, símbolo leído)

LEFT, RIGHT, STAY = "L", "R", "S"
DIRECTIONS = {LEFT: -1, RIGHT: 1, STAY: 0}


@dataclass(frozen=True)
class Transition:
    """Una regla δ([state, cache], read) = ([next_state, next_cache], write, move)."""

    state: str
    cache: Symbol
    read: Symbol
    next_state: str
    next_cache: Symbol
    write: Symbol
    move: str

    @property
    def key(self) -> TransitionKey:
        return (self.state, self.cache, self.read)


@dataclass
class TuringMachine:
    states: List[str]
    initial_state: str
    final_states: Set[str]
    input_alphabet: Set[str]
    tape_alphabet: Set[Symbol]  # incluye BLANK y el alfabeto de entrada
    transitions: Dict[TransitionKey, Transition]
    simulation_strings: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def get_transition(self, state: str, cache: Symbol, read: Symbol) -> Optional[Transition]:
        return self.transitions.get((state, cache, read))

    def is_final(self, state: str) -> bool:
        return state in self.final_states
