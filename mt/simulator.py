"""Simulación de la MT y generación de descripciones instantáneas (IDs)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .models import BLANK, Symbol, Transition, TuringMachine
from .tape import Tape

DEFAULT_MAX_STEPS = 10_000

# Motivos por los que termina una simulación
HALT_FINAL = "final"                 # llegó a un estado de aceptación
HALT_NO_TRANSITION = "no_transition" # no hay δ aplicable y no es estado final
HALT_MAX_STEPS = "max_steps"         # se alcanzó el límite (posible ciclo infinito)
HALT_INVALID_INPUT = "invalid_input" # la cadena tiene símbolos fuera del alfabeto


@dataclass(frozen=True)
class InstantaneousDescription:
    """ID: α [q, c] β, donde el cabezal apunta al primer símbolo de β."""

    step: int
    state: str
    cache: Symbol
    left: List[Symbol]
    right: List[Symbol]
    transition: Optional[Transition] = None  # δ aplicada para llegar a esta ID

    def format(self, blank: str = "B") -> str:
        def show(s: Symbol) -> str:
            return blank if s is BLANK else s

        symbols = [show(s) for s in self.left + self.right]
        sep = "" if all(len(s) == 1 for s in symbols) else " "
        left = sep.join(show(s) for s in self.left)
        right = sep.join(show(s) for s in self.right)
        return f"{left}[{self.state}, {show(self.cache)}]{right}"


@dataclass
class SimulationResult:
    input_string: str
    accepted: bool
    halt_reason: str
    ids: List[InstantaneousDescription] = field(default_factory=list)
    final_tape: List[Symbol] = field(default_factory=list)
    message: str = ""

    @property
    def steps(self) -> int:
        return max(len(self.ids) - 1, 0)


class Simulator:
    def __init__(self, machine: TuringMachine, max_steps: int = DEFAULT_MAX_STEPS):
        self.machine = machine
        self.max_steps = max_steps

    def _id(self, step: int, state: str, cache: Symbol, tape: Tape,
            transition: Optional[Transition] = None) -> InstantaneousDescription:
        left, right = tape.snapshot()
        return InstantaneousDescription(step, state, cache, left, right, transition)

    def run(self, input_string: str) -> SimulationResult:
        tm = self.machine

        invalid = sorted({c for c in input_string if c not in tm.tape_alphabet})
        if invalid:
            return SimulationResult(
                input_string, False, HALT_INVALID_INPUT,
                message=f"Símbolos fuera del alfabeto: {', '.join(invalid)}",
            )

        tape = Tape(input_string)
        state, cache = tm.initial_state, BLANK
        ids = [self._id(0, state, cache, tape)]

        step = 0
        while True:
            if tm.is_final(state):
                reason, accepted = HALT_FINAL, True
                break
            if step >= self.max_steps:
                reason, accepted = HALT_MAX_STEPS, False
                break
            t = tm.get_transition(state, cache, tape.read())
            if t is None:
                reason, accepted = HALT_NO_TRANSITION, False
                break

            tape.write(t.write)
            tape.move(t.move)
            state, cache = t.next_state, t.next_cache
            step += 1
            ids.append(self._id(step, state, cache, tape, t))

        messages = {
            HALT_FINAL: f"Se alcanzó el estado final '{state}'.",
            HALT_NO_TRANSITION: f"No hay transición para δ([{state}, {cache or 'B'}], {tape.read() or 'B'}).",
            HALT_MAX_STEPS: f"Se alcanzó el límite de {self.max_steps} pasos (posible ciclo infinito).",
        }
        return SimulationResult(input_string, accepted, reason, ids, tape.content(), messages[reason])
