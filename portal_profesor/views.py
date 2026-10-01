from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from alumnos.models import Alumno
from asistencia.models import Asistencia
from cursos.models import Curso, Sesion
from examenes.models import Examen, Resultado

from .decorators import profesor_required


@profesor_required
def mis_cursos(request):
    """Punto de entrada del portal: lista solo los cursos de este profesor."""
    cursos = Curso.objects.filter(profesor=request.user.profesor, activo=True)
    return render(request, "portal_profesor/mis_cursos.html", {"cursos": cursos})


def _get_curso_del_profesor(request, curso_id):
    """Nunca confiar en el curso_id de la URL sin validar que sea del profesor logueado."""
    return Curso.objects.filter(id=curso_id, profesor=request.user.profesor).first()


@profesor_required
def tomar_asistencia(request, curso_id):
    curso = _get_curso_del_profesor(request, curso_id)
    if curso is None:
        return HttpResponseForbidden("No tenés acceso a este curso.")

    fecha = timezone.localdate()
    sesion, _ = Sesion.objects.get_or_create(curso=curso, fecha=fecha)
    alumnos = curso.alumnos.filter(activo=True)

    if request.method == "POST":
        for alumno in alumnos:
            estado = request.POST.get(f"estado_{alumno.id}", Asistencia.Estado.AUSENTE)
            Asistencia.objects.update_or_create(
                sesion=sesion, alumno=alumno, defaults={"estado": estado}
            )
        return redirect("portal_profesor:mis_cursos")

    asistencias_actuales = {a.alumno_id: a.estado for a in sesion.asistencias.all()}
    return render(
        request,
        "portal_profesor/tomar_asistencia.html",
        {"curso": curso, "sesion": sesion, "alumnos": alumnos, "asistencias": asistencias_actuales},
    )


@profesor_required
def cargar_notas(request, curso_id, examen_id):
    curso = _get_curso_del_profesor(request, curso_id)
    if curso is None:
        return HttpResponseForbidden("No tenés acceso a este curso.")

    # get_object_or_404 con curso=curso asegura que el examen sea de un curso propio.
    examen = get_object_or_404(Examen, id=examen_id, curso=curso)
    alumnos = curso.alumnos.filter(activo=True)

    if request.method == "POST":
        for alumno in alumnos:
            Resultado.objects.update_or_create(
                examen=examen,
                alumno=alumno,
                defaults={
                    "puntaje_reading": request.POST.get(f"reading_{alumno.id}") or None,
                    "puntaje_writing": request.POST.get(f"writing_{alumno.id}") or None,
                    "puntaje_listening": request.POST.get(f"listening_{alumno.id}") or None,
                    "puntaje_oral": request.POST.get(f"oral_{alumno.id}") or None,
                    "observaciones": request.POST.get(f"obs_{alumno.id}", ""),
                },
            )
        return redirect("portal_profesor:mis_cursos")

    resultados_actuales = {r.alumno_id: r for r in examen.resultados.all()}
    return render(
        request,
        "portal_profesor/cargar_notas.html",
        {"curso": curso, "examen": examen, "alumnos": alumnos, "resultados": resultados_actuales},
    )


@profesor_required
def editar_ficha(request, alumno_id):
    # curso__profesor=... filtra a nivel de consulta: si el alumno no es de este
    # profesor, tira 404 en vez de dejarlo editar.
    alumno = get_object_or_404(Alumno, id=alumno_id, curso__profesor=request.user.profesor)

    if request.method == "POST":
        alumno.ficha_personal = request.POST.get("ficha_personal", "")
        alumno.save(update_fields=["ficha_personal"])
        return redirect("portal_profesor:mis_cursos")

    return render(request, "portal_profesor/editar_ficha.html", {"alumno": alumno})
