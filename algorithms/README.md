# Algoritmos de ISP Inteligente

Módulo Python independiente para procesar diagnósticos (CU-40), buscar rutas,
seleccionar técnicos y calcular proximidad. No importa Django, no consulta
PostgreSQL ni persiste resultados: Backend prepara los datos, llama a estas
funciones y guarda las respuestas.

## Entorno

El equipo acordó Python 3.14.4. Este módulo usa únicamente la biblioteca
estándar, por lo que `requirements.txt` no necesita paquetes externos.

## Rutas

`graph.Graph` representa un grafo ponderado. Las aristas son bidireccionales
por defecto; puede construirse como dirigido o especificar la dirección al
agregar cada arista. Los pesos deben ser finitos y no negativos.

Funciones disponibles en `algorithms.graph`:

- `breadth_first_search`: minimiza el número de aristas, no el costo ponderado.
- `depth_first_search`: explora por profundidad y no garantiza ruta óptima.
- `uniform_cost_search`: minimiza el costo total de la ruta.
- `greedy_best_first_search`: prioriza una heurística y no garantiza óptimo.
- `astar_search`: encuentra una ruta óptima si la heurística entregada es
  admisible.
- `compare_routes`: ejecuta las cinco búsquedas para el mismo origen y destino.

Cada búsqueda devuelve `PathResult(path, cost, algorithm, expanded_nodes,
elapsed_seconds)` o `None` si no hay ruta. `cost` suma los pesos de las aristas;
`expanded_nodes` cuenta los nodos cuyos vecinos se procesaron, y
`elapsed_seconds` mide búsqueda más reconstrucción (sin construir el grafo).
El tiempo depende de la máquina y de la carga del sistema. BFS y DFS seleccionan
según su estrategia, así que su costo puede ser mayor que el de UCS o A*.

Ejemplo de uso:

```python
from algorithms.graph import Graph, compare_routes

city = Graph[str]()
city.add_edge("A", "B", 4)
city.add_edge("A", "C", 2)
city.add_edge("C", "B", 1)
city.add_edge("B", "D", 3)
city.add_edge("C", "D", 8)

# La heurística depende de las coordenadas o datos del mapa que entregue
# el proyecto; cero es válida, aunque no acelera la búsqueda A*.
results = compare_routes(city, "A", "D", heuristic=lambda _node, _goal: 0)
```

La heurística para A* debe ser admisible para garantizar optimalidad. Para
Greedy puede utilizarse una estimación aproximada, teniendo presente que el
algoritmo no promete la ruta de menor costo.

## Diagnóstico (CU-40)

`ISPDiagnosticEngine` recibe hechos estructurados y devuelve un
`DiagnosisReport` con diagnósticos, recomendaciones, hechos inferidos y las
reglas que se activaron. `result.to_dict()` produce una estructura serializable
para la API. No interpreta texto libre del ticket ni accede al Backend.

```python
from algorithms import ISPDiagnosticEngine

engine = ISPDiagnosticEngine()
result = engine.process({"no_hay_internet", "router_apagado"})

print(result.diagnoses)       # ('router_apagado',)
print(result.recommendations) # ('encender_router',)
print(result.explanation)     # reglas que justifican el resultado

query = engine.verify_hypothesis(
    "recomendacion:contactar_proveedor",
    {"cable_correcto", "sin_conexion"},
)
print(query.proven)
print(query.explanation)
```

El motor genérico `KnowledgeBase` admite reglas propias con antecedentes,
conclusión, prioridad y descripción. `forward_chain` aplica reglas hasta llegar
a un punto fijo; `backward_chain` intenta probar una hipótesis y corta ciclos.
Las reglas compatibles se aplican todas: prioridad, especificidad y orden
determinan la traza, pero no eliminan conclusiones.

`default_isp_rules()` contiene un prototipo didáctico basado en el ejemplo de
diagnóstico de red de la Sesión 04: router apagado, revisión del cable y posible
contacto con el proveedor. No es una política técnica aprobada del ISP; el
equipo debe validar síntomas, diagnóstico y recomendaciones antes de usarlo en
operación. Si no hay hechos suficientes, el motor devuelve un informe sin
diagnóstico ni recomendación.

## Selección de técnicos

`TechnicianCandidate` acepta los campos que el Backend puede mapear desde el
modelo de técnico: identificador, especialidad, disponibilidad, estado activo,
carga de trabajo y coordenadas. La selección descarta inactivos, no
disponibles, especialidad distinta o ubicación incompleta.

`score_technicians` ordena candidatos por una combinación normalizada de
distancia geográfica y carga de trabajo. `select_technician` devuelve el mejor
candidato o `None`; Backend decide registrar la asignación o escalar el caso.
Los pesos son configurables por prioridad mediante `AssignmentPolicy`. La
política inicial propuesta aumenta la importancia de la cercanía al subir la
prioridad: baja 30/70, media 50/50, alta 70/30 y crítica 85/15 (distancia/carga).
Es una regla inicial explícita de Celeste, no una decisión ya validada por el
equipo; puede reemplazarse configurando otra política.

La distancia actual usa Haversine en línea recta, no la distancia por calles ni
la ruta del grafo. `is_within_radius` comparte esta medida para apoyar el caso
de proximidad del técnico (CU-45); el umbral debe proporcionarlo Backend o
configuración del sistema.

## Límites de integración pendientes

- Acordar el formato/fuente del grafo vial y qué significa el costo de una
  arista (distancia, tiempo u otro costo).
- Acordar la heurística y el sistema de coordenadas del mapa.
- Acordar el radio y frecuencia de detección para CU-45.
- Validar con el equipo la política inicial de pesos por prioridad.
- Validar la base de conocimiento ISP inicial de CU-40 con el equipo o un
  especialista del dominio.
- Acordar con Backend el formato estructurado de hechos de entrada y la
  respuesta que presentará y persistirá.
- Backend es responsable de validar permisos, estados, concurrencia y de
  persistir la asignación. Este módulo solo calcula.

## Verificación local

Desde la raíz del repositorio, ejecutar `python -m unittest discover -s algorithms/tests -v`.
Las pruebas cubren las cinco búsquedas y sus métricas, el puntaje y selección de
técnicos, y ambos encadenamientos de CU-40.
