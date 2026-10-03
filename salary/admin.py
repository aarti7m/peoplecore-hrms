from django.contrib import admin
from .models import Salary


@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = (
        'employee',
        'month',
        'basic_salary',
        'allowances',
        'deductions',
        'status',
        'payment_date',
    )
    list_filter = ('status', 'month')
    search_fields = (
        'employee__username',
        'employee__first_name',
        'employee__last_name',
    )
