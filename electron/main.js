const { app, BrowserWindow, shell, Menu } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const net = require('net');

// Keep a global reference of the window object
let mainWindow = null;
let flaskProcess = null;
const DEFAULT_PORT = 17600;

// Build version (compile date/time) — loaded from electron/build-info.json
function loadBuildInfo() {
  const buildInfoPath = path.join(__dirname, 'build-info.json');
  try {
    if (fs.existsSync(buildInfoPath)) {
      return JSON.parse(fs.readFileSync(buildInfoPath, 'utf8'));
    }
  } catch (_) {}
  return {
    version: app.getVersion(),
    buildDate: '',
    buildTime: '',
    buildTimestamp: '',
    buildLabel: app.getVersion(),
  };
}
const BUILD_INFO = loadBuildInfo();

// Check if a port is available
function isPortAvailable(port) {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.listen(port, () => {
      server.once('close', () => resolve(true));
      server.close();
    });
    server.on('error', () => resolve(false));
  });
}

// Production URL — load by default so the app is never blank (no Python/Flask required)
const PRODUCTION_URL = 'https://app.ahoy.ooo';
const USE_LOCAL_SERVER = process.env.AHOY_DESKTOP_LOCAL === '1' || process.env.AHOY_DESKTOP_LOCAL === 'true';

// Find an available port
async function findAvailablePort(startPort = DEFAULT_PORT, maxAttempts = 10) {
  for (let i = 0; i < maxAttempts; i++) {
    const port = startPort + i;
    if (await isPortAvailable(port)) {
      return port;
    }
  }
  throw new Error(`Could not find available port after ${maxAttempts} attempts`);
}

// Start Flask server
async function startFlaskServer(port) {
  const isDev = !app.isPackaged;

  // Try to find Python - prefer system Python for now
  // In future, we can bundle Python runtime
  let pythonExecutable = 'python3';
  if (!isDev) {
    // Try bundled Python first (if we add it later)
    const bundledPython = path.join(process.resourcesPath, 'python', 'python');
    if (fs.existsSync(bundledPython)) {
      pythonExecutable = bundledPython;
    } else {
      // For now, use system Python - document requirement
      pythonExecutable = 'python3';
    }
  }
  
  // Determine script path
  let scriptPath;
  let workingDir;
  
  if (isDev) {
    scriptPath = path.join(__dirname, '..', 'desktop_main.py');
    workingDir = path.join(__dirname, '..');
  } else {
    // In packaged app, files are in extraResources
    scriptPath = path.join(process.resourcesPath, 'desktop_main.py');
    workingDir = process.resourcesPath;
    
    // Fallback: try current directory if not in resources
    if (!fs.existsSync(scriptPath)) {
      scriptPath = path.join(__dirname, '..', 'desktop_main.py');
      workingDir = __dirname;
    }
  }

  const env = {
    ...process.env,
    FLASK_ENV: 'production',
    PORT: port.toString(),
    PYTHONUNBUFFERED: '1', // Ensure Python output is not buffered
  };

  // Set database path for desktop
  if (!env.DATABASE_URL) {
    const userDataPath = app.getPath('userData');
    const dbPath = path.join(userDataPath, 'ahoy.db');
    env.DATABASE_URL = `sqlite:///${dbPath}`;
  }
  
  // Set PYTHONPATH to include project directory
  const existingPythonPath = env.PYTHONPATH || '';
  env.PYTHONPATH = workingDir + (existingPythonPath ? `:${existingPythonPath}` : '');

  console.log(`Starting Flask server on port ${port}...`);
  console.log(`Python: ${pythonExecutable}`);
  console.log(`Script: ${scriptPath}`);
  console.log(`Working dir: ${workingDir}`);
  
  flaskProcess = spawn(pythonExecutable, [scriptPath, '--port', port.toString()], {
    env,
    cwd: workingDir,
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  flaskProcess.stdout.on('data', (data) => {
    console.log(`Flask: ${data}`);
  });

  flaskProcess.stderr.on('data', (data) => {
    console.error(`Flask Error: ${data}`);
  });

  flaskProcess.on('error', (error) => {
    console.error('Failed to start Flask server:', error);
    if (mainWindow) {
      mainWindow.webContents.send('server-error', error.message);
    }
  });

  flaskProcess.on('exit', (code) => {
    console.log(`Flask server exited with code ${code}`);
    if (code !== 0 && code !== null) {
      if (mainWindow) {
        mainWindow.webContents.send('server-error', `Server exited with code ${code}`);
      }
    }
  });

  // Wait for server to be ready
  await waitForServer(port);
}

// Wait for Flask server to be ready
function waitForServer(port, maxWait = 30000) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    const checkInterval = 500;

    const checkServer = setInterval(() => {
      const socket = net.createConnection(port, '127.0.0.1');
      
      socket.on('connect', () => {
        socket.end();
        clearInterval(checkInterval);
        resolve();
      });

      socket.on('error', () => {
        if (Date.now() - startTime > maxWait) {
          clearInterval(checkInterval);
          reject(new Error('Server did not start in time'));
        }
      });
    }, checkInterval);
  });
}

