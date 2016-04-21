from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views import generic
from django.db.models import Count, Q
from django.core import serializers
import json
from .models import *
from .forms import *

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
						data = {'id': '/client/' + str(client.id) + '/', 'label': client.first_name + ' ' + client.last_name }
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

def get_unsigned(request):
	return JsonResponse(Scan.objects.filter(signature_required=1, signed=0).aggregate(sig_required=Count('id')))

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
	template_name = 'insfiles/base_unsigned.html'
	context_object_name = 'unsigned_scans'

	def get_queryset(self):
		return Scan.objects.select_related().filter(signed=0, signature_required=1)

class NewScanView(generic.CreateView):
	form_class = NewScanForm
	template_name = 'insfiles/scan_form.html'
	success_url = reverse_lazy('index')

class UpdateScan(generic.UpdateView):
	model = Scan
	form_class = NewScanForm
	template_name = 'insfiles/scan_form.html'
	success_url = reverse_lazy('index')