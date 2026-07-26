# Guion de video — Semana 2

Guía para grabar. No es un libreto palabra por palabra: son los pasos y
los "momentos aha" a mostrar, en orden. Hay dos videos: **teoría** y
**práctica**. Cada bloque indica qué mostrar en pantalla.

---

## VIDEO 1 — Teoría (objetivo: ~15-25 min)

### Bloque 0 — Enganche (2 min)

Recordar el cierre de Semana 1: "declaramos las reglas en AGENTS.md y en
el core, pero declarar no es garantizar". Plantear la pregunta de la
semana: *¿dónde vive una regla de negocio, y quién la hace cumplir?*

Mencionar que esta duda no es trivial: surgió de un desacuerdo real entre
docentes. Eso da permiso a los cursantes de no tenerlo claro tampoco.

### Bloque 1 — Auditar el "antes": mostrar los problemas reales (5 min)

Este bloque usa la **versión inicial** del starter (la de Semana 1), no
la nueva. La idea es mostrar auditoría real sobre código imperfecto.

Mostrar en pantalla:

1. `app/application/use_cases.py` de la versión vieja → señalar
   `from app.infrastructure import repository`. "Application está
   importando infraestructura directamente. Esto viola la regla de
   dependencia de Clean Architecture."
2. Correr el test de arquitectura que falla:
   `pytest -m arquitectura_pendiente -v` (en la versión vieja) → se ve
   el FAILED con el mensaje. "El código mismo nos delata la fuga, sin
   opinión humana de por medio."
3. Mostrar la duplicación documental: la misma frase de RET-001 repetida
   textual en `docs/reglas.md` y `docs/alcance_starter.md`. "Dos fuentes
   de verdad para lo mismo: si edito una y no la otra, quedan
   desincronizadas."
4. Mostrar `docs/trazabilidad_reglas.md` viejo → estructura desordenada,
   tabla que solo referencia un test. "Una tabla de trazabilidad
   incompleta no cumple su promesa."

Momento aha: **auditar no es leer teoría bonita; es encontrar lo que no
cierra en tu propio proyecto.**

### Bloque 2 — La teoría, con vocabulario preciso (8-10 min)

Apoyarse en `docs/frontera_core_application.md`. No leerlo entero;
explicar con las propias palabras estos puntos, en este orden:

1. "La regla vive en el core" = está *expresada* en términos de negocio
   ahí, no que sea el único lugar con protección. Separar *declarar* de
   *garantizar*. Diferencia asegurar vs. garantizar (RET-001 en Semana 1
   está asegurada, no garantizada).
2. La tabla de responsabilidades (quién pregunta / quién tiene efectos /
   quién sabe de negocio). Mostrarla desde `docs/arquitectura.md`.
3. La prueba del verbo: `puede_...` → core; `intentar_...` → caso de uso.
   Usar `puede_crear_retencion` (real, en `rules.py`) como ejemplo de
   core bien hecho.
4. TOCTOU: explicar con el flujo de 4 pasos por qué el core "acierta" y
   aun así la regla se viola bajo concurrencia. Conectar con
   `test_race_demo.py`. "La garantía real no puede vivir en el core —
   llega en Semana 3, en la base de datos."
5. Honestidad teórica (opcional, si hay tiempo): mencionar que la teoría
   estricta admitiría un puerto en el núcleo (DIP), y que nosotros
   elegimos ser más estrictos a propósito. No es dogma, es una decisión
   verificable.

### Bloque 3 — Mostrar el "después": la versión resuelta (5 min)

Cambiar a la **versión nueva** (Semana 2). Mostrar:

1. `app/application/ports.py` → el puerto `HoldRepository`. "Esto es solo
   una firma, un contrato. No ejecuta nada."
2. `app/infrastructure/repository.py` → `SqlAlchemyHoldRepository`
   implementa el puerto. "El adaptador concreto."
3. `app/application/use_cases.py` → ahora recibe `repo: HoldRepository`,
   ya no importa infraestructura.
4. `app/api/routes.py` → `get_repo` construye el adaptador e inyecta.
   "El único lugar que decide qué implementación se usa."
5. Correr `pytest -v` → suite en verde. Correr los tests de arquitectura
   → ahora **pasan**. "La regla declarada en prosa ahora es imposible de
   violar sin que el CI se ponga rojo."
6. Cerrar con ADR-002: mostrar que la decisión (con su costo YAGNI) quedó
   documentada. "No escondimos que antes estaba mal; lo documentamos."

---

## VIDEO 2 — Práctica (objetivo: ~10-15 min)

### Bloque 1 — Levantar el proyecto (3 min)

- `docker compose up --build` → mostrar la API viva en
  `http://localhost:8000/docs` (Swagger autogenerado).
- Señalar que el contrato OpenAPI sale solo de los schemas de FastAPI:
  "la documentación de la API no se escribe a mano, se deriva del código".

### Bloque 2 — Actividad con el agente: diagrama desde el código (5 min)

- Abrir `docs/diagrama_estados.md` y mostrar el diagrama Mermaid ya
  incluido.
- Pedirle al agente (en vivo) que **regenere** el diagrama leyendo
  `app/core/entities.py` y `app/application/use_cases.py`.
- Comparar lo que produce el agente con el diagrama del archivo.
- Momento aha: señalar que `EXPIRED` y `RELEASED` existen en el enum pero
  no tienen transición implementada. "El modelo declara más de lo que el
  código cumple. Eso es un hallazgo de auditoría, no un error a esconder."

### Bloque 3 — Poner a prueba la constitución (opcional, 4 min)

- Pedirle al agente algo que viole una regla de AGENTS.md o que rompa la
  arquitectura (por ejemplo: "meté una consulta SQL directa en el
  endpoint de eventos"). Ver si el agente respeta AGENTS.md o si lo hace
  igual.
- Correr los tests de arquitectura después: si el agente contaminó una
  capa, el test lo detecta. "El test es la red de seguridad cuando la
  constitución no alcanza."

### Cierre

Enunciar el puente a Semana 3: "declaramos y aislamos la regla; ahora
falta hacerla imposible de violar bajo concurrencia, con una garantía
real en PostgreSQL". Y recordar el acuerdo: la integración con Frontend
se hace en Semana 4, sobre un contrato ya congelado.