// Create the application window
function createWindow() {
  const title = `Ahoy Indie Media — ${BUILD_INFO.buildLabel || BUILD_INFO.version}`;
  // Create the browser window (native title bar so version is visible in top bar)
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    backgroundColor: '#1a1a1a',
    title,
    titleBarStyle: 'default', // native bar so version/title is visible
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      webSecurity: true,
    },
    icon: path.join(__dirname, '..', 'packaging', 'icons', 'ahoy.icns'),
    show: false, // Don't show until ready
  });

  // Show window when ready to prevent visual flash
  mainWindow.once('ready-to-show', () => {
    mainWindow.setTitle(title);
    mainWindow.show();
    if (process.env.NODE_ENV === 'development') {
      mainWindow.webContents.openDevTools();
    }
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // Keep app.ahoy.ooo and localhost in-window; open other links in system browser
  mainWindow.webContents.on('will-navigate', (event, navigationUrl) => {
    const parsedUrl = new URL(navigationUrl);
    const keepInApp = parsedUrl.hostname === '127.0.0.1' ||
      parsedUrl.hostname === 'localhost' ||
      parsedUrl.hostname === 'app.ahoy.ooo';
    if (!keepInApp) {
      event.preventDefault();
      shell.openExternal(navigationUrl);
    }
  });
}

// Initialize app
async function initialize() {
  try {
    let url;
    if (USE_LOCAL_SERVER) {
      const port = await findAvailablePort();
      console.log(`Using local server on port: ${port}`);
      await startFlaskServer(port);
      url = `http://127.0.0.1:${port}`;
    } else {
      url = PRODUCTION_URL;
      console.log(`Loading production: ${url}`);
    }

    createWindow();
    await mainWindow.loadURL(url);
  } catch (error) {
    console.error('Failed to initialize:', error);
    app.quit();
  }
}

// Create application menu (native top bar)
function createMenu() {
  const versionLine = BUILD_INFO.buildDate && BUILD_INFO.buildTime
    ? `Version ${BUILD_INFO.version} — Built ${BUILD_INFO.buildDate} ${BUILD_INFO.buildTime}`
    : `Version ${BUILD_INFO.version}`;
  app.setAboutPanelOptions({
    applicationName: 'Ahoy Indie Media',
    applicationVersion: versionLine,
    copyright: '© Ahoy Indie Media',
    credits: 'Independent music and media platform.',
  });

  const template = [
    {
      label: 'Ahoy Indie Media',
      submenu: [
        { role: 'about', label: 'About Ahoy Indie Media' },
        { type: 'separator' },
        { role: 'services', label: 'Services' },
        { type: 'separator' },
        { role: 'hide', label: 'Hide Ahoy Indie Media' },
        { role: 'hideOthers', label: 'Hide Others' },
        { role: 'unhide', label: 'Show All' },
        { type: 'separator' },
        { role: 'quit', label: 'Quit Ahoy Indie Media' },
      ],
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo', label: 'Undo' },
        { role: 'redo', label: 'Redo' },
        { type: 'separator' },
        { role: 'cut', label: 'Cut' },
        { role: 'copy', label: 'Copy' },
        { role: 'paste', label: 'Paste' },
        { role: 'pasteAndMatchStyle', label: 'Paste and Match Style' },
        { role: 'delete', label: 'Delete' },
        { role: 'selectAll', label: 'Select All' },
        { type: 'separator' },
        {
          label: 'Speech',
          submenu: [
            { role: 'startSpeaking', label: 'Start Speaking' },
            { role: 'stopSpeaking', label: 'Stop Speaking' },
          ],
        },
      ],
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload', label: 'Reload' },
        { role: 'forceReload', label: 'Force Reload' },
        { role: 'toggleDevTools', label: 'Toggle Developer Tools' },
        { type: 'separator' },
        { role: 'resetZoom', label: 'Actual Size' },
        { role: 'zoomIn', label: 'Zoom In' },
        { role: 'zoomOut', label: 'Zoom Out' },
        { type: 'separator' },
        { role: 'togglefullscreen', label: 'Toggle Full Screen' },
      ],
    },
    {
      label: 'Go',
      submenu: [
        { label: 'Back', accelerator: 'CmdOrCtrl+[', click: () => mainWindow?.webContents?.goBack() },
        { label: 'Forward', accelerator: 'CmdOrCtrl+]', click: () => mainWindow?.webContents?.goForward() },
      ],
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize', label: 'Minimize' },
        { role: 'zoom', label: 'Zoom' },
        { type: 'separator' },
        { role: 'close', label: 'Close' },
      ],
    },
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// App event handlers
app.whenReady().then(() => {
  createMenu();
  initialize();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      initialize();
    }
  });
});

app.on('window-all-closed', () => {
  if (flaskProcess) {
    flaskProcess.kill();
    flaskProcess = null;
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  if (flaskProcess) {
    flaskProcess.kill();
    flaskProcess = null;
  }
});

// Handle uncaught errors
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

