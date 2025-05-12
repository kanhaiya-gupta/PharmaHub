# main.py
"""Main entry point for running the FastAPI server and generating QR codes."""

import logging
import os
import socket
import sys

import qrcode
import uvicorn

# Add the current directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def get_local_ip() -> str:
    """Detect the local IP address of the system.

    Returns:
        Local IP address (e.g., '192.168.2.43') or '127.0.0.1' if detection fails.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        logger.warning(f"Could not detect local IP: {e}. Falling back to 127.0.0.1")
        return "127.0.0.1"

def generate_qr_code(url: str, filename: str = "static/server_qr.png") -> None:
    """Generate a QR code for the given URL and save it as an image file.

    Args:
        url: The URL to encode in the QR code (e.g., 'http://192.168.2.43:8000').
        filename: The path to the output image file (default: 'static/server_qr.png').
    """
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filename)
        logger.info(f"QR code generated and saved as '{filename}'")
    except Exception as e:
        logger.error(f"Failed to generate QR code: {e}")

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8000
    reload = True

    if len(sys.argv) < 2:
        logger.error("Usage: python main.py {local|remote} [platform]")
        sys.exit(1)

    mode = sys.argv[1].lower()
    platform = sys.argv[2].lower() if len(sys.argv) > 2 else None

    if mode not in ["local", "remote"]:
        logger.error("Invalid mode. Use 'local' or 'remote'.")
        sys.exit(1)

    if mode == "remote":
        local_ip = get_local_ip()
        server_url = f"http://{local_ip}:{port}"
        logger.info(f"Starting server for remote access on {server_url}")
        logger.info("Ensure firewall allows incoming connections on port 8000")
        if platform and platform not in ["windows", "mac", "linux"]:
            logger.warning(
                f"Unsupported platform '{platform}'. Assuming standard OS."
            )
        generate_qr_code(server_url)
        logger.info(
            f"Scan the QR code in 'static/server_qr.png' with your phone to access the server"
        )
    else:
        logger.info(f"Starting server for local access on http://{host}:{port}")

    try:
        uvicorn.run("api.api:app", host=host, port=port, reload=reload)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)