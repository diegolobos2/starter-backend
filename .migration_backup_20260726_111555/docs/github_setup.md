# Subir el proyecto a GitHub

Guía para pasar de "zip" a repositorio versionado. A partir de la Semana
2, tener el proyecto en GitHub deja de ser opcional: varias actividades
(guardar el diagrama versionado, correr los tests de arquitectura en CI,
que Frontend consuma un contrato estable) presuponen un repo real con
historial, no un archivo comprimido.

## Antes de subir: verificar que no se filtre nada

1. Confirmar que existe un `.gitignore` que excluya al menos:
   ```
   __pycache__/
   *.pyc
   .venv/
   venv/
   tests/test_data.db
   .env
   ```
2. No subir credenciales. En este starter las credenciales de Postgres
   están en `docker-compose.yml` con valores de ejemplo (`app`/`app`),
   que son inofensivos para un entorno didáctico local. Si en algún
   momento se usan credenciales reales, deben ir en un `.env` **no
   versionado**.

## Pasos para subir (primera vez)

Desde la carpeta del proyecto, en la terminal:

```bash
git init
git add .
git commit -m "Semana 2: puerto/adaptador, tests de arquitectura, docs consolidados"
```

Luego, crear un repositorio vacío en GitHub (sin README, para no generar
conflictos) y conectar:

```bash
git remote add origin https://github.com/TU_USUARIO/starter-backend-ia.git
git branch -M main
git push -u origin main
```

## Público o privado

- **Privado** al principio es lo más prudente: permite iterar sin
  exponer material a medio terminar, y se puede dar acceso puntual a
  Martín (Frontend) como colaborador.
- Se puede hacer público más adelante, cuando el material esté estable.

## Cómo lo consumen los alumnos

En lugar de repartir un zip nuevo cada vez que hay un cambio, los
cursantes clonan una vez y actualizan con `git pull`:

```bash
git clone https://github.com/TU_USUARIO/starter-backend-ia.git
cd starter-backend-ia
docker compose up --build
```

Si el repo es privado, agregar a los cursantes como colaboradores, o
usar una organización con un equipo.

## Cómo lo consume Frontend (Martín)

Martín no necesita que despliegues nada en un servidor. Le alcanza con:

```bash
git clone ...
docker compose up --build
```

y consumir el contrato en `http://localhost:8000/docs` (Swagger) o el
JSON de OpenAPI en `http://localhost:8000/openapi.json`. Cada quien corre
su propia copia local; no hace falta un backend compartido en la nube. El
despliegue a un VPS/Cloud, si alguna vez se necesita un endpoint
compartido y persistente, es tema de Semana 4 o posterior, no un
requisito para integrar.

## Próximo paso natural: CI

Una vez en GitHub, el cierre del círculo con Unidad 1 (que ya trabajó
GitHub Actions) es agregar un workflow que corra `pytest` en cada push.
Así, los tests de arquitectura de la Semana 2 se vuelven una barrera
automática: si alguien (persona o agente) contamina una capa, el pipeline
se pone en rojo sin que nadie tenga que revisarlo a mano. Esa integración
con CI es un buen contenido para conectar explícitamente con lo que los
cursantes ya hicieron en Unidad 1.
