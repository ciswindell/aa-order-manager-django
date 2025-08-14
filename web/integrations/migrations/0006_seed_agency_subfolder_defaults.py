from django.db import migrations


NMSLO_DEFAULTS = {
    "runsheet_subfolder_documents_name": "^Document Archive",
    "runsheet_subfolder_misc_index_name": "^MI Index",
    "runsheet_subfolder_runsheets_name": "Runsheets",
}

BLM_DEFAULTS = {
    "runsheet_subfolder_documents_name": "^Document Archive",
    "runsheet_subfolder_misc_index_name": None,
    "runsheet_subfolder_runsheets_name": "Runsheets",
}


def seed_defaults(apps, schema_editor):
    AgencyStorageConfig = apps.get_model("integrations", "AgencyStorageConfig")

    for agency, defaults in (("NMSLO", NMSLO_DEFAULTS), ("BLM", BLM_DEFAULTS)):
        try:
            cfg = AgencyStorageConfig.objects.get(agency=agency)
        except AgencyStorageConfig.DoesNotExist:
            continue

        updated = False
        for field, value in defaults.items():
            current = getattr(cfg, field, None)
            if not current and value:
                setattr(cfg, field, value)
                updated = True
        # Ensure toggle is true only if not already set to False
        if getattr(cfg, "auto_create_lease_directories", True) is None:
            cfg.auto_create_lease_directories = True
            updated = True
        if updated:
            cfg.save(
                update_fields=[
                    "runsheet_subfolder_documents_name",
                    "runsheet_subfolder_misc_index_name",
                    "runsheet_subfolder_runsheets_name",
                    "auto_create_lease_directories",
                ]
            )


def noop_reverse(apps, schema_editor):
    # No-op: data migration does not need rollback
    pass


class Migration(migrations.Migration):

    dependencies = [
        (
            "integrations",
            "0005_agencystorageconfig_auto_create_lease_directories_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(seed_defaults, noop_reverse),
    ]
