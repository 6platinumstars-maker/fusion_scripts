import os
import sys

import adsk.core
import adsk.fusion

try:
    from . import naming
except ImportError:
    import naming


def load_fusion_helpers():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    core_dir = os.path.join(os.path.dirname(script_dir), 'core')

    if core_dir not in sys.path:
        sys.path.append(core_dir)

    import fusion_helpers

    return fusion_helpers


def get_active_design():
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    if not design:
        raise RuntimeError('Fusion Design workspace is not active.')
    return design


def get_root_component(design=None):
    if design is None:
        design = get_active_design()
    return design.rootComponent


def add_named_attribute(entity, name):
    existing = entity.attributes.itemByName(
        naming.ATTRIBUTE_GROUP,
        naming.ATTRIBUTE_NAME_KEY
    )
    if existing:
        existing.deleteMe()
    entity.attributes.add(
        naming.ATTRIBUTE_GROUP,
        naming.ATTRIBUTE_NAME_KEY,
        name
    )


def set_body_identity(body, name):
    body.name = name
    add_named_attribute(body, name)


def find_body_by_named_attribute(root_comp, name):
    for index in range(root_comp.bRepBodies.count):
        body = root_comp.bRepBodies.item(index)
        attr = body.attributes.itemByName(
            naming.ATTRIBUTE_GROUP,
            naming.ATTRIBUTE_NAME_KEY
        )
        if attr and attr.value == name:
            return body
    return None


def find_body_by_name(root_comp, name):
    for index in range(root_comp.bRepBodies.count):
        body = root_comp.bRepBodies.item(index)
        if body.name == name:
            return body
    return None


def find_body_by_name_or_attribute(root_comp, name):
    body = find_body_by_name(root_comp, name)
    if body:
        return body
    return find_body_by_named_attribute(root_comp, name)


def find_construction_plane_by_name(root_comp, name):
    planes = root_comp.constructionPlanes
    for index in range(planes.count):
        plane = planes.item(index)
        if plane.name == name:
            return plane
    return None


def find_construction_plane_by_named_attribute(root_comp, name):
    planes = root_comp.constructionPlanes
    for index in range(planes.count):
        plane = planes.item(index)
        attr = plane.attributes.itemByName(
            naming.ATTRIBUTE_GROUP,
            naming.ATTRIBUTE_NAME_KEY,
        )
        if attr and attr.value == name:
            return plane
    return None


def find_construction_plane_by_name_or_attribute(root_comp, name):
    plane = find_construction_plane_by_name(root_comp, name)
    if plane:
        return plane
    return find_construction_plane_by_named_attribute(root_comp, name)
