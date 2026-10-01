from django.db import models


class Cuota(models.Model):
    """Lo que un alumno debe/pagó: mensualidad o matrícula. Independiente de la Factura SIFEN."""

    class Tipo(models.TextChoices):
        MATRICULA = "matricula", "Matrícula"
        MENSUALIDAD = "mensualidad", "Mensualidad"

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        PAGADA = "pagada", "Pagada"
        VENCIDA = "vencida", "Vencida"

    alumno = models.ForeignKey("alumnos.Alumno", on_delete=models.CASCADE, related_name="cuotas")
    curso = models.ForeignKey("cursos.Curso", on_delete=models.CASCADE, related_name="cuotas")
    tipo = models.CharField(max_length=15, choices=Tipo.choices, default=Tipo.MENSUALIDAD)
    anio_lectivo = models.PositiveSmallIntegerField(help_text="Año lectivo, ej: 2026")
    mes = models.CharField(
        max_length=7,
        blank=True,
        help_text="Formato AAAA-MM. Vacío para matrícula (es un cobro único por año).",
    )
    monto = models.DecimalField(max_digits=10, decimal_places=0)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.PENDIENTE)
    fecha_pago = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Cuota"
        verbose_name_plural = "Cuotas"
        constraints = [
            models.UniqueConstraint(
                fields=["alumno", "anio_lectivo", "mes", "tipo"], name="unica_cuota_por_periodo"
            )
        ]
        ordering = ["-anio_lectivo", "-mes"]

    def __str__(self):
        periodo = self.mes or f"Matrícula {self.anio_lectivo}"
        return f"{self.alumno} - {periodo} ({self.get_estado_display()})"


class Factura(models.Model):
    """Documento fiscal (SIFEN) generado a partir de una cuota ya pagada."""

    cuota = models.OneToOneField(Cuota, on_delete=models.PROTECT, related_name="factura")
    fecha = models.DateTimeField(auto_now_add=True)
    razon_social = models.CharField(max_length=150)
    ruc_ci = models.CharField(max_length=20, verbose_name="RUC/CI")
    descripcion = models.CharField(max_length=255, blank=True)
    monto = models.DecimalField(max_digits=10, decimal_places=0)
    cdc = models.CharField(max_length=44, unique=True, blank=True, verbose_name="CDC (SIFEN)")
    estado_sifen = models.CharField(
        max_length=20, blank=True, help_text="Aprobado / Rechazado / Pendiente"
    )

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Factura #{self.id} - {self.razon_social}"
