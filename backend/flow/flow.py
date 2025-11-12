import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

import requests

# Load environment variables
load_dotenv()


FLOW_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(FLOW_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

CORE_DIR = os.path.join(BACKEND_DIR, 'core')
STATE_DIR = os.path.join(PROJECT_ROOT, 'State')
STATE_CAPTURE_DIR = os.path.join(PROJECT_ROOT, 'State_capturing_engine')
LOCAL_DDNA_DIR = os.path.join(BACKEND_DIR, 'local_ddna')

for path in (PROJECT_ROOT, CORE_DIR, BACKEND_DIR, STATE_CAPTURE_DIR):
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)

os.makedirs(STATE_DIR, exist_ok=True)

from logging_config import setup_logging

try:
    from ddna_manager import DDNAManager
except Exception:
    DDNAManager = None

try:
    from vector_db import VectorDBManager
except Exception:
    VectorDBManager = None

logger = setup_logging()

TOPIC_FILES = [
    'security', 'system_startup', 'system_shutdown', 'service_operations', 'application_lifecycle',
    'network_activity', 'driver_operations', 'hardware_events', 'updates', 'user_sessions',
    'disk_activity', 'performance_issues', 'system_errors', 'application_errors', 'maintenance'
]


def _state_default_path() -> str:
    return os.path.join(STATE_DIR, 'state.json')


def _state_to_logs(state: dict) -> List[dict]:
    sys.path.insert(0, STATE_CAPTURE_DIR)
    try:
        from state_processor import state_to_logs
        return state_to_logs(state)
    except ImportError:
        logger.error("Failed to import state_processor module")
        return []


def _append_log_to_topic(topic: str, log: dict) -> None:
    fname = os.path.join(LOCAL_DDNA_DIR, f'{topic}.json')
    try:
        os.makedirs(os.path.dirname(fname), exist_ok=True)

        streamlined_log = {
            'event_type': log.get('event_type'),
            'summary': log.get('summary'),
            'saved_at': log.get('saved_at'),
            'timestamp': log.get('saved_at')
        }

        if log.get('event_type') == 'app_state':
            streamlined_log.update({
                'app_name': log.get('app_name'),
                'exe_path': log.get('app_info', {}).get('exe_path') if 'app_info' in log else log.get('exe_path'),
                'pid': log.get('app_info', {}).get('pid') if 'app_info' in log else log.get('pid'),
                'window_count': log.get('app_info', {}).get('window_count') if 'app_info' in log else log.get('window_count'),
                'captured_at': log.get('app_info', {}).get('captured_at') if 'app_info' in log else log.get('captured_at')
            })
        elif log.get('event_type') == 'browser_tab':
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

        for topic_match in log.get('topic_matches', []):
            if topic_match.get('topic') == topic:
                streamlined_log['topic_score'] = topic_match.get('score')
                streamlined_log['topic_description'] = topic_match.get('description')
                break

        if os.path.exists(fname):
            with open(fname, 'r', encoding='utf-8') as file:
                entries = json.load(file)
        else:
            entries = []

        entries.append(streamlined_log)

        with open(fname, 'w', encoding='utf-8') as file:
            json.dump(entries, file, indent=2)
        logger.info("Added streamlined log to topic file %s", topic)
    except Exception as exc:
        logger.error("Failed to append to topic file %s: %s", fname, exc)


