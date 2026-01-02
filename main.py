import time
import threading
import sys
import os
import urllib.parse
import ctypes
from ctypes import wintypes
import tkinter as tk
from tkinter import ttk, messagebox
import win32clipboard
import win32con
from PIL import Image, ImageDraw
import pystray
import logging

# --- Logging Configuration ---
# Only show INFO and above in console to avoid flooding
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# --- Debug mode ---
DEBUG = False

# --- Custom clipboard format names (used by Electron apps) ---
ELECTRON_URI_LIST = "text/uri-list"
VSCODE_EDITOR_DROP = "vscode-editor-drop"
VSCODE_FILE_LIST = "code/file-list"  # Format thực tế VSCode dùng khi copy file
ATOM_URI_LIST = "atom-uri-list"

# --- Cấu trúc dữ liệu DROPFILES cho Windows Clipboard ---
class DROPFILES(ctypes.Structure):
    _fields_ = [
        ("pFiles", wintypes.DWORD),
        ("pt", wintypes.POINT),
        ("fNC", wintypes.BOOL),
        ("fWide", wintypes.BOOL),
    ]

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class VSCodeBridgeApp:
    def __init__(self):
        self.is_running = False
        self.root = tk.Tk()
        self.root.title("VS Code File Bridge")
        self.root.geometry("300x150")
        self.root.resizable(False, False)
        
        # Xử lý đóng cửa sổ -> thu xuống tray (ẩn window)
        self.root.protocol('WM_DELETE_WINDOW', self.hide_window)

        self.setup_ui()
        
        # Tray icon logic variables
        self.tray_icon = None
        self.tray_thread = None
        
        # Setup tray icon in a separate thread
        self.setup_tray_thread()
        
        # Biến lưu nội dung clipboard gần nhất để tránh lặp
        self.last_clipboard_text = ""

    def setup_ui(self):
        # Frame chính
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Label trạng thái
        self.status_label = ttk.Label(main_frame, text="Trạng thái: Đang dừng", foreground="red", font=("Helvetica", 10, "bold"))
        self.status_label.pack(pady=10)

        # Nút Bật/Tắt
        self.toggle_btn = ttk.Button(main_frame, text="Bật Tool", command=self.toggle_monitoring)
        self.toggle_btn.pack(pady=5, fill=tk.X)

        # Hướng dẫn
        note = ttk.Label(main_frame, text="Hướng dẫn: Chọn file trong VS Code -> Ctrl+C -> Paste vào nơi cần.", font=("Helvetica", 8), wraplength=260, justify="center")
        note.pack(pady=10)
        
        # Thêm icon cho window (title bar)
        icon_path = get_resource_path("icon.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

    def create_tray_image(self):
        # Ưu tiên load icon từ file
        icon_path = get_resource_path("icon.png")
        if os.path.exists(icon_path):
            try:
                return Image.open(icon_path)
            except Exception as e:
                logger.error(f"Cannot load icon.png: {e}")
        
        # Fallback: Tạo icon màu xanh
        width = 64
        height = 64
        color1 = "blue"
        color2 = "white"
        image = Image.new('RGB', (width, height), color1)
        d = ImageDraw.Draw(image)
        d.rectangle((16, 16, 48, 48), fill=color2)
        return image

    def setup_tray_thread(self):
        """Khởi tạo và chạy tray icon trong một thread riêng biệt"""
        self.tray_thread = threading.Thread(target=self._run_tray_icon, daemon=True)
        self.tray_thread.start()

    def _run_tray_icon(self):
        menu = (
             pystray.MenuItem('Hiện giao diện', self.show_window_from_tray),
             pystray.MenuItem('Thoát', self.quit_app_from_tray)
        )
        self.tray_icon = pystray.Icon("VSCodeBridge", self.create_tray_image(), "VS Code Bridge", menu)
        # Mouse click listener to show window on left click
        self.tray_icon.run()

    def show_window_from_tray(self, icon=None, item=None):
        # Hàm này được gọi từ thread của pystray, cần schedule update GUI trên main thread
        self.root.after(0, self.deiconify_window)

    def deiconify_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def quit_app_from_tray(self, icon=None, item=None):
        # Dừng icon
        if self.tray_icon:
            self.tray_icon.stop()
        # Schedule thoát GUI trên main thread
        self.root.after(0, self.destroy_app)

    def destroy_app(self):
        self.is_running = False
        self.root.destroy()
        sys.exit()

    def hide_window(self):
        """Ẩn cửa sổ chính, app vẫn chạy dưới background (tray)"""
        self.root.withdraw()
        # Có thể hiện thông báo notification ở đây nếu muốn
        
    def toggle_monitoring(self):
        if not self.is_running:
            self.is_running = True
            self.status_label.config(text="Trạng thái: Đang chạy ngầm", foreground="green")
            self.toggle_btn.config(text="Dừng Tool")
            
            # Chạy thread monitor
            self.monitor_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
            self.monitor_thread.start()
        else:
            self.is_running = False
            self.status_label.config(text="Trạng thái: Đang dừng", foreground="red")
            self.toggle_btn.config(text="Bật Tool")

    def clean_path(self, raw_path):
        """Làm sạch đường dẫn từ VS Code (loại bỏ file://, decode URL)"""
        # Loại bỏ quotes nếu có
        raw_path = raw_path.strip().strip('"').strip("'")
        
        # Decode URL (ví dụ %20 -> space, %3A -> :)
        decoded_path = urllib.parse.unquote(raw_path)
        
        # Xử lý prefix file:///
        if decoded_path.startswith("file:///"):
            decoded_path = decoded_path[8:]
        elif decoded_path.startswith("file://"):
            decoded_path = decoded_path[7:]
            
        # Chuẩn hóa đường dẫn Windows (/) -> (\)
        decoded_path = os.path.normpath(decoded_path)
        return decoded_path

    def text_to_files(self, text):
        """Kiểm tra xem text có phải là đường dẫn file hợp lệ không"""
        if not text:
            return None
        
        # VS Code có thể copy nhiều file, phân tách bằng xuống dòng
        lines = text.splitlines()
        valid_files = []
        
        for line in lines:
            cleaned = self.clean_path(line)
            if os.path.exists(cleaned):
                valid_files.append(cleaned)
        
        return valid_files if valid_files else None

    def set_clipboard_files(self, file_list):
        """Ghi đè Clipboard bằng cấu trúc CF_HDROP (File Drop)"""
        # Chuẩn bị buffer cho DropFiles
        offset = ctypes.sizeof(DROPFILES)
        length = sum(len(f) + 1 for f in file_list) + 1
        size = offset + length * ctypes.sizeof(wintypes.WCHAR)
        
        buf = (ctypes.c_char * size)()
        df = DROPFILES.from_buffer(buf)
        df.pFiles = offset
        df.fWide = True # Unicode
        
        # Ghi danh sách file vào buffer
        current_offset = offset
        for f in file_list:
            array_t = ctypes.c_wchar * (len(f) + 1)
            path_buf = array_t.from_buffer(buf, current_offset)
            path_buf.value = f
            current_offset += ctypes.sizeof(path_buf)
            
        # Null terminator cuối cùng
        buf[current_offset] = b'\0'
        buf[current_offset+1] = b'\0'

        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_HDROP, buf)
            win32clipboard.CloseClipboard()
            logger.info(f"Converted {len(file_list)} paths to file objects in clipboard.")
        except Exception as e:
            logger.error(f"Error writing to clipboard: {e}")

    def get_registered_format_id(self, format_name):
        """Đăng ký hoặc lấy ID của custom clipboard format"""
        return ctypes.windll.user32.RegisterClipboardFormatW(format_name)
    
    def get_custom_format_data(self, format_name):
        """Đọc dữ liệu từ custom clipboard format"""
        try:
            format_id = self.get_registered_format_id(format_name)
            if win32clipboard.IsClipboardFormatAvailable(format_id):
                data = win32clipboard.GetClipboardData(format_id)
                if isinstance(data, bytes):
                    # Thử decode với nhiều encoding
                    for encoding in ['utf-8', 'utf-16', 'latin-1']:
                        try:
                            return data.decode(encoding)
                        except:
                            continue
                return data
        except Exception as e:
            if DEBUG:
                logger.debug(f"Error reading {format_name}: {e}")
        return None
    
    def extract_file_paths_from_clipboard(self):
        """
        Trích xuất đường dẫn file từ clipboard với nhiều format khác nhau.
        Trả về (file_list, source_format) hoặc (None, None) nếu không tìm thấy.
        """
        # Kiểm tra xem clipboard đã có CF_HDROP chưa (đã là file object)
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
            # Nếu đã có file drop, không cần làm gì thêm
            return None, None
        
        # 1. Thử đọc code/file-list (format thực tế VSCode dùng khi copy file)
        vscode_file_list_data = self.get_custom_format_data(VSCODE_FILE_LIST)
        if vscode_file_list_data:
            file_list = self.text_to_files(vscode_file_list_data)
            if file_list:
                return file_list, VSCODE_FILE_LIST
        
        # 2. Thử đọc text/uri-list (format phổ biến cho Electron apps)
        uri_list_data = self.get_custom_format_data(ELECTRON_URI_LIST)
        if uri_list_data:
            file_list = self.text_to_files(uri_list_data)
            if file_list:
                return file_list, ELECTRON_URI_LIST
        
        # 3. Thử đọc vscode-editor-drop  
        vscode_data = self.get_custom_format_data(VSCODE_EDITOR_DROP)
        if vscode_data:
            file_list = self.text_to_files(vscode_data)
            if file_list:
                return file_list, VSCODE_EDITOR_DROP
        
        # 4. Thử đọc atom-uri-list
        atom_data = self.get_custom_format_data(ATOM_URI_LIST)
        if atom_data:
            file_list = self.text_to_files(atom_data)
            if file_list:
                return file_list, ATOM_URI_LIST
        
        # 5. Fallback: đọc CF_UNICODETEXT
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            text_data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            if text_data:
                # Chỉ xử lý nếu text chứa file:// URI hoặc đường dẫn tuyệt đối
                if 'file://' in text_data or (len(text_data) > 2 and text_data[1] == ':'):
                    file_list = self.text_to_files(text_data)
                    if file_list:
                        return file_list, 'CF_UNICODETEXT'
        
        return None, None

    def monitor_clipboard(self):
        """Vòng lặp chính theo dõi clipboard"""
        logger.info("Started clipboard monitoring...")
        
        while self.is_running:
            try:
                win32clipboard.OpenClipboard()
                
                # Trích xuất file paths từ clipboard
                file_list, source_format = self.extract_file_paths_from_clipboard()
                
                win32clipboard.CloseClipboard()
                
                if file_list:
                    # Tạo key để tránh xử lý lặp lại cùng một clipboard content
                    files_key = "|".join(sorted(file_list))
                    
                    # Chỉ xử lý nếu nội dung file thay đổi so với lần xử lý trước
                    if files_key != self.last_clipboard_text:
                        self.last_clipboard_text = files_key
                        
                        logger.info(f"Detected {len(file_list)} files from {source_format}")
                        
                        # Đợi một chút rồi ghi đè clipboard
                        time.sleep(0.1)
                        self.set_clipboard_files(file_list)
                        
                        # Reset để tránh trigger lại khi đã convert xong
                        # Tuy nhiên khi convert xong, clipboard sẽ có CF_HDROP, 
                        # nên vòng logic ở đầu hàm extract sẽ tự bỏ qua.
                        # Dòng này chỉ để đảm bảo logic so sánh chuỗi.
                        self.last_clipboard_text = files_key + "_converted"
                    
            except Exception as e:
                # Chỉ log error nếu thực sự nghiêm trọng, tránh spam
                if DEBUG:
                    logger.error(f"Error in monitor loop: {e}")
                try:
                    win32clipboard.CloseClipboard()
                except:
                    pass
            
            time.sleep(0.5)  # Tăng thời gian sleep lên 0.5s để giảm tải CPU

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = VSCodeBridgeApp()
    app.run()
