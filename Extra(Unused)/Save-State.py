import os
import sys
import json
import datetime
import requests
import psutil
import win32com.client
import win32process
import win32gui

OUT_FILE = r"D:\\Major\\Restoration_engine\\state.json"
BROWSER_PORTS_FILE = r"D:\\Major\\IntelliOS\\Restoration_engine\\browser_ports.json"
USE_HANDLE = True  # Not implemented, placeholder

def get_devtools_tabs(base_url):
    try:
        resp = requests.get(f"{base_url}/json", timeout=10)
        tabs = resp.json()
        formatted_tabs = []
        for tab in tabs:
            if (tab.get('url') and 
                any(tab['url'].startswith(prefix) for prefix in ['https://', 'http://', 'file://', 'chrome://', 'edge://']) and
                not any(tab.get('title', '').startswith(prefix) for prefix in ['https://', 'http://']) and tab.get('type') == 'page'):
                formatted_tabs.append({
                    "url": tab.get("url"),
                    "title": tab.get("title"),
                    "description": tab.get("description", "")
                })
        return formatted_tabs
    except Exception:
        return []

def get_chrome_state(port):
    wins = get_devtools_tabs(f"http://localhost:{port}")
    if wins:
        return {"browser": "chrome", "port": port, "windows": wins}

def get_edge_state(port):
    wins = get_devtools_tabs(f"http://localhost:{port}")
    if wins:
        return {"browser": "edge", "port": port, "windows": wins}

def get_word_docs():
    try:
        word = win32com.client.GetActiveObject("Word.Application")
        return [doc.FullName for doc in word.Documents]
    except Exception:
        return []

def get_excel_books():
    try:
        xl = win32com.client.GetActiveObject("Excel.Application")
        return [wb.FullName for wb in xl.Workbooks]
    except Exception:
        return []

def get_powerpoint_pres():
    try:
        pp = win32com.client.GetActiveObject("PowerPoint.Application")
        return [pres.FullName for pres in pp.Presentations]
    except Exception:
        return []
    
def get_visio_drawings():
    try:
        visio = win32com.client.GetActiveObject("Visio.Application")
        return [doc.FullName for doc in visio.Documents]
    except Exception:
        return []

def get_publisher_docs():
    try:
        pub = win32com.client.GetActiveObject("Publisher.Application")
        return [doc.FullName for doc in pub.Documents]
    except Exception:
        return []

def get_project_files():
    try:
        proj = win32com.client.GetActiveObject("MSProject.Application")
        return [proj.FullName for proj in proj.Projects]
    except Exception:
        return []

def get_access_dbs():
    try:
        access = win32com.client.GetActiveObject("Access.Application")
        return [access.CurrentProject.FullName] if access.CurrentProject else []
    except Exception:
        return []

def get_onenote_files():
    try:
        onenote = win32com.client.GetActiveObject("OneNote.Application")
        hierarchy = onenote.GetHierarchy("", 3)  # 3 = hsPages
        return [page.Path for page in hierarchy.PageNodes]
    except Exception:
        return []

def get_file_args_from_commandline(cmd):
    if not cmd:
        return []
    import re
    candidates = []
    quoted = re.findall(r'"([^"]+)"', cmd)
    candidates.extend(quoted)
    parts = cmd.split()
    for p in parts:
        if re.match(r'^[A-Za-z]:\\', p) or re.match(r'^\\\\', p):
            candidates.append(p.strip('"'))
        if p.startswith("file:///"):
            from urllib.parse import unquote
            decoded = unquote(p).replace("file:/", "")
            candidates.append(decoded)
    files = []
    for c in candidates:
        norm = c.strip().strip('"')
        if os.path.isfile(norm):
            files.append(norm)
    return list(set(files))

def get_main_window_info(pid):
    def callback(hwnd, window_info):
        try:
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid and win32gui.IsWindowVisible(hwnd):
                # Get window title
                title = win32gui.GetWindowText(hwnd)
                
                # Get window rect (position and size)
                rect = win32gui.GetWindowRect(hwnd)
                left, top, right, bottom = rect
                
                # Get window state
                style = win32gui.GetWindowLong(hwnd, -16)  # GWL_STYLE
                state = "minimized" if style & 0x20000000 else "maximized" if style & 0x01000000 else "normal"
                
                window_info.append({
                    "title": title,
                    "position": {
                        "x": left,
                        "y": top
                    },
                    "size": {
                        "width": right - left,
                        "height": bottom - top
                    },
                    "state": state
                })
        except Exception:
            pass
        return True
    
    window_info = []
    win32gui.EnumWindows(lambda hwnd, _: callback(hwnd, window_info), None)
    return window_info[0] if window_info else None

