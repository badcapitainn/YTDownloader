#!/usr/bin/env python3
"""
Build script to create executable from the YouTube downloader GUI.
"""

import os
import sys
import subprocess
from pathlib import Path

def build_executable():
    """Build executable using PyInstaller."""
    print("Building YouTube Downloader executable...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Create a single executable file
        "--windowed",                   # No console window (GUI only)
        "--name=YouTube_Downloader",     # Name of the executable
        "--icon=icon.ico",              # Icon file (if exists)
        "yt_downloader_gui.py"          # Main script
    ]
    
    # Remove icon parameter if icon file doesn't exist
    if not Path("icon.ico").exists():
        cmd.remove("--icon=icon.ico")
    
    try:
        print("Running PyInstaller...")
        subprocess.run(cmd, check=True)
        
        print("\n" + "="*50)
        print("BUILD SUCCESSFUL!")
        print("="*50)
        print(f"Executable created: dist/YouTube_Downloader.exe")
        print(f"Size: {Path('dist/YouTube_Downloader.exe').stat().st_size / (1024*1024):.1f} MB")
        print("\nYou can now distribute the executable file!")
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False
    
    return True

def create_icon():
    """Create a simple icon file if it doesn't exist."""
    icon_path = Path("icon.ico")
    if icon_path.exists():
        print("Icon file already exists.")
        return
    
    print("Creating icon file...")
    try:
        from PIL import Image, ImageDraw
        
        # Create a simple icon
        img = Image.new('RGBA', (64, 64), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a simple play button
        draw.rectangle([10, 10, 54, 54], fill=(255, 0, 0, 255))
        draw.polygon([(20, 20), (20, 44), (44, 32)], fill=(255, 255, 255, 255))
        
        img.save(icon_path, format='ICO')
        print("Icon created successfully!")
        
    except ImportError:
        print("PIL not available. Creating icon without image library...")
        # Create a minimal ICO file
        with open(icon_path, 'wb') as f:
            # Minimal ICO file header
            f.write(b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x08\x00\x68\x05\x00\x00\x16\x00\x00\x00')
            # Add minimal bitmap data
            f.write(b'\x00' * 1280)  # 16x16 icon data

if __name__ == "__main__":
    print("YouTube Downloader - Executable Builder")
    print("="*40)
    
    # Check if GUI file exists
    if not Path("yt_downloader_gui.py").exists():
        print("Error: yt_downloader_gui.py not found!")
        sys.exit(1)
    
    # Create icon if needed
    create_icon()
    
    # Build executable
    if build_executable():
        print("\nBuild completed successfully!")
        print("\nTo run the executable:")
        print("1. Navigate to the 'dist' folder")
        print("2. Double-click 'YouTube_Downloader.exe'")
        print("\nNote: The first run might be slower as Windows scans the executable.")
    else:
        print("Build failed!")
        sys.exit(1)
