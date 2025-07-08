
from django.db import migrations

def create_default_jd(apps, schema_editor):
    JobDescription = apps.get_model("ai_int_app", "JobDescription")
    JobDescription.objects.create(
        title="Backend Developer",
        description="Experience with Python, Django, and REST APIs."
    )

class Migration(migrations.Migration):

    dependencies = [
        # your dependencies here
    ]

    operations = [
        migrations.RunPython(create_default_jd),
    ]
