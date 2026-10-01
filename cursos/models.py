from django.conf import settings
from django.db import models


class Profesor(models.Model):
    nombre = models.CharField(max_length=150)
    ci = models.CharField(max_length=20, blank=True, verbose_name="CI")
    telefono = models.CharField(max_length=30, blank=True)
    tarifa_alumno = models.DecimalField(
        max_digits=10, decimal_places=0, help_text="Monto que se le paga por alumno pagante"
    )
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profesor",
        help_text="Cuenta de Django con la que este profesor inicia sesión",
    )

    class Meta:
        verbose_name = "Profesor"
        verbose_name_plural = "Profesores"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    profesor = models.ForeignKey(
        Profesor, on_delete=models.SET_NULL, null=True, related_name="cursos"
    )
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Horario(models.Model):
    """Uno o más bloques semanales por curso (día + hora + aula).
    Permite que un curso se reúna varias veces por semana en horarios distintos."""

    class Aula(models.TextChoices):
        ROOM_1 = "room_1", "Room 1"
        ROOM_2 = "room_2", "Room 2"
        ROOM_3 = "room_3", "Room 3"

    class DiaSemana(models.IntegerChoices):
        LUNES = 1, "Lunes"
        MARTES = 2, "Martes"
        MIERCOLES = 3, "Miércoles"
        JUEVES = 4, "Jueves"
        VIERNES = 5, "Viernes"
        SABADO = 6, "Sábado"

    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="horarios")
    dia_semana = models.PositiveSmallIntegerField(choices=DiaSemana.choices)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    aula = models.CharField(max_length=10, choices=Aula.choices)

    class Meta:
        verbose_name = "Bloque de horario"
        verbose_name_plural = "Horarios"
        ordering = ["dia_semana", "hora_inicio"]

    def __str__(self):
        return (
            f"{self.curso} - {self.get_dia_semana_display()} "
            f"{self.hora_inicio}-{self.hora_fin} ({self.get_aula_display()})"
        )


class Sesion(models.Model):
    """Una fila por cada clase que efectivamente ocurre (para poder colgar asistencia)."""

    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="sesiones")
    fecha = models.DateField()

    class Meta:
        verbose_name = "Sesión"
        verbose_name_plural = "Sesiones"
        unique_together = ("curso", "fecha")
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.curso} - {self.fecha}"
