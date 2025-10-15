"""Module for processing and converting captured states into log entries."""
import re
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s [%(levelname)s] %(message)s',
                   datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

def parse_browser_window_title(window_title):
    """
    Parse browser window titles to extract meaningful information.
    Returns tuple of (page_title, domain, is_browser_tab)
    """
    # Default values
    page_title = window_title
    domain = None
    url = None
    is_browser_tab = False
    
    # Extract browser type and remove it from title
    browser_type = None
    if ' - Google Chrome' in window_title:
        browser_type = 'chrome'
        page_title = window_title.replace(' - Google Chrome', '')
    elif ' - Microsoft Edge' in window_title:
        browser_type = 'edge'
        page_title = window_title.replace(' - Microsoft Edge', '')
    elif ' - Firefox' in window_title:
        browser_type = 'firefox'
        page_title = window_title.replace(' - Firefox', '')
    elif ' - Brave' in window_title:
        browser_type = 'brave'
        page_title = window_title.replace(' - Brave', '')
    
    # Special case for "Google Chrome" empty window
    if window_title == "Google Chrome":
        return ("New Tab", "chrome://newtab", True)
    
    # Check if it's likely a browser tab
    is_browser_tab = (
        browser_type is not None and 
        (
            'google search' in window_title.lower() or
            'google.com' in window_title.lower() or
            'github' in window_title.lower() or
            'mail' in window_title.lower() or
            'outlook' in window_title.lower() or
            'youtube' in window_title.lower() or
            'wikipedia' in window_title.lower() or
            'whatsapp' in window_title.lower() or  # Common web app
            'facebook' in window_title.lower() or  # Common web app
            'twitter' in window_title.lower() or   # Common web app
            'linkedin' in window_title.lower() or  # Common web app
            'instagram' in window_title.lower() or # Common web app
            '·' in window_title or  # Common in GitHub/website titles
            '@' in window_title or  # Email addresses
            'inbox' in window_title.lower() or
            'http' in window_title.lower() or
            'www.' in window_title.lower() or
            'chrome://' in window_title.lower() or
            'edge://' in window_title.lower() or
            'about:' in window_title.lower() or
            'file:///' in window_title.lower() or
            # More generous pattern matching - windows with numbers in parentheses
            # often indicate notifications in web apps like WhatsApp, Discord, etc.
            (browser_type == 'chrome' and re.search(r'\(\d+\)', window_title))
        )
    )
    
    # Try to extract URL if present
    url_match = re.search(r'https?://[^\s]+', window_title)
    if url_match:
        url = url_match.group(0)
        domain = url.split('//')[1].split('/')[0]
    else:
        # Try to determine domain from common patterns
        if 'google search' in window_title.lower():
            domain = 'google.com'
        elif 'github' in window_title.lower():
            domain = 'github.com'
        elif 'mail' in window_title.lower() and 'google' in window_title.lower():
            domain = 'mail.google.com'
        elif 'youtube' in window_title.lower():
            domain = 'youtube.com'
        elif 'outlook' in window_title.lower():
            domain = 'outlook.com'
    
    # For Gmail and similar services, try to extract more meaningful information
    if 'inbox' in window_title.lower() and '@' in window_title:
        # Try to extract email address
        email_match = re.search(r'[\w\.-]+@[\w\.-]+', window_title)
        if email_match:
            email = email_match.group(0)
            page_title = f"Inbox - {email}"
    
    # For GitHub, try to extract repo/page info
    if 'github' in window_title.lower():
        # Handle common GitHub patterns like "Repo - User/Repo - GitHub"
        github_match = re.search(r'^(.*?)\s+·\s+(.*?)\s+-\s+GitHub', window_title)
        if github_match:
            page = github_match.group(1)
            repo = github_match.group(2)
            page_title = f"{page} - {repo}"
    
    # Try to extract the actual title for Google Search results
    if 'google search' in window_title.lower():
        search_match = re.search(r'^(.*?)\s+-\s+Google\s+Search', window_title, re.IGNORECASE)
        if search_match:
            search_term = search_match.group(1).strip()
            page_title = f"Google Search: {search_term}"
    
    # Construct URL from domain if we have one but no URL
    if domain and not url:
        url = f"https://{domain}"
    
    return (page_title, url, is_browser_tab)

