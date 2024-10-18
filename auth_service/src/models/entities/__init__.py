import importlib
import os
import pkgutil

MODELS_DIR = os.path.dirname(__file__)


def import_all_models():
    """
    Import all models dynamically.
    """
    package_name = __name__

    for _, module_name, _ in pkgutil.iter_modules([MODELS_DIR]):
        full_module_name = f'{package_name}.{module_name}'
        importlib.import_module(full_module_name)


import_all_models()
