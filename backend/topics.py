# topics.py
"""
Merged topics for system events and workspace classification.

Defines TOPICS and TOPIC_EXAMPLES that are loaded by VectorDBManager.
This file contains both system-oriented topics (used for OS/event logs)
and workspace-oriented topics (web_development, machine_learning, etc.)
to support richer workspace classification.
"""

# System / OS topics
SYSTEM_TOPICS = {
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

# Workspace / user-activity topics
WORKSPACE_TOPICS = {
    "web_development": "Building websites and web applications. Includes code editors, local servers, terminals, and documentation.",
    "machine_learning": "Developing ML/AI models. Involves data analysis, model training, and notebooks in environments like Jupyter or Colab.",
    "dsa_coding": "Competitive programming and practicing data structures & algorithms on platforms like LeetCode or Codeforces.",
    "data_analytics": "Analyzing data and creating visualizations. Common tools include Excel, Tableau, Power BI, and SQL.",
    "web_design": "UI/UX design and prototyping using tools like Figma and Adobe XD, focusing on visual elements.",
    "extracurricular": "Leisure activities like watching videos on YouTube/Netflix or listening to music on Spotify.",
    "web_surfing": "General internet browsing, social media, reading news, and online shopping without a specific work focus."
}

# Combine into a single TOPICS dict used by the VectorDBManager
TOPICS = {**SYSTEM_TOPICS, **WORKSPACE_TOPICS}

# Examples for each topic
TOPIC_EXAMPLES = {
    # system examples (kept short)
    "security": [
        "Failed login attempt for user admin from IP 192.168.1.100",
        "Firewall blocked outbound connection to suspicious IP",
        "User account locked after 5 failed login attempts"
    ],
    "system_startup": ["System boot completed successfully", "Startup services initialized successfully"],
    "system_shutdown": ["System shutdown initiated by administrator", "Clean system shutdown completed"],
    "service_operations": ["Windows Update service started successfully", "SQL Server service failed to start due to configuration error"],
    "application_lifecycle": ["Microsoft Word started by user", "Chrome browser crashed with error code 0x80004005"],
    "network_activity": ["HTTP connection established to www.example.com", "VPN connection established to corporate network"],
    "driver_operations": ["Graphics driver updated to version 472.33", "USB driver failed to load for device VID_1234"],
    "hardware_events": ["New USB device detected: Kingston DataTraveler", "CPU temperature exceeds normal threshold at 85°C"],
    "updates": ["Windows Update installed 3 critical updates", "Feature update to Windows pending restart"],
    "user_sessions": ["User John logged in successfully", "Remote desktop session established for administrator"],
    "disk_activity": ["Disk cleanup freed 2.5GB of storage space", "Disk error detected on sector 234813 of drive D:"],
    "performance_issues": ["Memory usage at 92% due to application Chrome.exe", "CPU throttling engaged due to thermal constraints"],
    "system_errors": ["Blue Screen of Death occurred with stop code MEMORY_MANAGEMENT", "Critical system file missing: C:\\Windows\\System32\\ntoskrnl.exe"],
    "application_errors": ["Application Microsoft Word crashed with error code 0x0000142", "Excel.exe stopped responding while processing large dataset"],
    "maintenance": ["Scheduled maintenance started: disk defragmentation", "System restore point created before updates"],

    # workspace examples (from user-provided list)
    "web_development": [
        "App: Code.exe | Window: index.html - my-portfolio - Visual Studio Code | File: C:\\projects\\my-app\\src\\App.js",
        "App: powershell.exe | Window: C:\\WINDOWS\\system32\\cmd.exe - npm run dev",
        "Tab: React – A JavaScript library for building user interfaces | URL: https://reactjs.org/docs/getting-started.html",
        "Tab: Stack Overflow - Where Developers Learn, Share, & Build Careers | URL: https://stackoverflow.com/questions/tagged/javascript",
        "Tab: localhost:3000 | URL: http://localhost:3000/"
    ],
    "machine_learning": [
        "App: Code.exe | File: C:\\Users\\user\\ml-projects\\notebooks\\data-exploration.ipynb",
        "Tab: Google Colab - model_training.ipynb | URL: https://colab.research.google.com/",
        "App: jupyter.exe | Window: Jupyter Notebook Server",
        "Tab: TensorFlow Core | Get started | URL: https://www.tensorflow.org/overview"
    ],
    "dsa_coding": [
        "Tab: Two Sum - LeetCode | URL: https://leetcode.com/problems/two-sum/",
        "App: Code.exe | Window: solution.cpp - dsa-practice - Visual Studio Code | File: C:\\dsa\\arrays\\solution.cpp",
        "Tab: Contest 1800 - Codeforces | URL: https://codeforces.com/contest/1800"
    ],
    "data_analytics": [
        "App: EXCEL.EXE | Window: Q4_Sales_Report.xlsx - Excel | File: D:\\Reports\\Sales\\Q4_Sales_Report.xlsx",
        "App: Tableau.exe | Window: Regional Sales Dashboard - Tableau Desktop",
        "Tab: Google Sheets | URL: https://docs.google.com/spreadsheets/"
    ],
    "web_design": [
        "App: Figma.exe | Window: Mobile App Wireframes - Figma",
        "App: Adobe XD.exe | Window: Website Prototype.xd",
        "Tab: Color Palettes for Designers and Artists - Color Hunt | URL: https://colorhunt.co/"
    ],
    "extracurricular": [
        "Tab: YouTube | URL: https://www.youtube.com/",
        "App: Spotify.exe | Window: Spotify Premium",
        "Tab: Netflix | URL: https://www.netflix.com/browse"
    ],
    "web_surfing": [
        "Tab: Amazon.com. Spend less. Smile more. | URL: https://www.amazon.com/",
        "Tab: Reddit - Dive into anything | URL: https://www.reddit.com/",
        "Tab: Gmail | URL: https://mail.google.com/mail/u/0/#inbox"
    ]
}