def read_state_file(state_path):
    """Read the state file from disk"""
    try:
        with open(state_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading state file: {e}")
        return {}

def state_to_logs(state: dict) -> list:
    """Enhanced conversion of state -> list of detailed log dicts for indexing."""
    logs = []
    
    # Process browser states from dedicated browsers section (DevTools Protocol)
    browsers = state.get('browsers') or []
    browser_tabs_detected = len(browsers) > 0
    
    if isinstance(browsers, dict):
        browser_iter = browsers.items()
    else:
        browser_iter = enumerate(browsers)

    for b, info in browser_iter:
        browser_name = info.get('browser') if isinstance(info, dict) else b
        windows = info.get('windows') if isinstance(info, dict) else (info or [])
        
        for w in windows or []:
            for t in (w.get('tabs') or []):
                log_entry = {
                    'event_type': 'browser_tab',
                    'summary': t.get('title') or t.get('url') or '',
                    'url': t.get('url'),
                    'app_name': browser_name,
                    'window_info': {
                        'profile': w.get('profile'),
                        'debugging_port': w.get('debuggingPort')
                    },
                    'tab_info': {
                        'active': t.get('active', False),
                        'favicon': t.get('favicon', ''),
                        'description': t.get('description', '')
                    },
                    'capture_method': 'devtools_protocol'
                }
                logs.append(log_entry)

    # Process application states
    for app in state.get('apps') or []:
        name = app.get('name') or app.get('exe') or 'unknown'
        windows = app.get('windows') or []
        items = app.get('items') or []
        files = app.get('files') or []
        
        # Generate standard app state log
        log_entry = {
            'event_type': 'app_state',
            'summary': f"App {name} - {len(windows)} windows, {len(items)} items, {len(files)} files",
            'app_name': name,
            'app_info': {
                'exe_path': app.get('exe'),
                'pid': app.get('pid'),
                'window_count': len(windows),
                'item_count': len(items),
                'file_count': len(files),
                'captured_at': app.get('captured_at')
            }
        }
        logs.append(log_entry)
        
        # Extract browser tabs from window titles (even if browser tabs were detected via DevTools)
        # This gives us a complete view combining both methods
        is_browser_app = (
            name.lower().endswith('.exe') and 
            any(browser_name in name.lower() for browser_name in ['chrome', 'firefox', 'edge', 'opera', 'brave'])
        )
        
        if is_browser_app:
            browser_name = None
            if 'chrome' in name.lower():
                browser_name = 'chrome'
            elif 'edge' in name.lower():
                browser_name = 'edge'
            elif 'firefox' in name.lower():
                browser_name = 'firefox'
            elif 'opera' in name.lower():
                browser_name = 'opera'
            elif 'brave' in name.lower():
                browser_name = 'brave'
                
            # Process all windows in this browser application
            tab_count = 0
            for window in windows:
                window_title = window.get('title', '')
                page_title, url, is_browser_tab = parse_browser_window_title(window_title)
                
                if is_browser_tab:
                    tab_count += 1
                    browser_tab_entry = {
                        'event_type': 'browser_tab',
                        'summary': page_title,
                        'url': url or 'unknown_url',
                        'domain': url.split('//')[1].split('/')[0] if url and '//' in url else None,
                        'app_name': name,
                        'browser_name': browser_name,
                        'window_info': {
                            'hwnd': window.get('hwnd'),
                            'is_foreground': window.get('is_foreground', False),
                            'position': window.get('position'),
                            'size': window.get('size'),
                            'state': window.get('state')
                        },
                        'tab_info': {
                            'active': window.get('is_foreground', False),
                            'title': page_title,
                            'window_title': window_title
                        },
                        'capture_method': 'window_title'
                    }
                    logs.append(browser_tab_entry)
            
            # Add summary log for this browser
            if tab_count > 0:
                browser_summary_entry = {
                    'event_type': 'browser_summary',
                    'summary': f"{browser_name.capitalize()} browser with {tab_count} tabs",
                    'app_name': name,
                    'browser_name': browser_name,
                    'tab_count': tab_count,
                    'capture_method': 'window_title'
                }
                logs.append(browser_summary_entry)
    
    # Add timestamp info
    for log in logs:
        log['saved_at'] = state.get('saved_at')
        
    logger.info(f"Processed state with {len(logs)} log entries")
    return logs

def process_state_file(state_path=None):
    """Process a state file and return logs"""
    if not state_path:
        # Try to find state in default location
        state_path = os.path.join(os.environ.get('STATE_DIR', ''), 'state.json')
        if not os.path.exists(state_path):
            # Try relative path
            state_path = os.path.join('..', 'State', 'state.json')
            if not os.path.exists(state_path):
                logger.error("No state file found")
                return []
    
    logger.info(f"Processing state file: {state_path}")
    state = read_state_file(state_path)
    if not state:
        logger.error("Failed to read state file or empty state")
        return []
        
    return state_to_logs(state)
        
    return logs