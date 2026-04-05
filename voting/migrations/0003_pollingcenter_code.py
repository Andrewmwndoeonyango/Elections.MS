# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0002_otpverification'),
    ]

    operations = [
        migrations.AddField(
            model_name='pollingcenter',
            name='code',
            field=models.CharField(max_length=8, unique=True, default='TEMP001'),
        ),
    ]
