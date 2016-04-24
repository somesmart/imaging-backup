from django import template
from insfiles.models import *
from django.db.models import Count

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
		for extended_value in extended_values:
			extended_count = ExtensionField.objects.select_related().filter(extensiontype=extended_value).aggregate(ext_count=Count('scan__id'))
			data = {'type': extended_value.description, 'count': extended_count['ext_count'], 'url': 'type-view', 'url_arg': extended_value.id}
			results.append(data)
	results = {'required': results}
	return results
