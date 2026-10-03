from django.db import models
from django.conf import settings
from departments.models import Department


class EmployeeProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    employee_id = models.CharField(
        max_length=20,
        unique=True
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_of_joining = models.DateField(null=True, blank=True)

    # --- New fields (migration required) ---
    # No existing field/combination of fields could represent these,
    # so they are genuinely new columns.
    designation = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='employee_photos/', blank=True, null=True)

    def __str__(self):
        return self.employee_id

    # --- Bridging properties (NOT database fields, no migration needed) ---
    # These exist purely so the existing Lovable templates, which reference
    # employee.name / employee.email / employee.joining_date / employee.status /
    # employee.is_active, keep working without renaming or duplicating real
    # columns on User/EmployeeProfile.

    @property
    def name(self):
        """Frontend expects employee.name; we derive it from the User."""
        full_name = self.user.get_full_name()
        return full_name if full_name else self.user.username

    @property
    def email(self):
        """Frontend expects employee.email; email actually lives on User."""
        return self.user.email

    @property
    def joining_date(self):
        """Frontend expects employee.joining_date; DB column is date_of_joining."""
        return self.date_of_joining

    @property
    def is_active(self):
        """Frontend expects employee.is_active; this reflects the User account state."""
        return self.user.is_active

    @property
    def status(self):
        """Frontend expects employee.status as a display string."""
        return "Active" if self.user.is_active else "Inactive"
