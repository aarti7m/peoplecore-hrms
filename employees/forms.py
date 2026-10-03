

from django import forms
from django.contrib.auth import get_user_model
from .models import EmployeeProfile

User = get_user_model()


class EmployeeForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150, required=False, widget=forms.HiddenInput())
    last_name = forms.CharField(max_length=150, required=False, widget=forms.HiddenInput())

    full_name = forms.CharField(max_length=300)

    email = forms.EmailField()

    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        help_text="Enter a password when creating an employee."
    )

    joining_date = forms.DateField(
        input_formats=['%Y-%m-%d'],
        required=False
    )

    is_active = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = EmployeeProfile
        fields = [
            'employee_id',
            'department',
            'phone',
            'address',
            'designation',
            'photo',
        ]

    def __init__(self, *args, editing=False, **kwargs):
        self.editing = editing
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.user_id:
            user = self.instance.user

            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email
            self.fields['full_name'].initial = user.get_full_name()
            self.fields['is_active'].initial = user.is_active
            self.fields['joining_date'].initial = self.instance.date_of_joining

        self.fields['password'].required = not editing

    def clean_username(self):
        username = self.cleaned_data['username']

        qs = User.objects.filter(username=username)

        if self.instance and self.instance.pk and self.instance.user_id:
            qs = qs.exclude(pk=self.instance.user_id)

        if qs.exists():
            raise forms.ValidationError(
                "This username is already taken."
            )

        return username

    def clean_email(self):
        email = self.cleaned_data['email']

        qs = User.objects.filter(email=email)

        if self.instance and self.instance.pk and self.instance.user_id:
            qs = qs.exclude(pk=self.instance.user_id)

        if qs.exists():
            raise forms.ValidationError(
                "This email is already registered."
            )

        return email

    def clean_employee_id(self):
        employee_id = self.cleaned_data['employee_id']

        qs = EmployeeProfile.objects.filter(
            employee_id=employee_id
        )

        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError(
                "This employee ID is already in use."
            )

        return employee_id

    def clean(self):
        cleaned_data = super().clean()

        full_name = cleaned_data.get('full_name', '').strip()

        if not full_name:
            self.add_error('full_name', 'Full name is required.')

        joining_date = cleaned_data.get('joining_date')

        if joining_date:
            cleaned_data['date_of_joining'] = joining_date

        return cleaned_data

    def save(self, commit=True):
        profile = super().save(commit=False)

        full_name = self.cleaned_data.get('full_name', '').strip()
        name_parts = full_name.split(maxsplit=1)

        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        if profile.pk and profile.user_id:
            user = profile.user
        else:
            user = User(role='EMPLOYEE')

        user.username = self.cleaned_data['username']
        user.first_name = first_name
        user.last_name = last_name
        user.email = self.cleaned_data['email']
        user.is_active = self.cleaned_data.get('is_active', True)

        password = self.cleaned_data.get('password')

        if password:
            user.set_password(password)

        if commit:
            user.save()

            profile.user = user

            joining_date = self.cleaned_data.get('joining_date')
            if joining_date:
                profile.date_of_joining = joining_date

            profile.save()

        else:
            profile.user = user

        return profile


class EmployeeSelfEditForm(forms.ModelForm):
    full_name = forms.CharField(max_length=300)

    email = forms.EmailField()

    class Meta:
        model = EmployeeProfile
        fields = [
            'phone',
            'address',
            'designation',
            'photo',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.user_id:
            user = self.instance.user
            self.fields['full_name'].initial = user.get_full_name()
            self.fields['email'].initial = user.email

    def clean(self):
        cleaned_data = super().clean()

        full_name = cleaned_data.get('full_name', '').strip()

        if not full_name:
            self.add_error('full_name', 'Full name is required.')

        return cleaned_data

    def save(self, commit=True):
        profile = super().save(commit=False)

        full_name = self.cleaned_data['full_name'].strip()
        name_parts = full_name.split(maxsplit=1)

        user = profile.user
        user.first_name = name_parts[0] if name_parts else ''
        user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            profile.save()

        return profile
