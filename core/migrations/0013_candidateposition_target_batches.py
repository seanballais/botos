# Generated by Django 2.2.13 on 2020-06-10 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20200608_0704'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidateposition',
            name='target_batches',
            field=models.ManyToManyField(blank=True, default=None, null=True, related_name='candidate_positions', to='core.Batch'),
        ),
    ]
