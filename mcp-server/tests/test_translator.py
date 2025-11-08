"""Tests for command translator."""

import pytest
from translator import CommandTranslator

translator = CommandTranslator()


def test_simple_button():
    element_type, props = translator.parse_command("create a button")
    assert element_type == "rectangle"
    assert "name" in props


def test_primary_button_with_brand():
    element_type, props = translator.parse_command(
        "create a primary CTA button",
        project="compel-english"
    )
    assert element_type == "rectangle"
    assert props.get("fills")[0]["fillColor"] == "#FF5733"
    assert props["borderRadius"] == 8


def test_dimensions():
    element_type, props = translator.parse_command("create a 300x50 button")
    assert props["width"] == 300
    assert props["height"] == 50


def test_text_element():
    element_type, props = translator.parse_command('create text "Hello World"')
    assert element_type == "text"
    assert props["text"] == "Hello World"
