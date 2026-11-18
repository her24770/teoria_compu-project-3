"""Parsing del archivo YAML que describe la MT."""
from __future__ import annotations

from typing import Any, Dict, List

import yaml

from .models import BLANK, DIRECTIONS, Symbol, Transition, TuringMachine

# Valores que se interpretan como blank además de la entrada vacía.
_BLANK_LITERALS = {"", "~", "null", "None"}


class TMParseError(Exception):
    """Error en la descripción formal de la MT."""


def load_machine(path: str) -> TuringMachine:
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        raise TMParseError(f"No se pudo abrir el archivo '{path}': {e}") from e
    return parse_machine_text(text)


def parse_machine_text(text: str) -> TuringMachine:
    # BaseLoader deja todos los escalares como strings: así '0', 'yes', '1.0'
    # no se convierten a int/bool/float. Una entrada vacía queda como ''.
    try:
        data = yaml.load(text, Loader=yaml.BaseLoader)
    except yaml.YAMLError as e:
        raise TMParseError(f"YAML inválido: {e}") from e
    if not isinstance(data, dict):
        raise TMParseError("El YAML debe ser un objeto con las claves de la MT.")
    return parse_machine(data)


def _symbol(value: Any) -> Symbol:
    if value is None:
        return BLANK
    value = str(value)
    return BLANK if value in _BLANK_LITERALS else value


def _require(data: Dict[str, Any], key: str, where: str) -> Any:
    if not isinstance(data, dict) or key not in data:
        raise TMParseError(f"Falta la clave '{key}' en {where}.")
    return data[key]


def _as_list(value: Any, where: str) -> List[Any]:
    if value is None or value == "":
        return []
    if not isinstance(value, list):
        raise TMParseError(f"'{where}' debe ser una lista.")
    return value


def parse_machine(data: Dict[str, Any]) -> TuringMachine:
    warnings: List[str] = []

    # --- Estados ---
    q_states = _require(data, "q_states", "la raíz")
    states = [str(q) for q in _as_list(_require(q_states, "q_list", "q_states"), "q_list")]
    if not states:
        raise TMParseError("'q_list' no puede estar vacía.")
    state_set = set(states)

    initial = str(_require(q_states, "initial", "q_states"))
    if initial not in state_set:
        raise TMParseError(f"El estado inicial '{initial}' no está en q_list.")

    raw_final = _require(q_states, "final", "q_states")
    finals = {str(q) for q in (raw_final if isinstance(raw_final, list) else [raw_final])}
    for q in finals:
        if q not in state_set:
            raise TMParseError(f"El estado final '{q}' no está en q_list.")

    # --- Alfabetos ---
    input_alphabet = {s for s in map(_symbol, _as_list(_require(data, "alphabet", "la raíz"), "alphabet")) if s is not BLANK}
    tape_alphabet = set(map(_symbol, _as_list(_require(data, "tape_alphabet", "la raíz"), "tape_alphabet")))
    missing = input_alphabet - tape_alphabet
    if missing:
        # El alfabeto de cinta siempre contiene al de entrada.
        tape_alphabet |= missing
    tape_alphabet.add(BLANK)

    # --- Función de transición ---
    transitions: Dict[tuple, Transition] = {}
    origin: Dict[tuple, int] = {}
    for i, entry in enumerate(_as_list(_require(data, "delta", "la raíz"), "delta"), start=1):
        where = f"delta[{i}]"
        params = _require(entry, "params", where)
        output = _require(entry, "output", where)

        state = str(_require(params, "initial_state", f"{where}.params"))
        cache = _symbol(params.get("mem_cache_value"))
        read = _symbol(params.get("tape_input"))
        next_state = str(_require(output, "final_state", f"{where}.output"))
        next_cache = _symbol(output.get("mem_cache_value"))
        write = _symbol(output.get("tape_output"))
        move = str(_require(output, "tape_displacement", f"{where}.output")).upper()

        for q in (state, next_state):
            if q not in state_set:
                raise TMParseError(f"{where}: el estado '{q}' no está en q_list.")
        for label, s in (("tape_input", read), ("tape_output", write)):
            if s not in tape_alphabet:
                raise TMParseError(f"{where}: el símbolo '{s}' de {label} no está en tape_alphabet.")
        for s in (cache, next_cache):
            if s not in tape_alphabet:
                warnings.append(f"{where}: el valor de caché '{s}' no está en tape_alphabet.")
        if move not in DIRECTIONS:
            raise TMParseError(f"{where}: desplazamiento '{move}' inválido (use L, R o S).")

        t = Transition(state, cache, read, next_state, next_cache, write, move)
        if t.key in transitions:
            # Una MT determinista no puede tener dos reglas para la misma entrada.
            raise TMParseError(
                f"{where}: transición duplicada para δ([{state}, {cache or 'B'}], {read or 'B'}); "
                f"ya definida en delta[{origin[t.key]}]."
            )
        transitions[t.key] = t
        origin[t.key] = i

    # --- Cadenas a simular ---
    strings = ["" if _symbol(s) is BLANK else str(s) for s in _as_list(data.get("simulation_strings"), "simulation_strings")]

    return TuringMachine(
        states=states,
        initial_state=initial,
        final_states=finals,
        input_alphabet=input_alphabet,
        tape_alphabet=tape_alphabet,
        transitions=transitions,
        simulation_strings=strings,
        warnings=warnings,
    )
