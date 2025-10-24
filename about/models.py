from django.db import models

class AboutCompany(models.Model):
    title = models.CharField(max_length=200, verbose_name="Sarlavha")
    description = models.TextField(verbose_name="Tavsif")
    history = models.TextField(verbose_name="Tarix", blank=True, null=True)
    technology = models.TextField(verbose_name="Texnologiyalar", blank=True, null=True)
    projects = models.TextField(verbose_name="Joriy loyihalar", blank=True, null=True)
    investors = models.TextField(verbose_name="Investorlar uchun ma’lumot", blank=True, null=True)
    image = models.ImageField(upload_to='about/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kompaniya haqida"
        verbose_name_plural = "Kompaniya haqida"

    def __str__(self):
        return self.title
