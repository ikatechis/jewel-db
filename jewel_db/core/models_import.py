# jewel_db/core/models_import.py
from importlib import import_module


def import_models() -> None:
    """
    Import all ORM model modules exactly once.
    Keeps metadata discovery explicit and centralised.
    """
    import_module("jewel_db.models.jewelry_item")
    import_module("jewel_db.models.jewelry_tag")
    import_module("jewel_db.models.jewelry_image")
