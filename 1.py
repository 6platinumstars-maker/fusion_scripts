import importlib
try:
    from .fusion_app import inner_shell_structure
except ImportError:
    from fusion_app import inner_shell_structure


def run(context):
    importlib.reload(inner_shell_structure)
    inner_shell_structure.run(context)
