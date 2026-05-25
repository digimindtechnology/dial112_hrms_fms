from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0003_setup_lookup_tables'),
    ]

    operations = [
        migrations.AddField(
            model_name='shiftcategory',
            name='how_many_hours',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
    ]
