#!/usr/bin/env python3
"""
Cross-Platform Build Script for VSCode Clipboard Helper

Builds standalone executables using PyInstaller:
- Windows: Creates .exe file
- macOS: Creates .app bundle
"""

import os
import sys
import platform
import PyInstaller.__main__


def is_windows():
    return sys.platform == 'win32'


def is_macos():
    return sys.platform == 'darwin'


def get_data_separator():
    """Get the correct data separator for PyInstaller --add-data."""
    return ';' if is_windows() else ':'


def build():
    """Build the application for the current platform."""
    print(f"Building for {platform.system()}...")
    
    sep = get_data_separator()
    
    # Common PyInstaller arguments
    args = [
        'main.py',
        '--name=VSCodeClipboardHelper',
        '--clean',
        f'--add-data=icon.png{sep}.',
    ]
    
    if is_windows():
        # Windows-specific options
        args.extend([
            '--onefile',
            '--noconsole',
            '--icon=icon.ico',
            f'--add-data=icon.ico{sep}.',
        ])
        print("Building Windows executable (.exe)...")
        
    elif is_macos():
        # macOS-specific options
        args.extend([
            '--windowed',  # Creates .app bundle
            '--onedir',    # Better for macOS app bundles
        ])
        
        # Use .icns if available, otherwise .png
        if os.path.exists('icon.icns'):
            args.append('--icon=icon.icns')
        elif os.path.exists('icon.png'):
            args.append('--icon=icon.png')
            
        print("Building macOS application (.app)...")
        
    else:
        # Linux/other - basic build
        args.extend([
            '--onefile',
            '--noconsole',
        ])
        print("Building Linux executable...")
    
    # Run PyInstaller
    try:
        PyInstaller.__main__.run(args)
        print("\n✓ Build complete!")
        print(f"  Output location: {os.path.abspath('dist')}")
        
        if is_macos():
            print("  → VSCodeClipboardHelper.app")
        else:
            print("  → VSCodeClipboardHelper.exe" if is_windows() else "  → VSCodeClipboardHelper")
            
    except Exception as e:
        print(f"\n✗ Build failed: {e}")
        sys.exit(1)


def check_requirements():
    """Check if required files exist."""
    warnings = []
    
    if not os.path.exists('icon.png'):
        warnings.append("icon.png not found - using default icon")
        
    if is_windows() and not os.path.exists('icon.ico'):
        warnings.append("icon.ico not found - Windows exe may have generic icon")
        
    if is_macos() and not os.path.exists('icon.icns'):
        warnings.append("icon.icns not found - macOS app may have generic icon")
    
    for warning in warnings:
        print(f"⚠ Warning: {warning}")
    
    return len(warnings) == 0


if __name__ == "__main__":
    print("=" * 50)
    print("VSCode Clipboard Helper - Build Script")
    print("=" * 50)
    print()
    
    check_requirements()
    print()
    
    build()
