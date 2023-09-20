# Generated by Django 3.1.14 on 2023-09-13 19:12

from django.db import migrations, models, connection


class Migration(migrations.Migration):

    dependencies = [
        ('mathesar', '0006_auto_20230906_0413'),
    ]

    operations = [
        migrations.RunSQL('ALTER TABLE mathesar_tablesettings ALTER column_order TYPE jsonb USING array_to_json(column_order)')
        if connection.settings_dict['ENGINE'].startswith('django.db.backends.postgresql')
        else migrations.AlterField(
            model_name='tablesettings',
            name='column_order',
            field=models.JSONField(default=None, null=True),
        )
    ]