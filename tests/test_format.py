import re
from dataclasses import replace
from typing import Any, Iterator
from unittest.mock import patch

import pytest

import pyink
from tests.util import (
    DEFAULT_MODE,
    PY36_VERSIONS,
    all_data_cases,
    assert_format,
    dump_to_stderr,
    read_data,
)


@pytest.fixture(autouse=True)
def patch_dump_to_file(request: Any) -> Iterator[None]:
    with patch("pyink.dump_to_file", dump_to_stderr):
        yield


def check_file(
    subdir: str, filename: str, mode: pyink.Mode, *, data: bool = True
) -> None:
    source, expected = read_data(subdir, filename, data=data)
    assert_format(source, expected, mode, fast=False)


@pytest.mark.filterwarnings("ignore:invalid escape sequence.*:DeprecationWarning")
@pytest.mark.parametrize("filename", all_data_cases("simple_cases"))
def test_simple_format(filename: str) -> None:
    magic_trailing_comma = filename != "skip_magic_trailing_comma"
    check_file(
        "simple_cases", filename, pyink.Mode(magic_trailing_comma=magic_trailing_comma)
    )


@pytest.mark.parametrize("filename", all_data_cases("preview"))
def test_preview_format(filename: str) -> None:
    check_file("preview", filename, pyink.Mode(preview=True))


@pytest.mark.parametrize("filename", all_data_cases("pyink"))
def test_pyink_format(filename: str) -> None:
    check_file(
        "pyink",
        filename,
        pyink.Mode(preview=True, line_length=80, is_pyink=True, pyink_indentation=2),
    )


def test_preview_context_managers_targeting_py38() -> None:
    source, expected = read_data("preview_context_managers", "targeting_py38.py")
    mode = pyink.Mode(preview=True, target_versions={pyink.TargetVersion.PY38})
    assert_format(source, expected, mode, minimum_version=(3, 8))


def test_preview_context_managers_targeting_py39() -> None:
    source, expected = read_data("preview_context_managers", "targeting_py39.py")
    mode = pyink.Mode(preview=True, target_versions={pyink.TargetVersion.PY39})
    assert_format(source, expected, mode, minimum_version=(3, 9))


@pytest.mark.parametrize(
    "filename", all_data_cases("preview_context_managers/auto_detect")
)
def test_preview_context_managers_auto_detect(filename: str) -> None:
    match = re.match(r"features_3_(\d+)", filename)
    assert match is not None, "Unexpected filename format: %s" % filename
    source, expected = read_data("preview_context_managers/auto_detect", filename)
    mode = pyink.Mode(preview=True)
    assert_format(source, expected, mode, minimum_version=(3, int(match.group(1))))


# =============== #
# Complex cases
# ============= #


def test_empty() -> None:
    source = expected = ""
    assert_format(source, expected)


@pytest.mark.parametrize("filename", all_data_cases("py_36"))
def test_python_36(filename: str) -> None:
    source, expected = read_data("py_36", filename)
    mode = pyink.Mode(target_versions=PY36_VERSIONS)
    assert_format(source, expected, mode, minimum_version=(3, 6))


@pytest.mark.parametrize("filename", all_data_cases("py_37"))
def test_python_37(filename: str) -> None:
    source, expected = read_data("py_37", filename)
    mode = pyink.Mode(target_versions={pyink.TargetVersion.PY37})
    assert_format(source, expected, mode, minimum_version=(3, 7))


@pytest.mark.parametrize("filename", all_data_cases("py_38"))
def test_python_38(filename: str) -> None:
    source, expected = read_data("py_38", filename)
    mode = pyink.Mode(target_versions={pyink.TargetVersion.PY38})
    assert_format(source, expected, mode, minimum_version=(3, 8))


@pytest.mark.parametrize("filename", all_data_cases("py_39"))
def test_python_39(filename: str) -> None:
    source, expected = read_data("py_39", filename)
    mode = pyink.Mode(target_versions={pyink.TargetVersion.PY39})
    assert_format(source, expected, mode, minimum_version=(3, 9))


@pytest.mark.parametrize("filename", all_data_cases("py_310"))
def test_python_310(filename: str) -> None:
    source, expected = read_data("py_310", filename)
    mode = pyink.Mode(target_versions={pyink.TargetVersion.PY310})
    assert_format(source, expected, mode, minimum_version=(3, 10))


@pytest.mark.parametrize("filename", all_data_cases("py_310"))
def test_python_310_without_target_version(filename: str) -> None:
    source, expected = read_data("py_310", filename)
    mode = pyink.Mode()
    assert_format(source, expected, mode, minimum_version=(3, 10))


def test_patma_invalid() -> None:
    source, expected = read_data("miscellaneous", "pattern_matching_invalid")
    mode = pyink.Mode(target_versions={pyink.TargetVersion.PY310})
    with pytest.raises(pyink.parsing.InvalidInput) as exc_info:
        assert_format(source, expected, mode, minimum_version=(3, 10))

    exc_info.match("Cannot parse: 10:11")


@pytest.mark.parametrize("filename", all_data_cases("py_311"))
def test_python_311(filename: str) -> None:
    source, expected = read_data("py_311", filename)
    mode = pyink.Mode(target_versions={pyink.TargetVersion.PY311})
    assert_format(source, expected, mode, minimum_version=(3, 11))


@pytest.mark.parametrize("filename", all_data_cases("fast"))
def test_fast_cases(filename: str) -> None:
    source, expected = read_data("fast", filename)
    assert_format(source, expected, fast=True)


def test_python_2_hint() -> None:
    with pytest.raises(pyink.parsing.InvalidInput) as exc_info:
        assert_format("print 'daylily'", "print 'daylily'")
    exc_info.match(pyink.parsing.PY2_HINT)


@pytest.mark.filterwarnings("ignore:invalid escape sequence.*:DeprecationWarning")
def test_docstring_no_string_normalization() -> None:
    """Like test_docstring but with string normalization off."""
    source, expected = read_data("miscellaneous", "docstring_no_string_normalization")
    mode = replace(DEFAULT_MODE, string_normalization=False)
    assert_format(source, expected, mode)


def test_docstring_line_length_6() -> None:
    """Like test_docstring but with line length set to 6."""
    source, expected = read_data("miscellaneous", "linelength6")
    mode = pyink.Mode(line_length=6)
    assert_format(source, expected, mode)


def test_preview_docstring_no_string_normalization() -> None:
    """
    Like test_docstring but with string normalization off *and* the preview style
    enabled.
    """
    source, expected = read_data(
        "miscellaneous", "docstring_preview_no_string_normalization"
    )
    mode = replace(DEFAULT_MODE, string_normalization=False, preview=True)
    assert_format(source, expected, mode)


def test_long_strings_flag_disabled() -> None:
    """Tests for turning off the string processing logic."""
    source, expected = read_data("miscellaneous", "long_strings_flag_disabled")
    mode = replace(DEFAULT_MODE, experimental_string_processing=False)
    assert_format(source, expected, mode)


def test_stub() -> None:
    mode = replace(DEFAULT_MODE, is_pyi=True)
    source, expected = read_data("miscellaneous", "stub.pyi")
    assert_format(source, expected, mode)


def test_power_op_newline() -> None:
    # requires line_length=0
    source, expected = read_data("miscellaneous", "power_op_newline")
    assert_format(source, expected, mode=pyink.Mode(line_length=0))
