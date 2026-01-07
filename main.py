#!/usr/bin/env python3
"""
VSCode Clipboard Helper - Entry Point

A cross-platform utility that converts VS Code's file copy format
to native file drop format for seamless paste operations.

Supports Windows and macOS.
"""

import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)

def main():
    """Main entry point for the application."""
    from app.gui import VSCodeBridgeApp
    from app.utils.platform import get_platform_name
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting VSCode Clipboard Helper on {get_platform_name()}")
    
    try:
        app = VSCodeBridgeApp()
        app.run()
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
