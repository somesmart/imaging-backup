from django import template
from insfiles.models import *
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()

@register.inclusion_tag('insfiles/required.html')
def get_required_stats():
	results = []
	signature_required = Scan.objects.filter(signature_required=1, signed=0).aggregate(sig_required=Count('id'))
	pending_review = Scan.objects.filter(client__id=1).aggregate(pending_review=Count('id'))
	if signature_required:
		data = {'type': 'Signature Required', 'count': signature_required['sig_required'], 'url': 'unsigned-view', 'url_arg': None}
		results.append(data)
	if pending_review:
		data = {'type': 'Pending Review', 'count': pending_review['pending_review'], 'url': 'pending-view', 'url_arg': None}
		results.append(data)
	extended_values = ExtensionType.objects.filter(required=True)
	if extended_values:
		scans = Scan.objects.aggregate(scans=Count('id'))
		total_extended = scans['scans']
		for extended_value in extended_values:
			if extended_value.get_data_type_display() == 'bool_value':
				extended_count = ExtensionField.objects.select_related().filter(extensiontype=extended_value, bool_value=True).aggregate(ext_count=Count('scan__id'))
				total_extended = total_extended - extended_count['ext_count']
			else:
				extended_count = ExtensionField.objects.select_related().filter(extensiontype=extended_value).exclude(**{ extended_value.get_data_type_display(): None})	
				total_extended = total_extended - extended_count['ext_count']
			try:
				data = {'type': extended_value.description, 'count': total_extended, 'url': 'type-view', 'url_arg': extended_value.id}
			except ObjectDoesNotExist:
				pass
			results.append(data)
	results = {'required': results}
	return results

@register.inclusion_tag('insfiles/extension_fields.html')
def get_extension_fields(scan):
	results = []
	try:
		extension_fields = ExtensionField.objects.select_related().filter(scan__id=scan)
	except:
		extended_values = ExtensionType.objects.filter(required=True)
		if extended_values:
			for extended_value in extended_values:
				extension_fields = ExtensionField(extensiontype=extended_value, scan=self.scan, char_value='', date_value='', bool_value=False)
	results = {'extension_fields': extension_fields }
	return results