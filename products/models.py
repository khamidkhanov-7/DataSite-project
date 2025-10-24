from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Mahsulot nomi")
    description = models.TextField(verbose_name="Tavsif")
    technical_specs = models.TextField(verbose_name="Texnik xarakteristikalar", blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Narx (so‘mda)")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Rasm")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo‘shilgan sana")

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ['-created_at']

    def __str__(self):
        return self.name
