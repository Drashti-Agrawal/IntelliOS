# LOCAL_DDNA_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'local_ddna'))
# TOPIC_FILES = [
#     'security', 'system_startup', 'system_shutdown', 'service_operations', 'application_lifecycle',
#     'network_activity', 'driver_operations', 'hardware_events', 'updates', 'user_sessions',
#     'disk_activity', 'performance_issues', 'system_errors', 'application_errors', 'maintenance'
# ]

# def _append_log_to_topic(topic: str, log: dict):
#     """Append log to the correct topic file in local_ddna."""
#     fname = os.path.join(LOCAL_DDNA_DIR, f'{topic}.json')
#     try:
#         # Read existing logs
#         if os.path.exists(fname):
#             with open(fname, 'r', encoding='utf-8') as f:
#                 arr = json.load(f)
#         else:
#             arr = []
#         arr.append(log)
#         with open(fname, 'w', encoding='utf-8') as f:
#             json.dump(arr, f, indent=2)
#     except Exception as e:
#         logger.error(f"Failed to append to topic file {fname}: {e}")

# def _get_log_topics(log: dict) -> list:
#     """Extract topic names from log's topic_matches (if present)."""
#     topics = []
#     for t in log.get('topic_matches', []):
#         if t.get('topic'):
#             topics.append(t['topic'])
#     return topics
import os
import sys
import json
import logging
from typing import Optional

# make core modules importable (backend/core contains helpers we reuse)
CORE_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'core'))
if CORE_DIR not in sys.path:
    sys.path.insert(0, CORE_DIR)

# ensure backend/ is on sys.path so local backend modules (logging_config, vector_db, etc.)
# can be imported when this file is run directly from the repo root
BACKEND_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

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
    return os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'State', 'state.json'))

def _state_to_logs(state: dict) -> list:
    """Lightweight conversion of state -> list of short log dicts for indexing."""
    logs = []
    # browsers may be a dict or list depending on capture version
    browsers = state.get('browsers') or []
    if isinstance(browsers, dict):
        browser_iter = browsers.items()
    else:
        browser_iter = enumerate(browsers)

    for b, info in browser_iter:
        windows = info.get('windows') if isinstance(info, dict) else (info or [])
        for w in windows or []:
            for t in (w.get('tabs') or []):
                logs.append({
                    'event_type': 'browser_tab',
                    'summary': t.get('title') or t.get('url') or '',
                    'url': t.get('url'),
                    'app_name': b if isinstance(b, str) else t.get('browser'),
                })

    for app in state.get('apps') or []:
        name = app.get('name') or app.get('exe') or 'unknown'
        logs.append({
            'event_type': 'app_state',
            'summary': f"App {name} open items: {len(app.get('items') or [])}",
            'app_name': name,
        })

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


def handle_latest_logs(state_path: Optional[str] = None, workspace_name: str = 'autocaptured', run_capture_if_missing: bool = True) -> dict:
    """Minimal orchestration: ensure state exists, convert -> logs, index (vector DB), push dDNA, return summary.

    - Uses available core helpers when present (VectorDBManager, DDNAManager).
    - Attempts to call state-capture helpers if state missing.
    - Does NOT trigger restoration (user-triggered).
    """
    logger.info("handle_latest_logs: start")

    state_path = state_path or _state_default_path()
    if not os.path.exists(state_path):
        logger.warning("state file missing: %s", state_path)
        if run_capture_if_missing:
            sc_mod = _try_import_module([
                'state_capturing_engine', 'State.state_capturing_engine', 'state_capturing_engine.engine', 'state_capturing_engine.capture'
            ])
            _try_call(sc_mod, ['capture_latest', 'capture_and_save', 'capture_once', 'run_capture'], state_path)
    if not os.path.exists(state_path):
        logger.error("state still missing after capture attempt: %s", state_path)
        return {'status': 'error', 'reason': 'state_file_missing', 'path': state_path}

    try:
        with open(state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
    except Exception as e:
        logger.exception("failed to read state")
        return {'status': 'error', 'reason': 'read_failed', 'error': str(e)}

    logs = _state_to_logs(state)
    logger.info("converted state -> %d logs", len(logs))

    # By default do not feed logs into vector DB here. Keep flow lightweight.
    # To index/enrich via the vector DB, run this script with --feed-topics (CLI) which will
    # initialize topics in the vector DB. Indexing logs manually is available via VectorDBManager.
    enriched = logs
    if VectorDBManager:
        try:
            vdb = VectorDBManager()
            # Index logs and get topic matches if the manager supports it
            if hasattr(vdb, 'add_logs_with_topic_matches'):
                enriched = vdb.add_logs_with_topic_matches(logs)
            elif hasattr(vdb, 'add_logs'):
                enriched = vdb.add_logs(logs)
            elif hasattr(vdb, 'upsert'):
                vdb.upsert(logs)
                enriched = logs
            logger.info("vector DB: processed %d logs", len(enriched))
        except Exception:
            logger.exception("vector DB processing failed")

    # append simple similarity/segregation if vector DB returned topic matches
    for l in enriched:
        topics = l.get('topic_matches') or []
        top_score = max((t.get('score', 0.0) for t in topics), default=0.0)
        l['similarity'] = round(float(top_score), 4)
        l['segregation'] = bool(top_score >= 0.75 or any('security' in (t.get('description') or '').lower() for t in topics))

    # persist to cloud (dDNA) if available 
    ddna_ok = False
    if DDNAManager:
        try:
            ddna = DDNAManager()
            if hasattr(ddna, 'create_workspace_ddna'):
                ddna.create_workspace_ddna(workspace_name, log_data=enriched)
                ddna_ok = True
            elif hasattr(ddna, 'push'):
                ddna.push(workspace_name, enriched)
                ddna_ok = True
            logger.info("dDNA: push complete for workspace %s", workspace_name)
        except Exception:
            logger.exception("dDNA push failed")

    # attempt to notify restoration engine (register candidates) but do NOT trigger restore
    re_mod = _try_import_module(['Restoration_engine', 'restoration_engine', 'Restoration_engine.engine', 'restoration_engine.api'])
    _try_call(re_mod, ['register_restore_candidates', 'queue_restore_candidates', 'mark_for_restore'], enriched)

    result = {
        'status': 'success',
        'workspace': workspace_name,
        'n_logs': len(enriched),
        'ddna_pushed': ddna_ok,
        'logs': enriched,
    }
    # local ddna topic appending is disabled here (helpers commented out). Keep flow simple.

    logger.info("handle_latest_logs: done")
    return result

if __name__ == '__main__':
    out = handle_latest_logs()
    print(json.dumps(out, indent=2))
