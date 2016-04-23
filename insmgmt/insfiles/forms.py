from django import forms
from .models import Scan, Client

class NewClientForm(forms.ModelForm):

	class Meta:
		model = Client
		fields = ['first_name', 'last_name']

class ScanFormAjax(forms.ModelForm):

	class Meta:
		model = Scan
		fields = ['document', 'document_type', 'signature_required', 'signed']