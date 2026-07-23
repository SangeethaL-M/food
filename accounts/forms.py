from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    # Changed default='customer' to initial='customer'
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, initial='customer')
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                role=self.cleaned_data.get('role', 'customer'),
                phone=self.cleaned_data.get('phone', ''),
                address=self.cleaned_data.get('address', '')
            )
        return user