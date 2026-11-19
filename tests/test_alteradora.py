"""Pruebas de integración de la MT que ordena cadenas sobre {a, b}."""

import os
import sys
import unittest
from collections import Counter
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mt import Simulator, load_machine
from mt.simulator import HALT_FINAL, HALT_INVALID_INPUT, HALT_NO_TRANSITION

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestAlteradora(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.machine = load_machine(os.path.join(ROOT, "maquinas", "alteradora.yaml"))

    def comprobar_ordenacion(self, entrada, salida_esperada):
        resultado = Simulator(self.machine).run(entrada)

        # Llegar al estado final comprueba que no faltaron reglas ni se agotó
        # el límite de pasos del simulador para esta entrada.
        self.assertTrue(resultado.accepted, resultado.message)
        self.assertEqual(resultado.halt_reason, HALT_FINAL)
        self.assertEqual(resultado.final_tape, list(salida_esperada))
        self.assertEqual(len(resultado.final_tape), len(entrada))
        self.assertEqual(Counter(resultado.final_tape), Counter(entrada))
        self.assertTrue(resultado.final_tape, "La cinta final no debe quedar vacía.")

    def test_cuatro_cadenas_de_demostracion(self):
        esperadas = {
            "babab": "aabbb",
            "bbaaa": "aaabb",
            "aabbb": "aabbb",
            "bbbbb": "bbbbb",
        }
        self.assertEqual(len(self.machine.simulation_strings), 4)
        self.assertEqual(set(self.machine.simulation_strings), set(esperadas))
        for entrada in self.machine.simulation_strings:
            with self.subTest(entrada=entrada):
                self.assertGreaterEqual(len(entrada), 5)
                self.comprobar_ordenacion(entrada, esperadas[entrada])

    def test_todas_las_cadenas_de_longitud_1_a_8(self):
        # 510 entradas: incluye a, b, ab, ba, cadenas homogéneas y ordenadas.
        # sorted proporciona el resultado esperado sin repetir el algoritmo
        # de intercambios vecinos implementado por la MT.
        for longitud in range(1, 9):
            for simbolos in product("ab", repeat=longitud):
                entrada = "".join(simbolos)
                with self.subTest(entrada=entrada):
                    self.comprobar_ordenacion(entrada, sorted(entrada))

    def test_cadenas_mas_largas(self):
        casos = [
            ("b" * 12 + "a" * 12, "a" * 12 + "b" * 12),
            ("ba" * 12, "a" * 12 + "b" * 12),
            ("a" * 12 + "b" * 12, "a" * 12 + "b" * 12),
            ("a" * 24, "a" * 24),
            ("b" * 24, "b" * 24),
        ]
        for entrada, esperada in casos:
            with self.subTest(entrada=entrada):
                self.comprobar_ordenacion(entrada, esperada)

    def test_cadena_vacia_fuera_del_dominio(self):
        resultado = Simulator(self.machine).run("")
        self.assertFalse(resultado.accepted)
        self.assertEqual(resultado.halt_reason, HALT_NO_TRANSITION)
        self.assertEqual(resultado.steps, 0)

    def test_simbolos_fuera_del_alfabeto(self):
        for entrada in ("ababa#", "aabcb", "ABABA", "ab ab"):
            with self.subTest(entrada=entrada):
                resultado = Simulator(self.machine).run(entrada)
                self.assertFalse(resultado.accepted)
                self.assertEqual(resultado.halt_reason, HALT_INVALID_INPUT)


if __name__ == "__main__":
    unittest.main()
