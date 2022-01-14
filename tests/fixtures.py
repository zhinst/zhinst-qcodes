import pytest
from unittest.mock import patch
from pathlib import Path
from zhinst.qcodes import ZISession


@pytest.fixture()
def data_dir(request):
    yield Path(request.fspath).parent / "data"


@pytest.fixture()
def mock_connection():
    with patch(
        "zhinst.toolkit.session.ziPython.ziDAQServer", autospec=True
    ) as connection:
        yield connection


@pytest.fixture()
def session(data_dir, mock_connection):
    json_path = data_dir / "nodedoc_zi.json"
    with json_path.open("r", encoding="UTF-8") as file:
        nodes_json = file.read()
    mock_connection.return_value.listNodesJSON.return_value = nodes_json
    yield ZISession("localhost")
