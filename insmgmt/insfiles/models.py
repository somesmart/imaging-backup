from django.db import models
from .functions import get_image_path
import os

class Client(models.Model):
	first_name = models.CharField(max_length=200)
	last_name = models.CharField(max_length=200)

	def __unicode__(self):
		return u"%s %s" % (self.first_name, self.last_name)	

class ExtensionType(models.Model):
	DATATYPE = (
		(1, 'char_value'),
		(2, 'date_value'),
		(3, 'bool_value'),
	)
	description = models.CharField(max_length=200)
	required = models.BooleanField()
	data_type = models.IntegerField(choices=DATATYPE)

	def __unicode__(self):
		return unicode(self.description)

class Scan(models.Model):
	DOCTYPE = (
		(1, 'Policy'),
		(2, 'License'),
		(3, 'Other'),
		(4, 'Pending'),
	)

	client = models.ForeignKey(Client)
	document = models.FileField(upload_to=get_image_path)
	document_type = models.IntegerField(choices=DOCTYPE)
	scan_date = models.DateTimeField(auto_now_add=True)
	signature_required = models.BooleanField()
	signed = models.BooleanField(default=False)
	signed_date = models.DateTimeField(blank=True, null=True)

	def save(self, *args, **kwargs):
		# delete old file when replacing by updating the file
		try:
			this = Scan.objects.get(id=self.id)
			if this.document != self.document:
				this.document.delete(save=False)
		except: pass # when new document then we do nothing, normal case
		super(Scan, self).save(*args, **kwargs)

	def extension(self):
		_, extension = os.path.splitext(self.document.url)
		return extension

	def __unicode__(self):
		return unicode(self.client)

class ExtensionField(models.Model):
	extensiontype = models.ForeignKey(ExtensionType)
	scan = models.ForeignKey(Scan)
	char_value = models.CharField(max_length=200, blank=True, null=True)
	date_value = models.DateTimeField(blank=True, null=True)
	bool_value = models.BooleanField()

	def __unicode__(self):
		return u'%s %s' % (self.extensiontype, self.bool_value)
