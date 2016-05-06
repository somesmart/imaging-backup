from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views import generic
from django.db.models import Count, Q
from django.core import serializers
from django.conf import settings
from django.template.defaultfilters import slugify
import json
from .models import *
from .forms import *
from datetime import datetime
import os

def thanks(request):
	return HttpResponse("<p>Scan information has been updated.</p>")

# ****************************************************************** #
# ********************* autocomplete views ************************* #
# ****************************************************************** #

def autocomplete(request):
	if request.method == "GET":
		if request.GET.has_key(u'term'):
			value = request.GET[u'term']
			search = request.GET[u'search']
			results = []
			if search == "name":
				# Ignore queries shorter than length 3
				if len(value) > 3:
					model_results = Client.objects.filter(Q(last_name__icontains=value) | Q(first_name__icontains=value))
					for client in model_results:
						data = {'id': str(client.id), 'label': client.first_name + ' ' + client.last_name }
						results.append(data)
					json_results = json.dumps(results)
					return HttpResponse(json_results, content_type='application/json')
				else:
					return HttpResponseRedirect(reverse('no-results'))
		else:
			return HttpResponseRedirect(reverse('no-results'))

class IndexView(generic.ListView):
	template_name = 'insfiles/base_index.html'
	context_object_name = 'latest_scans'

	def get_queryset(self):
		"""Return the last five published questions."""
		return Scan.objects.select_related().order_by('-scan_date')[:10]

	def get_context_data(self, **kwargs):
		context = super(IndexView, self).get_context_data(**kwargs)
		context['scan_count'] = Scan.objects.aggregate(scans=Count('id'))
		return context

class ClientView(generic.DetailView):
	model = Client
	template_name = 'insfiles/base_client.html'

	def get_context_data(self, **kwargs):
		context = super(ClientView, self).get_context_data(**kwargs)
		context['client_scans'] = Scan.objects.select_related().filter(client__id=self.kwargs['pk'])
		return context

class NewClient(generic.CreateView):
	form_class = NewClientForm
	template_name = 'insfiles/client_form.html'
	success_url = reverse_lazy('index')

class UpdateClient(generic.UpdateView):
	model = Client
	form_class = NewClientForm
	template_name = 'insfiles/client_form.html'
	success_url = reverse_lazy('index')

class UnsignedView(generic.ListView):
	template_name = 'insfiles/base_required.html'
	context_object_name = 'required_list'

	def get_queryset(self):
		return Scan.objects.select_related().filter(signed=0, signature_required=1)

class NewScanView(generic.CreateView):
	form_class = ScanFormAjax
	template_name = 'insfiles/scan_form_ajax.html'
	
	def form_valid (self, form):
		if form.is_valid():
			client_id = self.request.POST[u'client']
			self.client = Client.objects.get(id=client_id)
			obj = form.save(commit=False) 
			obj.client = self.client
			obj.save()
			extended_values = ExtensionType.objects.filter(required=True)
			if extended_values:
				for extended_value in extended_values:
					ExtensionField(extensiontype=extended_value, scan=obj, char_value=None, date_value=None, bool_value=False).save()
			return HttpResponseRedirect(reverse('thanks'))

class UpdateScanAjax(generic.UpdateView):
	model = Scan
	form_class = ScanFormAjax
	template_name = 'insfiles/scan_form_ajax.html'

	def form_valid(self, form):
		if form.is_valid():
			obj = form.save(commit=False) 
			client_id = self.request.POST[u'client']
			self.client = Client.objects.get(id=client_id)
			# save extension field values
			extension_fields = ExtensionField.objects.select_related().filter(scan__id=obj.id)
			for field in extension_fields:
				field_type = field.extensiontype.get_data_type_display()
				field_name = slugify(field.extensiontype.description)
				if field_type == 'bool_value':
					field.bool_value = self.request.POST[field_name]
				elif field_type == 'char_value':
					field.char_value = self.request.POST[field_name]
				elif field_type == 'date_value':
					field.date_value = self.request.POST[field_name]
				field.save()
			obj.client = self.client
			obj.save()
			return HttpResponseRedirect(reverse('thanks'))

def scan_directory(request):
	new_location = os.path.normpath(settings.MEDIA_ROOT + settings.PENDING_CLIENT)
	scan_count = 0
	for directory in settings.SCAN_DIRS:
		dir_norm = os.path.normpath(directory)
		dirlist = os.listdir(dir_norm)
		
		if dirlist:
			client = Client.objects.get(id=1)
			for item in dirlist:
				or_doc = dir_norm + '/' + item
				doc = new_location + '/' + item
				os.rename (or_doc, doc)
				scan_count = scan_count + 1
				scan = Scan(client=client, document=settings.PENDING_CLIENT + '/' + item, document_type=4, scan_date=datetime.now(), signature_required=0, signed=0, signed_date=None)
				scan.save()
				extended_values = ExtensionType.objects.filter(required=True)
				if extended_values:
					for extended_value in extended_values:
						ExtensionField(extensiontype=extended_value, scan=scan, char_value=None, date_value=None, bool_value=False).save()
			return HttpResponse("1")
	if scan_count == 0:
		return HttpResponse("2")

class PendingView(generic.ListView):
	template_name = 'insfiles/base_required.html'
	context_object_name = 'required_list'

	def get_queryset(self):
		return Scan.objects.select_related().filter(client__id=1)

class NewTypeView(generic.CreateView):
	form_class = TypeFormAjax
	template_name = 'insfiles/type_form_ajax.html'

class ExtensionTypeView(generic.ListView):
	template_name = 'insfiles/base_required.html'
	context_object_name = 'required_list'

	#If we add a new extension type do we want to create a blank entry for all scans already in the system, or just leave it as a going forward concern?
	def get_queryset(self):
		extension_type = ExtensionType.objects.get(id=self.kwargs['pk'])
		if extension_type.get_data_type_display() == 'bool_value':
			extension_fields = ExtensionField.objects.select_related().filter(extensiontype=extension_type, bool_value=True).values('scan__id')
		else:
			extension_fields = ExtensionField.objects.select_related().exclude(extensiontype=extension_type).filter(**{ extension_type.get_data_type_display(): None}).values('scan__id')
		scans = Scan.objects.select_related().exclude(pk__in=extension_fields)
		return scans