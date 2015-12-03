from django import forms
from .models import Scan, Client

class NewScanForm(forms.ModelForm):

	class Meta:
		model = Scan
		fields = ['client', 'document', 'document_type', 'signature_required', 'signed']

class NewClientForm(forms.ModelForm):

	class Meta:
		model = Client
		fields = ['first_name', 'last_name']