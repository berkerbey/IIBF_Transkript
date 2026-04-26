const { app, BrowserWindow, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const { autoUpdater } = require('electron-updater');

let mainWindow;
let pythonProcess;

// Configure AutoUpdater
autoUpdater.autoDownload = true;
autoUpdater.autoInstallOnAppQuit = true;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    icon: path.join(__dirname, 'public/icon.ico'),
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    },
    titleBarStyle: 'hidden',
    titleBarOverlay: {
      color: '#FAFAFA',
      symbolColor: '#0F172A',
      height: 40
    }
  });

  // Load Vite dev server
  mainWindow.loadURL('http://localhost:5173');

  mainWindow.on('closed', function () {
    mainWindow = null;
  });

  // Check for updates once window is ready
  mainWindow.once('ready-to-show', () => {
    autoUpdater.checkForUpdatesAndNotify();
  });
}

// Auto-update events
autoUpdater.on('update-available', () => {
  console.log('Update available.');
});

autoUpdater.on('update-downloaded', (info) => {
  dialog.showMessageBox({
    type: 'info',
    title: 'Güncelleme Hazır',
    message: `Yeni sürüm (${info.version}) indirildi. Uygulama kapatıldığında yüklenecek. Şimdi yeniden başlatmak ister misiniz?`,
    buttons: ['Şimdi Yeniden Başlat', 'Sonra'],
    defaultId: 0
  }).then((result) => {
    if (result.response === 0) {
      autoUpdater.quitAndInstall();
    }
  });
});

autoUpdater.on('error', (err) => {
  console.error('Update error:', err);
});

app.whenReady().then(() => {
  // Fix for Windows Taskbar Icon
  if (process.platform === 'win32') {
    app.setAppUserModelId('pau.iibf.transcriber.electron');
  }

  // Start Python FastAPI backend
  let pythonExecutable;
  let pythonArgs;
  const isDev = !app.isPackaged;

  if (isDev) {
    pythonExecutable = 'C:\\Users\\Berker\\anaconda3\\envs\\whisper_env\\python.exe';
    pythonArgs = ['-m', 'uvicorn', 'src.api:app', '--host', '127.0.0.1', '--port', '8000'];
  } else {
    // In production, the python EXE will be in extraResources/python
    pythonExecutable = path.join(process.resourcesPath, 'python', 'WhisperTranscriber.exe');
    pythonArgs = ['--host', '127.0.0.1', '--port', '8000']; // Assuming the EXE starts uvicorn internally or is a wrapper
  }

  pythonProcess = spawn(pythonExecutable, pythonArgs, {
    cwd: isDev ? path.join(__dirname, '..') : path.join(process.resourcesPath, 'python')
  });

  pythonProcess.stdout.on('data', (data) => console.log(`Python: ${data}`));
  pythonProcess.stderr.on('data', (data) => console.error(`Python Error: ${data}`));

  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('quit', () => {
  if (pythonProcess) {
    pythonProcess.kill();
  }
});
