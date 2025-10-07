import os
import sys
import json
import datetime
import requests
import psutil
import win32com.client
import win32process
import win32gui

OUT_FILE = r"D:\Major\Restoration_engine\state.json"
CHROME_PORT = 9222
EDGE_PORT = 9223
USE_HANDLE = True  # Not implemented, placeholder

def get_devtools_tabs(base_url):
    try:
        resp = requests.get(f"{base_url}/json", timeout=10)
        tabs = resp.json()
        by_window = {}
        for tab in tabs:
            wid = tab.get("id")
            if wid not in by_window:
                by_window[wid] = []
            by_window[wid].append({
                "url": tab.get("url"),
                "title": tab.get("title"),
                "active": tab.get("active"),
                "pinned": tab.get("pinned")
            })
        windows = []
        for wid, tabs in by_window.items():
            windows.append({
                "windowId": wid,
                "tabs": tabs
            })
        return windows
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

def get_main_window_title(pid):
    def callback(hwnd, titles):
        try:
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid and win32gui.IsWindowVisible(hwnd):
                titles.append(win32gui.GetWindowText(hwnd))
        except Exception:
            pass
        return True
    titles = []
    win32gui.EnumWindows(lambda hwnd, _: callback(hwnd, titles), None)
    return titles[0] if titles else None

whitelist = [
    "WINWORD.EXE","EXCEL.EXE","POWERPNT.EXE","VISIO.EXE", "MSPUB.EXE","MSACCESS.EXE","WINPROJ.EXE","ONENOTE.EXE",
    "notepad.exe","notepad++.exe",
    "code.exe","Code.exe","devenv.exe","sublime_text.exe","Acrobat.exe","AcroRd32.exe",
    "vlc.exe","obs64.exe","photoshop.exe","idea64.exe","pycharm64.exe","chrome.exe","msedge.exe","firefox.exe"
]

apps = []
for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
    name = proc.info['name']
    if name not in whitelist:
        continue
    if name in ["chrome.exe", "msedge.exe", "firefox.exe"]:
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
    #     "mainWindow": main_window
    # })

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

for app, func in office_apps.items():
    if any(a["name"] == app for a in apps):
        continue
    files = func()
    if files:
        exe_path = next((proc.info['exe'] for proc in psutil.process_iter(['name', 'exe']) if proc.info['name'] == app), None)
        apps.append({
            "name": app,
            "pid": None,
            "exe": exe_path,
            "cmdline": None,
            "files": list(set(files)),
            "mainWindow": None
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
#         "mainWindow": None
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
#         "mainWindow": None
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
#         "mainWindow": None
#     })

browsers = []
chrome = get_chrome_state(CHROME_PORT)
if chrome:
    browsers.append(chrome)
edge = get_edge_state(EDGE_PORT)
if edge:
    browsers.append(edge)

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