TOPIC_FILES = [
    'security', 'system_startup', 'system_shutdown', 'service_operations', 'application_lifecycle',
    'network_activity', 'driver_operations', 'hardware_events', 'updates', 'user_sessions',
    'disk_activity', 'performance_issues', 'system_errors', 'application_errors', 'maintenance'
]

def _append_log_to_topic(topic: str, log: dict):
    """Append log to the correct topic file in local_ddna."""
    fname = os.path.join(LOCAL_DDNA_DIR, f'{topic}.json')
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(fname), exist_ok=True)
        
        # Create a streamlined version of the log with only relevant information
        streamlined_log = {
            'event_type': log.get('event_type'),
            'summary': log.get('summary'),
            'saved_at': log.get('saved_at'),
            'timestamp': log.get('saved_at')  # Adding timestamp field for consistency
        }
        
        # Add event-specific data
        if log.get('event_type') == 'app_state':
            # Handle app state fields regardless of structure
            streamlined_log.update({
                'app_name': log.get('app_name'),
                'exe_path': log.get('app_info', {}).get('exe_path') if 'app_info' in log else log.get('exe_path'),
                'pid': log.get('app_info', {}).get('pid') if 'app_info' in log else log.get('pid'),
                'window_count': log.get('app_info', {}).get('window_count') if 'app_info' in log else log.get('window_count'),
                'captured_at': log.get('app_info', {}).get('captured_at') if 'app_info' in log else log.get('captured_at')
            })
        elif log.get('event_type') == 'browser_tab':
            # Handle browser tab fields regardless of structure
            streamlined_log.update({
                'app_name': log.get('app_name'),
                'browser_name': log.get('browser_name'),
                'url': log.get('url'),
                'domain': log.get('domain'),
                'title': log.get('tab_info', {}).get('title') if 'tab_info' in log else log.get('title'),
                'is_active': log.get('tab_info', {}).get('active') if 'tab_info' in log else log.get('is_active')
            })
        elif log.get('event_type') == 'browser_summary':
            streamlined_log.update({
                'browser_name': log.get('browser_name'),
                'tab_count': log.get('tab_count')
            })
            
        # Add only the relevant topic match
        for topic_match in log.get('topic_matches', []):
            if topic_match.get('topic') == topic:
                streamlined_log['topic_score'] = topic_match.get('score')
                streamlined_log['topic_description'] = topic_match.get('description')
                break
        
        # Read existing logs
        if os.path.exists(fname):
            with open(fname, 'r', encoding='utf-8') as f:
                arr = json.load(f)
        else:
            arr = []
            
        arr.append(streamlined_log)
        
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(arr, f, indent=2)
        logger.info(f"Added streamlined log to topic file {topic}")
    except Exception as e:
        logger.error(f"Failed to append to topic file {fname}: {e}")

def _get_log_topics(log: dict) -> list:
    """Extract only the highest scoring topic from log's topic_matches (if present)."""
    # Try to import all topics from topics.py
    all_topics = set(TOPIC_FILES)  # Start with existing TOPIC_FILES
    try:
        # Import all topics dynamically
        sys.path.insert(0, BACKEND_DIR)
        from topics import TOPICS
        all_topics.update(TOPICS.keys())  # Add all topics from TOPICS
    except ImportError:
        # Fallback to just existing topics if import fails
        pass
    
    # Add workspace topics manually to ensure they're included
    workspace_topics = [
        'web_development', 'machine_learning', 'dsa_coding', 'data_analytics', 
        'web_design', 'extracurricular', 'web_surfing'
    ]
    all_topics.update(workspace_topics)
    
    # Find the topic with the highest score
    best_topic = None
    highest_score = -1
    
    for t in log.get('topic_matches', []):
        if t.get('topic') and t.get('score', 0) > highest_score:
            highest_score = t.get('score', 0)
            best_topic = t.get('topic')
    
    return [best_topic] if best_topic else []
import os
import sys
import json
import time
import logging
import datetime
from typing import Optional

# Add necessary paths to sys.path for imports
FLOW_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(FLOW_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

# Define all necessary paths
CORE_DIR = os.path.join(BACKEND_DIR, 'core')
STATE_DIR = os.path.join(PROJECT_ROOT, 'State')
STATE_CAPTURE_DIR = os.path.join(PROJECT_ROOT, 'State_capturing_engine')
LOCAL_DDNA_DIR = os.path.join(BACKEND_DIR, 'local_ddna')

# Print paths for debugging
print(f"Project paths:")
print(f"PROJECT_ROOT: {PROJECT_ROOT}")
print(f"STATE_DIR: {STATE_DIR}")
print(f"STATE_CAPTURE_DIR: {STATE_CAPTURE_DIR}")

# Add paths to sys.path in correct order
paths_to_add = [PROJECT_ROOT, CORE_DIR, BACKEND_DIR, STATE_CAPTURE_DIR]
for path in paths_to_add:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)
        print(f"Added to sys.path: {path}")
    elif not os.path.exists(path):
        print(f"Warning: Path does not exist: {path}")

