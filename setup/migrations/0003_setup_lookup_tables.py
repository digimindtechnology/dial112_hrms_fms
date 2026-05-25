# Generated manually for setup lookup modal tables.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def lookup_fields():
    return [
        ('id', models.AutoField(primary_key=True, serialize=False)),
        ('remark', models.TextField(blank=True, null=True)),
        ('created_date', models.DateTimeField(auto_now_add=True)),
        ('updated_date', models.DateTimeField(auto_now=True)),
        ('is_active', models.BooleanField(default=True)),
        ('name', models.CharField(max_length=255)),
        ('description', models.TextField(blank=True, null=True)),
        ('created_by', models.ForeignKey(
            on_delete=django.db.models.deletion.CASCADE,
            related_name='%(class)s_created',
            to=settings.AUTH_USER_MODEL,
        )),
        ('tenantProfile', models.ForeignKey(
            on_delete=django.db.models.deletion.CASCADE,
            to='tenant.tenantprofile',
        )),
        ('updated_by', models.ForeignKey(
            blank=True,
            null=True,
            on_delete=django.db.models.deletion.SET_NULL,
            related_name='%(class)s_updated',
            to=settings.AUTH_USER_MODEL,
        )),
    ]


def lookup_options(verbose_name, verbose_name_plural, constraint_name):
    return {
        'verbose_name': verbose_name,
        'verbose_name_plural': verbose_name_plural,
        'ordering': ('name',),
        'constraints': [
            models.UniqueConstraint(fields=('tenantProfile', 'name'), name=constraint_name)
        ],
    }


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0002_costcenterstatus_alter_costcenter_created_by_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeType',
            fields=lookup_fields(),
            options=lookup_options('Employee Type', 'Employee Types', 'setup_employee_type_tenant_name_uniq'),
        ),
        migrations.CreateModel(
            name='Designation',
            fields=lookup_fields(),
            options=lookup_options('Designation', 'Designations', 'setup_designation_tenant_name_uniq'),
        ),
        migrations.CreateModel(
            name='Grade',
            fields=lookup_fields(),
            options=lookup_options('Grade', 'Grades', 'setup_grade_tenant_name_uniq'),
        ),
        migrations.CreateModel(
            name='Language',
            fields=lookup_fields(),
            options=lookup_options('Language', 'Languages', 'setup_language_tenant_name_uniq'),
        ),
        migrations.CreateModel(
            name='Dialect',
            fields=lookup_fields(),
            options=lookup_options('Dialect', 'Dialects', 'setup_dialect_tenant_name_uniq'),
        ),
        migrations.CreateModel(
            name='LeaveType',
            fields=lookup_fields(),
            options=lookup_options('Leave Type', 'Leave Types', 'setup_leave_type_tenant_name_uniq'),
        ),
        migrations.CreateModel(
            name='ShiftCategory',
            fields=lookup_fields(),
            options=lookup_options('Shift Category', 'Shift Categories', 'setup_shift_category_tenant_name_uniq'),
        ),
        migrations.CreateModel(
            name='ViolationType',
            fields=lookup_fields(),
            options=lookup_options('Violation Type', 'Violation Types', 'setup_violation_type_tenant_name_uniq'),
        ),
        migrations.CreateModel(
            name='TrainerType',
            fields=lookup_fields(),
            options=lookup_options('Trainer Type', 'Trainer Types', 'setup_trainer_type_tenant_name_uniq'),
        ),
        migrations.CreateModel(
            name='FRVType',
            fields=lookup_fields(),
            options=lookup_options('FRV Type', 'FRV Types', 'setup_frv_type_tenant_name_uniq'),
        ),
        migrations.CreateModel(
            name='FRVMaintenanceType',
            fields=lookup_fields(),
            options=lookup_options(
                'FRV Maintenance Type',
                'FRV Maintenance Types',
                'setup_frv_maintenance_type_tenant_name_uniq',
            ),
        ),
    ]
