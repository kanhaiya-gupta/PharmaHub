import pytest
import sys
from unittest.mock import patch
import uvicorn

def test_server_local_mode():
    """Test server startup in local mode."""
    with patch('sys.argv', ['main.py', 'local']):
        with patch('uvicorn.run') as mock_run:
            # Import and run the main script
            with patch('builtins.__import__') as mock_import:
                mock_import.return_value = type('MockModule', (), {'__name__': '__main__'})
                exec(open('main.py').read())
                mock_run.assert_called_once()
                args, kwargs = mock_run.call_args
                assert kwargs['host'] == '0.0.0.0'
                assert kwargs['port'] == 8000
                assert kwargs['reload'] is True

def test_server_remote_mode():
    """Test server startup in remote mode."""
    with patch('sys.argv', ['main.py', 'remote']):
        with patch('uvicorn.run') as mock_run:
            with patch('main.get_local_ip', return_value='192.168.1.1'):
                # Import and run the main script
                with patch('builtins.__import__') as mock_import:
                    mock_import.return_value = type('MockModule', (), {'__name__': '__main__'})
                    exec(open('main.py').read())
                    mock_run.assert_called_once()
                    args, kwargs = mock_run.call_args
                    assert kwargs['host'] == '0.0.0.0'
                    assert kwargs['port'] == 8000
                    assert kwargs['reload'] is True

def test_server_invalid_mode():
    """Test server startup with invalid mode."""
    with patch('sys.argv', ['main.py', 'invalid']):
        with pytest.raises(SystemExit) as exc_info:
            # Import and run the main script
            with patch('builtins.__import__') as mock_import:
                mock_import.return_value = type('MockModule', (), {'__name__': '__main__'})
                exec(open('main.py').read())
        assert exc_info.value.code == 1 