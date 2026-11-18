# MT alteradora: ordenar símbolos mediante intercambios vecinos

## Objetivo

Transformar una cadena no vacía sobre el alfabeto `{a, b}` para que todas las
`a` queden antes de las `b`, conservando la longitud y la cantidad de cada
símbolo.

Si la entrada contiene `m` símbolos `a` y `n` símbolos `b`, la salida será
`a^m b^n`, con `m, n >= 0` y `m + n >= 1`.

Por ejemplo, `babab` se transforma en `aabbb`. Una entrada ya ordenada o con
un solo tipo de símbolo conserva su contenido.

## Algoritmo elegido

1. Comenzar un recorrido de izquierda a derecha, sin intercambios registrados.
2. Comparar símbolos vecinos. Si forman `ba`, reemplazarlos por `ab` y
   registrar que hubo un intercambio.
3. Continuar el recorrido hasta el blank que delimita el extremo derecho.
4. Si hubo intercambios, regresar al inicio y comenzar otro recorrido,
   restableciendo el registro de cambios.
5. Si un recorrido completo termina sin intercambios, entrar al estado final.

Cada intercambio requiere varios pasos de la MT, porque el cabezal solo puede
leer y escribir una celda a la vez. La caché (`mem_cache_value`) guardará
temporalmente un símbolo durante la comparación y el intercambio. Los estados
distinguirán los recorridos con cambios de los recorridos sin cambios.

La máquina tendrá una sola cinta. El alfabeto de cinta previsto es
`{a, b, blank}`; el blank se escribirá como `null` o un valor vacío en YAML.
La caché comienza en blank, según las convenciones del simulador.

## Por qué funciona

Un intercambio `ba -> ab` conserva ambos símbolos y reduce en uno el número
de inversiones: pares de posiciones donde una `b` aparece antes que una `a`.
Como esa cantidad es finita y no negativa, solo puede haber una cantidad
finita de intercambios.

Si un recorrido no encuentra ningún par vecino `ba`, todas las `a` están
antes de las `b`. Por tanto, al detenerse, la cinta contiene la cadena ordenada
y conserva su longitud y sus cantidades originales. Para entradas no vacías,
la cinta final nunca queda completamente en blanco.

## Casos previstos para la demostración

Las cuatro entradas tienen longitud 5.

| Entrada | Salida esperada | Caso |
| --- | --- | --- |
| `babab` | `aabbb` | Símbolos alternados. |
| `bbaaa` | `aaabb` | Todos los símbolos están en el orden opuesto. |
| `aabbb` | `aabbb` | Cadena ya ordenada. |
| `bbbbb` | `bbbbb` | Un solo tipo de símbolo. |

También se verificarán cadenas cortas como `a`, `b`, `ab` y `ba`, y cadenas
de solo `a`. La cadena vacía queda fuera del dominio definido.