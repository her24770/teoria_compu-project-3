import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mt import BLANK, Simulator, Tape, TMParseError, load_machine, parse_machine_text
from mt.simulator import HALT_FINAL, HALT_INVALID_INPUT, HALT_MAX_STEPS, HALT_NO_TRANSITION

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def machine(delta: str, states="['0', '1', '2']", final="'2'", tape="[a, b, X, '#', '']") -> str:
    return f"""
q_states:
  q_list: {states}
  initial: '0'
  final: {final}
alphabet: [a, b]
tape_alphabet: {tape}
delta:
{delta}
"""


def rule(q, c, r, q2, c2, w, d) -> str:
    return (f"- params: {{initial_state: '{q}', mem_cache_value: {c}, tape_input: {r}}}\n"
            f"  output: {{final_state: '{q2}', mem_cache_value: {c2}, tape_output: {w}, tape_displacement: {d}}}\n")


class TestParser(unittest.TestCase):
    def test_ejemplo_del_enunciado(self):
        tm = load_machine(os.path.join(ROOT, "maquinas/ejemplos/enunciado.yaml"))
        self.assertEqual(tm.states, ["0", "1", "2", "3", "4", "5"])
        self.assertEqual(tm.initial_state, "0")
        self.assertEqual(tm.final_states, {"5"})
        self.assertIn(BLANK, tm.tape_alphabet)
        # El alfabeto de entrada se agrega al de la cinta aunque no se liste.
        self.assertTrue({"a", "b", "#", "X"} <= tm.tape_alphabet)
        t = tm.get_transition("0", BLANK, "a")
        self.assertEqual((t.next_state, t.next_cache, t.write, t.move), ("1", "a", BLANK, "R"))
        self.assertEqual(tm.simulation_strings, ["aab#aab", "ab#ab", "abbababa#aba"])

    def test_estados_numericos_sin_comillas_son_strings(self):
        tm = parse_machine_text(machine(rule(0, "", "a", 2, "", "a", "S"), states="[0, 1, 2]", final="2"))
        self.assertEqual(tm.initial_state, "0")
        self.assertIsNotNone(tm.get_transition("0", BLANK, "a"))

    def test_transicion_duplicada(self):
        delta = rule(0, "", "a", 1, "", "a", "R") + rule(0, "", "a", 2, "", "b", "L")
        with self.assertRaisesRegex(TMParseError, "duplicada"):
            parse_machine_text(machine(delta))

    def test_estado_inexistente(self):
        with self.assertRaisesRegex(TMParseError, "'9'"):
            parse_machine_text(machine(rule(0, "", "a", 9, "", "a", "R")))

    def test_simbolo_fuera_de_cinta(self):
        with self.assertRaisesRegex(TMParseError, "'Z'"):
            parse_machine_text(machine(rule(0, "", "a", 1, "", "Z", "R")))

    def test_desplazamiento_invalido(self):
        with self.assertRaisesRegex(TMParseError, "desplazamiento"):
            parse_machine_text(machine(rule(0, "", "a", 1, "", "a", "X")))

    def test_desplazamiento_en_minuscula(self):
        tm = parse_machine_text(machine(rule(0, "", "a", 1, "", "a", "r")))
        self.assertEqual(tm.get_transition("0", BLANK, "a").move, "R")

    def test_falta_clave(self):
        with self.assertRaisesRegex(TMParseError, "delta"):
            parse_machine_text("q_states: {q_list: ['0'], initial: '0', final: '0'}\nalphabet: [a]\ntape_alphabet: [a]")


class TestTape(unittest.TestCase):
    def test_crece_a_la_izquierda(self):
        tape = Tape("ab")
        tape.move("L")
        self.assertIs(tape.read(), BLANK)
        tape.write("X")
        self.assertEqual(tape.content(), ["X", "a", "b"])
        self.assertEqual(tape.snapshot(), ([], ["X", "a", "b"]))

    def test_escribir_blank_borra(self):
        tape = Tape("ab")
        tape.write(BLANK)
        self.assertEqual(tape.content(), ["b"])
        tape.move("R")
        tape.write(BLANK)
        self.assertTrue(tape.is_blank())


class TestSimulator(unittest.TestCase):
    def setUp(self):
        self.tm = load_machine(os.path.join(ROOT, "maquinas/ejemplos/primero_igual_ultimo.yaml"))

    def test_aceptada(self):
        res = Simulator(self.tm).run("abbaba")
        self.assertTrue(res.accepted)
        self.assertEqual(res.halt_reason, HALT_FINAL)
        self.assertEqual(res.ids[0].format(), "[0, B]abbaba")
        self.assertEqual(res.ids[-1].format(), "abbab[3, B]a")
        self.assertEqual(res.steps, 8)

    def test_rechazada_sin_transicion(self):
        res = Simulator(self.tm).run("abbab")
        self.assertFalse(res.accepted)
        self.assertEqual(res.halt_reason, HALT_NO_TRANSITION)

    def test_cadena_vacia(self):
        res = Simulator(self.tm).run("")
        self.assertFalse(res.accepted)
        self.assertEqual(res.ids[0].format(), "[0, B]B")

    def test_simbolo_invalido(self):
        res = Simulator(self.tm).run("abc")
        self.assertFalse(res.accepted)
        self.assertEqual(res.halt_reason, HALT_INVALID_INPUT)

    def test_ciclo_infinito(self):
        delta = rule(0, "", "a", 0, "", "a", "S")
        res = Simulator(parse_machine_text(machine(delta)), max_steps=50).run("a")
        self.assertFalse(res.accepted)
        self.assertEqual(res.halt_reason, HALT_MAX_STEPS)
        self.assertEqual(res.steps, 50)

    def test_alteradora_invierte_simbolos(self):
        # Cambia a<->b recorriendo la cadena y acepta al llegar al blank.
        delta = (rule(0, "", "a", 0, "", "b", "R") + rule(0, "", "b", 0, "", "a", "R")
                 + rule(0, "", "''", 1, "", "''", "L") + rule(1, "", "a", 1, "", "a", "L")
                 + rule(1, "", "b", 1, "", "b", "L") + rule(1, "", "''", 2, "", "''", "R"))
        res = Simulator(parse_machine_text(machine(delta))).run("aabab")
        self.assertTrue(res.accepted)
        self.assertEqual("".join(res.final_tape), "bbaba")
        self.assertEqual(res.ids[-1].format(), "[2, B]bbaba")


if __name__ == "__main__":
    unittest.main()
