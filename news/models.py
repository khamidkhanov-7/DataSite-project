from django.db import models  # type: ignore

class News(models.Model):
    title = models.CharField(max_length=255, verbose_name="Sarlavha")
    short_description = models.CharField(max_length=300, verbose_name="Qisqa tavsif")
    content = models.TextField(verbose_name="To‘liq matn")
    image = models.ImageField(upload_to='news/', blank=True, null=True, verbose_name="Rasm")
    published_date = models.DateTimeField(auto_now_add=True, verbose_name="E’lon qilingan sana")
    category = models.CharField(
        max_length=100,
        choices=[
            ('exhibition', 'Ko‘rgazma'),
            ('production', 'Yangi ishlab chiqarish'),
            ('other', 'Boshqa yangilik'),
        ],
        default='other',
        verbose_name="Kategoriya"
    )

    class Meta:
        verbose_name = "Yangilik"
        verbose_name_plural = "Yangiliklar"
        ordering = ['-published_date']

    def __str__(self):
        return self.title
