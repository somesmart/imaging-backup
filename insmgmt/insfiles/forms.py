from django import forms
from .models import Scan, Client, ExtensionField, ExtensionType
from django.forms import ModelForm
from django.forms.models import inlineformset_factory

class NewClientForm(forms.ModelForm):
	class Meta:
		model = Client
		fields = ['first_name', 'last_name']

class ScanFormAjax(forms.ModelForm):
	class Meta:
		model = Scan
		fields = ['document', 'document_type', 'signature_required', 'signed']

class ExtensionFieldForm(ModelForm):
	class Meta:
		model = ExtensionField
		fields = '__all__'

TypeFormAjax = inlineformset_factory(ExtensionType, ExtensionField, form=ExtensionFieldForm, fields='__all__')