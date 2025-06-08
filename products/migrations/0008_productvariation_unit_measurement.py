from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_alter_product_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvariation',
            name='unit_measurement',
            field=models.CharField(default='piece', max_length=20),
        ),
    ] 