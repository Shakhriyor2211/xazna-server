from django.core.validators import MinValueValidator
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CreditRateBaseModel(BaseModel):
    limit = models.PositiveBigIntegerField(default=0)
    usage = models.DecimalField(max_digits=16, decimal_places=4, validators=[MinValueValidator(0)], default=0)
    time = models.PositiveIntegerField(default=0)
    reset = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