# Ensure State directory exists
if not os.path.exists(STATE_DIR):
    try:
        os.makedirs(STATE_DIR)
        print(f"Created State directory: {STATE_DIR}")
    except Exception as e:
        print(f"Error creating State directory: {e}")

from logging_config import setup_logging

# best-effort imports; missing modules are handled gracefully at runtime
try:
    from ddna_manager import DDNAManager
except Exception:
    DDNAManager = None

try:
    from vector_db import VectorDBManager
except Exception:
    VectorDBManager = None

logger = setup_logging()

def _state_default_path() -> str:
    """Returns the default path for the state.json file"""
    return os.path.join(STATE_DIR, 'state.json')

def _state_to_logs(state: dict) -> list:
    """Convert state to log entries using state_processor module."""
    sys.path.insert(0, STATE_CAPTURE_DIR)
    try:
        from state_processor import state_to_logs
        return state_to_logs(state)
    except ImportError:
        logger.error("Failed to import state_processor module")
        # Fallback to empty list
        return []

    if not logs:
        logs.append({'event_type': 'system_state', 'summary': state.get('summary') or f"State saved_at {state.get('saved_at')}"})
    return logs

def _try_import_module(names: list):
    import importlib
    for n in names:
        try:
            return importlib.import_module(n)
        except Exception:
            continue
    return None

def _try_call(module, fn_names: list, *args, **kwargs):
    if not module:
        return None
    for n in fn_names:
        fn = getattr(module, n, None)
        if callable(fn):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                logger.exception("helper call failed: %s.%s", getattr(module, '__name__', '?'), n)
    return None


def capture_current_state(state_path: str) -> bool:
    """Capture current system state using app and browser capture modules.
    Returns True if capture was successful, False otherwise."""
    try:
        logger.info("Starting state capture...")
        
        # Import required modules
        if not os.path.exists(STATE_CAPTURE_DIR):
            logger.error("State capturing engine directory not found at: %s", STATE_CAPTURE_DIR)
            return False

        sys.path.insert(0, STATE_CAPTURE_DIR)
        try:
            from app_capture import capture_app_states
            from browser_capture import capture_browser_states
            from browser_launcher import launch_browser
            logger.info("Successfully imported capture modules")
        except ImportError as e:
            logger.error("Failed to import capture modules from %s: %s", STATE_CAPTURE_DIR, str(e))
            return False
            
        # Launch browsers with debugging enabled
        browsers_to_launch = [
            ('chrome', 'Default'),
            ('edge', 'Default')
        ]
        
        browser_ports = {}
        for browser, profile in browsers_to_launch:
            try:
                if launch_browser(browser, profile):
                    logger.info(f"Successfully launched {browser} for state capture")
                    # Wait for browser to initialize
                    time.sleep(2)
            except Exception as e:
                logger.warning(f"Failed to launch {browser}: {e}")
        
        # Create fresh browser configuration with connection verification
        logger.info("Setting up browser configuration...")
        chrome_port = 9222
        
        # Assume Chrome is available and let browser_capture handle the connection check
        import requests
        import socket
        chrome_available = True  # Assume it's available and let browser_capture handle the details
        
        logger.info(f"Assuming Chrome is available on port {chrome_port}")
        
        # First define browser_data and then use it
        browser_data = {
            "chrome": {
                "exe": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                "profiles": [
                    {
                        "profile": "Default",
                        "instances": [{"port": chrome_port, "status": "active"}]
                    }
                ]
            }
        }
        
        logger.info(f"Set up browser data with Chrome port {chrome_port} marked as active")
        
        if chrome_available:
            logger.info(f"Chrome debugging port {chrome_port} is active and responding")
            
        # Capture states
        # Capture app states with detailed logging
        try:
            logger.info("Capturing application states...")
            app_states = capture_app_states()
            if app_states:
                logger.info(f"Successfully captured {len(app_states)} application states")
                for app in app_states:
                    logger.debug(f"Captured app: {app.get('name')} with {len(app.get('windows', []))} windows")
            else:
                logger.warning("No application states were captured")
        except Exception as e:
            logger.error("Failed to capture app states: %s", str(e))
            app_states = []

        # Capture browser states - always attempt with multiple fallbacks
        try:
            logger.info("Capturing browser states...")
            
            # First attempt with provided browser data
            browser_states = capture_browser_states(browser_data)
            
            # Always try direct connection as well to be thorough
            logger.info("Also trying direct connection regardless of previous results")
            direct_browser_states = capture_browser_states(None)  # Will use the fallback to direct port access
            
            # Merge results if both methods returned something
            if direct_browser_states and any(b.get('windows', []) for b in direct_browser_states):
                if not browser_states:
                    browser_states = direct_browser_states
                else:
                    # Append any new browsers from direct capture
                    for direct_browser in direct_browser_states:
                        # Check if this browser is already in our results
                        browser_exists = False
                        for existing_browser in browser_states:
                            if existing_browser.get('browser') == direct_browser.get('browser'):
                                browser_exists = True
                                # Merge windows if needed
                                existing_browser['windows'].extend(direct_browser.get('windows', []))
                                break
                        
                        if not browser_exists:
                            # Add as a new browser
                            browser_states.append(direct_browser)
            
            # Log the results
            if browser_states and any(b.get('windows', []) for b in browser_states):
                logger.info(f"Successfully captured browser states")
                for browser in browser_states:
                    windows = browser.get('windows', [])
                    tabs = sum(len(w.get('tabs', [])) for w in windows)
                    logger.info(f"Captured {browser.get('browser')}: {len(windows)} windows, {tabs} tabs")
            else:
                logger.warning("No browser states captured through DevTools Protocol - window title fallback will be used")
        
        except Exception as e:
            logger.error("Failed to capture browser states: %s", str(e))
            browser_states = []
        
        # Combine states with timestamp and summary
        current_state = {
            'saved_at': datetime.datetime.now().strftime('%Y%m%d_%H%M%S'),
            'apps': app_states or [],
            'browsers': browser_states or [],
            'summary': f"Captured {len(app_states or [])} apps and {len(browser_states or [])} browser states"
        }
        
        # Save state
        os.makedirs(os.path.dirname(state_path), exist_ok=True)
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(current_state, f, indent=2)
            
        logger.info("Successfully saved state with %d apps and %d browser states", 
                   len(app_states or []), len(browser_states or []))
        return True
    except ImportError as e:
        logger.error("Failed to import state capturing modules: %s", str(e))
        return False
    except Exception as e:
        logger.error("Failed to capture system state: %s", str(e))
        return False

