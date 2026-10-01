from django.db import models


class Evento(models.Model):
    """Feriados y vacaciones. Los cumpleaños de alumnos y las fechas de examen NO se
    duplican acá: se calculan a partir de Alumno.fecha_nacimiento y Examen.fecha."""

    class Tipo(models.TextChoices):
        FERIADO = "feriado", "Feriado"
        VACACIONES = "vacaciones", "Vacaciones"
        OTRO = "otro", "Otro"

    nombre = models.CharField(max_length=150)
    tipo = models.CharField(max_length=15, choices=Tipo.choices, default=Tipo.FERIADO)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(help_text="Igual a fecha_inicio si es un solo día")

    class Meta:
        verbose_name = "Evento de calendario"
        verbose_name_plural = "Eventos de calendario"
        ordering = ["fecha_inicio"]

    def __str__(self):
        return f"{self.nombre} ({self.fecha_inicio})"
