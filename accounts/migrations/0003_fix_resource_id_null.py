# Manual migration to fix resource_id NOT NULL constraint
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_auditlog_resource_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auditlog',
            name='resource_id',
            field=models.CharField(
                max_length=100,
                blank=True,
                null=True,
                default='',
                help_text='ID of the affected resource'
            ),
        ),
    ]
