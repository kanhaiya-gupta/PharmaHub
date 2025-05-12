import os
import pytest
from main import generate_qr_code, get_local_ip

def test_get_local_ip():
    """Test the local IP detection function."""
    ip = get_local_ip()
    assert isinstance(ip, str)
    assert len(ip.split('.')) == 4  # Should be a valid IP address format

def test_generate_qr_code(tmp_path):
    """Test QR code generation."""
    # Create a temporary directory for the test
    test_dir = tmp_path / "static"
    test_dir.mkdir()
    
    # Test file path
    test_file = test_dir / "test_qr.png"
    
    # Generate QR code
    test_url = "http://test.example.com"
    generate_qr_code(test_url, str(test_file))
    
    # Check if file was created
    assert test_file.exists()
    assert test_file.stat().st_size > 0  # File should not be empty

def test_generate_qr_code_invalid_path():
    """Test QR code generation with invalid path."""
    with pytest.raises(Exception):
        generate_qr_code("http://test.example.com", "/invalid/path/test.png") 