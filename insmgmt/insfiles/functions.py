import os

def get_image_path(instance, filename):
		return os.path.join('scans/client', str(instance.client.id), filename)