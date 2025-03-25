import serial
import base64
from typing import Optional, Tuple
import time

class FingerprintScanner:
    def __init__(self, port: str = 'COM3', baud_rate: int = 57600):
        """
        Initialize the fingerprint scanner
        Args:
            port: Serial port (e.g., 'COM3' for Windows)
            baud_rate: Communication speed
        """
        self.port = port
        self.baud_rate = baud_rate
        self.serial = None
        self.connected = False

    def connect(self) -> bool:
        """
        Connect to the fingerprint scanner
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=1
            )
            self.connected = True
            return True
        except Exception as e:
            print(f"Error connecting to scanner: {str(e)}")
            self.connected = False
            return False

    def disconnect(self):
        """Disconnect from the fingerprint scanner"""
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.connected = False

    def capture_fingerprint(self) -> Optional[bytes]:
        """
        Capture fingerprint data from the scanner
        Returns:
            bytes: Raw fingerprint data or None if capture failed
        """
        if not self.connected:
            print("Scanner not connected")
            return None

        try:
            # Send command to capture fingerprint
            self.serial.write(b'\x01')  # Example command, adjust based on your scanner's protocol
            
            # Wait for response
            time.sleep(2)  # Adjust based on your scanner's response time
            
            # Read the response
            if self.serial.in_waiting:
                data = self.serial.read(self.serial.in_waiting)
                return data
            return None
            
        except Exception as e:
            print(f"Error capturing fingerprint: {str(e)}")
            return None

    def get_scanner_status(self) -> Tuple[bool, str]:
        """
        Get the current status of the scanner
        Returns:
            Tuple[bool, str]: (is_connected, status_message)
        """
        if not self.connected:
            return False, "Scanner not connected"
            
        try:
            # Send status check command
            self.serial.write(b'\x02')  # Example command, adjust based on your scanner's protocol
            
            # Wait for response
            time.sleep(0.5)
            
            if self.serial.in_waiting:
                response = self.serial.read(self.serial.in_waiting)
                return True, "Scanner ready"
            return True, "Scanner busy"
            
        except Exception as e:
            return False, f"Error checking scanner status: {str(e)}"

    def initialize_scanner(self) -> Tuple[bool, str]:
        """
        Initialize the fingerprint scanner
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            if self.connect():
                return True, "Scanner initialized successfully"
            return False, "Failed to connect to scanner"
        except Exception as e:
            return False, f"Error initializing scanner: {str(e)}" 