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
PLANETX_BUTTON = ROOT / "lib" / "planetx" / "button.py"


def _module_ast(path):
    return ast.parse(path.read_text())


def _class_names(tree):
    return {n.name for n in tree.body if isinstance(n, ast.ClassDef)}


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
    """Display constants are a 5×5 grid (25 pixels).

    - Covers: leftover Exp14 8×8 WIDTH/HEIGHT after the overnight swap.
    - How: ``WIDTH == HEIGHT == 5`` and ``NUM_PIXELS == 25``.
    """
    assert WIDTH == HEIGHT == 5
    assert NUM_PIXELS == 25


def test_display_student_ops_exist_on_display_class():
    """``Display`` still has the LightTower operation names.

    - Covers: rename/drop of ``show_string`` / ``show_icon`` / … during the 5×5 fork.
    - How: AST of ``core.py`` (no import); membership of the name list.
    """
    methods = _class_methods(_module_ast(CORE), "Display")
    for name in ("show_string", "pause", "show_icon", "show_number", "show_arrow", "clear"):
        assert name in methods, name


def test_button_student_ops_exist():
    """Board button classes have letter properties + ``run`` / ``clear``, no ``Buttons``, no ``update``.

    - Covers: leftover 4-pin ``Buttons``, missing A/B, PlanetX class still in ``buttons.py``.
    - How: AST of ``buttons.py``; class names + required methods; ``update`` absent.
    """
    tree = _module_ast(BUTTONS)
    names = _class_names(tree)
    assert "Buttons" not in names
    assert "PlanetXButtonSensor" not in names
    assert {"PushButtonBase", "Button", "OnboardButtons"} <= names

    push = _class_methods(tree, "PushButtonBase")
    for name in ("on_pressed", "on_released", "clear", "clear_pressed", "clear_released"):
        assert name in push, name
    assert "run" not in push
    assert "update" not in push

    button = _class_methods(tree, "Button")
    assert "run" in button
    assert "update" not in button

    ab = _class_methods(tree, "OnboardButtons")
    for name in ("button_a", "button_b", "clear", "run"):
        assert name in ab, name
    assert "update" not in ab


def test_planetx_button_student_ops_exist():
    """``PlanetXButtonSensor`` lives in ``planetx`` with C/D button objects, no ``update``.

    - Covers: class left in ``buttons.py``, or missing ``button_c`` / ``button_d``.
    - How: AST of ``planetx/button.py``; required properties; ``update`` absent.
    """
    tree = _module_ast(PLANETX_BUTTON)
    names = _class_names(tree)
    assert "PlanetXButtonSensor" in names
    px = _class_methods(tree, "PlanetXButtonSensor")
    for name in ("button_c", "button_d"):
        assert name in px, name
    assert "update" not in px


def test_brightness_cap_in_core_source():
    """``BRIGHTNESS`` in ``core.py`` is 0.20 (Exp09 used 0.1).

    - Covers: leftover 0.1 / 1.0 after the copy.
    - How: AST literal of the module-level assignment; ``pytest.approx(0.20)``.
    """
    assert _assign_literal(_module_ast(CORE), "BRIGHTNESS") == pytest.approx(0.20)


def test_pixel_pin_is_neopixel_in_core_source():
    """``PIXEL_PIN`` is ``board.NEOPIXEL``, not a GPIO number.

    - Covers: leftover Exp14 pin (e.g. GP0) after the BPI-Bit-S2 copy.
    - How: AST of the assignment; attribute name ``NEOPIXEL``. Does not import ``board``.
    """
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
    """``core.py`` points at ``font_makecode_5``, not Exp14 ``font_free_mono_8``.

    - Covers: leftover PCF path after the DAL table swap.
    - How: substring search of ``core.py`` source (no import).
    """
    src = CORE.read_text()
    assert "font_makecode_5" in src
    assert "font_free_mono_8" not in src


def test_fused_scan_is_wired_in_render_pattern():
    """``Display.render_pattern`` calls ``_write_pattern_on_the_fly`` (not only defines it).

    - Covers: helper present in the module but unused (Exp14 sketch state).
    - How: AST walk of ``render_pattern``; a ``Name`` call to ``_write_pattern_on_the_fly``.
    """
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
