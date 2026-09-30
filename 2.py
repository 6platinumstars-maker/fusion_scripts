import importlib
try:
    from .fusion_app import outer_shell_structure
except ImportError:
    from fusion_app import outer_shell_structure


def run(context):
    importlib.reload(outer_shell_structure)
    outer_shell_structure.run(context)
