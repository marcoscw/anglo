from django.db import models


class Examen(models.Model):
    """Uno de los 4 exámenes del año lectivo para un curso."""

    curso = models.ForeignKey("cursos.Curso", on_delete=models.CASCADE, related_name="examenes")
    nombre = models.CharField(max_length=100, blank=True, help_text="Ej: Examen 1, Examen 2...")
    fecha = models.DateField()

    class Meta:
        verbose_name = "Examen"
        verbose_name_plural = "Exámenes"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.curso} - {self.nombre or self.fecha}"


class Resultado(models.Model):
    """Puntajes de un alumno en un examen: cada examen tiene 4 partes."""

    examen = models.ForeignKey(Examen, on_delete=models.CASCADE, related_name="resultados")
    alumno = models.ForeignKey(
        "alumnos.Alumno", on_delete=models.CASCADE, related_name="resultados"
    )
    puntaje_reading = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    puntaje_writing = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    puntaje_listening = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    puntaje_oral = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    observaciones = models.TextField(
        blank=True, help_text="Comentario sobre el rendimiento del alumno en este examen"
    )

    class Meta:
        verbose_name = "Resultado"
        verbose_name_plural = "Resultados"
        unique_together = ("examen", "alumno")

    @property
    def puntaje_total(self):
        partes = [self.puntaje_reading, self.puntaje_writing, self.puntaje_listening, self.puntaje_oral]
        valores = [p for p in partes if p is not None]
        return sum(valores) if valores else None

    def __str__(self):
        return f"{self.alumno} - {self.examen}"
