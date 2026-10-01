from django.urls import path

from . import views

app_name = "portal_profesor"

urlpatterns = [
    path("", views.mis_cursos, name="mis_cursos"),
    path("cursos/<int:curso_id>/asistencia/", views.tomar_asistencia, name="tomar_asistencia"),
    path(
        "cursos/<int:curso_id>/examenes/<int:examen_id>/notas/",
        views.cargar_notas,
        name="cargar_notas",
    ),
    path("alumnos/<int:alumno_id>/ficha/", views.editar_ficha, name="editar_ficha"),
]
