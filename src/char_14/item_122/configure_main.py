# configure_main.py
from configure_dialog import configure as dialog_configure

def configure_all(*modules):
    for module in modules:
        if hasattr(module, "configure"):
            module.configure()
    dialog_configure()