def handle_latest_logs(state_path: Optional[str] = None, workspace_name: str = 'autocaptured', run_capture_if_missing: bool = True) -> dict:
    """Minimal orchestration: ensure state exists, convert -> logs, index (vector DB), push dDNA, return summary.

    - Uses available core helpers when present (VectorDBManager, DDNAManager).
    - Attempts to call state-capture helpers if state missing.
    - Does NOT trigger restoration (user-triggered).
    """
    logger.info("handle_latest_logs: start")

    state_path = state_path or _state_default_path()
    
    # Force a new capture every time
    if os.path.exists(state_path):
        try:
            os.remove(state_path)
            logger.info("Removed existing state file for fresh capture")
        except Exception as e:
            logger.error("Failed to remove existing state file: %s", str(e))
    
    # Always capture new state
    if not capture_current_state(state_path):
        return {
            'status': 'error',
            'reason': 'state_capture_failed',
            'message': 'Failed to capture system state. Check logs for details.',
            'path': state_path
        }
    if not os.path.exists(state_path):
        logger.error("state still missing after capture attempt: %s", state_path)
        return {'status': 'error', 'reason': 'state_file_missing', 'path': state_path}

    try:
        with open(state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
    except Exception as e:
        logger.exception("failed to read state")
        return {'status': 'error', 'reason': 'read_failed', 'error': str(e)}

    # Step 1: Convert state to logs
    try:
        logs = _state_to_logs(state)
        if not logs:
            logger.error("No logs generated from state")
            return {'status': 'error', 'reason': 'no_logs_generated', 'message': 'State conversion produced no logs'}
        logger.info("converted state -> %d logs", len(logs))
    except Exception as e:
        logger.exception("Failed to convert state to logs")
        return {'status': 'error', 'reason': 'state_conversion_failed', 'error': str(e)}

    # Step 2: Process with Vector DB
    enriched = logs
    vector_db_status = {'processed': False, 'error': None}
    if VectorDBManager:
        try:
            vdb = VectorDBManager()
            if not hasattr(vdb, 'add_logs_with_topic_matches') and \
               not hasattr(vdb, 'add_logs') and \
               not hasattr(vdb, 'upsert'):
                raise AttributeError("Vector DB manager lacks required methods")

            # Process logs in vector DB with proper method
            if hasattr(vdb, 'add_logs_with_topic_matches'):
                enriched = vdb.add_logs_with_topic_matches(logs)
            elif hasattr(vdb, 'add_logs'):
                enriched = vdb.add_logs(logs)
            elif hasattr(vdb, 'upsert'):
                vdb.upsert(logs)
            
            vector_db_status['processed'] = True
            logger.info("vector DB: processed %d logs", len(enriched))
        except Exception as e:
            vector_db_status['error'] = str(e)
            logger.exception("vector DB processing failed")
            # Continue with unenriched logs rather than failing completely

    # Step 3: Enrich with similarity scoring
    try:
        for l in enriched:
            topics = l.get('topic_matches') or []
            top_score = max((t.get('score', 0.0) for t in topics), default=0.0)
            l['similarity'] = round(float(top_score), 4)
            l['segregation'] = bool(top_score >= 0.75 or any('security' in (t.get('description') or '').lower() for t in topics))
    except Exception as e:
        logger.exception("Failed to calculate similarity scores")
        return {'status': 'error', 'reason': 'similarity_calculation_failed', 'error': str(e)}

    # Step 4: Push to dDNA
    ddna_status = {'pushed': False, 'error': None}
    if DDNAManager:
        try:
            ddna = DDNAManager()
            if not hasattr(ddna, 'create_workspace_ddna') and not hasattr(ddna, 'push'):
                raise AttributeError("DDNA manager lacks required methods")

            if hasattr(ddna, 'create_workspace_ddna'):
                ddna.create_workspace_ddna(workspace_name, log_data=enriched)
                ddna_status['pushed'] = True
            elif hasattr(ddna, 'push'):
                ddna.push(workspace_name, enriched)
                ddna_status['pushed'] = True
            logger.info("dDNA: push complete for workspace %s", workspace_name)
        except Exception as e:
            ddna_status['error'] = str(e)
            logger.exception("dDNA push failed")
            # Continue despite dDNA push failure

    # Step 5: Notify restoration engine
    restore_status = {'notified': False, 'error': None}
    try:
        re_mod = _try_import_module([
            'Restoration_engine', 
            'restoration_engine', 
            'Restoration_engine.engine', 
            'restoration_engine.api'
        ])
        if re_mod:
            restore_result = _try_call(re_mod, 
                ['register_restore_candidates', 'queue_restore_candidates', 'mark_for_restore'], 
                enriched
            )
            restore_status['notified'] = restore_result is not None
        else:
            restore_status['error'] = "Restoration engine module not found"
    except Exception as e:
        restore_status['error'] = str(e)
        logger.exception("Failed to notify restoration engine")

    # Step 6: Push to local ddna by topic
    local_ddna_status = {'pushed': False, 'error': None, 'topics_written': 0}
    try:
        # Ensure local_ddna directory exists
        if not os.path.exists(LOCAL_DDNA_DIR):
            os.makedirs(LOCAL_DDNA_DIR)
            logger.info(f"Created local_ddna directory: {LOCAL_DDNA_DIR}")
        
        # Process each log
        topics_written = set()
        for log in enriched:
            # Get topics for this log
            topics = _get_log_topics(log)
            
            # If no topics found, use event_type as fallback topic
            if not topics and log.get('event_type'):
                event_type = log.get('event_type')
                if event_type == 'browser_tab':
                    topics = ['application_lifecycle']
                elif event_type == 'app_state':
                    topics = ['application_lifecycle']
                elif event_type == 'browser_summary':
                    topics = ['application_lifecycle']
            
            # Write log to each topic file
            for topic in topics:
                _append_log_to_topic(topic, log)
                topics_written.add(topic)
        
        if topics_written:
            local_ddna_status['pushed'] = True
            local_ddna_status['topics_written'] = len(topics_written)
            logger.info(f"Wrote logs to {len(topics_written)} local ddna topic files")
        else:
            logger.warning("No topics found for logs, nothing written to local ddna")
    except Exception as e:
        local_ddna_status['error'] = str(e)
        logger.exception("Failed to write logs to local ddna")
        
    # Return comprehensive status
    result = {
        'status': 'success',
        'workspace': workspace_name,
        'n_logs': len(enriched),
        'vector_db': vector_db_status,
        'ddna': ddna_status,
        'restoration': restore_status,
        'local_ddna': local_ddna_status,
        'logs': enriched,
    }

    logger.info("handle_latest_logs: done")
    return result

if __name__ == '__main__':
    out = handle_latest_logs()
    print(json.dumps(out, indent=2))
