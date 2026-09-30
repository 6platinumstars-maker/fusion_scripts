import importlib
try:
    from .fusion_app import grip_structure
except ImportError:
    from fusion_app import grip_structure


def run(context):
    importlib.reload(grip_structure)
    grip_structure.run(context)
