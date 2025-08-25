import React from 'react';
import '../styles/dashboard.css';

const Dashboard = () => {
  return (
    <div className="dashboard">
      {/* Sidebar Section */}
      <div className="sidebar">
        <div className="sidebar-section recent-activity">
          <h3>Recent Activity</h3>
          <ul>
            <li>Updated main.css</li>
            <li>Committed changes to Git</li>
            <li>Opened new terminal</li>
          </ul>
        </div>

        <div className="sidebar-section ai-suggestions">
          <h3>AI Suggestions</h3>
          <ul>
            <li>Optimize database queries</li>
            <li>Refactor authentication module</li>
            <li>Update dependencies of X project</li>
          </ul>
        </div>

        <div className="sidebar-section active-workspace">
          <h3>Active Workspace</h3>
          <p>Current project: IntelliOS Dashboard</p>
          <p>Last synced: <strong>5 minutes ago</strong></p>
        </div>
      </div>

      {/* Main Content Section */}
      <div className="main-content">
        <h2 className="restore-heading">Restore Topic</h2>
        <div className="project-grid">
          {[1, 2, 3, 4].map((_, i) => (
            <div className="project-card" key={i}>
              <h3>Project X</h3>
              <div className="icons">
                <div className="sync-icon">🔄</div>
                <button className="edit-btn">Edit Resources</button>
                <button className="sync-btn">Sync with dDNA</button>
              </div>
              <h4>Resource Utilization</h4>
              <div className="resource-bars">
                <div className="bar"><label>CPU Usage</label><progress value="45" max="100"></progress></div>
                <div className="bar"><label>Memory Usage</label><progress value="60" max="100"></progress></div>
                <div className="bar"><label>Disk Usage</label><progress value="75" max="100"></progress></div>
                <div className="bar"><label>Network Usage</label><progress value="30" max="100"></progress></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
