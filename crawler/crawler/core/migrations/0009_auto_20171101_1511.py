# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-01 15:11
from __future__ import unicode_literals

import crawler.core.resource_models
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0008_auto_20171031_1605'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParentModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('leaf_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='preservationtag',
            managers=[
            ],
        ),
        migrations.RemoveField(
            model_name='preservationtag',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='preservationtag',
            name='id',
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('parentmodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.ParentModel')),
                ('resource_file', models.FileField(upload_to=crawler.core.resource_models.resource_path)),
            ],
            bases=('core.parentmodel',),
        ),
        migrations.AddField(
            model_name='parentmodel',
            name='content_type',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='preservationtag',
            name='parentmodel_ptr',
            field=models.OneToOneField(auto_created=True, default=None, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.ParentModel'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='HTMLResource',
            fields=[
                ('resource_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Resource')),
            ],
            bases=('core.resource',),
        ),
        migrations.CreateModel(
            name='ImageResource',
            fields=[
                ('resource_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Resource')),
            ],
            bases=('core.resource',),
        ),
        migrations.CreateModel(
            name='ScriptResource',
            fields=[
                ('resource_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Resource')),
            ],
            bases=('core.resource',),
        ),
        migrations.CreateModel(
            name='StyeResource',
            fields=[
                ('resource_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Resource')),
            ],
            bases=('core.resource',),
        ),
        migrations.AddField(
            model_name='resource',
            name='article',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resources', to='core.Article'),
        ),
    ]
