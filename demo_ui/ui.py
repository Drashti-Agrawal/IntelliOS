
import streamlit as st
import json
import os
import datetime
from local_ddna_helper import (
    get_local_ddna_topics,
    get_local_ddna_topic,
    get_latest_local_ddna,
    get_local_ddna_stats,
    search_local_ddna
)

# Import restore_state if available
try:
    from restore_state_mac import restore_state
except ImportError:
    restore_state = None

# Load workspaces from JSON file
WORKSPACES_PATH = os.path.join(os.path.dirname(__file__), "workspaces.json")
if os.path.exists(WORKSPACES_PATH):
    with open(WORKSPACES_PATH) as f:
        workspaces = json.load(f)
else:
    workspaces = []

lastRestored = next((ws for ws in workspaces if ws.get('lastRestored')), None)
aiSuggestion = "Based on your usage pattern, I recommend creating a 'Research Mode' workspace for your frequent article reading sessions."
username = "Drashti"

st.set_page_config(page_title="Adaptive Workspace Dashboard", layout="wide")

# Top Bar
st.markdown(f"""
<div style='background: linear-gradient(to right, #2d2d44, #3f8dfc); padding: 1.5rem; border-radius: 1rem; margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;'>
  <div style='display: flex; align-items: center; gap: 1rem;'>
    <span style='font-size:2rem; color:#b086f2;'>🧠</span>
    <span style='font-size:1.5rem; font-weight:bold; background: linear-gradient(to right, #b086f2, #3f8dfc); -webkit-background-clip: text; color: transparent;'>Adaptive Workspace</span>
  </div>
  <div style='display: flex; align-items: center; gap: 1rem;'>
    <span style='color:#ccc;'>Welcome back, {username}</span>
    <button style='background: linear-gradient(to right, #3f8dfc, #00ffb3); color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; border: none;'>Real-Time Monitoring</button>
  </div>
</div>
""", unsafe_allow_html=True)

# Dashboard Overview
col1, col2 = st.columns(2)
with col1:
    st.subheader("Dashboard Overview")
    if lastRestored:
        st.success(f"Last restored: {lastRestored['name']}")
        st.write(f"{lastRestored['apps'].__len__()} apps • {lastRestored['files']} files • {lastRestored['tabs']} browser tabs")
        st.write(f"{lastRestored['lastRestored']}")
    else:
        st.info("No workspace restored yet.")
