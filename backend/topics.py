# topics.py
"""
Defines common log topics for categorization and matching.
"""

# List of predefined topics with descriptions
TOPICS = {
    "security": "Security-related events including authentication, authorization, and security updates",
    "system_startup": "System startup, boot, and initialization events",
    "system_shutdown": "System shutdown, restart, and power-off events",
    "service_operations": "Service start, stop, pause, and configuration events",
    "application_lifecycle": "Application start, stop, crash, and update events",
    "network_activity": "Network connections, disconnections, and communication events",
    "driver_operations": "Device driver installation, updates, and issues",
    "hardware_events": "Hardware-related events including device connections and errors",
    "updates": "System and application update events",
    "user_sessions": "User login, logout, and session-related events",
    "disk_activity": "Disk operations, errors, and storage-related events",
    "performance_issues": "Performance bottlenecks, resource usage, and optimization events",
    "system_errors": "Critical system errors and failures",
    "application_errors": "Application crashes, hangs, and errors",
    "maintenance": "System maintenance and cleanup activities"
}

# Example logs for each topic to enhance semantic matching
TOPIC_EXAMPLES = {
    "security": [
        "Failed login attempt for user admin from IP 192.168.1.100",
        "Security policy updated to require password complexity",
        "Antivirus definition updated to version 15.2.3",
        "Firewall blocked outbound connection to suspicious IP",
        "User account locked after 5 failed login attempts"
    ],
    "system_startup": [
        "System boot completed successfully",
        "Operating system initialized in 45 seconds",
        "Boot loader loaded kernel image",
        "System startup sequence initiated",
        "Startup services initialized successfully"
    ],
    "system_shutdown": [
        "System shutdown initiated by administrator",
        "Clean system shutdown completed",
        "Emergency system power off due to temperature warning",
        "System restart scheduled for maintenance",
        "Unexpected shutdown detected during recovery"
    ],
    "service_operations": [
        "Windows Update service started successfully",
        "SQL Server service failed to start due to configuration error",
        "Print Spooler service paused by user",
        "Background Intelligent Transfer Service (BITS) resumed",
        "Remote Desktop service configuration changed"
    ],
    "application_lifecycle": [
        "Microsoft Word started by user",
        "Chrome browser crashed with error code 0x80004005",
        "Notepad.exe terminated unexpectedly",
        "Adobe Reader updated to version 22.1.5",
        "Microsoft Teams installation completed successfully"
    ],
    "network_activity": [
        "Network adapter disconnected from wireless network",
        "HTTP connection established to www.example.com",
        "DNS resolution failed for hostname server.local",
        "VPN connection established to corporate network",
        "High network traffic detected on adapter Ethernet0"
    ],
    "driver_operations": [
        "Graphics driver updated to version 472.33",
        "USB driver failed to load for device VID_1234",
        "Audio driver causing BSOD identified and rollback initiated",
        "Printer driver successfully installed for HP LaserJet",
        "Network driver optimized for performance"
    ],
    "hardware_events": [
        "New USB device detected: Kingston DataTraveler",
        "CPU temperature exceeds normal threshold at 85°C",
        "Memory module in slot 2 reporting errors",
        "Hard disk S.M.A.R.T. warning on drive C:",
        "Battery health degraded to 65% of original capacity"
    ],
    "updates": [
        "Windows Update installed 3 critical updates",
        "Security Intelligence Update for Microsoft Defender Antivirus installed",
        "Feature update to Windows 10 21H2 pending restart",
        "Microsoft Office updates downloaded and ready to install",
        "System firmware update available from manufacturer"
    ],
    "user_sessions": [
        "User John logged in successfully",
        "Remote desktop session established for administrator",
        "User session timed out after 30 minutes of inactivity",
        "Fast user switching initiated for profile Alice",
        "Console session locked by user"
    ],
    "disk_activity": [
        "Disk cleanup freed 2.5GB of storage space",
        "Disk fragmentation level at 15% on drive C:",
        "Disk error detected on sector 234813 of drive D:",
        "Volume shadow copy created for backup",
        "Disk throughput bottleneck detected during high I/O operation"
    ],
    "performance_issues": [
        "Memory usage at 92% due to application Chrome.exe",
        "CPU throttling engaged due to thermal constraints",
        "Excessive paging detected due to low memory",
        "Process Explorer.exe consuming high CPU resources",
        "System responsiveness degraded due to background processes"
    ],
    "system_errors": [
        "Blue Screen of Death occurred with stop code MEMORY_MANAGEMENT",
        "Critical system file missing: C:\\Windows\\System32\\ntoskrnl.exe",
        "Registry corruption detected in HKLM\\SOFTWARE hive",
        "System unable to boot from primary partition",
        "Critical service winlogon.exe failed to initialize"
    ],
    "application_errors": [
        "Application Microsoft Word crashed with error code 0x0000142",
        "Application Adobe Photoshop encountered unhandled exception",
        "Excel.exe stopped responding while processing large dataset",
        "Chrome browser reported memory error in tab process",
        "Application error: The instruction at 0x00007FF87E5C1F2D referenced memory at 0x0000000000000000"
    ],
    "maintenance": [
        "Scheduled maintenance started: disk defragmentation",
        "System restore point created before updates",
        "Temporary files cleanup completed successfully",
        "Diagnostic scan completed with 3 issues identified",
        "Automatic maintenance tasks completed at 3:00 AM"
    ]
}
