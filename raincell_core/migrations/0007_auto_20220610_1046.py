# Generated by Django 3.2.13 on 2022-06-10 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raincell_core', '0006_update_MVT_function'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='cell',
            name='raincell_co_cell_id_e44593_idx',
        ),
        migrations.RenameField(
            model_name='cell',
            old_name='cell_id',
            new_name='id',
        ),
        migrations.AddIndex(
            model_name='cell',
            index=models.Index(fields=['id'], name='raincell_co_id_89bb88_idx'),
        ),
    ]
