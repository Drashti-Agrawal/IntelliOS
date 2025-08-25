# regex_parsers.py
import re
import logging

# Set up logger
logger = logging.getLogger(__name__)

def handle_app_error(match):
    """Handler for a standard Application Error event (Event ID 1000)."""
    groups = match.groupdict()
    logger.debug(f"Regex handler 'handle_app_error' matched groups: {groups}")
    return {
        "event_type": "application_crash",
        "app_name": groups.get("app_name"),
        "module_name": groups.get("module_name"),
        "error_code": groups.get("error_code")
    }

def handle_service_control(match):
    """Handler for Service Control Manager events."""
    groups = match.groupdict()
    logger.debug(f"Regex handler 'handle_service_control' matched groups: {groups}")
    
    service_name = groups.get("service_name") or groups.get("service_name_alt") or "Unknown service"
    action = groups.get("action")
    state = groups.get("state")
    details = groups.get("details")
    
    if state:
        summary = f"Service '{service_name}' entered the {state} state"
    elif action:
        summary = f"Service '{service_name}' {action}" + (f": {details}" if details else "")
    else:
        summary = f"Service '{service_name}' event"
        
    return {
        "event_type": "service_event",
        "app_name": service_name,
        "summary": summary
    }

def handle_kernel_power(match):
    """Handler for Kernel-Power events."""
    groups = match.groupdict()
    logger.debug(f"Regex handler 'handle_kernel_power' matched groups: {groups}")
    
    if groups.get("sleep_time"):
        summary = f"System sleep time: {groups.get('sleep_time')}" + (f" ({groups.get('sleep_details').strip()})" if groups.get('sleep_details') else "")
        event_subtype = "sleep_event"
    elif "The system is entering sleep" in str(groups):
        summary = "System is entering sleep state"
        event_subtype = "sleep_event"
    elif "The system is exiting sleep" in str(groups):
        summary = "System is exiting sleep state"
        event_subtype = "sleep_event"
    elif groups.get("shutdown_reason"):
        summary = f"System shutdown: {groups.get('shutdown_reason')}" + (f" ({groups.get('shutdown_details').strip()})" if groups.get('shutdown_details') else "")
        event_subtype = "shutdown_event"
    else:
        # For numeric power messages we can indicate they are power transitions
        summary = f"Power event: {groups.get('message')}"
        event_subtype = "power_transition"
        
    return {
        "event_type": "power_event",
        "event_subtype": event_subtype,
        "summary": summary
    }

def handle_generic_event(match):
    """Generic handler for other event types."""
    groups = match.groupdict()
    logger.debug(f"Regex handler 'handle_generic_event' matched groups: {groups}")
    return {
        "event_type": "system_event",
        "summary": f"System event: {groups.get('message')}"
    }

def handle_kernel_general(match):
    """Handler for Kernel-General events."""
    groups = match.groupdict()
    logger.debug(f"Regex handler 'handle_kernel_general' matched groups: {groups}")
    
    code = groups.get("code")
    file_path = groups.get("file_path")
    param1 = groups.get("param1")
    param2 = groups.get("param2")
    
    summary = f"File system operation: Code {code} on {file_path} (params: {param1}, {param2})"
    
    return {
        "event_type": "file_system_event",
        "file_path": file_path,
        "operation_code": code,
        "summary": summary
    }

def handle_dcom_event(match):
    """Handler for DCOM events."""
    groups = match.groupdict()
    logger.debug(f"Regex handler 'handle_dcom_event' matched groups: {groups}")
    
    app_name = groups.get("app_name")
    action = groups.get("action")
    error_type = groups.get("error_type")
    status = groups.get("status")
    
    summary = f"DCOM {error_type} {action}: {app_name} ({status})"
    
    return {
        "event_type": "dcom_event",
        "app_name": app_name,
        "status": status,
        "summary": summary
    }

# A registry of all high-precision parsers. Easily extensible.
PARSER_REGISTRY = [
    {
        "provider_name": "Application Error",
        "regex": re.compile(
            r"Faulting application name: (?P<app_name>[\w\.]+), .*"
            r"Faulting module name: (?P<module_name>[\w\.]+), .*"
            r"Exception code: (?P<error_code>0x[0-9a-fA-F]+)"
        ),
        "handler": handle_app_error
    },
    # Add Service Control Manager parser
    {
        "provider_name": "Service Control Manager",
        "regex": re.compile(
            r"(?:The )?(?P<service_name>[^%\s]+)(?:.*?service entered the )(?P<state>\w+)(?:.*)|\s*(?P<service_name_alt>[^%\s]+)(?:\s+)(?P<action>\w+\s+\w+)(?:\s+)(?P<details>.*)"
        ),
        "handler": handle_service_control
    },
    # Add Microsoft-Windows-Kernel-Power parser
    {
        "provider_name": "Microsoft-Windows-Kernel-Power",
        "regex": re.compile(
            r"(?:The system is entering sleep\.|The system is exiting sleep\.|(?:Sleep|Hibernate) Time: (?P<sleep_time>.*))(?P<sleep_details>.*)?|"
            r"(?:Shutdown reason: (?P<shutdown_reason>.*))(?P<shutdown_details>.*)?|"
            r"(?P<message>.*)"
        ),
        "handler": handle_kernel_power
    },
    # Add DCOM parser
    {
        "provider_name": "DCOM",
        "regex": re.compile(
            r"(?P<error_type>application-specific) (?P<action>Local Activation) (?P<clsid>\{[A-F0-9-]+\}) (?P<app_id>\{[A-F0-9-]+\}) (?P<computer_name>\S+) (?P<user_name>\S+) (?P<sid>S-\d+-\d+(?:-\d+)*) (?P<client_info>.*?) (?P<app_name>.*?) (?P<status>.*)"
        ),
        "handler": handle_dcom_event
    },
    # Add Win32k parser
    {
        "provider_name": "Win32k",
        "regex": re.compile(
            r"(?P<message>.*)"
        ),
        "handler": handle_generic_event
    },
    # Add Microsoft-Windows-Kernel-General parser
    {
        "provider_name": "Microsoft-Windows-Kernel-General",
        "regex": re.compile(
            r"(?P<code>\d+)\s+(?P<file_path>\\[^\\].*)\s+(?P<param1>\d+)\s+(?P<param2>\d+)"
        ),
        "handler": handle_kernel_general
    },
    # Add TPM parser
    {
        "provider_name": "TPM",
        "regex": re.compile(
            r"(?P<message>.*)"
        ),
        "handler": handle_generic_event
    },
    # Add IsolatedUserMode parser
    {
        "provider_name": "Microsoft-Windows-IsolatedUserMode",
        "regex": re.compile(
            r"(?P<message>.*)"
        ),
        "handler": handle_generic_event
    }
]

def parse_with_regex(provider: str, message: str):
    """
    Attempts to parse a log message using the PARSER_REGISTRY.
    Returns a dictionary on success, or None on failure.
    """
    logger.info(f"Attempting regex parsing for provider: '{provider}'")
    for parser in PARSER_REGISTRY:
        if parser["provider_name"] == provider:
            logger.debug(f"Found matching provider in registry. Trying regex: {parser['regex'].pattern}")
            match = parser["regex"].search(message)
            if match:
                logger.info(f"Successfully parsed log from '{provider}' with regex.")
                return parser["handler"](match)
    logger.info(f"No regex match found for provider '{provider}'.")
    return None
