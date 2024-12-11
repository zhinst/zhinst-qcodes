import pytest
from unittest.mock import patch
from fixtures import mock_connection, data_dir, session


class TestDataServerSession:
    def test_setup(self, mock_connection, session):
        mock_connection.assert_called_once_with(
            "localhost", 8004, 6, allow_version_mismatch=False
        )
        mock_connection.return_value.listNodesJSON.assert_called_once_with("/zi/*")
        assert not session.is_hf2_server
        assert session.server_host == mock_connection.return_value.host
        assert session.server_port == mock_connection.return_value.port
