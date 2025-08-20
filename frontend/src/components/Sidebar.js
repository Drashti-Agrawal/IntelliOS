import React from 'react';

function Sidebar() {
  return (
    <div className="sidebar bg-dark text-white p-3">
      <div className="mb-4">
        <h3 className="text-gradient">Dashboard</h3>
      </div>
      <div className="card mb-3 bg-success text-white p-3">
        <h5>Recent Activity</h5>
        <ul>
          <li>Updated main.css</li>
          <li>Committed to Git</li>
          <li>Opened new terminal</li>
        </ul>
      </div>
      <div className="card mb-3 bg-warning text-dark p-3">
        <h5>AI Suggestions</h5>
        <ul>
          <li>Optimize DB queries</li>
          <li>Refactor auth module</li>
          <li>Update dependencies</li>
        </ul>
      </div>
      <div className="card bg-info text-white p-3">
        <h5>Active Workspace</h5>
        <p>Current project: IntelliOS Dashboard</p>
        <p>Last synced: 5 mins ago</p>
      </div>
    </div>
  );
}

export default Sidebar;
