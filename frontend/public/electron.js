const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');

let mainWindow;
let appWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 900,
    height: 700,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    resizable: false,
    maximizable: false,
    autoHideMenuBar: true,
    titleBarStyle: 'default',
    center: true,
    show: false
  });

  mainWindow.loadURL(
    isDev 
      ? 'http://localhost:3000' 
      : `file://${path.join(__dirname, '../build/index.html')}`
  );

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
    if (appWindow) {
      appWindow.close();
    }
  });
}

function createAppWindow() {
  appWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
    autoHideMenuBar: true,
    center: true,
    show: false
  });

  // Load a simple app window (you can replace this with your actual app)
  appWindow.loadURL('data:text/html;charset=utf-8,' + encodeURIComponent(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>MyApp - ML Monitoring System</title>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
          margin: 0;
          padding: 40px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          text-align: center;
        }
        .container {
          background: rgba(255,255,255,0.1);
          padding: 40px;
          border-radius: 20px;
          backdrop-filter: blur(10px);
        }
        h1 { font-size: 2.5rem; margin-bottom: 20px; }
        p { font-size: 1.2rem; opacity: 0.9; line-height: 1.6; }
        .status {
          margin-top: 30px;
          padding: 15px;
          background: rgba(0,255,0,0.2);
          border-radius: 10px;
          border: 1px solid rgba(0,255,0,0.3);
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>🚀 MyApp ML Monitoring System</h1>
        <p>Your application has been successfully installed and is now running!</p>
        <div class="status">
          <p><strong>✅ System Status:</strong> Active</p>
          <p><strong>🔍 ML Model:</strong> Initialized</p>
          <p><strong>📊 Monitoring:</strong> Live</p>
          <p><strong>☁️ Cloud Sync:</strong> Connected</p>
        </div>
      </div>
    </body>
    </html>
  `));

  appWindow.once('ready-to-show', () => {
    appWindow.show();
  });

  appWindow.on('closed', () => {
    appWindow = null;
  });
}

// IPC handlers
ipcMain.handle('select-directory', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory'],
    defaultPath: 'C:\\Program Files\\MyApp'
  });
  
  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths[0];
  }
  return null;
});

ipcMain.handle('launch-app', async (event, preferences) => {
  console.log('Launching app with preferences:', preferences);
  
  // Close installer window
  if (mainWindow) {
    mainWindow.close();
  }
  
  // Create and show main app window
  createAppWindow();
  
  return true;
});

ipcMain.handle('simulate-installation', async (event, step) => {
  // Simulate different installation steps with delays
  const delays = {
    'fetching-logs': 800,
    'preprocessing': 1200,
    'ml-model': 1500,
    'fine-tuning': 1000,
    'personalization': 900,
    'finalizing': 600
  };
  
  await new Promise(resolve => setTimeout(resolve, delays[step] || 500));
  return true;
});

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});