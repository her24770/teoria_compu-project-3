# MT reconocedora de cadenas duplicadas

## Lenguaje

La máquina reconoce

\[
L = \{ww \mid w \in \{a,b\}^{+}\}.
\]

Una cadena pertenece a `L` si tiene longitud par, no es vacía y su primera
mitad es idéntica a su segunda mitad. Por ejemplo, `abbabb` pertenece porque
puede separarse como `abb · abb`; `abbaba` no pertenece porque sus mitades son
`abb` y `aba`.

Este lenguaje no es libre de contexto. La dificultad central es que la entrada
no contiene un separador que indique dónde termina la primera copia de `w`.

## Idea del algoritmo

La máquina trabaja en dos fases.

### 1. Encontrar la mitad

En cada recorrido marca el primer símbolo libre desde la izquierda y el último
símbolo libre desde la derecha. Las marcas conservan tanto el símbolo original
como la mitad a la que pertenece:

| Símbolo original | Primera mitad | Segunda mitad |
|---|---|---|
| `a` | `A` | `C` |
| `b` | `B` | `D` |

Después de cada pareja vuelve al inicio. Si, al buscar el extremo derecho de
una pareja, la máquina llega a `A` o `B`, quedó un símbolo sin pareja: la
longitud es impar y la máquina rechaza porque no existe una transición.

Para una entrada de longitud par, al terminar queda una cinta de la forma
`(A|B)^n(C|D)^n`. En ese momento la frontera entre las dos mitades ya está
identificada sin haber borrado sus valores.

Ejemplo para `abbabb`:

```text
abbabb -> AbbabD -> ABbaCD -> ABBCCD
```

### 2. Comparar las mitades

La máquina procesa las marcas `A/B` de izquierda a derecha. Convierte la marca
elegida en `X` y guarda su valor original (`a` o `b`) en
`mem_cache_value`. Después cruza el resto de la primera mitad y las marcas
derechas ya procesadas hasta encontrar el primer `C/D` pendiente:

- caché `a` solo puede emparejarse con `C`;
- caché `b` solo puede emparejarse con `D`.

Una coincidencia se convierte en `Z`; para una desigualdad no hay transición y
la cadena se rechaza. Después de cada coincidencia se vuelve al blank izquierdo
y se repite el proceso. Cuando la cinta contiene únicamente `X` y `Z`, se
verifica que no quede ningún `C/D` y se entra en `aceptar`.

Ejemplo de la segunda fase:

```text
ABBCCD -> XBBZCD -> XXBZZD -> XXXZZZ -> aceptar
```

## Tabla de estados

| Estado | Propósito |
|---|---|
| `buscar_izquierda` | Omite `A/B` y marca el primer `a/b` libre de la izquierda. También detecta que terminó la fase 1. |
| `ir_al_final` | Recorre la cinta hasta el blank derecho. |
| `buscar_derecha` | Omite `C/D` y marca el último `a/b` libre. Llegar a `A/B` implica longitud impar. |
| `volver_a_marcar` | Regresa al blank izquierdo para marcar otra pareja de extremos. |
| `preparar_comparacion` | Regresa al inicio una vez localizada la mitad. |
| `tomar_izquierda` | Elige el siguiente `A/B`, lo cambia a `X` y guarda `a/b` en caché. |
| `ir_a_segunda` | Busca el siguiente `C/D` y lo compara con la caché. |
| `volver_a_comparar` | Regresa al inicio después de una comparación correcta. |
| `verificar_final` | Comprueba que la segunda mitad contiene solo marcas `Z`. |
| `aceptar` | Estado final; entrar en él acepta inmediatamente. |

## Función de transición

Se usa `□` para el blank. Cada regla tiene la forma
`δ([estado, caché], leído) = ([estado nuevo, caché nueva], escrito, movimiento)`.
Las familias con varios símbolos representan una transición por cada símbolo
indicado, conservándolo en la cinta.

### Fase 1: localizar la mitad

