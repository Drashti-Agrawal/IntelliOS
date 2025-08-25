import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Play, 
  Edit3, 
  Trash2, 
  Plus, 
  Settings, 
  Zap, 
  FolderSync, 
  Activity 
} from 'lucide-react';

const Dashboard = () => {
  const [workspaces, setWorkspaces] = useState([]);
  const [lastRestored, setLastRestored] = useState(null);
  const [aiSuggestion, setAiSuggestion] = useState('');
  const [username] = useState("Drashti");

  // Fetch workspaces from backend
  useEffect(() => {
    async function fetchWorkspaces() {
      try {
        const res = await fetch('http://localhost:5000/api/workspaces');
        const data = await res.json();
        setWorkspaces(data);

        // Set last restored from backend if exists
        const last = data.find(ws => ws.lastRestored);
        if (last) {
          setLastRestored({
            workspace: last.name,
            time: last.lastRestored,
            apps: last.apps?.length || 0,
            files: last.files || 0,
            tabs: last.tabs || 0
          });
        }

        // Set AI suggestion from backend or default
        setAiSuggestion("Based on your usage pattern, I recommend creating a 'Research Mode' workspace for your frequent article reading sessions.");

      } catch (err) {
        console.error("Error fetching workspaces:", err);
      }
    }

    fetchWorkspaces();
  }, []);

  // Handlers
  const handleRestoreWorkspace = async (workspace) => {
    try {
      await fetch(`http://localhost:5000/api/workspaces/${workspace.id}/restore`, { method: 'POST' });
      setLastRestored({
        workspace: workspace.name,
        time: new Date().toLocaleString(),
        apps: workspace.apps?.length || 0,
        files: workspace.files || 0,
        tabs: workspace.tabs || 0
      });
      alert(`Workspace "${workspace.name}" restored!`);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSyncWorkspace = async (workspaceId) => {
    try {
      await fetch(`http://localhost:5000/api/workspaces/${workspaceId}/sync`, { method: 'PUT' });
      setWorkspaces(prev => prev.map(ws => ws.id === workspaceId ? { ...ws, synced: true } : ws));
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteWorkspace = async (workspaceId) => {
    try {
      await fetch(`http://localhost:5000/api/workspaces/${workspaceId}`, { method: 'DELETE' });
      setWorkspaces(prev => prev.filter(ws => ws.id !== workspaceId));
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateWorkspace = () => {
    alert("Redirect to Create Workspace page or open modal");
  };

  const handleCustomizePreferences = () => {
    alert("Redirect to Preferences page or open modal");
  };

  const handleSyncSettings = () => {
    alert("Sync Settings clicked");
  };

  const handleRealTimeMonitoring = () => {
    // In Electron, you can use window.electronAPI.navigateToRealTimeMonitoring()
    alert("Navigating to Real-Time Monitoring page...");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-6">
      {/* Top Bar */}
      <div className="border-b border-slate-700/50 bg-black/20 backdrop-blur-sm mb-8 flex justify-between items-center px-6 py-4 rounded-xl">
        <div className="flex items-center space-x-3">
          <Brain className="w-8 h-8 text-purple-400" />
          <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
            Adaptive Workspace
          </h1>
        </div>
        <div className="flex items-center space-x-4">
          <span className="text-sm text-slate-300">Welcome back, {username}</span>
          <button
            onClick={handleRealTimeMonitoring}
            className="flex items-center space-x-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 px-4 py-2 rounded-lg transition-all duration-200 shadow-lg hover:shadow-cyan-500/25"
          >
            <Activity className="w-4 h-4" />
            <span>Real-Time Monitoring</span>
          </button>
        </div>
      </div>

      {/* Dashboard Overview */}
      <div className="mb-8 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6 grid md:grid-cols-2 gap-6">
        <div>
          <h2 className="text-xl font-semibold mb-3 text-slate-200">Dashboard Overview</h2>
          {lastRestored ? (
            <div className="space-y-2 text-sm">
              <div className="flex items-center space-x-2 text-green-400">
                <CheckCircle className="w-4 h-4" />
                <span>Last restored: {lastRestored.workspace}</span>
              </div>
              <div className="text-slate-400 ml-6">
                {lastRestored.apps} apps • {lastRestored.files} files • {lastRestored.tabs} browser tabs
              </div>
              <div className="flex items-center space-x-2 text-slate-400 ml-6">
                <Clock className="w-3 h-3" />
                <span>{lastRestored.time}</span>
              </div>
            </div>
          ) : (
            <p className="text-slate-400">No workspace restored yet.</p>
          )}
        </div>

        {/* AI Suggestion */}
        <div className="bg-gradient-to-r from-purple-500/10 to-cyan-500/10 rounded-lg p-4 border border-purple-500/20">
          <div className="flex items-start space-x-3">
            <Zap className="w-5 h-5 text-yellow-400 mt-0.5" />
            <div>
              <h3 className="font-medium text-purple-300 mb-1">AI Suggestion</h3>
              <p className="text-sm text-slate-300">{aiSuggestion}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Workspace Cards */}
      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-slate-200">Your Workspaces</h2>
           
          </div>

          <div className="space-y-4">
            {workspaces.length === 0 && <p className="text-slate-400">No workspaces found.</p>}

            {workspaces.map((workspace) => (
              <div
                key={workspace.id}
                className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6 hover:border-slate-600/50 transition-all duration-200"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-slate-200">{workspace.name}</h3>
                    <div className="flex items-center space-x-2 text-sm text-slate-400">
                      <Clock className="w-3 h-3" />
                      <span>Last used: {workspace.lastUsed}</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {workspace.synced ? (
                      <div className="flex items-center space-x-1 text-green-400">
                        <CheckCircle className="w-4 h-4" />
                        <span className="text-xs">Synced</span>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-1 text-orange-400">
                        <AlertCircle className="w-4 h-4" />
                        <span className="text-xs">Not Synced</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="mb-4">
                  <div className="flex flex-wrap gap-2 mb-3">
                    {workspace.apps?.map((app, idx) => (
                      <span key={idx} className="px-2 py-1 bg-slate-700 rounded text-xs text-slate-300">
                        {app}
                      </span>
                    ))}
                  </div>
                  <div className="text-sm text-slate-400">
                    {workspace.files || 0} files • {workspace.tabs || 0} browser tabs
                  </div>
                </div>

                <div className="flex space-x-3">
                  <button
                    onClick={() => handleRestoreWorkspace(workspace)}
                    className="flex items-center space-x-2 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 px-3 py-2 rounded-lg transition-all duration-200 text-sm"
                  >
                    <Play className="w-4 h-4" />
                    <span>Restore</span>
                  </button>
                  <button className="flex items-center space-x-2 bg-slate-700 hover:bg-slate-600 px-3 py-2 rounded-lg transition-colors text-sm">
                    <Edit3 className="w-4 h-4" />
                    <span>Edit</span>
                  </button>
                  {!workspace.synced && (
                    <button
                      onClick={() => handleSyncWorkspace(workspace.id)}
                      className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 px-3 py-2 rounded-lg transition-colors text-sm"
                    >
                      <FolderSync className="w-4 h-4" />
                      <span>Sync</span>
                    </button>
                  )}
                  <button
                    onClick={() => handleDeleteWorkspace(workspace.id)}
                    className="flex items-center space-x-2 bg-red-600 hover:bg-red-700 px-3 py-2 rounded-lg transition-colors text-sm"
                  >
                    <Trash2 className="w-4 h-4" />
                    <span>Delete</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Quick Actions + Stats */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6">
            <h3 className="text-lg font-semibold text-slate-200 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <button
                onClick={handleCreateWorkspace}
                className="w-full flex items-center space-x-3 bg-slate-700 hover:bg-slate-600 px-4 py-3 rounded-lg transition-colors text-left"
              >
                <Plus className="w-5 h-5 text-purple-400" />
                <span>Create New Workspace</span>
              </button>
              <button
                onClick={handleCustomizePreferences}
                className="w-full flex items-center space-x-3 bg-slate-700 hover:bg-slate-600 px-4 py-3 rounded-lg transition-colors text-left"
              >
                <Settings className="w-5 h-5 text-blue-400" />
                <span>Customize Preferences</span>
              </button>
              <button
                onClick={handleSyncSettings}
                className="w-full flex items-center space-x-3 bg-slate-700 hover:bg-slate-600 px-4 py-3 rounded-lg transition-colors text-left"
              >
                <FolderSync className="w-5 h-5 text-green-400" />
                <span>Sync Settings</span>
              </button>
            </div>
          </div>

          {/* Stats Panel */}
          <div className="bg-gradient-to-br from-purple-500/10 to-cyan-500/10 rounded-xl border border-purple-500/20 p-6">
            <h3 className="text-lg font-semibold text-slate-200 mb-4">Today's Activity</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-400">Workspaces Used</span>
                <span className="text-white">{workspaces.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Apps Launched</span>
                <span className="text-white">
                  {workspaces.reduce((sum, ws) => sum + (ws.apps?.length || 0), 0)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Files Opened</span>
                <span className="text-white">
                  {workspaces.reduce((sum, ws) => sum + (ws.files || 0), 0)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Browser Tabs</span>
                <span className="text-white">
                  {workspaces.reduce((sum, ws) => sum + (ws.tabs || 0), 0)}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
