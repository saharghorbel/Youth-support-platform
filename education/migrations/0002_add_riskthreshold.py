# Generated migration for RiskThreshold model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('education', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RiskThreshold',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Descriptive name for this threshold configuration', max_length=100)),
                ('description', models.TextField(blank=True, help_text='Explanation of when to use this threshold')),
                ('attendance_threshold', models.FloatField(default=75.0, help_text='Minimum acceptable attendance rate (%)', validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('grade_threshold', models.FloatField(default=10.0, help_text='Minimum acceptable average grade (0-20 scale)', validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(20.0)])),
                ('behavior_threshold', models.IntegerField(default=3, help_text='Maximum acceptable number of behavior incidents', validators=[django.core.validators.MinValueValidator(0)])),
                ('missed_appointments_threshold', models.IntegerField(default=2, help_text='Maximum acceptable number of missed appointments', validators=[django.core.validators.MinValueValidator(0)])),
                ('is_active', models.BooleanField(default=False, help_text='Only one threshold can be active at a time')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_thresholds', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'risk_thresholds',
                'ordering': ['-created_at'],
            },
        ),
    ]
