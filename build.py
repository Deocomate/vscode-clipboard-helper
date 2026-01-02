import PyInstaller.__main__
import os

def build_exe():
    print("Building EXE...")
    
    # Ensure dist and build directories exist or are clean (PyInstaller handles this mostly)
    
    # Define PyInstaller arguments
    args = [
        'main.py',                        # Main script
        '--name=VSCodeClipboardHelper',   # Name of the executable
        '--onefile',                      # Create a single executable file
        '--noconsole',                    # Do not show a console window
        '--clean',                        # Clean PyInstaller cache and remove temporary files
        '--icon=icon.ico',                # Use icon.ico for the EXE file icon
        '--add-data=icon.png;.',          # Bundle icon.png (Windows separator ;)
        '--add-data=icon.ico;.',          # Bundle icon.ico for runtime usage if needed
    ]
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print("Build complete. Check the 'dist' folder.")

if __name__ == "__main__":
    if not os.path.exists("icon.ico") or not os.path.exists("icon.png"):
        print("Warning: icon.ico or icon.png not found. Build might fail or have generic icon.")
    
    build_exe()
