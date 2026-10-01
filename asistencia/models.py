from django.db import models


class Asistencia(models.Model):
    class Estado(models.TextChoices):
        PRESENTE = "presente", "Presente"
        AUSENTE = "ausente", "Ausente"
        TARDANZA = "tardanza", "Tardanza"

    sesion = models.ForeignKey(
        "cursos.Sesion", on_delete=models.CASCADE, related_name="asistencias"
    )
    alumno = models.ForeignKey(
        "alumnos.Alumno", on_delete=models.CASCADE, related_name="asistencias"
    )
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.PRESENTE)

    class Meta:
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"
        unique_together = ("sesion", "alumno")

    def __str__(self):
        return f"{self.alumno} - {self.sesion} - {self.get_estado_display()}"
