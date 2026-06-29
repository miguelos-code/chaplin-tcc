import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chaplin_project.settings")
django.setup()

from apps.tasks.models import TaskEvidence
from django.conf import settings

print("MEDIA_ROOT:", settings.MEDIA_ROOT)
print("MEDIA_URL:", settings.MEDIA_URL)

for ev in TaskEvidence.objects.all():
    if ev.photo:
        url = ev.photo.url
        path = ev.photo.path
        exists = os.path.exists(path)
        print(f"ID: {ev.id}, URL: {url}, PATH: {path}, EXISTS: {exists}")
    else:
        print(f"ID: {ev.id}, NO PHOTO")
