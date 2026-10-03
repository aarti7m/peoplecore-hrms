import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import django
from datetime import date, timedelta
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from accounts.models import User
from departments.models import Department
from employees.models import EmployeeProfile
from attendance.models import Attendance
from leaves.models import LeaveRequest
from announcements.models import Announcement
from salary.models import Salary


print("Starting PeopleCore demo data...")

# -------------------------
# Departments
# -------------------------
department_names = [
    ("Engineering", "Software development and technology"),
    ("Human Resources", "People and employee management"),
    ("Finance", "Finance and accounting operations"),
    ("Marketing", "Marketing and business promotion"),
]

departments = {}

for name, description in department_names:
    department, _ = Department.objects.get_or_create(
        name=name,
        defaults={"description": description}
    )
    departments[name] = department

print("Departments ready.")

# -------------------------
# Demo employees
# -------------------------
employees = [
    ("EMP001", "Aarav", "Patil", "Python Developer", "Engineering"),
    ("EMP002", "Ananya", "Sharma", "Software Developer", "Engineering"),
    ("EMP003", "Rohan", "Kulkarni", "QA Engineer", "Engineering"),
    ("EMP004", "Sneha", "Joshi", "Data Analyst", "Engineering"),
    ("EMP005", "Aditya", "Deshmukh", "Backend Developer", "Engineering"),
    ("EMP006", "Priya", "More", "HR Executive", "Human Resources"),
    ("EMP007", "Neha", "Jadhav", "HR Coordinator", "Human Resources"),
    ("EMP008", "Kunal", "Shinde", "Recruiter", "Human Resources"),
    ("EMP009", "Vivek", "Pawar", "Accountant", "Finance"),
    ("EMP010", "Isha", "Mane", "Finance Executive", "Finance"),
    ("EMP011", "Rahul", "Kadam", "Financial Analyst", "Finance"),
    ("EMP012", "Sakshi", "Chavan", "Marketing Executive", "Marketing"),
    ("EMP013", "Om", "Gaikwad", "Marketing Associate", "Marketing"),
    ("EMP014", "Tanvi", "Bhosale", "Content Specialist", "Marketing"),
    ("EMP015", "Yash", "Wagh", "UI Developer", "Engineering"),
]

created_users = []

for employee_id, first_name, last_name, designation, department_name in employees:
    username = employee_id.lower()

    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "first_name": first_name,
            "last_name": last_name,
            "email": f"{username}@peoplecore.demo",
            "role": "EMPLOYEE",
            "is_active": True,
        }
    )

    if created:
        user.set_password("Demo@12345")
        user.save()
        created_users.append(user)

    profile = EmployeeProfile.objects.filter(user=user).first()

    if profile is None:
        profile = EmployeeProfile.objects.filter(employee_id=employee_id).first()

    if profile is None:
        profile = EmployeeProfile.objects.create(
            user=user,
            employee_id=employee_id,
            department=departments[department_name],
            phone="9000000000",
            address="Pune, Maharashtra",
            date_of_joining=date(2025, 6, 1),
            designation=designation,
        )
    else:
        profile.department = departments[department_name]
        profile.designation = designation
        profile.save()

print(f"Employees ready: {len(employees)}")

# -------------------------
# Attendance
# -------------------------
demo_users = list(
    User.objects.filter(username__startswith="emp")
    .filter(role="EMPLOYEE")
    .order_by("username")
)[:15]

attendance_created = 0

for user in demo_users:
    for days_ago in range(1, 11):
        attendance_date = date.today() - timedelta(days=days_ago)

        if attendance_date.weekday() >= 5:
            continue

        status = "ABSENT" if days_ago % 7 == 0 else "PRESENT"

        _, created = Attendance.objects.get_or_create(
            employee=user,
            date=attendance_date,
            defaults={
                "status": status,
            }
        )

        if created:
            attendance_created += 1

print(f"Attendance records added: {attendance_created}")

# -------------------------
# Leave requests
# -------------------------
leave_data = [
    ("CASUAL", 1, 2, "Personal work", "APPROVED"),
    ("SICK", 3, 4, "Not feeling well", "APPROVED"),
    ("CASUAL", 5, 5, "Family function", "PENDING"),
    ("OTHER", 7, 8, "Personal reason", "REJECTED"),
    ("SICK", 9, 10, "Medical appointment", "APPROVED"),
    ("CASUAL", 11, 12, "Personal work", "PENDING"),
    ("OTHER", 13, 13, "Important appointment", "APPROVED"),
    ("SICK", 15, 16, "Fever and rest", "PENDING"),
    ("CASUAL", 18, 18, "Family event", "APPROVED"),
    ("OTHER", 20, 21, "Personal work", "REJECTED"),
]

leaves_created = 0

for index, data in enumerate(leave_data):
    if index >= len(demo_users):
        break

    leave_type, start_days, end_days, reason, status = data
    user = demo_users[index]

    start_date = date.today() + timedelta(days=start_days)
    end_date = date.today() + timedelta(days=end_days)

    _, created = LeaveRequest.objects.get_or_create(
        employee=user,
        start_date=start_date,
        end_date=end_date,
        defaults={
            "leave_type": leave_type,
            "reason": reason,
            "status": status,
        }
    )

    if created:
        leaves_created += 1

print(f"Leave requests added: {leaves_created}")

# -------------------------
# Salary records
# -------------------------
salary_amounts = [
    35000, 38000, 42000, 40000, 45000,
    32000, 34000, 36000, 39000, 41000,
    43000, 33000, 35000, 37000, 40000,
]

salary_created = 0

for index, user in enumerate(demo_users):
    basic = Decimal(str(salary_amounts[index % len(salary_amounts)]))

    _, created = Salary.objects.get_or_create(
        employee=user,
        month=date(2026, 10, 1),
        defaults={
            "basic_salary": basic,
            "allowances": Decimal("5000"),
            "deductions": Decimal("1000"),
            "status": "PAID" if index % 3 != 0 else "PENDING",
            "payment_date": date(2026, 10, 3) if index % 3 != 0 else None,
        }
    )

    if created:
        salary_created += 1

print(f"Salary records added: {salary_created}")

# -------------------------
# Announcements
# -------------------------
admin = User.objects.filter(role="ADMIN").first()

announcements = [
    ("Welcome to PeopleCore", "Welcome to the PeopleCore employee workspace."),
    ("Team Meeting", "Monthly team meeting will be held on Friday at 10 AM."),
    ("Attendance Reminder", "Please make sure your attendance is updated regularly."),
    ("Salary Update", "October salary processing has been completed for eligible employees."),
    ("Office Holiday", "The office will remain closed on the upcoming public holiday."),
]

announcement_created = 0

if admin:
    for title, message in announcements:
        _, created = Announcement.objects.get_or_create(
            title=title,
            defaults={
                "message": message,
                "created_by": admin,
            }
        )

        if created:
            announcement_created += 1

print(f"Announcements added: {announcement_created}")

print()
print("====================================")
print("PeopleCore demo data completed!")
print("====================================")
print(f"Demo employees : {User.objects.filter(role='EMPLOYEE').count()}")
print(f"Departments    : {Department.objects.count()}")
print(f"Attendance     : {Attendance.objects.count()}")
print(f"Leaves         : {LeaveRequest.objects.count()}")
print(f"Salaries       : {Salary.objects.count()}")
print(f"Announcements  : {Announcement.objects.count()}")
print()
print("Demo employee password: Demo@12345")
print("Demo usernames: emp001 ... emp015")
print("====================================")
