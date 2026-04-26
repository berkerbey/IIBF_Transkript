const { app, BrowserWindow, dialog, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const { autoUpdater } = require('electron-updater');

// Manual update check listeners
ipcMain.on('check-for-updates', () => {
  autoUpdater.checkForUpdatesAndNotify();
});

ipcMain.on('install-update', () => {
  autoUpdater.quitAndInstall();
});

let mainWindow;
let pythonProcess;

// Configure AutoUpdater
autoUpdater.autoDownload = true;
autoUpdater.autoInstallOnAppQuit = true;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 850,
    minWidth: 1400,
    minHeight: 750,
    icon: app.isPackaged
      ? path.join(__dirname, 'icon.ico')
      : path.join(__dirname, 'public/icon.ico'),
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

  // Load app
  if (app.isPackaged) {
    mainWindow.loadFile(path.join(__dirname, 'dist', 'index.html'));
  } else {
    mainWindow.loadURL('http://localhost:5173');
  }

  mainWindow.on('closed', function () {
    mainWindow = null;
  });

  // Check for updates once window is ready
  mainWindow.once('ready-to-show', () => {
    autoUpdater.checkForUpdatesAndNotify();
  });
}

// Auto-update events
autoUpdater.on('checking-for-update', () => {
  mainWindow?.webContents.send('update-status', 'checking');
});

autoUpdater.on('update-available', (info) => {
  mainWindow?.webContents.send('update-status', 'available', info.version);
});

autoUpdater.on('update-not-available', () => {
  mainWindow?.webContents.send('update-status', 'latest');
});

autoUpdater.on('update-downloaded', (info) => {
  mainWindow?.webContents.send('update-status', 'downloaded', info.version);
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

  // Wait for backend to be ready
  const checkBackend = () => {
    const http = require('http');
    let attempts = 0;
    const maxAttempts = 30; // 30 seconds

    const interval = setInterval(() => {
      attempts++;
      http.get('http://127.0.0.1:8000/config', (res) => {
        if (res.statusCode === 200) {
          clearInterval(interval);
          createWindow();
        }
      }).on('error', (err) => {
        if (attempts >= maxAttempts) {
          clearInterval(interval);
          dialog.showErrorBox("Başlatma Hatası", "Yapay zeka motoru başlatılamadı. Lütfen uygulamayı kapatıp tekrar açmayı deneyin.\nHata: " + err.message);
          app.quit();
        }
      });
    }, 1000);
  };

  checkBackend();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) {
      // Only create if backend was ready (we'll simplify for now)
      createWindow();
    }
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
