"""
Overnight public-name and hardware-hook checks without importing ``board`` or ``core``.
"""

import ast
import pathlib

import pytest

from display._constants import WIDTH, HEIGHT, NUM_PIXELS


ROOT = pathlib.Path(__file__).resolve().parent.parent
CORE = ROOT / "lib" / "display" / "core.py"
BUTTONS = ROOT / "lib" / "buttons.py"


def _module_ast(path):
    return ast.parse(path.read_text())


def _class_methods(tree, class_name):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return {
                n.name
                for n in node.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
    raise AssertionError(f"class {class_name} not found")


def _assign_literal(tree, name):
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == name:
                    return ast.literal_eval(node.value)
    raise AssertionError(f"assignment {name} not found")


def test_geometry_is_5x5():
    assert WIDTH == HEIGHT == 5
    assert NUM_PIXELS == 25


def test_display_student_ops_exist_on_display_class():
    methods = _class_methods(_module_ast(CORE), "Display")
    for name in ("show_string", "pause", "show_icon", "show_number", "show_arrow", "clear"):
        assert name in methods, name


def test_button_student_ops_exist():
    methods = _class_methods(_module_ast(BUTTONS), "Buttons")
    for name in (
        "on_a_pressed",
        "on_b_pressed",
        "on_c_pressed",
        "on_d_pressed",
        "clear",
        "run",
    ):
        assert name in methods, name
    assert "update" not in methods


def test_brightness_cap_in_core_source():
    assert _assign_literal(_module_ast(CORE), "BRIGHTNESS") == pytest.approx(0.20)


def test_pixel_pin_is_neopixel_in_core_source():
    tree = _module_ast(CORE)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "PIXEL_PIN":
                    assert isinstance(node.value, ast.Attribute)
                    assert node.value.attr == "NEOPIXEL"
                    return
    raise AssertionError("PIXEL_PIN not found")


def test_font_path_is_makecode_5_not_freemono():
    src = CORE.read_text()
    assert "font_makecode_5" in src
    assert "font_free_mono_8" not in src


def test_fused_scan_is_wired_in_render_pattern():
    src = CORE.read_text()
    assert "_write_pattern_on_the_fly" in src
    # render_pattern body must call the fused helper (not only define it).
    tree = _module_ast(CORE)
    display_methods = [
        n for n in tree.body
        if isinstance(n, ast.ClassDef) and n.name == "Display"
    ][0]
    render = [
        n for n in display_methods.body
        if isinstance(n, ast.FunctionDef) and n.name == "render_pattern"
    ][0]
    calls = [n.func.id for n in ast.walk(render) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
    assert "_write_pattern_on_the_fly" in calls
