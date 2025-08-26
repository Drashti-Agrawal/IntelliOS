const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  selectDirectory: () => ipcRenderer.invoke('select-directory'),
  launchApp: (preferences) => ipcRenderer.invoke('launch-app', preferences),
  simulateInstallation: (step) => ipcRenderer.invoke('simulate-installation', step),
  navigateToDashboard: () => ipcRenderer.send('navigate-to-dashboard')
});
