
## Contexto general
- Instituto de inglés en Paraguay, 150-250 alumnos por año lectivo (marzo-diciembre).
- Cada alumno cursa un solo curso a la vez (no hay relación muchos-a-muchos alumno-curso).
- Hay matrícula (pago único anual) además de la cuota mensual.
- 3 profesores actualmente; se les paga por alumno pagante, según el curso que dictan.
- La mayoría de los cursos se reúnen 2 veces por semana, 1.5 horas cada sesión.
- 3 aulas fijas: Room 1, Room 2, Room 3.
- Exámenes: 4 por año lectivo por curso, cada uno con 4 partes (Reading, Writing, Listening, Oral).
- Se necesita facturación electrónica para Paraguay (sistema SIFEN/DNIT).

## Decisiones de stack
- **Backend + frontend**: Django (el usuario no tenía experiencia real con Flask pese a un proyecto anterior; se descartó FastAPI por no traer admin/CRUD automático, que es clave para esta app).
- **Base de datos**: PostgreSQL (ya instalado localmente, DB ya creada).
- **Hosting recomendado**: servidor local en el instituto (LAN), ya que la operación diaria no depende de internet; solo hace falta conexión para transmitir facturas a SIFEN (hay ventana de 72 hs, "validación posterior") y para backups offsite.
- **Redundancia de datos**: backups automáticos del proveedor + backup independiente (pg_dump a Backblaze B2 / Cloudflare R2) + PITR si está disponible.
- **Estilo/UI**: Tailwind (ya lo conoce de otro proyecto) + django-crispy-forms (formularios) + django-unfold o django-jazzmin (admin con mejor cara) + HTMX (interactividad sin frontend separado, ej. marcar asistencia sin recargar).
- **Facturación SIFEN**: se decidió NO construir la integración directa con SIFEN (estimado 4-8 semanas de trabajo); usar un proveedor certificado con API REST en su lugar. Candidatos identificados: FactPy, eVENDÉ, TracertSystem (pendiente pedir cotizaciones/comparar).

## Modelo de datos (apps y modelos de Django)

**alumnos/models.py**
- `Padre`: nombre, ruc_ci (único), telefono
- `Alumno`: nombre, fecha_nacimiento, colegio, grado_colegio, `padres` (ManyToMany a Padre — puede tener padre y madre por separado), `curso` (FK directa a Curso, no junction table), ficha_personal (texto libre), activo, fecha_inscripcion

**cursos/models.py**
- `Profesor`: nombre, ci, telefono, tarifa_alumno, `usuario` (OneToOne a User de Django, para el login del portal de profesores)
- `Curso`: nombre, profesor (FK), activo
- `Horario`: curso (FK), dia_semana, hora_inicio, hora_fin, aula (choices Room 1/2/3) — permite varios bloques semanales por curso
- `Sesion`: curso (FK), fecha — una fila por clase que efectivamente ocurre, de donde cuelga la asistencia

**asistencia/models.py**
- `Asistencia`: sesion (FK), alumno (FK), estado (presente/ausente/tardanza)

**examenes/models.py**
- `Examen`: curso (FK), nombre, fecha
- `Resultado`: examen (FK), alumno (FK), puntaje_reading, puntaje_writing, puntaje_listening, puntaje_oral, observaciones, property `puntaje_total`

**facturacion/models.py**
- `Cuota`: alumno (FK), curso (FK), tipo (matrícula/mensualidad), anio_lectivo, mes, monto, estado (pendiente/pagada/vencida), fecha_pago — separada de Factura a propósito
- `Factura`: cuota (OneToOne, PROTECT), fecha, razon_social, ruc_ci, descripcion, monto, cdc (SIFEN), estado_sifen

**calendario/models.py**
- `Evento`: nombre, tipo (feriado/vacaciones/otro), fecha_inicio, fecha_fin — SOLO feriados/vacaciones; los cumpleaños y fechas de examen se calculan desde Alumno.fecha_nacimiento y Examen.fecha, no se duplican

**portal_profesor/** (acceso separado para profesores, no usa el admin)
- `decorators.py`: `profesor_required` — exige login + que el usuario tenga un Profesor vinculado
- `views.py`: `mis_cursos`, `tomar_asistencia`, `cargar_notas`, `editar_ficha` — cada vista filtra explícitamente por `profesor=request.user.profesor` para que un profesor nunca pueda ver/editar cursos ajenos
- `urls.py`: rutas de las vistas de arriba

## Progreso de implementación (ya hecho)
- Proyecto Django creado: workspace "Anglo", paquete interno llamado `config` (no "instituto")
- Entorno virtual (.venv) activo, Django instalado
- Las 7 apps creadas con `startapp`: alumnos, cursos, asistencia, examenes, facturacion, calendario, portal_profesor
- `models.py` de cada app ya reemplazado con el contenido definitivo de arriba
- En `portal_profesor`: `views.py` reemplazado; `urls.py` y `decorators.py` creados a mano (no los genera `startapp`)
- `config/settings.py` reemplazado: 7 apps en INSTALLED_APPS, conexión a Postgres vía `python-decouple` y `.env`, `LOGIN_URL`/`LOGIN_REDIRECT_URL` configurados para el portal de profesores, TIME_ZONE = America/Asuncion
- `config/urls.py` reemplazado: admin, `django.contrib.auth.urls` (login/logout), rutas de portal_profesor bajo `/profesores/`
- `requirements.txt`: Django, psycopg2-binary, python-decouple
- `.env` creado y completado con los datos de la base Postgres local
- PostgreSQL instalado y base de datos local ya creada


## Development Guidelines

- Sigue las buenas prácticas de Django.
- Mantén la lógica de negocio fuera de las plantillas.
- Utiliza el ORM de Django en lugar de SQL nativo, a menos que sea estrictamente necesario.
- No incluyas secretos directamente en el código (*hardcoding*).
- Utiliza variables de entorno para la configuración específica de cada entorno.
- No modifiques `.venv`.
- No incluyas `.env` en el control de versiones (*commit*).
- Explica los cambios arquitectónicos significativos antes de implementarlos.