def _normalize_browser_ports(raw_data: Optional[dict]) -> Dict[str, dict]:
    """Normalize browser ports metadata into the structure expected by capture_browser_states."""
    if not isinstance(raw_data, dict):
        return {}

    browsers_section = raw_data.get('browsers') if 'browsers' in raw_data else raw_data
    if not isinstance(browsers_section, dict):
        return {}

    normalized: Dict[str, dict] = {}

    for key, entry in browsers_section.items():
        if not isinstance(entry, dict):
            continue

        browser_name = entry.get('browser') or key.split('_', 1)[0]
        exe_path = entry.get('exe') or entry.get('exe_path')
        profiles: List[dict] = []

        raw_profiles = entry.get('profiles')

        # Helper to produce a normalized profile dict
        def _build_profile(name_hint: str, payload: Optional[dict]) -> Optional[dict]:
            payload = payload or {}
            if not isinstance(payload, dict):
                payload = {}

            profile_name = payload.get('profile') or payload.get('user_data_dir') or name_hint or 'Default'
            user_dir = payload.get('user_data_dir') or profile_name

            instances = payload.get('instances')
            if isinstance(instances, dict):
                instances = [{**data, 'port': str(port)} for port, data in instances.items() if isinstance(data, dict)]
            elif isinstance(instances, list):
                instances = [inst for inst in instances if isinstance(inst, dict)]
            else:
                instances = []

            ports = payload.get('ports')
            if isinstance(ports, list):
                instances.extend({'port': str(port), 'status': payload.get('status', 'active')} for port in ports)

            if not instances and isinstance(entry.get('ports'), list):
                instances.extend({'port': str(port), 'status': 'active'} for port in entry['ports'])

            if not instances:
                return None

            return {
                'profile': profile_name,
                'user_data_dir': user_dir,
                'instances': instances
            }

        if isinstance(raw_profiles, dict):
            for prof_name, prof_payload in raw_profiles.items():
                normalized_profile = _build_profile(prof_name, prof_payload if isinstance(prof_payload, dict) else None)
                if normalized_profile:
                    profiles.append(normalized_profile)
        elif isinstance(raw_profiles, list):
            for idx, prof_payload in enumerate(raw_profiles):
                if isinstance(prof_payload, dict):
                    name_hint = prof_payload.get('profile') or prof_payload.get('user_data_dir') or f'Profile_{idx}'
                    normalized_profile = _build_profile(name_hint, prof_payload)
                elif isinstance(prof_payload, str):
                    normalized_profile = _build_profile(prof_payload, {'profile': prof_payload})
                else:
                    normalized_profile = None
                if normalized_profile:
                    profiles.append(normalized_profile)
        else:
            normalized_profile = _build_profile(key, {'ports': entry.get('ports')})
            if normalized_profile:
                profiles.append(normalized_profile)

        if profiles:
            normalized[browser_name] = {
                'exe': exe_path,
                'profiles': profiles,
            }

    return normalized


def _get_log_topics(log: dict) -> List[str]:
    all_topics = set(TOPIC_FILES)
    try:
        from topics import TOPICS
        all_topics.update(TOPICS.keys())
    except ImportError:
        pass

    all_topics.update({
        'web_development', 'machine_learning', 'dsa_coding', 'data_analytics',
        'web_design', 'extracurricular', 'web_surfing'
    })

    best_topic = None
    highest_score = -1.0
    for topic_match in log.get('topic_matches', []):
        score = topic_match.get('score', 0.0)
        if topic_match.get('topic') and score > highest_score:
            highest_score = score
            best_topic = topic_match.get('topic')

    return [best_topic] if best_topic else []


def _try_import_module(names: List[str]):
    import importlib

    for name in names:
        try:
            return importlib.import_module(name)
        except Exception:
            continue
    return None


def _try_call(module, fn_names: List[str], *args, **kwargs):
    if not module:
        return None
    for name in fn_names:
        fn = getattr(module, name, None)
        if callable(fn):
            try:
                return fn(*args, **kwargs)
            except Exception:
                logger.exception("helper call failed: %s.%s", getattr(module, '__name__', '?'), name)
    return None


def capture_current_state(state_path: str) -> bool:
    logger.info("capture_current_state: monitoring capture is currently disabled")
    return False


# File-based state helpers removed: state will be provided via API or direct logs input


def _process_vector_db(logs: List[dict]) -> Tuple[List[dict], Dict[str, Optional[str]]]:
    enriched = logs
    status: Dict[str, Optional[str]] = {'processed': False, 'error': None}

    if not VectorDBManager:
        return enriched, status

    try:
        vdb = VectorDBManager()
        if hasattr(vdb, 'add_logs_with_topic_matches'):
            enriched = vdb.add_logs_with_topic_matches(logs)
        elif hasattr(vdb, 'add_logs'):
            enriched = vdb.add_logs(logs)
        elif hasattr(vdb, 'upsert'):
            vdb.upsert(logs)
        else:
            raise AttributeError('Vector DB manager lacks required methods')
        status['processed'] = True
        logger.info('vector DB: processed %d logs', len(enriched))
    except Exception as exc:
        status['error'] = str(exc)
        logger.exception('vector DB processing failed')

    return enriched, status


