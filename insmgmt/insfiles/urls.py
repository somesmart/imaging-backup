from django.conf.urls import url
from django.views.generic import DetailView, ListView, UpdateView, CreateView, DeleteView, TemplateView

from . import views

urlpatterns = [
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'home/$', views.IndexView.as_view(), name='home'),
	url(r'autocomplete/$','insfiles.views.autocomplete', name='autocomplete'),
	url(r'noresults/', TemplateView.as_view(template_name = 'insfiles/base_noresults.html'), name='no-results'),
	url(r'client/(?P<pk>[0-9]+)/', views.ClientView.as_view(), name='client-view'),
	url(r'client/new/$', views.NewClient.as_view(), name='new-client'),
	url(r'client/update/(?P<pk>[0-9]+)/$', views.UpdateClient.as_view(), name='update-client'),
	url(r'pending/$', views.PendingView.as_view(), name='pending-view'),
	url(r'unsigned/$', views.UnsignedView.as_view(), name='unsigned-view'),
	url(r'unsigned/stats/$', 'insfiles.views.get_unsigned', name='unsigned-stats'),
	url(r'scan/update/(?P<pk>[0-9]+)/$', views.UpdateScan.as_view(), name='update-scan'),
	url(r'scan/directory/$', 'insfiles.views.scan_directory', name='scan-directory'),
	url(r'scan/$', views.NewScanView.as_view(), name='new-scan'),
]