with col2:
    st.markdown(f"""
    <div style='background: linear-gradient(to right, #b086f2, #3f8dfc); padding: 1rem; border-radius: 0.75rem;'>
      <span style='font-size:1.2rem;'>⚡</span>
      <span style='color:#fff; font-weight:500;'>AI Suggestion</span>
      <div style='color:#eee; margin-top:0.5rem;'>{aiSuggestion}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Workspace Cards
st.subheader("Your Workspaces")
for ws in workspaces:
    with st.container():
        st.markdown(f"<div style='background: #2d2d44; border-radius: 1rem; padding: 1rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)
        cols = st.columns([3, 1])
        with cols[0]:
            st.markdown(f"<span style='font-size:1.1rem; font-weight:600;'>{ws['name']}</span>", unsafe_allow_html=True)
            st.write(f"Last used: {ws['lastUsed']}")
            st.write(f"{' • '.join(ws['apps'])}")
            st.write(f"{ws['files']} files • {ws['tabs']} browser tabs")
        with cols[1]:
            if ws.get('synced'):
                st.success("Synced")
            else:
                st.warning("Not Synced")
            if st.button(f"Restore {ws['name']}"):
                restore_state()
                st.success(f"Workspace '{ws['name']}' restored!")
            if st.button(f"Delete {ws['name']}"):
                st.error(f"Workspace '{ws['name']}' deleted!")
        st.markdown("</div>", unsafe_allow_html=True)

# Quick Actions & Stats
colA, colB = st.columns([1,1])
with colA:
    st.subheader("Quick Actions")
    st.button("Create New Workspace")
    st.button("Customize Preferences")
    st.button("Sync Settings")
with colB:
    st.subheader("Today's Activity")
    st.write(f"Workspaces Used: {len(workspaces)}")
    st.write(f"Apps Launched: {sum(len(ws['apps']) for ws in workspaces)}")
    st.write(f"Files Opened: {sum(ws['files'] for ws in workspaces)}")
    st.write(f"Browser Tabs: {sum(ws['tabs'] for ws in workspaces)}")

st.markdown("---")

# Local DDNA Section
st.subheader("🧬 Local DDNA Activity Monitoring")

# Get DDNA stats
ddna_stats = get_local_ddna_stats()

if ddna_stats.get("status") == "success":
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Topics", ddna_stats.get("topics", 0))
    with col2:
        st.metric("Total Logs", ddna_stats.get("total_logs", 0))
    with col3:
        timestamp_range = ddna_stats.get("timestamp_range", {})
        if timestamp_range.get("latest"):
            st.metric("Last Activity", timestamp_range["latest"][:19])
        else:
            st.metric("Last Activity", "N/A")
    
    # Display topics
    st.subheader("Available Topics")
    topics_response = get_local_ddna_topics()
    
    if topics_response.get("status") == "success" and topics_response.get("count", 0) > 0:
        topics = topics_response.get("topics", [])
        logs_by_topic = ddna_stats.get("logs_by_topic", {})
        
        # Create a grid of topics
        cols_per_row = 3
        for i in range(0, len(topics), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(topics):
                    topic = topics[i + j]
                    log_count = logs_by_topic.get(topic, 0)
                    with col:
                        with st.expander(f"📂 {topic.replace('_', ' ').title()} ({log_count})"):
                            if st.button(f"View Details", key=f"view_{topic}"):
                                st.session_state['selected_topic'] = topic
    
    # Display selected topic details
    if 'selected_topic' in st.session_state:
        selected_topic = st.session_state['selected_topic']
        st.subheader(f"Topic Details: {selected_topic.replace('_', ' ').title()}")
        
        topic_data = get_local_ddna_topic(selected_topic, limit=10)
        
        if topic_data.get("status") == "success":
            st.write(f"Showing {topic_data.get('count', 0)} of {topic_data.get('total', 0)} logs")
            
            logs = topic_data.get("logs", [])
            for idx, log in enumerate(logs):
                with st.expander(f"Log {idx + 1} - {log.get('event_type', 'Unknown')} - {log.get('timestamp', 'N/A')[:19]}"):
                    st.json(log)
        else:
            st.error(f"Error loading topic: {topic_data.get('message', 'Unknown error')}")
    
    # Search functionality
    st.markdown("---")
    st.subheader("🔍 Search Local DDNA")
    
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        search_query = st.text_input("Enter search query", key="search_query")
    with search_col2:
        case_sensitive = st.checkbox("Case Sensitive", key="case_sensitive")
    
    if st.button("Search") and search_query:
        search_results = search_local_ddna(search_query, case_sensitive=case_sensitive)
        
        if search_results.get("status") == "success":
            st.success(f"Found {search_results.get('total_matches', 0)} matches across {search_results.get('matched_topics', 0)} topics")
            
            results = search_results.get("results", {})
            for topic, matches in results.items():
                with st.expander(f"{topic.replace('_', ' ').title()} ({len(matches)} matches)"):
                    for idx, match in enumerate(matches[:5]):  # Show first 5 matches per topic
                        st.json(match)
                    if len(matches) > 5:
                        st.info(f"... and {len(matches) - 5} more matches")
        else:
            st.warning(search_results.get("message", "No results found"))
    
else:
    st.warning(f"⚠️ {ddna_stats.get('message', 'Unable to load Local DDNA data')}")
    st.info("Make sure the Local DDNA directory exists and contains data files.")
