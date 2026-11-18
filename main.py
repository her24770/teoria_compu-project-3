"""CLI del simulador de Máquinas de Turing.

Uso:
    python main.py maquinas/ejemplos/primero_igual_ultimo.yaml
    python main.py archivo.yaml --cadena abba --max-pasos 500
"""
from __future__ import annotations

import argparse
import sys

from mt import TMParseError, Simulator, load_machine
from mt.models import BLANK, TuringMachine
from mt.simulator import DEFAULT_MAX_STEPS, SimulationResult


class Colors:
    def __init__(self, enabled: bool):
        self.enabled = enabled

    def _wrap(self, code: str, text: str) -> str:
        return f"\033[{code}m{text}\033[0m" if self.enabled else text

    def bold(self, t): return self._wrap("1", t)
    def dim(self, t): return self._wrap("2", t)
    def green(self, t): return self._wrap("32;1", t)
    def red(self, t): return self._wrap("31;1", t)
    def yellow(self, t): return self._wrap("33", t)
    def cyan(self, t): return self._wrap("36", t)


def blank_repr(tm: TuringMachine) -> str:
    """Usa 'B' para el blank salvo que 'B' sea un símbolo de la cinta."""
    return "□" if "B" in tm.tape_alphabet else "B"


def show_symbols(symbols, blank: str) -> str:
    shown = [blank if s is BLANK else s for s in symbols]
    sep = "" if all(len(s) == 1 for s in shown) else " "
    return sep.join(shown) or blank


def print_machine(tm: TuringMachine, c: Colors, blank: str) -> None:
    fmt = lambda xs: "{" + ", ".join(sorted(blank if x is BLANK else x for x in xs)) + "}"
    print(c.bold("Máquina de Turing"))
    print(f"  Q  = {{{', '.join(tm.states)}}}")
    print(f"  Σ  = {fmt(tm.input_alphabet)}")
    print(f"  Γ  = {fmt(tm.tape_alphabet)}")
    print(f"  q0 = {tm.initial_state}    F = {fmt(tm.final_states)}")
    print(f"  δ  : {len(tm.transitions)} transiciones")
    for w in tm.warnings:
        print(c.yellow(f"  Advertencia: {w}"))


def print_transitions(tm: TuringMachine, blank: str) -> None:
    b = lambda s: blank if s is BLANK else s
    print("  Función de transición:")
    for t in tm.transitions.values():
        print(f"    δ([{t.state}, {b(t.cache)}], {b(t.read)}) = "
              f"([{t.next_state}, {b(t.next_cache)}], {b(t.write)}, {t.move})")


def print_result(res: SimulationResult, c: Colors, blank: str, quiet: bool) -> None:
    title = f"Cadena: '{res.input_string}'" if res.input_string else "Cadena: ε (vacía)"
    print()
    print(c.bold(c.cyan("─" * 60)))
    print(c.bold(title))

    if not quiet and res.ids:
        width = len(str(res.ids[-1].step))
        for i, d in enumerate(res.ids):
            prefix = "  " if i == 0 else "⊢ "
            print(f"  {c.dim(str(d.step).rjust(width))}  {prefix}{d.format(blank)}")

    print(f"  Pasos: {res.steps}")
    print(f"  Cinta final: {show_symbols(res.final_tape, blank)}")
    print(f"  {res.message}")
    if res.accepted:
        print("  Resultado: " + c.green("ACEPTADA"))
    else:
        print("  Resultado: " + c.red("RECHAZADA"))
    if res.ids and not res.final_tape and res.input_string:
        print(c.yellow("  Nota: la cinta final quedó completamente en blank."))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Simulador de Máquinas de Turing de una cinta.")
    ap.add_argument("archivo", help="Archivo YAML con la descripción formal de la MT")
    ap.add_argument("-c", "--cadena", action="append",
                    help="Cadena a simular (se puede repetir). Reemplaza simulation_strings.")
    ap.add_argument("--max-pasos", type=int, default=DEFAULT_MAX_STEPS,
                    help=f"Límite de pasos por cadena (default {DEFAULT_MAX_STEPS})")
    ap.add_argument("-d", "--delta", action="store_true", help="Mostrar la función de transición")
    ap.add_argument("-q", "--quiet", action="store_true", help="No mostrar las IDs, solo el resultado")
    ap.add_argument("--sin-color", action="store_true", help="Desactivar colores")
    args = ap.parse_args(argv)

    c = Colors(sys.stdout.isatty() and not args.sin_color)

    try:
        tm = load_machine(args.archivo)
    except TMParseError as e:
        print(c.red(f"Error: {e}"), file=sys.stderr)
        return 1

    blank = blank_repr(tm)
    print_machine(tm, c, blank)
    if args.delta:
        print_transitions(tm, blank)

    strings = args.cadena if args.cadena is not None else tm.simulation_strings
    if not strings:
        print(c.yellow("\nNo hay cadenas para simular (simulation_strings vacío)."))
        return 0

    sim = Simulator(tm, max_steps=args.max_pasos)
    results = [sim.run(s) for s in strings]
    for res in results:
        print_result(res, c, blank, args.quiet)

    accepted = sum(r.accepted for r in results)
    print(c.bold(c.cyan("─" * 60)))
    print(c.bold(f"Resumen: {accepted} aceptada(s), {len(results) - accepted} rechazada(s)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
