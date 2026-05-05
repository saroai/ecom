from django import forms
from .models import ShippingAddress


class ShippingAddressForm(forms.ModelForm):
    """Checkout shipping address form with Bootstrap 5 styling."""

    class Meta:
        model  = ShippingAddress
        fields = [
            "first_name", "last_name", "email", "phone_no",
            "address", "city", "state", "pin_code", "country"
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First Name",  "class": "form-control"}),
            "last_name":  forms.TextInput(attrs={"placeholder": "Last Name",   "class": "form-control"}),
            "email":      forms.EmailInput(attrs={"placeholder": "Email",       "class": "form-control"}),
            "phone_no":   forms.TextInput(attrs={"placeholder": "Phone Number","class": "form-control"}),
            "address":    forms.TextInput(attrs={"placeholder": "Street Address","class":"form-control"}),
            "city":       forms.TextInput(attrs={"placeholder": "City",         "class": "form-control"}),
            "state":      forms.TextInput(attrs={"placeholder": "State",        "class": "form-control"}),
            "pin_code":   forms.TextInput(attrs={"placeholder": "PIN Code",     "class": "form-control"}),
            "country":    forms.TextInput(attrs={"placeholder": "Country",      "class": "form-control"}),
        }
