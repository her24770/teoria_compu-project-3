# Arquitectura del simulador

```
archivo.yaml ──► parser.py ──► TuringMachine ──► simulator.py ──► IDs + aceptada/rechazada ──► main.py (salida)
                                (models.py)          │
                                                     └── tape.py (cinta)
```

## Módulos (`mt/`)

| Módulo | Responsabilidad |
|---|---|
| `models.py` | Estructuras de datos: `Transition` y `TuringMachine`. El blank es `None`. |
| `parser.py` | Lee el YAML, valida la descripción formal y construye la `TuringMachine`. |
| `tape.py` | Cinta infinita en ambas direcciones. |
| `simulator.py` | Aplica δ paso a paso, genera las descripciones instantáneas y decide si acepta. |
| `main.py` (raíz) | CLI: carga la MT, simula las cadenas e imprime los resultados. |

## Decisiones de diseño

- **Estado = par `[q, caché]`.** Cada transición es
  `δ([q, c], x) = ([q', c'], y, D)`. La función δ se guarda en un diccionario con
  llave `(q, c, x)`, así buscar la transición siguiente es O(1).
- **Determinismo.** Si dos reglas tienen la misma llave `(q, c, x)`, el parser
  marca un error en lugar de escoger una de las dos.
- **Cinta como diccionario `posición → símbolo`.** Solo se guardan las celdas
  que no son blank. El cabezal puede moverse a posiciones negativas sin copiar
  listas, y escribir un blank borra la celda.
- **YAML con `BaseLoader`.** Todos los valores se leen como texto para que `0`,
  `1` o `yes` no se conviertan en int o bool. La entrada vacía, `~` o `null`
  se interpreta como blank.
- **Validaciones.** El parser verifica que los estados existan en `q_list`, que
  los símbolos leídos y escritos estén en `tape_alphabet` y que el
  desplazamiento sea L, R o S. El alfabeto de entrada se agrega
  automáticamente al de cinta.

## Simulación

1. La cinta se inicializa con la cadena, el cabezal en la posición 0, el estado
   en `q0` y la caché en blank.
2. En cada paso:
   - Si el estado es final, se detiene y **acepta**.
   - Si se alcanzó `--max-pasos`, se detiene y **rechaza** (posible ciclo infinito).
   - Se busca `δ(q, c, símbolo_actual)`. Si no existe, se detiene y **rechaza**.
   - Se escribe el símbolo, se mueve el cabezal, se actualiza `[q, c]` y se
     registra la nueva ID.
3. Cada ID tiene la forma `α[q, c]β` (notación de Hopcroft): α es lo que está a
   la izquierda del cabezal y β empieza en la celda bajo el cabezal. Los blanks
   de los extremos se recortan.
