from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import StudentProfile, Order, OrderItem, BreakTimeSlot, FoodItem


class StudentRegistrationForm(UserCreationForm):
    """Registration form for students"""
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    registration_number = forms.CharField(max_length=20, required=True,
        help_text="Your LPU Registration Number (e.g. 12306789)")
    phone = forms.CharField(max_length=15, required=True)
    department = forms.CharField(max_length=100, required=True)
    semester = forms.IntegerField(min_value=1, max_value=10, initial=1)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email',
                  'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                registration_number=self.cleaned_data['registration_number'],
                phone=self.cleaned_data['phone'],
                department=self.cleaned_data['department'],
                semester=self.cleaned_data['semester'],
            )
        return user


class OrderForm(forms.ModelForm):
    """Form for placing a food order"""
    time_slot = forms.ModelChoiceField(
        queryset=BreakTimeSlot.objects.all(),
        empty_label="-- Select Break Time --",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    special_instructions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Any special requests or allergies?',
            'class': 'form-control'
        })
    )

    class Meta:
        model = Order
        fields = ['time_slot', 'special_instructions']


class CartItemForm(forms.Form):
    """Form to add an item to cart"""
    food_item_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(
        min_value=1, max_value=10, initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'width:80px'})
    )