| Estado y caché | Lee | Acción |
|---|---|---|
| `[buscar_izquierda, □]` | `A` o `B` | conservar, `R`, seguir en `buscar_izquierda` |
| `[buscar_izquierda, □]` | `a` | escribir `A`, `R`, ir a `ir_al_final` |
| `[buscar_izquierda, □]` | `b` | escribir `B`, `R`, ir a `ir_al_final` |
| `[buscar_izquierda, □]` | `C` o `D` | conservar, `L`, ir a `preparar_comparacion` |
| `[ir_al_final, □]` | `a`, `b`, `C` o `D` | conservar, `R`, seguir en `ir_al_final` |
| `[ir_al_final, □]` | `□` | escribir `□`, `L`, ir a `buscar_derecha` |
| `[buscar_derecha, □]` | `C` o `D` | conservar, `L`, seguir en `buscar_derecha` |
| `[buscar_derecha, □]` | `a` | escribir `C`, `L`, ir a `volver_a_marcar` |
| `[buscar_derecha, □]` | `b` | escribir `D`, `L`, ir a `volver_a_marcar` |
| `[volver_a_marcar, □]` | `a`, `b`, `A`, `B`, `C` o `D` | conservar, `L`, seguir en `volver_a_marcar` |
| `[volver_a_marcar, □]` | `□` | escribir `□`, `R`, ir a `buscar_izquierda` |
| `[preparar_comparacion, □]` | `A` o `B` | conservar, `L`, seguir en `preparar_comparacion` |
| `[preparar_comparacion, □]` | `□` | escribir `□`, `R`, ir a `tomar_izquierda` |

No se define una transición desde `buscar_derecha` al leer `A/B`. Esa es la
condición de rechazo para longitudes impares. Tampoco se define una transición
inicial sobre blank, por lo que `ε` se rechaza y se exige `w ≠ ε`.

### Fase 2: comparar las copias

| Estado y caché | Lee | Acción |
|---|---|---|
| `[tomar_izquierda, □]` | `X` | conservar, `R`, seguir en `tomar_izquierda` |
| `[tomar_izquierda, □]` | `A` | escribir `X`, guardar `a`, `R`, ir a `ir_a_segunda` |
| `[tomar_izquierda, □]` | `B` | escribir `X`, guardar `b`, `R`, ir a `ir_a_segunda` |
| `[tomar_izquierda, □]` | `Z` | conservar, `R`, ir a `verificar_final` |
| `[ir_a_segunda, a]` | `A`, `B` o `Z` | conservar, `R`, seguir en `ir_a_segunda` con caché `a` |
| `[ir_a_segunda, a]` | `C` | escribir `Z`, limpiar caché, `L`, ir a `volver_a_comparar` |
| `[ir_a_segunda, b]` | `A`, `B` o `Z` | conservar, `R`, seguir en `ir_a_segunda` con caché `b` |
| `[ir_a_segunda, b]` | `D` | escribir `Z`, limpiar caché, `L`, ir a `volver_a_comparar` |
| `[volver_a_comparar, □]` | `X`, `A`, `B`, `Z`, `C` o `D` | conservar, `L`, seguir en `volver_a_comparar` |
| `[volver_a_comparar, □]` | `□` | escribir `□`, `R`, ir a `tomar_izquierda` |
| `[verificar_final, □]` | `Z` | conservar, `R`, seguir en `verificar_final` |
| `[verificar_final, □]` | `□` | escribir `□`, `S`, ir a `aceptar` |

Las combinaciones `[ir_a_segunda, a]` con `D` y
`[ir_a_segunda, b]` con `C` se omiten intencionalmente: representan una
desigualdad entre las dos mitades y provocan rechazo.

## Cadenas de demostración

| Cadena | Separación | Resultado esperado |
|---|---|---|
| `abbabb` | `abb · abb` | Aceptada |
| `abaaba` | `aba · aba` | Aceptada |
| `abbaba` | `abb · aba` | Rechazada |
| `aabbab` | `aab · bab` | Rechazada |

Las cuatro cadenas tienen longitud 6 y cumplen el mínimo de longitud 5 de la
rúbrica.

## Puntos clave para explicarla en el video

1. No existe un separador; la primera fase construye la frontera entre mitades.
2. Las marcas `A/B/C/D` conservan el símbolo original y a qué mitad pertenece.
3. Una longitud impar se detecta cuando un extremo izquierdo queda sin pareja.
4. La caché transporta un `a` o `b` desde la primera mitad hasta la segunda.
5. Las transiciones ausentes implementan el rechazo; el único estado final es
   `aceptar`.