def _augment_similarity(logs: List[dict]) -> None:
    for log in logs:
        topics = log.get('topic_matches') or []
        top_score = max((topic.get('score', 0.0) for topic in topics), default=0.0)
        log['similarity'] = round(float(top_score), 4)
        log['segregation'] = bool(
            top_score >= 0.75 or any('security' in (topic.get('description') or '').lower() for topic in topics)
        )


def _push_ddna(logs: List[dict], workspace_name: str) -> Dict[str, Optional[str]]:
    status: Dict[str, Optional[str]] = {'pushed': False, 'error': None}
    if not DDNAManager:
        return status

    try:
        ddna = DDNAManager()
        if hasattr(ddna, 'create_workspace_ddna'):
            ddna.create_workspace_ddna(workspace_name, log_data=logs)
        elif hasattr(ddna, 'push'):
            ddna.push(workspace_name, logs)
        else:
            raise AttributeError('DDNA manager lacks required methods')
        status['pushed'] = True
        logger.info('dDNA: push complete for workspace %s', workspace_name)
    except Exception as exc:
        status['error'] = str(exc)
        logger.exception('dDNA push failed')

    return status


def _notify_restoration(logs: List[dict]) -> Dict[str, Optional[str]]:
    status: Dict[str, Optional[str]] = {'notified': False, 'error': None}
    try:
        module = _try_import_module([
            'Restoration_engine',
            'restoration_engine',
            'Restoration_engine.engine',
            'restoration_engine.api'
        ])
        if not module:
            # Restoration is optional - don't treat missing modules as an error
            return status

        result = _try_call(module, ['register_restore_candidates', 'queue_restore_candidates', 'mark_for_restore'], logs)
        status['notified'] = result is not None
    except Exception as exc:
        status['error'] = str(exc)
        logger.debug('Failed to notify restoration engine: %s', exc)  # Changed to debug level

    return status


def _write_local_ddna(logs: List[dict]) -> Dict[str, Optional[int]]:
    status: Dict[str, Optional[int]] = {'pushed': False, 'error': None, 'topics_written': 0}
    try:
        os.makedirs(LOCAL_DDNA_DIR, exist_ok=True)
        topics_written = set()

        for log in logs:
            topics = _get_log_topics(log)
            if not topics and log.get('event_type') in {'browser_tab', 'app_state', 'browser_summary'}:
                topics = ['application_lifecycle']

            for topic in topics:
                _append_log_to_topic(topic, log)
                topics_written.add(topic)

        if topics_written:
            status['pushed'] = True
            status['topics_written'] = len(topics_written)
            logger.info('Wrote logs to %d local ddna topic files', len(topics_written))
        else:
            logger.warning('No topics found for logs, nothing written to local ddna')
    except Exception as exc:
        status['error'] = str(exc)
        logger.exception('Failed to write logs to local ddna')

    return status


