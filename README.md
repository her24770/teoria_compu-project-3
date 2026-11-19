# Proyecto 3 – Simulador de Máquinas de Turing

Teoría de la Computación · Universidad del Valle de Guatemala

Simulador de Máquinas de Turing de una cinta escrito en Python. La máquina se
describe en un archivo YAML (estados, alfabetos, función de transición y
cadenas de prueba); el programa la carga, simula cada cadena y muestra todas
las descripciones instantáneas hasta que la máquina acepta o rechaza.

## Video

**Enlace: https://youtu.be/8H94gJyUJ2Y**

## Integrantes

- Josué Hernández - carné 24770 (her24770).
- José Sanchez - carné 24092 (josesan28).
- Juan Daniel Ordoñez - carné 24979 (ord24979).

---

## Requisitos

- Python 3.9 o superior
- PyYAML (`requirements.txt`)

## Instalación

```bash
git clone git@github.com:her24770/teoria_compu-project-3.git
cd teoria_compu-project-3

python3 -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

```bash
python main.py <archivo.yaml> [opciones]
```

Las dos máquinas de la entrega:

```bash
python main.py maquinas/reconocedora.yaml
python main.py maquinas/alteradora.yaml
```

Opciones:

| Opción | Qué hace |
| --- | --- |
| `-d`, `--delta` | Muestra la función de transición completa |
| `-c CADENA` | Simula esa cadena en lugar de `simulation_strings` (se puede repetir) |
| `-q`, `--quiet` | Solo muestra el resultado, sin las descripciones instantáneas |
| `--max-pasos N` | Límite de pasos por cadena (por defecto 10 000) |
| `--sin-color` | Salida sin colores |

Ejemplo de salida:

```
Cadena: 'babab'
   0    [inicio, B]babab
   1  ⊢ b[limpia, b]abab
   2  ⊢ [intercambiar, a]bbbab
  ...
  36  ⊢ aabbb[aceptar, B]B
  Pasos: 36
  Cinta final: aabbb
  Resultado: ACEPTADA
```

Cada línea es una descripción instantánea con la forma `α[q, c]β`: `α` es lo
que hay a la izquierda del cabezal, `[q, c]` es el estado junto con el valor en
caché, y el cabezal está sobre el primer símbolo de `β`.

---

## Máquinas entregadas

### MT reconocedora – `maquinas/reconocedora.yaml`

Reconoce **L = { ww | w ∈ {a, b}⁺ }**: cadenas formadas por una misma palabra
escrita dos veces, sin separador. No es un lenguaje libre de contexto.

1. Marca alternadamente el primer y el último símbolo libre hasta encontrar la
   mitad. Si la longitud es impar, se queda sin transición y rechaza.
2. Toma cada símbolo de la primera mitad, lo guarda en la caché y lo compara
   con el símbolo correspondiente de la segunda mitad.

| Cadena | Mitades | Resultado |
| --- | --- | --- |
| `abbabb` | abb · abb | Aceptada |
| `abaaba` | aba · aba | Aceptada |
| `abbaba` | abb · aba | Rechazada |
| `aabbab` | aab · bab | Rechazada |

Diseño completo: [`docs/reconocedora.md`](docs/reconocedora.md)

### MT alteradora – `maquinas/alteradora.yaml`

Ordena una cadena sobre {a, b} dejando todas las `a` antes que las `b`, por
medio de intercambios vecinos `ba → ab`. Recorre la cinta hasta que una pasada
completa termina sin cambios. La caché guarda el símbolo vecino durante cada
intercambio.

| Entrada | Salida |
| --- | --- |
| `babab` | `aabbb` |
| `bbaaa` | `aaabb` |
| `abbaba` | `aaabbb` |
| `bbbaab` | `aabbbb` |

Diseño completo: [`docs/alteradora.md`](docs/alteradora.md)

---

## Formato del archivo YAML

```yaml
q_states:
  q_list: ['0', '1', '2']    # todos los estados
  initial: '0'
  final: '2'                 # también acepta una lista de estados finales
alphabet: [a, b]             # alfabeto de entrada
tape_alphabet:               # alfabeto de la cinta
- X
-                            # entrada vacía = blank
delta:
- params:
    initial_state: '0'
    mem_cache_value:         # vacío = blank
    tape_input: a
  output:
    final_state: '1'
    mem_cache_value: a
    tape_output: X
    tape_displacement: R     # L, R o S
simulation_strings:
- aabab
```

Convenciones del simulador:

- El **blank** se escribe como una entrada vacía (también vale `null` o `~`).
  En la salida se muestra como `B`, o como `□` si la máquina usa `B` como
  símbolo.
- El **estado** es el par `[q, caché]`. La caché comienza en blank.
- El alfabeto de entrada se agrega automáticamente al de la cinta.
- La máquina **acepta** en cuanto entra a un estado final.
- **Rechaza** si no existe una transición para el estado, la caché y el
  símbolo actuales, o si supera el límite de pasos (posible ciclo infinito).
- Debe ser determinista: dos transiciones con la misma entrada producen un
  error al cargar el archivo.

Si el YAML tiene un error (un estado que no existe, un símbolo fuera del
alfabeto, un desplazamiento inválido, etc.), el programa indica en qué
transición está, por ejemplo `delta[7]`.

---

## Estructura del proyecto

```
.
├── main.py                 # programa de consola
├── mt/
│   ├── models.py           # Transition y TuringMachine
│   ├── parser.py           # lectura y validación del YAML
│   ├── tape.py             # cinta infinita en ambas direcciones
│   └── simulator.py        # simulación y descripciones instantáneas
├── maquinas/
│   ├── reconocedora.yaml
│   ├── alteradora.yaml
│   └── ejemplos/           # máquinas pequeñas de prueba
├── tests/                  # pruebas unitarias
├── docs/
│   ├── arquitectura.md
│   ├── reconocedora.md
│   └── alteradora.md
└── requirements.txt
```

La explicación de cómo funciona el simulador por dentro está en
[`docs/arquitectura.md`](docs/arquitectura.md).

## Pruebas

```bash
python -m unittest discover -s tests
```
