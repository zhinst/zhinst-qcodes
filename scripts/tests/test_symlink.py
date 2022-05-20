from pathlib import Path
import tempfile
from unittest.mock import Mock, patch

from scripts import symlink


@patch("builtins.print")
@patch("scripts.symlink.os")
def test_create_symlink(mock_os, mock_print):
    with tempfile.TemporaryDirectory() as tmpdirname:
        src = Path(tmpdirname) / "foo/bar"
        src.mkdir(parents=True, exist_ok=True)
        dest = Path(tmpdirname) / "tester"
        mock_os.symlink = Mock()
        symlink.create_symlink(src, dest)
        mock_os.symlink.assert_called_with(src, dest)
        mock_print.assert_called_with(
            f"Symlink created. Source: {src}, Destination: {dest}"
        )


@patch("builtins.print")
def test_create_symlink_exists(mock_print):
    with tempfile.TemporaryDirectory() as tmpdirname:
        src = Path(tmpdirname) / "foo/bar"
        src.mkdir(parents=True, exist_ok=True)
        dest = Path(tmpdirname) / "foo"
        dest.mkdir(parents=True, exist_ok=True)
        symlink.create_symlink(src, dest)
        mock_print.assert_called_with(f"Destination: {dest} already exists.")