def handle_latest_logs(
    logs: Optional[List[dict]] = None,
    api_url: Optional[str] = None,
    workspace_name: str = 'autocaptured'
) -> dict:
    logger.info('handle_latest_logs: start')

    # If an API URL is provided, delegate to handle_remote_logs (reuse existing implementation)
    if api_url:
        return handle_remote_logs(api_url, workspace_name)
    
    # Use default API URL from environment if none provided and no logs given
    if not logs and not api_url:
        default_api_url = os.getenv('CAPTURE_API_URL')
        if default_api_url:
            return handle_remote_logs(default_api_url.rstrip('/') + '/api/capture', workspace_name)
        
        # If no API URL configured, capture state directly
        logger.info('No API URL configured, capturing state directly')
        try:
            # Import capture modules
            sys.path.insert(0, STATE_CAPTURE_DIR)
            from browser_capture import capture_browser_states
            from app_capture import capture_app_states
            
            # Read browser ports file
            browser_ports_file = os.path.join(FLOW_DIR, 'browser_ports.json')
            browser_ports_data = {}
            if os.path.exists(browser_ports_file):
                with open(browser_ports_file, 'r', encoding='utf-8') as f:
                    raw_ports = json.load(f)
                browser_ports_data = _normalize_browser_ports(raw_ports)
                if not browser_ports_data and isinstance(raw_ports, dict):
                    browser_ports_data = raw_ports
            
            # Capture browser and app states
            browsers = capture_browser_states(browser_ports_data)
            raw_apps = capture_app_states()
            
            # Normalize app data
            apps = []
            for a in (raw_apps or []):
                items = a.get('files') or a.get('items') or []
                apps.append({
                    'name': a.get('name'),
                    'pid': a.get('pid'),
                    'exe': a.get('exe'),
                    'cmdline': a.get('cmdline'),
                    'items': items,
                    'windowInfo': a.get('windowInfo')
                })
            
            # Create state object
            state = {
                "saved_at": datetime.utcnow().isoformat(),
                "user": os.environ.get("USERNAME", ""),
                "browsers": browsers,
                "apps": apps
            }
            
            # Convert state to logs
            logs = _state_to_logs(state)
            logger.info(f'Captured state and converted to {len(logs)} logs')
            
        except Exception as exc:
            logger.exception('Failed to capture state directly')
            return {'status': 'error', 'reason': 'capture_failed', 'message': f'Failed to capture state: {exc}'}

    # Require logs to be provided either directly or via api_url
    if not logs:
        return {'status': 'error', 'reason': 'no_logs_provided', 'message': 'No logs available to process'}

    try:
        logger.info('processing %d logs', len(logs))
    except Exception as exc:
        logger.exception('Failed to prepare logs for processing')
        return {'status': 'error', 'reason': 'log_preparation_failed', 'error': str(exc)}

    # Optionally enrich logs via vector DB before annotating local metadata.
    enriched, vector_db_status = _process_vector_db(logs)

    try:
        # Add similarity and segregation fields derived from topic matches.
        _augment_similarity(enriched)
    except Exception as exc:
        logger.exception('Failed to calculate similarity scores')
        return {'status': 'error', 'reason': 'similarity_calculation_failed', 'error': str(exc)}

    # Fan out the enriched logs to downstream systems and local storage.
    ddna_status = _push_ddna(enriched, workspace_name)
    restore_status = _notify_restoration(enriched)
    local_ddna_status = _write_local_ddna(enriched)

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

    logger.info('handle_latest_logs: done')
    return result


def handle_remote_logs(api_url: str, workspace_name: str = 'autocaptured') -> dict:
    payload = requests.get(api_url, timeout=60).json()
    state = payload.get('state') or {}
    logs = _state_to_logs(state) if state else []
    
    # Collect all enriched logs
    all_enriched_logs = []
    results = []
    
    for log in logs:
        enriched, vector_db_status = _process_vector_db([log])
        _augment_similarity(enriched)
        ddna_status = _push_ddna(enriched, workspace_name)
        restore_status = _notify_restoration(enriched)
        local_ddna_status = _write_local_ddna(enriched)
        
        # Add enriched log to the list
        if enriched:
            all_enriched_logs.extend(enriched)
        
        results.append({
            'vector_db': vector_db_status,
            'ddna': ddna_status,
            'restoration': restore_status,
            'local_ddna': local_ddna_status,
            'log': enriched[0] if enriched else log,
        })
    
    return {
        'status': payload.get('status', 'success') if all_enriched_logs else 'error',
        'message': payload.get('message', f'Processed {len(all_enriched_logs)} logs'),
        'workspace': workspace_name,
        'count': len(results),
        'n_logs': len(all_enriched_logs),
        'logs': all_enriched_logs,  # Add logs key for UI compatibility
        'results': results
    }


if __name__ == '__main__':
    output = handle_latest_logs()
    print(json.dumps(output, indent=2))

