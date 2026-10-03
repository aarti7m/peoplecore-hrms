from django.db import models
from django.conf import settings


class Salary(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
    )

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'EMPLOYEE'},
        related_name='salary_records'
    )
    month = models.DateField()
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    allowances = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    deductions = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    payment_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-month']
        unique_together = ('employee', 'month')

    @property
    def net_salary(self):
        return (
            self.basic_salary
            + self.allowances
            - self.deductions
        )

    def __str__(self):
        return f"{self.employee.username} - {self.month:%B %Y}"