whitelist = [
    "WINWORD.EXE","EXCEL.EXE","POWERPNT.EXE","VISIO.EXE", "MSPUB.EXE","MSACCESS.EXE","WINPROJ.EXE","ONENOTE.EXE",
    "notepad.exe","notepad++.exe",
    "code.exe","Code.exe","devenv.exe","sublime_text.exe","Acrobat.exe","AcroRd32.exe",
    "vlc.exe","obs64.exe","photoshop.exe","idea64.exe","pycharm64.exe"
]

office_apps = {
    "WINWORD.EXE": get_word_docs,
    "EXCEL.EXE": get_excel_books,
    "POWERPNT.EXE": get_powerpoint_pres,
    "VISIO.EXE": get_visio_drawings,
    "MSPUB.EXE": get_publisher_docs,
    "MSACCESS.EXE": get_access_dbs,
    "WINPROJ.EXE": get_project_files,
    "ONENOTE.EXE": get_onenote_files
}

apps = []
for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
    name = proc.info['name']
    if name not in whitelist:
        continue
    
    # files = []
    # cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
    # files += get_file_args_from_commandline(cmdline)
    # # USE_HANDLE not implemented
    # files = list(set(files))
    # main_window = get_main_window_title(proc.info['pid'])
    # apps.append({
    #     "name": name,
    #     "pid": proc.info['pid'],
    #     "exe": proc.info['exe'],
    #     "cmdline": cmdline,
    #     "files": files,
    #     "windowInfo": main_window
    # })

    if name in office_apps.keys():
        files = office_apps[name]()
        if files:
            apps.append({
                "name": name,
                "pid": proc.info['pid'],
                "exe": proc.info['exe'],
                "cmdline": ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else '',
                "files": list(set(files)),
                "windowInfo": get_main_window_info(proc.info['pid'])
            })

# Office COM
# word_docs = get_word_docs()
# if word_docs:
#     word_exe = next((proc.info['exe'] for proc in psutil.process_iter(['name', 'exe']) if proc.info['name'] == "WINWORD.EXE"), None)
#     apps.append({
#         "name": "WINWORD.EXE",
#         "pid": None,
#         "exe": word_exe,
#         "cmdline": None,
#         "files": list(set(word_docs)),
#         "windowInfo": None
#     })
# xl_books = get_excel_books()
# if xl_books:
#     xl_exe = next((proc.info['exe'] for proc in psutil.process_iter(['name', 'exe']) if proc.info['name'] == "EXCEL.EXE"), None)
#     apps.append({
#         "name": "EXCEL.EXE",
#         "pid": None,
#         "exe": xl_exe,
#         "cmdline": None,
#         "files": list(set(xl_books)),
#         "windowInfo": None
#     })
# pp_pres = get_powerpoint_pres()
# if pp_pres:
#     pp_exe = next((proc.info['exe'] for proc in psutil.process_iter(['name', 'exe']) if proc.info['name'] == "POWERPNT.EXE"), None)
#     apps.append({
#         "name": "POWERPNT.EXE",
#         "pid": None,
#         "exe": pp_exe,
#         "cmdline": None,
#         "files": list(set(pp_pres)),
#         "windowInfo": None
#     })

def get_browser_states():
    try:
        with open(BROWSER_PORTS_FILE, 'r') as f:
            browser_data = json.load(f)
    except Exception as e:
        print(f"Error reading browser ports file: {e}")
        return []

    browsers = []
    
    # Process all browser types
    for browser_name, browser_info in browser_data.items():
        browser_windows = []
        browser_exe = browser_info.get("exe")
        
        # Process all profiles for this browser
        for profile_info in browser_info.get("profiles", []):
            # Handle both profile name formats
            profile_path = profile_info.get("profile") or profile_info.get("user_data_dir")
            if not profile_path:
                continue
            
            # Process all instances of this profile
            for instance in profile_info.get("instances", []):
                if instance.get("status") == "active":
                    port = instance["port"]
                    tabs = get_devtools_tabs(f"http://localhost:{port}")
                    
                    if tabs:
                        window = {
                            "profile": profile_path,
                            "debuggingPort": int(port),
                            "tabs": tabs
                        }
                        browser_windows.append(window)
        
        # Add browser to list if it has active windows
        if browser_windows:
            browsers.append({
                "browser": browser_name,  
                "exe": browser_exe,
                "windows": browser_windows
            })
    
    return browsers

browsers = get_browser_states()

state = {
    "saved_at": datetime.datetime.now().isoformat(),
    "user": os.environ.get("USERNAME", ""),
    "browsers": browsers,
    "apps": sorted(apps, key=lambda x: x["name"])
}

os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(state, f, indent=2, ensure_ascii=False)
print(f"State saved to {OUT_FILE}")