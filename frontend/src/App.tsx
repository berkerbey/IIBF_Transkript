import { useState, useRef, useEffect, useMemo } from 'react';
import { Settings, Database, ArrowRight, Play, Home, HelpCircle, Info, FolderOpen, CheckCircle, Plus, Trash2, Pause, Clock, Cpu, Zap, Languages, MousePointer2, ShieldCheck, Star, Search, FileText, RefreshCw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// Import assets to let Vite handle paths correctly
import pauLogo from './assets/Pamukkale_University_logo.svg';
import iibfLogo from './assets/iibf_logo.png';
import iibfTranskriptLogo from './assets/iibf_transkript.png';

type AppState = 'WELCOME' | 'EMPTY' | 'STAGING' | 'PROCESSING' | 'READY';
type TabState = 'MAIN' | 'HISTORY' | 'SETTINGS' | 'HELP' | 'ABOUT';

function formatDuration(seconds: number) {
  if (!seconds) return "0s";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}sa ${m}dk`;
  if (m > 0) return `${m}dk ${s}sn`;
  return `${s}sn`;
}

const MODEL_SIZES: Record<string, string> = {
  'faster-whisper-tiny': '75MB',
  'faster-whisper-base': '150MB',
  'faster-whisper-medium': '1.5GB',
  'faster-whisper-large-v2': '3GB'
};

const MODEL_DETAILS: Record<string, { summary: string, technical: string }> = {
  'faster-whisper-tiny': {
    summary: 'Maksimum hız, temel doğruluk.',
    technical: 'Düşük kaynaklı bilgisayarlar için optimize edilmiştir. Hızlı önizlemeler için uygundur ancak karmaşık akademik terimlerde hata payı yüksektir.'
  },
  'faster-whisper-base': {
    summary: 'Hızlı ve günlük kullanım için ideal.',
    technical: 'Net ses kayıtlarında ve günlük konuşmalarda iyi performans sergiler. Orta düzey doğruluk sunar.'
  },
  'faster-whisper-medium': {
    summary: 'Akademik transkripsiyon için en iyi seçenek.',
    technical: 'Türkçe dili üzerinde en yüksek başarı oranına sahip modeldir. Röportajlar, toplantılar ve bilimsel veriler için standart seçimdir.'
  },
  'faster-whisper-large-v2': {
    summary: 'En yüksek doğruluk, yüksek donanım ihtiyacı.',
    technical: 'En gelişmiş yapay zeka modelidir. Zorlu ses koşullarında ve teknik jargonlarda en iyi sonucu verir, ancak güçlü bir CPU/GPU gerektirir.'
  }
};

function formatBytes(bytes: number) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

const ParticleBackground = () => {
  const { nodes, lines } = useMemo(() => {
    return {
      nodes: Array.from({ length: 40 }).map((_, i) => ({
        id: i, x: Math.random() * 100, y: Math.random() * 100, size: Math.random() * 2 + 1, duration: 15 + Math.random() * 15
      })),
      lines: Array.from({ length: 25 }).map((_, i) => ({
        id: i, x1: Math.random() * 100, y1: Math.random() * 100, x2: Math.random() * 100, y2: Math.random() * 100, duration: 25 + Math.random() * 25
      }))
    };
  }, []);

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none z-0 bg-[#F8FAFC]">
      {/* Mesh Gradient Blobs */}
      <motion.div
        className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-blue-400/10 rounded-full blur-[120px]"
        animate={{ x: [0, 50, 0], y: [0, 30, 0] }}
        transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute bottom-[-10%] right-[-10%] w-[60%] h-[60%] bg-indigo-500/10 rounded-full blur-[120px]"
        animate={{ x: [0, -40, 0], y: [0, -50, 0] }}
        transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute top-[40%] left-[40%] w-[30%] h-[30%] bg-purple-500/5 rounded-full blur-[100px]"
        animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* SVG Particle Network */}
      <svg className="absolute inset-0 w-full h-full opacity-40">
        {lines.map((line) => (
          <motion.line
            key={`line-${line.id}`}
            stroke="#818CF8"
            strokeWidth="0.5"
            strokeOpacity="0.4"
            initial={{ x1: `${line.x1}%`, y1: `${line.y1}%`, x2: `${line.x2}%`, y2: `${line.y2}%` }}
            animate={{
              x1: [`${line.x1}%`, `${line.x1 + 5}%`, `${line.x1}%`],
              y1: [`${line.y1}%`, `${line.y1 + 5}%`, `${line.y1}%`],
              x2: [`${line.x2}%`, `${line.x2 - 5}%`, `${line.x2}%`],
              y2: [`${line.y2}%`, `${line.y2 - 5}%`, `${line.y2}%`]
            }}
            transition={{ duration: line.duration, repeat: Infinity, ease: "linear" }}
          />
        ))}
        {nodes.map((node) => (
          <motion.circle
            key={`node-${node.id}`}
            r={node.size}
            fill="#6366F1"
            initial={{ cx: `${node.x}%`, cy: `${node.y}%`, opacity: 0.2 }}
            animate={{
              cx: [`${node.x}%`, `${node.x + 2}%`, `${node.x}%`],
              cy: [`${node.y}%`, `${node.y - 2}%`, `${node.y}%`],
              opacity: [0.2, 0.8, 0.2]
            }}
            transition={{ duration: node.duration, repeat: Infinity, ease: "easeInOut" }}
          />
        ))}
      </svg>
    </div>
  );
};

function App() {
  const [dragActive, setDragActive] = useState(false);
  const [appState, setAppState] = useState<AppState>('WELCOME');
  const [activeTab, setActiveTab] = useState<TabState>('MAIN');
  const [config, setConfig] = useState<any>({
    model_name: "faster-whisper-medium",
    device: "auto",
    default_language: "auto"
  });
  const [currentPercent, setCurrentPercent] = useState(0);
  const [isDownloading, setIsDownloading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const addMoreInputRef = useRef<HTMLInputElement>(null);

  // Batch Processing State
  const [queue, setQueue] = useState<File[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [completedSessions, setCompletedSessions] = useState<any[]>([]);
  const [activeResultIndex, setActiveResultIndex] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [showUpdateToast, setShowUpdateToast] = useState(false);
  const [showCompletionModal, setShowCompletionModal] = useState(false);
  const [isCheckingUpdates, setIsCheckingUpdates] = useState(false);
  const [updateStatus, setUpdateStatus] = useState<{ type: 'idle' | 'checking' | 'available' | 'latest' | 'downloaded', version?: string }>({ type: 'idle' });
  const [currentTime, setCurrentTime] = useState(0);

  useEffect(() => {
    // Listen for update status from main process
    // @ts-ignore
    const { ipcRenderer } = window.require('electron');

    const handleStatus = (_event: any, status: any, version: any) => {
      setUpdateStatus({ type: status, version });
      setIsCheckingUpdates(status === 'checking');
      
      // Show update toast only for final states (not checking)
      if (status !== 'checking' && status !== 'idle') {
        setShowUpdateToast(true);
      }
      
      const timeoutId = setTimeout(() => {
        setShowUpdateToast(false);
        setTimeout(() => setUpdateStatus({ type: 'idle' }), 500);
      }, 5000);

      return () => clearTimeout(timeoutId);
    };

    ipcRenderer.on('update-status', handleStatus);

    // Initial check on startup
    ipcRenderer.send('check-for-updates');

    return () => ipcRenderer.removeListener('update-status', handleStatus);
  }, []);

  // Audio Playback State
  const audioRef = useRef<HTMLAudioElement>(null);
  const [playingFile, setPlayingFile] = useState<File | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playingBlock, setPlayingBlock] = useState<{ start: number, end: number } | null>(null);
  const requestRef = useRef<number | null>(null);

  // High-precision time tracking loop
  const animateTime = () => {
    if (audioRef.current && isPlaying) {
      setCurrentTime(audioRef.current.currentTime);
      
      // Safety check for block end
      if (playingBlock && audioRef.current.currentTime >= playingBlock.end) {
        audioRef.current.pause();
        setIsPlaying(false);
        setPlayingBlock(null);
      }
      requestRef.current = requestAnimationFrame(animateTime);
    }
  };

  useEffect(() => {
    if (isPlaying) {
      requestRef.current = requestAnimationFrame(animateTime);
    } else {
      if (requestRef.current !== null) cancelAnimationFrame(requestRef.current);
    }
    return () => {
      if (requestRef.current !== null) cancelAnimationFrame(requestRef.current);
    };
  }, [isPlaying, playingBlock]);

  const checkForUpdates = () => {
    // Only trigger if not already checking
    if (isCheckingUpdates) return;

    setIsCheckingUpdates(true);
    setUpdateStatus({ type: 'checking' });
    // REMOVED: setShowUpdateToast(true); // Don't show toast while checking

    // @ts-ignore
    const { ipcRenderer } = window.require('electron');
    ipcRenderer.send('check-for-updates');

    // Safety timeout to reset button if no response from main process
    setTimeout(() => setIsCheckingUpdates(false), 10000);
  };

  // History State
  const [historyItems, setHistoryItems] = useState<any[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);

  useEffect(() => {
    // checkModelStatus(); // REMOVED FROM STARTUP
    if (activeTab === 'HISTORY') {
      setIsLoadingHistory(true);
      fetch('http://127.0.0.1:8000/history')
        .then(res => res.json())
        .then(data => setHistoryItems(data))
        .catch(console.error)
        .finally(() => setIsLoadingHistory(false));
    }
  }, [activeTab]);

  const loadFromHistory = async (item: any) => {
    // Reconstruct file object for playback if possible
    let fileForPlayback = { name: item.filename, size: item.file_size };
    
    // Try to load the actual file from path if we are in Electron
    try {
      // @ts-ignore
      const fs = window.require('fs');
      if (item.filepath && fs.existsSync(item.filepath)) {
        const buffer = fs.readFileSync(item.filepath);
        const blob = new Blob([buffer]);
        // @ts-ignore
        fileForPlayback = new File([blob], item.filename, { type: 'audio/mpeg' });
        // @ts-ignore
        fileForPlayback.path = item.filepath; // Attach path for reference
      }
    } catch (e) {
      console.warn("Could not load original file from history path:", e);
    }

    const reconstructedSession = {
      session_id: item.session_id,
      file: fileForPlayback,
      transcript: item.transcript
    };
    setCompletedSessions(prev => {
      // Avoid duplicates
      if (prev.find(s => s.session_id === item.session_id)) return prev;
      return [reconstructedSession, ...prev];
    });
    setAppState('READY');
    setActiveResultIndex(0);
    setActiveTab('MAIN');
  };

  useEffect(() => {
    // Load config from backend
    fetch('http://127.0.0.1:8000/config')
      .then(res => res.json())
      .then(data => setConfig(data))
      .catch(console.error);
  }, []);

  // Cleanup object URLs to prevent memory leaks
  useEffect(() => {
    return () => {
      if (audioRef.current?.src) {
        URL.revokeObjectURL(audioRef.current.src);
      }
    };
  }, []);

  const saveConfig = (newConfig: any) => {
    setConfig(newConfig);
    fetch('http://127.0.0.1:8000/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newConfig)
    }).catch(console.error);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const addToQueue = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setQueue(prev => [...prev, ...Array.from(files)]);
    if (appState === 'EMPTY') {
      setAppState('STAGING');
    }
  };

  const removeFromQueue = (index: number) => {
    setQueue(prev => prev.filter((_, i) => i !== index));
    if (queue.length === 1) {
      setAppState('EMPTY');
      stopAudio();
    }
  };

  const startTranscription = async () => {
    if (queue.length === 0) return;

    // Check model first
    try {
      const response = await fetch('http://localhost:8000/check-model');
      const data = await response.json();
      if (!data.exists) {
        setIsDownloading(true);
      }
    } catch (e) {
      console.error("Model check failed", e);
    }

    stopAudio();
    setCurrentIndex(0);
    setCurrentPercent(0);
    setCompletedSessions([]);
    setAppState('PROCESSING');

    await processNextFile(0, queue);
  };

  const processNextFile = async (index: number, allFiles: File[]) => {
    if (index >= allFiles.length) {
      // Batch complete
      setAppState('READY');
      setActiveResultIndex(0);
      setShowCompletionModal(true);
      return;
    }

    const file = allFiles[index];
    const formData = new FormData();
    formData.append("file", file);

    try {
      const uploadRes = await fetch('http://127.0.0.1:8000/upload', {
        method: 'POST',
        body: formData
      });
      const uploadData = await uploadRes.json();
      const sid = uploadData.session_id;

      await fetch(`http://127.0.0.1:8000/transcribe/${sid}?model=${config.model_name}&lang=${config.default_language}&device=${config.device}`, {
        method: 'POST'
      });

      pollStatus(sid, index, allFiles);
    } catch (err) {
      console.error(err);
      alert(`${file.name} analiz için hazırlanamadı.`);
      // Try next file
      processNextFile(index + 1, allFiles);
    }
  };

  const pollStatus = async (sid: string, index: number, allFiles: File[]) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/status/${sid}`);
      const data = await res.json();

      if (data.state === 'READY') {
        setCompletedSessions(prev => [...prev, {
          file: allFiles[index],
          transcript: data.transcript
        }]);
        // Move to next
        setCurrentIndex(index + 1);
        setCurrentPercent(0);
        setIsDownloading(false);
        processNextFile(index + 1, allFiles);
      } else if (data.state === 'ERROR') {
        alert(`${allFiles[index].name} işlenirken hata oluştu: ` + data.error);
        setCurrentIndex(index + 1);
        setCurrentPercent(0);
        setIsDownloading(false);
        processNextFile(index + 1, allFiles);
      } else {
        if (data.phase === 'TRANSCRIBING') {
          setIsDownloading(false);
        } else if (data.phase === 'DOWNLOADING') {
          setIsDownloading(true);
        } else if (data.phase === 'PREPARING') {
          // Do nothing, keep current isDownloading state
        }

        if (data.percent !== undefined) {
          setCurrentPercent(data.percent);
        }
        setTimeout(() => pollStatus(sid, index, allFiles), 1500);
      }
    } catch (err) {
      console.error(err);
      setTimeout(() => pollStatus(sid, index, allFiles), 2000);
    }
  };

  // --- Audio Playback Controls ---
  const togglePlayFile = (file: File) => {
    if (!audioRef.current) return;

    // If clicking same file, toggle pause/play
    if (playingFile?.name === file.name) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        audioRef.current.play();
        setIsPlaying(true);
      }
      return;
    }

    // New file
    if (audioRef.current.src) URL.revokeObjectURL(audioRef.current.src);
    const url = URL.createObjectURL(file);
    audioRef.current.src = url;
    audioRef.current.play();
    setPlayingFile(file);
    setIsPlaying(true);
    setPlayingBlock(null);
  };

  const playTranscriptSegment = (file: File, startTime: number, endTime: number) => {
    if (!audioRef.current) return;

    // Toggle pause if clicking the currently playing block
    if (playingFile?.name === file.name && playingBlock?.start === startTime && isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
      return;
    }

    try {
      if (playingFile?.name !== file.name) {
        if (audioRef.current.src) URL.revokeObjectURL(audioRef.current.src);
        const url = URL.createObjectURL(file);
        audioRef.current.src = url;
        setPlayingFile(file);
      }

      audioRef.current.currentTime = startTime;
      const playPromise = audioRef.current.play();

      if (playPromise !== undefined) {
        playPromise.then(() => {
          setIsPlaying(true);
          setPlayingBlock({ start: startTime, end: endTime });
        }).catch(err => {
          console.error("Playback error:", err);
        });
      }
    } catch (err) {
      console.error("Source error:", err);
      // If file object is lost (e.g. from history), we might need to prompt or handle differently
    }
  };

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
      setPlayingFile(null);
    }
  };

  const openOutputFolder = async () => {
    try {
      await fetch('http://127.0.0.1:8000/open-folder', { method: 'POST' });
    } catch (err) {
      console.error(err);
    }
  };

  const dismissWelcome = () => {
    setAppState('EMPTY');
  };

  const resetToNew = () => {
    stopAudio();
    setQueue([]);
    setCompletedSessions([]);
    setAppState('EMPTY');
  };

  const exportToWord = () => {
    const session = completedSessions[activeResultIndex];
    if (!session || !session.transcript) return;

    let content = `
      <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
      <head><meta charset='utf-8'><title>${session.file.name}</title>
      <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; padding: 40px; }
        .header { text-align: center; border-bottom: 2px solid #0F172A; padding-bottom: 20px; margin-bottom: 30px; }
        .footer { text-align: center; font-size: 10px; color: #94A3B8; margin-top: 50px; border-top: 1px solid #E2E8F0; padding-top: 10px; }
        .meta { color: #64748B; font-size: 12px; margin-bottom: 30px; background: #F8FAFC; padding: 15px; border-radius: 10px; }
        .segment { margin-bottom: 25px; page-break-inside: avoid; }
        .speaker { font-weight: bold; color: #0F172A; font-size: 14px; }
        .timestamp { color: #4F46E5; font-size: 11px; margin-left: 10px; }
        .text { margin-top: 5px; color: #334155; }
      </style>
      </head>
      <body>
        <div class="header">
          <h1 style="color: #0F172A; margin-bottom: 5px;">PAÜ İİBF Transkripsiyon Raporu</h1>
          <p style="color: #64748B; margin-top: 0;">Yapay Zeka ve Dijital Uygulamalar Koordinatörlüğü</p>
        </div>
        <div class="meta">
          <p><strong>Dosya Adı:</strong> ${session.file.name}</p>
          <p><strong>İşlem Tarihi:</strong> ${new Date().toLocaleString('tr-TR')}</p>
          <p><strong>Toplam Süre:</strong> ${formatDuration(session.transcript.duration)}</p>
        </div>
    `;

    session.transcript.blocks.forEach((block: any) => {
      content += `
        <div class="segment">
          <p><span class="speaker">${block.speaker || 'KONUŞMACI'}</span> <span class="timestamp">[${new Date(block.start_time * 1000).toISOString().substr(11, 8)}]</span></p>
          <p class="text">${block.text}</p>
        </div>
      `;
    });

    content += `
        <div class="footer">
          <p>© ${new Date().getFullYear()} Pamukkale Üniversitesi İİBF - Bu rapor yapay zeka tarafından oluşturulmuştur.</p>
        </div>
      </body></html>`;

    const blob = new Blob(['\ufeff', content], { type: 'application/msword' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${session.file.name.split('.')[0]}_Transkript.doc`;
    link.click();
    URL.revokeObjectURL(url);
  };


  const navItems = [
    { id: 'MAIN', label: 'Ana İşlem', icon: Home },
    { id: 'HISTORY', label: 'Geçmiş', icon: Clock },
    { id: 'SETTINGS', label: 'Ayarlar', icon: Settings },
    { id: 'HELP', label: 'Yardım', icon: HelpCircle },
    { id: 'ABOUT', label: 'Hakkında', icon: Info },
  ] as const;

  return (
    <div className="h-screen w-full flex bg-[var(--color-surface-bg)] text-[#0F172A] font-sans relative overflow-hidden min-w-[1400px]">
      {/* Electron Titlebar Drag Region */}
      <div className="absolute top-0 left-0 w-full h-6 z-[9999]" style={{ WebkitAppRegion: 'drag' } as any} />

      {/* Hidden Global Audio Player */}
      <audio
        ref={audioRef}
        onEnded={() => { setIsPlaying(false); setPlayingBlock(null); }}
        onPause={() => setIsPlaying(false)}
        onPlay={() => setIsPlaying(true)}
        className="hidden"
      />

      {/* Update Toast Notifications */}
      <AnimatePresence>
        {showUpdateToast && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
            className="fixed bottom-10 left-1/2 -translate-x-1/2 z-[9999] bg-[#0F172A] text-white px-6 py-4 rounded-2xl shadow-2xl flex items-center gap-3 border border-slate-700/50 backdrop-blur-xl"
          >
            <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center">
              <RefreshCw className={`w-5 h-5 text-indigo-400 ${updateStatus.type === 'checking' ? 'animate-spin' : ''}`} />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-bold">
                {updateStatus.type === 'checking' && 'Güncellemeler denetleniyor...'}
                {updateStatus.type === 'available' && `Yeni versiyon bulundu: v${updateStatus.version}`}
                {updateStatus.type === 'latest' && 'Uygulamanız güncel.'}
                {updateStatus.type === 'downloaded' && 'Güncelleme indirildi ve hazır.'}
              </span>
              <span className="text-[10px] text-slate-400">
                {updateStatus.type === 'available' && 'Arka planda indiriliyor...'}
                {updateStatus.type === 'downloaded' && 'Yüklemek için hazır.'}
                {updateStatus.type === 'latest' && 'En son özellikleri kullanıyorsunuz.'}
              </span>
            </div>
            {updateStatus.type === 'downloaded' && (
              <button
                onClick={() => {
                  // @ts-ignore
                  const { ipcRenderer } = window.require('electron');
                  ipcRenderer.send('install-update');
                }}
                className="ml-2 px-3 py-1.5 bg-indigo-500 hover:bg-indigo-600 text-white text-[10px] font-bold rounded-lg transition-colors shadow-lg shadow-indigo-500/20"
              >
                Şimdi Yükle
              </button>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Full Screen Completion Popup */}
      <AnimatePresence>
        {showCompletionModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[10000] bg-[#0F172A]/60 backdrop-blur-md flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              className="bg-white rounded-[2rem] p-10 max-w-sm w-full text-center shadow-2xl border border-white"
            >
              <div className="w-20 h-20 bg-emerald-50 rounded-full flex items-center justify-center mx-auto mb-6">
                <CheckCircle className="w-10 h-10 text-emerald-500" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900 mb-2">İşlem Tamamlandı</h2>
              <p className="text-slate-500 mb-8 text-sm">Tüm dosyalarınız başarıyla metin formatına çevrildi ve hazırlandı.</p>
              <button
                onClick={() => setShowCompletionModal(false)}
                className="w-full bg-[#0F172A] hover:bg-slate-800 text-white font-medium py-4 rounded-2xl transition-colors shadow-lg flex items-center justify-center gap-2"
              >
                Sonuçları Görüntüle <ArrowRight className="w-4 h-4" />
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Dark Sidebar */}
      <aside className="w-64 bg-[#0F172A] flex flex-col justify-between border-r border-[#1E293B] shadow-2xl z-20 shrink-0">
        <div className="p-6 pb-2">
          <div className="flex items-center gap-3 mb-6">
            <img src={pauLogo} alt="PAU" className="h-20 w-auto filter brightness-0 invert opacity-90" />
            <img src={iibfLogo} alt="IIBF" className="h-20 w-auto filter brightness-0 invert opacity-90" />
          </div>
          <h1 className="text-[#F8FAFC] font-semibold text-sm tracking-wide">Pamukkale Üniversitesi İktisadi ve İdari Bilimler Fakültesi</h1>
          <p className="text-[#64748B] text-xs mt-1">Sesten Metne Döküm Aracı</p>
          <p className="text-[#64748B] text-xs mt-1">Versiyon: 0.1.0-alpha.1</p>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  setActiveTab(item.id);
                  if (item.id === 'MAIN' && appState !== 'WELCOME') {
                    if (appState === 'EMPTY') setAppState('EMPTY');
                  }
                }}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200
                  ${isActive
                    ? 'bg-[#1E293B] text-white shadow-inner border border-[#334155]/50'
                    : 'text-[#94A3B8] hover:text-white hover:bg-[#1E293B]/50'
                  }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-[var(--color-primary)]' : ''}`} />
                <span className={`text-sm font-medium ${isActive ? 'font-semibold' : ''}`}>{item.label}</span>
                {isActive && (
                  <motion.div
                    layoutId="activeTabIndicator"
                    className="absolute left-0 w-1 h-8 bg-[var(--color-primary)] rounded-r-full"
                  />
                )}
              </button>
            );
          })}
        </nav>

        <div className="p-6 border-t border-[#1E293B]/50">
          <p className="text-[#64748B] text-xs text-center font-mono">
            &copy; {new Date().getFullYear()} PAÜ İİBF</p>
          <p className="text-[#64748B] text-xs text-center font-mono">Yapay Zeka ve Dijital Uygulamalar Koordinatörlüğü</p>
        </div>
      </aside>

      {/* Main Canvas Area */}
      <main className="flex-1 relative overflow-hidden flex flex-col bg-transparent z-0">

        {/* Dynamic header for states other than Welcome */}
        {activeTab === 'MAIN' && appState !== 'WELCOME' && appState !== 'EMPTY' && (
          <div className="w-full px-10 py-6 mb-2 bg-white/50 backdrop-blur-xl border-b border-white/60 shadow-[0_4px_30px_rgba(0,0,0,0.02)] relative z-20 flex items-center justify-between">
            <h1 className="text-xl font-bold text-[#0F172A] tracking-tight flex items-center gap-3">
              Çalışma Alanı
            </h1>
          </div>
        )}
        {activeTab === 'HISTORY' && (
          <div className="flex-1 overflow-y-auto p-12 bg-white/50 backdrop-blur-xl relative z-10 [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-slate-200 hover:[&::-webkit-scrollbar-thumb]:bg-slate-300 [&::-webkit-scrollbar-thumb]:rounded-full">
            <ParticleBackground />
            <div className="max-w-4xl mx-auto relative z-10">
              <div className="mb-8">
                <h2 className="text-3xl font-bold tracking-tight text-slate-900 mb-2">Geçmiş Analizler</h2>
                <p className="text-slate-500">Daha önce işlenmiş dosyalarınıza ve analiz sonuçlarına buradan ulaşabilirsiniz.</p>
              </div>

              {isLoadingHistory ? (
                <div className="flex flex-col items-center justify-center py-20 opacity-50">
                  <div className="w-10 h-10 border-4 border-slate-200 border-t-[var(--color-primary)] rounded-full animate-spin mb-4" />
                  <p className="font-medium text-slate-500">Geçmiş yükleniyor...</p>
                </div>
              ) : historyItems.length === 0 ? (
                <div className="bg-white/60 backdrop-blur-md rounded-3xl border border-white p-16 text-center shadow-lg">
                  <div className="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <Database className="w-10 h-10 text-slate-400" />
                  </div>
                  <h3 className="text-xl font-bold text-slate-800 mb-2">Henüz Veri Yok</h3>
                  <p className="text-slate-500 max-w-md mx-auto">Daha önce analiz edilmiş herhangi bir dosya bulunamadı. Yeni bir dosya işlediğinizde sonuçlar burada görünecektir.</p>
                </div>
              ) : (
                <div className="grid gap-4">
                  {historyItems.map((item, idx) => (
                    <div key={idx} className="bg-white/60 backdrop-blur-md rounded-2xl border border-white hover:border-blue-200 hover:shadow-xl transition-all p-6 flex items-center justify-between group cursor-pointer" onClick={() => loadFromHistory(item)}>
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-full bg-blue-50 text-[var(--color-primary)] flex items-center justify-center group-hover:scale-110 transition-transform">
                          <FolderOpen className="w-6 h-6" />
                        </div>
                        <div>
                          <h4 className="font-bold text-slate-800 text-lg mb-1">{item.filename}</h4>
                          <div className="flex gap-4 text-xs font-medium text-slate-500">
                            <span>Tarih: {new Date(item.created_at * 1000).toLocaleString('tr-TR')}</span>
                            <span>Boyut: {formatBytes(item.file_size)}</span>
                            <span>Süre: {formatDuration(item.transcript?.duration || 0)}</span>
                          </div>
                        </div>
                      </div>
                      <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                        <button className="flex items-center gap-2 bg-[#0F172A] text-white px-4 py-2 rounded-xl text-sm font-medium hover:scale-105 transition-transform shadow-md">
                          Sonuçları Gör <ArrowRight className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'SETTINGS' && (
          <div className="flex-1 overflow-y-auto p-12 bg-[#F8FAFC]">
            <div className="max-w-4xl mx-auto space-y-10">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-3xl font-bold tracking-tight text-slate-900 mb-2">Ayarlar</h2>
                  <p className="text-slate-500 text-sm">Transkripsiyon motorunu ve donanım kullanımını buradan yapılandırabilirsiniz.</p>
                </div>
                <div className="bg-blue-50 px-4 py-2 rounded-2xl border border-blue-100 flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                  <span className="text-xs font-bold text-blue-600 uppercase tracking-wider">Yerel Çalışma Modu</span>
                </div>
              </div>

              <div className="space-y-6">
                <div className="flex items-center gap-2 mb-2">
                  <Cpu className="w-5 h-5 text-slate-400" />
                  <h3 className="font-bold text-slate-800 uppercase text-xs tracking-widest">Yapay Zeka Modeli Seçimi</h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {['faster-whisper-tiny', 'faster-whisper-base', 'faster-whisper-medium', 'faster-whisper-large-v2'].map(model => (
                    <div
                      key={model}
                      onClick={() => saveConfig({ ...config, model_name: model })}
                      className={`relative p-6 rounded-[1.5rem] border-2 cursor-pointer transition-all duration-300 group
                        ${config.model_name === model
                          ? 'bg-white border-[var(--color-primary)] shadow-[0_20px_50px_rgba(79,70,229,0.15)] ring-1 ring-[var(--color-primary)]/20'
                          : 'bg-white border-transparent hover:border-slate-200 shadow-sm hover:shadow-md'}`}
                    >
                      <div className="flex justify-between items-start mb-4">
                        <div className="flex items-center gap-3">
                          <div className={`p-2 rounded-xl ${config.model_name === model ? 'bg-indigo-50 text-indigo-600' : 'bg-slate-50 text-slate-400 group-hover:bg-slate-100'}`}>
                            <Database className="w-5 h-5" />
                          </div>
                          <div>
                            <span className="font-bold text-slate-900 block">{model.split('-').pop()?.toUpperCase()}</span>
                            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">{MODEL_SIZES[model]}</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {model === 'faster-whisper-medium' && (
                            <span className="bg-emerald-50 text-emerald-600 text-[10px] px-2.5 py-1 rounded-lg font-bold">EN İYİ SEÇENEK</span>
                          )}
                          <div className="relative group/info">
                            <Info className="w-4 h-4 text-slate-300 hover:text-slate-600 transition-colors" />
                            <div className="absolute bottom-full right-0 mb-3 w-64 p-4 bg-slate-900 text-white text-[11px] rounded-2xl shadow-2xl opacity-0 invisible group-hover/info:opacity-100 group-hover/info:visible transition-all duration-300 z-50 leading-relaxed border border-white/10 backdrop-blur-sm">
                              <div className="font-bold mb-2 text-indigo-300 uppercase tracking-widest border-b border-white/10 pb-2 flex items-center gap-2">
                                <Zap className="w-3 h-3" /> Teknik Bilgi
                              </div>
                              {MODEL_DETAILS[model].technical}
                              <div className="absolute top-full right-4 border-8 border-transparent border-t-slate-900"></div>
                            </div>
                          </div>
                        </div>
                      </div>
                      <p className="text-sm text-slate-600 font-medium leading-snug">
                        {MODEL_DETAILS[model].summary}
                      </p>

                      {config.model_name === model && (
                        <div className="absolute -top-2 -right-2 bg-[var(--color-primary)] text-white p-1 rounded-full shadow-lg">
                          <CheckCircle className="w-4 h-4" />
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-6 border-t border-slate-200">
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Zap className="w-5 h-5 text-slate-400" />
                    <h3 className="font-bold text-slate-800 uppercase text-xs tracking-widest">Donanım Hızlandırma</h3>
                  </div>
                  <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
                    <select
                      value={config.device}
                      onChange={(e) => saveConfig({ ...config, device: e.target.value })}
                      className="w-full p-4 rounded-2xl border-2 border-slate-100 bg-slate-50 text-sm font-semibold focus:outline-none focus:border-indigo-500/50 focus:bg-white transition-all appearance-none cursor-pointer"
                    >
                      <option value="auto">Otomatik Algıla (Önerilen)</option>
                      <option value="cuda">NVIDIA GPU (En Hızlı)</option>
                      <option value="cpu">İşlemci / CPU (Güvenli Mod)</option>
                    </select>
                    <p className="text-[10px] text-slate-400 mt-4 leading-relaxed italic">
                      Uygulama, sisteminizdeki en uygun donanımı otomatik olarak seçecektir. NVIDIA kartınız yoksa "İşlemci" modu kullanılacaktır.
                    </p>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Languages className="w-5 h-5 text-slate-400" />
                    <h3 className="font-bold text-slate-800 uppercase text-xs tracking-widest">Dil Ayarları</h3>
                  </div>
                  <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
                    <select
                      value={config.default_language}
                      onChange={(e) => saveConfig({ ...config, default_language: e.target.value })}
                      className="w-full p-4 rounded-2xl border-2 border-slate-100 bg-slate-50 text-sm font-semibold focus:outline-none focus:border-indigo-500/50 focus:bg-white transition-all appearance-none cursor-pointer"
                    >
                      <option value="auto">Otomatik Dil Algılama</option>
                      <option value="tr">Türkçe</option>
                      <option value="en">İngilizce</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'HELP' && (
          <div className="flex-1 overflow-y-auto p-12 bg-[#F8FAFC]">
            <div className="max-w-4xl mx-auto space-y-12">
              <div className="text-center space-y-4 mb-12">
                <div className="w-16 h-16 bg-indigo-100 text-indigo-600 rounded-2xl flex items-center justify-center mx-auto shadow-sm">
                  <HelpCircle className="w-8 h-8" />
                </div>
                <h2 className="text-3xl font-bold tracking-tight text-slate-900">Yardım & Kullanım Kılavuzu</h2>
                <p className="text-slate-500 max-w-xl mx-auto italic">
                  Sistemle ilgili teknik detaylar ve en iyi sonuçları alma yöntemleri.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Section 1: Workflow */}
                <div className="bg-white p-8 rounded-[2rem] border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="w-10 h-10 bg-slate-50 text-slate-400 rounded-xl flex items-center justify-center shrink-0">
                      <MousePointer2 className="w-5 h-5" />
                    </div>
                    <h3 className="text-lg font-bold text-slate-800">1. Nasıl Başlanır?</h3>
                  </div>
                  <p className="text-sm text-slate-600 leading-relaxed space-y-2">
                    Ana işlem ekranındaki geniş alana ses veya video dosyalarınızı <strong>sürükleyip bırakabilir</strong> veya
                    tıklayarak bilgisayarınızdan seçebilirsiniz. Çoklu dosya seçimi yaparak bir liste oluşturabilirsiniz.
                  </p>
                </div>

                {/* Section 2: Models */}
                <div className="bg-white p-8 rounded-[2rem] border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="w-10 h-10 bg-slate-50 text-slate-400 rounded-xl flex items-center justify-center shrink-0">
                      <Database className="w-5 h-5" />
                    </div>
                    <h3 className="text-lg font-bold text-slate-800">2. Doğru Model Seçimi</h3>
                  </div>
                  <div className="text-sm text-slate-600 leading-relaxed space-y-3">
                    <p><strong>Medium (Önerilen):</strong> Akademik çalışmalar ve mülakatlar için en dengeli modeldir.</p>
                    <p><strong>Large-V2:</strong> En yüksek doğruluk oranına sahiptir ancak güçlü donanım gerektirir.</p>
                    <p><strong>Tiny/Base:</strong> Çok hızlıdır, önizleme için uygundur.</p>
                  </div>
                </div>

                {/* Section 3: Hardware */}
                <div className="bg-white p-8 rounded-[2rem] border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="w-10 h-10 bg-slate-50 text-slate-400 rounded-xl flex items-center justify-center shrink-0">
                      <Zap className="w-5 h-5" />
                    </div>
                    <h3 className="text-lg font-bold text-slate-800">3. Donanım ve Hız</h3>
                  </div>
                  <p className="text-sm text-slate-600 leading-relaxed">
                    Sistem, NVIDIA ekran kartınız varsa otomatik olarak <strong>CUDA</strong> teknolojisini kullanarak 10 kat daha hızlı çalışır.
                    Eğer kartınız yoksa uygulama hata vermez, sessizce işlemciniz (CPU) üzerinden güvenli modda çalışmaya devam eder.
                  </p>
                </div>

                {/* Section 4: Privacy */}
                <div className="bg-white p-8 rounded-[2rem] border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="w-10 h-10 bg-slate-50 text-slate-400 rounded-xl flex items-center justify-center shrink-0">
                      <ShieldCheck className="w-5 h-5" />
                    </div>
                    <h3 className="text-lg font-bold text-slate-800">4. Veri Gizliliği</h3>
                  </div>
                  <p className="text-sm text-slate-600 leading-relaxed">
                    <strong>Sistem tamamen yerel çalışır.</strong> Dosyalarınız hiçbir uzak sunucuya yüklenmez, internete gönderilmez.
                    Tüm işlemler bilgisayarınızın içinde gerçekleşir, bu da görüşmelerinizin ve akademik verilerinizin tam güvenliğini sağlar.
                  </p>
                </div>

                {/* Section 5: Tips */}
                <div className="bg-[#0F172A] p-8 rounded-[2rem] text-white shadow-xl md:col-span-2 flex flex-col md:flex-row gap-8 items-center">
                  <div className="w-16 h-16 bg-white/10 text-white rounded-2xl flex items-center justify-center shrink-0">
                    <Star className="w-8 h-8 text-amber-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold mb-2">Kullanım İpuçları</h3>
                    <ul className="text-sm text-slate-300 space-y-2 list-disc pl-4 leading-relaxed">
                      <li>Ses kaydındaki gürültünün az olması çözümleme doğruluğunu artırır.</li>
                      <li>Mikrofonun konuşmacıya yakın olduğu kayıtlar en iyi sonucu verir.</li>
                      <li>Analiz bittiğinde, her cümlenin yanındaki <strong>Oynat</strong> butonuyla sesin o anını dinleyip metni doğrulayabilirsiniz.</li>
                      <li>Çıktılar bilgisayarınızda otomatik olarak saklanır.</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'ABOUT' && (
          <div className="flex-1 flex items-center justify-center p-12">
            <div className="max-w-md w-full bg-white p-10 rounded-3xl border border-[var(--color-border-light)] shadow-sm text-center">
              <div className="flex justify-center gap-4 mb-8">
                <img src={pauLogo} alt="PAU" className="h-20 w-auto" />
                <img src={iibfLogo} alt="IIBF" className="h-20 w-auto" />
              </div>
              <h2 className="text-2xl font-bold mb-2">PAÜ İİBF Transkripsiyon Aracı</h2>
              <p className="text-sm text-[#64748B] mb-6">Versiyon 0.1.0-alpha.1 • Deneme Sürümü</p>
              <div className="bg-[#F8FAFC] p-4 rounded-xl border border-[var(--color-border-light)] text-sm text-left space-y-3">
                <p><strong>Geliştirici:</strong></p>
                <p>Pamukkale Üniversitesi - İktisadi ve İdari Bilimler Fakültesi</p>
                <p>Yapay Zeka ve Dijital Uygulamalar Koordinatörlüğü</p>
                <p><strong>Mimari:</strong></p>
                <p>React, Electron, FastAPI, faster-whisper</p>
                <p className="text-[#64748B] mb-2">Dönüt ve önerileriniz için <a href="mailto:iibf_yzkoord@pau.edu.tr" className="text-blue-600 hover:underline">iibf_yzkoord@pau.edu.tr</a> adresine e-posta gönderebilirsiniz.</p>

                <div className="pt-4 border-t border-slate-100 flex justify-center">
                  <button
                    onClick={checkForUpdates}
                    disabled={isCheckingUpdates}
                    className={`flex items-center gap-2 px-6 py-3 rounded-xl font-bold transition-all
                      ${isCheckingUpdates
                        ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                        : 'bg-indigo-50 text-indigo-600 hover:bg-indigo-100 active:scale-95 shadow-sm hover:shadow-md'}`}
                  >
                    <RefreshCw className={`w-4 h-4 ${isCheckingUpdates ? 'animate-spin' : ''}`} />
                    {isCheckingUpdates ? 'Kontrol Ediliyor...' : 'Güncellemeleri Denetle'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'MAIN' && (
          <div className="flex-1 flex flex-col relative z-10 h-full min-h-0">
            <ParticleBackground />
            <div className="flex-1 flex items-center justify-center p-8 relative z-10 min-h-0 overflow-hidden">
              <AnimatePresence mode="wait">
                {appState === 'WELCOME' && (
                  <motion.div
                    key="welcome"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0, filter: 'blur(10px)' }}
                    transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
                    className="absolute inset-0 z-50 bg-[#0F172A] text-white flex overflow-hidden font-sans"
                  >
                    {/* Left Side: Content %55 */}
                    <div className="w-[55%] flex flex-col justify-center p-12 lg:p-20 relative z-10 overflow-hidden">
                      {/* Hero Content */}
                      <div className="max-w-2xl">
                        <h1 className="text-3xl lg:text-4xl font-semibold tracking-tight text-white mb-4 leading-[1.15]">
                          Ses Verisinden Yapılandırılmış Nitel Analiz Çıktılarına
                        </h1>
                        <p className="text-sm lg:text-base text-[#A1A1AA] leading-relaxed mb-8 max-w-xl">
                          Görüşme, odak grup ve saha kayıtlarınızı ham metinden öteye taşıyın. Sistem, ses verisini doğrudan MAXQDA ve ATLAS.ti gibi nitel veri analizi (CAQDAS) programlarına entegre edilebilir, zaman damgalı ve analize hazır formatlara dönüştürür. Çözümleme süreci dış sunuculara ihtiyaç duymadan tamamen yerel donanımınızda gerçekleşir.
                        </p>

                        {/* Value Blocks */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10">
                          <div className="border-l border-[#27272A] pl-3">
                            <h3 className="text-sm font-medium text-white mb-1">Tamamen Yerel</h3>
                            <p className="text-xs text-[#71717A] leading-relaxed">Verileriniz internete yüklenmez, cihazınızda kapalı devre işlenir.</p>
                          </div>
                          <div className="border-l border-[#27272A] pl-3">
                            <h3 className="text-sm font-medium text-white mb-1">CAQDAS Uyumlu</h3>
                            <p className="text-xs text-[#71717A] leading-relaxed">MAXQDA için zaman damgalı, yapılandırılmış çıktılar üretir.</p>
                          </div>
                          <div className="border-l border-[#27272A] pl-3">
                            <h3 className="text-sm font-medium text-white mb-1">Kesintisiz Akış</h3>
                            <p className="text-xs text-[#71717A] leading-relaxed">Birden fazla veri kuyruk mimarisiyle arka planda otomatik işlenir.</p>
                          </div>
                        </div>

                        {/* CTA */}
                        <button
                          onClick={dismissWelcome}
                          className="group relative inline-flex items-center justify-center bg-white text-black px-6 py-3.5 text-sm font-medium transition-all hover:bg-[#E4E4E7] rounded-sm"
                        >
                          Çalışma Alanını Başlat
                          <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                        </button>
                      </div>
                    </div>

                    {/* Right Side: Visual Concept %45 */}
                    <div className="w-[45%] bg-[#0B1121] border-l border-[#1E293B] relative overflow-hidden flex items-center justify-center shadow-inner">
                      <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 to-transparent" />

                      {/* Abstract Waveform to Graph Animation */}
                      <div className="relative w-full h-full flex items-center justify-center">

                        {/* HUGE Central Logo */}
                        <motion.div
                          className="absolute z-20"
                          animate={{ y: [0, -10, 0] }}
                          transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                        >
                          <img
                            src={iibfTranskriptLogo}
                            alt="PAU IIBF"
                            className="w-64 lg:w-80 h-auto object-contain"
                            style={{ filter: 'drop-shadow(0 0 20px rgba(99, 102, 241, 0.2))' }}
                          />
                        </motion.div>
                        {/* Left raw wave lines */}
                        <div className="absolute left-0 flex flex-col gap-6 opacity-20">
                          {[...Array(12)].map((_, i) => (
                            <motion.div
                              key={`wave-${i}`}
                              className="h-[1px] bg-indigo-400"
                              initial={{ width: 10 }}
                              animate={{ width: [10, 80 + Math.random() * 120, 10] }}
                              transition={{ duration: 1.5 + Math.random() * 2, repeat: Infinity, ease: "easeInOut" }}
                            />
                          ))}
                        </div>

                        {/* Middle transformation nodes */}
                        <div className="absolute left-1/3 flex flex-col gap-12 opacity-40">
                          {[...Array(5)].map((_, i) => (
                            <motion.div
                              key={`node-${i}`}
                              className="w-1.5 h-1.5 rounded-full bg-indigo-500 shadow-[0_0_15px_rgba(99,102,241,0.5)]"
                              animate={{ scale: [1, 2, 1], opacity: [0.3, 1, 0.3] }}
                              transition={{ duration: 1.5 + Math.random(), repeat: Infinity }}
                            />
                          ))}
                        </div>

                        {/* Right structured data blocks */}
                        <div className="absolute right-16 flex flex-col gap-6">
                          {[...Array(6)].map((_, i) => (
                            <motion.div
                              key={`block-${i}`}
                              className="h-10 w-56 bg-[#18181B] border border-[#27272A] rounded flex items-center px-4 gap-3 shadow-lg"
                              initial={{ x: 20, opacity: 0 }}
                              animate={{ x: 0, opacity: 1 }}
                              transition={{ delay: i * 0.2, duration: 0.8 }}
                            >
                              <div className="w-1.5 h-3.5 bg-indigo-500/50 rounded-full" />
                              <div className="flex flex-col gap-1.5 w-full">
                                <div className="w-full h-1 bg-[#27272A] rounded-full" />
                                <div className="w-2/3 h-1 bg-[#27272A] rounded-full" />
                              </div>
                            </motion.div>
                          ))}
                        </div>

                        {/* Connecting SVG lines */}
                        <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-10">
                          <motion.path
                            d="M 100 300 C 200 300, 300 150, 500 150"
                            stroke="#6366F1" strokeWidth="1" fill="none"
                            initial={{ pathLength: 0 }}
                            animate={{ pathLength: 1 }}
                            transition={{ duration: 3, repeat: Infinity }}
                          />
                          <motion.path
                            d="M 100 450 C 250 450, 300 350, 500 350"
                            stroke="#6366F1" strokeWidth="1" fill="none"
                            initial={{ pathLength: 0 }}
                            animate={{ pathLength: 1 }}
                            transition={{ duration: 4, repeat: Infinity }}
                          />
                          <motion.path
                            d="M 100 600 C 200 600, 350 750, 500 750"
                            stroke="#6366F1" strokeWidth="1" fill="none"
                            initial={{ pathLength: 0 }}
                            animate={{ pathLength: 1 }}
                            transition={{ duration: 3.5, repeat: Infinity }}
                          />
                        </svg>
                      </div>
                    </div>
                  </motion.div>
                )}

                {appState === 'EMPTY' && (
                  <motion.div
                    key="empty"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0, filter: 'blur(10px)' }}
                    transition={{ duration: 0.6 }}
                    className="absolute inset-0 z-20 flex items-center justify-center overflow-hidden"
                  >

                    {/* Floating Abstract Elements */}
                    <div className="absolute inset-0 pointer-events-none">
                      <motion.div
                        className="absolute top-1/4 left-[15%] w-32 h-40 bg-white/40 backdrop-blur-md border border-white/60 rounded-2xl shadow-[0_8px_32px_rgba(0,0,0,0.05)] p-4 flex flex-col gap-3"
                        animate={{ y: [0, -20, 0], rotate: [-2, 2, -2] }}
                        transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
                      >
                        <div className="w-full h-2 bg-slate-200 rounded-full" />
                        <div className="w-3/4 h-2 bg-slate-200 rounded-full" />
                        <div className="mt-auto flex items-end gap-1">
                          <div className="w-1.5 h-4 bg-indigo-400 rounded-sm" />
                          <div className="w-1.5 h-8 bg-indigo-500 rounded-sm" />
                          <div className="w-1.5 h-6 bg-indigo-300 rounded-sm" />
                        </div>
                      </motion.div>

                      <motion.div
                        className="absolute bottom-1/3 right-[15%] w-40 h-24 bg-white/40 backdrop-blur-md border border-white/60 rounded-2xl shadow-[0_8px_32px_rgba(0,0,0,0.05)] p-4 flex items-center justify-center gap-2"
                        animate={{ y: [0, 25, 0], rotate: [2, -1, 2] }}
                        transition={{ duration: 7, repeat: Infinity, ease: "easeInOut", delay: 1 }}
                      >
                        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                          <Play className="w-4 h-4 text-blue-500 ml-0.5" />
                        </div>
                        <div className="flex-1 space-y-2">
                          <div className="w-full h-1.5 bg-slate-200 rounded-full" />
                          <div className="w-2/3 h-1.5 bg-slate-200 rounded-full" />
                        </div>
                      </motion.div>
                    </div>

                    {/* Invisible Input */}
                    <input
                      type="file"
                      ref={fileInputRef}
                      className="hidden"
                      accept="audio/*,video/*"
                      multiple
                      onChange={(e) => addToQueue(e.target.files)}
                    />

                    {/* Central Glassmorphic Portal (Dropzone) */}
                    <motion.div
                      className="relative z-10 w-[32rem] h-[32rem] flex items-center justify-center group cursor-pointer"
                      onDragEnter={handleDrag}
                      onDragLeave={handleDrag}
                      onDragOver={handleDrag}
                      onDrop={(e) => {
                        e.preventDefault(); e.stopPropagation(); setDragActive(false);
                        addToQueue(e.dataTransfer.files);
                      }}
                      onClick={() => fileInputRef.current?.click()}
                    >
                      {/* Orbital Rings */}
                      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                        <motion.div
                          className={`absolute rounded-full border border-indigo-200 border-dashed transition-all duration-700 ${dragActive ? 'w-[36rem] h-[36rem] opacity-80' : 'w-[28rem] h-[28rem] opacity-40'}`}
                          animate={{ rotate: 360 }}
                          transition={{ duration: dragActive ? 10 : 30, repeat: Infinity, ease: "linear" }}
                        />
                        <motion.div
                          className={`absolute rounded-full border border-blue-300 transition-all duration-700 ${dragActive ? 'w-[32rem] h-[32rem] opacity-60' : 'w-[24rem] h-[24rem] opacity-20'}`}
                          animate={{ rotate: -360 }}
                          transition={{ duration: dragActive ? 15 : 40, repeat: Infinity, ease: "linear" }}
                        />
                      </div>

                      {/* Core Glass Portal */}
                      <div className={`relative w-[26rem] h-[26rem] rounded-full flex flex-col items-center justify-center text-center transition-all duration-500 overflow-hidden shadow-2xl
                      ${dragActive
                          ? 'bg-blue-50/60 backdrop-blur-2xl border border-blue-300 scale-105 shadow-blue-500/20'
                          : 'bg-white/50 backdrop-blur-xl border border-white/80 hover:bg-white/60 hover:scale-[1.02]'}`}
                      >
                        {/* Inner Glow */}
                        <div className={`absolute inset-0 bg-gradient-to-b from-white/60 to-transparent pointer-events-none transition-opacity ${dragActive ? 'opacity-0' : 'opacity-100'}`} />
                        <div className={`absolute inset-0 bg-gradient-to-b from-blue-400/20 to-indigo-500/20 pointer-events-none transition-opacity duration-500 ${dragActive ? 'opacity-100' : 'opacity-0'}`} />

                        {/* Content inside Portal */}
                        <div className="relative z-10 flex flex-col items-center justify-center p-6">
                          <motion.div
                            className={`mb-6 flex items-center justify-center transition-all duration-500 w-36 h-36
                            ${dragActive ? 'scale-110' : 'opacity-100 hover:scale-105'}`}
                            animate={dragActive ? { y: [0, -5, 0] } : { y: 0 }}
                            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                          >
                            <img src={iibfTranskriptLogo} alt="Logo" className={`h-full w-full object-contain drop-shadow-2xl transition-all duration-500 ${dragActive ? 'brightness-110' : ''}`} />
                          </motion.div>

                          <h2 className={`text-3xl font-bold tracking-tight mb-2 transition-colors duration-500 ${dragActive ? 'text-indigo-900' : 'text-slate-800'}`}>
                            {dragActive ? 'Verileri Bırakın' : 'Ses veya Video Dosyası Yükleyin'}
                          </h2>

                          <p className="text-slate-500 max-w-[16rem] leading-relaxed mb-6 text-base">
                            {dragActive
                              ? 'İşlem anında başlayacaktır...'
                              : 'Dosya sürükleyin veya bilgisayarınızdan seçmek için tıklayın.'}
                          </p>

                          {!dragActive && (
                            <div className="flex gap-2 relative z-10 justify-center">
                              {['MP3', 'MP4', 'WAV'].map(ext => (
                                <span key={ext} className="px-3 py-1 bg-white/60 border border-white/80 rounded-full text-[10px] font-bold text-slate-400 shadow-sm uppercase tracking-widest">
                                  {ext}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </motion.div>

                    {/* Security Badge */}
                    <div className="absolute bottom-8 flex items-center justify-center w-full pointer-events-none z-10">
                      <div className="flex items-center gap-2 text-xs font-medium text-slate-500 px-4 py-2 bg-white/60 backdrop-blur-md rounded-full border border-white/80 shadow-sm">
                        <CheckCircle className="w-4 h-4 text-emerald-500" />
                        Tüm veriler bilgisayarınızda kalır ve lokalde çalışır, üçüncü taraflarla paylaşılmaz.
                      </div>
                    </div>
                  </motion.div>
                )}

                {/* STAGING AREA (Bekleme Odası) */}
                {appState === 'STAGING' && (
                  <motion.div
                    key="staging"
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 1.05, filter: 'blur(10px)' }}
                    transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
                    className="w-full max-w-[1400px] bg-white/70 backdrop-blur-2xl rounded-[2rem] border border-white shadow-2xl flex flex-col overflow-hidden max-h-full relative"
                  >
                    <div className="p-8 pb-0 flex items-center justify-between">
                      <div>
                        <h2 className="text-2xl font-bold">Bekleme Odası</h2>
                        <p className="text-sm text-[#64748B] mt-1">{queue.length} dosya işlenmeyi bekliyor</p>
                      </div>

                      <input
                        type="file"
                        ref={addMoreInputRef}
                        className="hidden"
                        accept="audio/*,video/*"
                        multiple
                        onChange={(e) => addToQueue(e.target.files)}
                      />
                      <button
                        onClick={() => addMoreInputRef.current?.click()}
                        className="flex items-center gap-2 bg-white border border-[#CBD5E1] hover:border-[#94A3B8] px-4 py-2.5 rounded-xl text-sm font-medium transition-colors shadow-sm"
                      >
                        <Plus className="w-4 h-4" /> Yeni Dosya Ekle
                      </button>
                    </div>

                    {/* Queue List */}
                    <div className="flex-1 overflow-y-auto space-y-3 pr-2 mb-8"
                      onDragEnter={handleDrag}
                      onDragLeave={handleDrag}
                      onDragOver={handleDrag}
                      onDrop={(e) => {
                        e.preventDefault(); e.stopPropagation(); setDragActive(false);
                        addToQueue(e.dataTransfer.files);
                      }}
                    >
                      {queue.map((file, idx) => {
                        const isThisPlaying = playingFile?.name === file.name && isPlaying;
                        return (
                          <div key={idx} className="bg-white p-4 rounded-2xl border border-[var(--color-border-light)] shadow-sm flex items-center justify-between group">
                            <div className="flex items-center gap-4 overflow-hidden">
                              <button
                                onClick={() => togglePlayFile(file)}
                                className={`w-10 h-10 rounded-full flex items-center justify-center transition-colors shrink-0
                                ${isThisPlaying ? 'bg-[var(--color-primary)] text-white' : 'bg-[#F1F5F9] text-[#64748B] group-hover:bg-[#E2E8F0]'}`}
                              >
                                {isThisPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 ml-0.5" />}
                              </button>
                              <div className="overflow-hidden">
                                <p className="font-semibold text-sm truncate" title={file.name}>{file.name}</p>
                                <p className="text-xs text-[#64748B]">{formatBytes(file.size)}</p>
                              </div>
                            </div>

                            <button
                              onClick={() => removeFromQueue(idx)}
                              className="p-2 text-[#94A3B8] hover:text-red-500 hover:bg-red-50 rounded-xl transition-colors"
                              title="Listeden Kaldır"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        );
                      })}

                      {/* Drop Target Hint inside Staging */}
                      {dragActive && (
                        <div className="w-full h-24 border-2 border-dashed border-[var(--color-primary)] bg-[var(--color-primary)]/5 rounded-2xl flex items-center justify-center">
                          <p className="text-sm font-medium text-[var(--color-primary)]">Buraya Bırakın</p>
                        </div>
                      )}
                    </div>

                    <div className="relative p-6 border-t border-[var(--color-border-light)] flex justify-center bg-slate-50/30 mt-auto">
                      <button
                        onClick={startTranscription}
                        className="relative overflow-hidden group bg-[#0F172A] hover:bg-[#1E293B] text-white px-12 py-4 rounded-2xl font-bold text-lg shadow-2xl transition-all hover:scale-[1.02] active:scale-95 flex items-center gap-3"
                      >
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]" />
                        Çözümlemeyi Başlat <ArrowRight className="w-5 h-5" />
                      </button>
                    </div>
                  </motion.div>
                )}

                {appState === 'PROCESSING' && (
                  <motion.div
                    key="processing"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20, filter: 'blur(10px)' }}
                    className="flex flex-col items-center"
                  >
                    <div className="relative w-48 h-48 mb-8 flex items-center justify-center">
                      <motion.div
                        animate={{ scale: [1, 1.2, 1], rotate: [0, 90, 180] }}
                        transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                        className="absolute inset-0 bg-gradient-to-tr from-[var(--color-primary)] to-indigo-300 rounded-full blur-3xl opacity-30"
                      />
                      <motion.div
                        animate={{ scale: [1, 1.05, 1] }}
                        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                        className="w-40 h-40 flex items-center justify-center relative z-10"
                      >
                        <img src={iibfTranskriptLogo} alt="Logo" className="w-full h-full object-contain drop-shadow-xl animate-[pulse_3s_ease-in-out_infinite]" />
                      </motion.div>
                    </div>

                    <div className="text-center mb-10 flex flex-col items-center">
                      <h2 className="text-2xl font-bold tracking-tight mb-2 text-slate-800">
                        {isDownloading ? 'Yapay Zeka Modeli Hazırlanıyor' : 'Sinyaller Çözümleniyor'}
                      </h2>
                      <p className="text-[#64748B] mb-8 text-sm">
                        {isDownloading
                          ? `İlk kullanım için gerekli ${config.model_name.split('-').pop()?.toUpperCase()} modeli indiriliyor (yaklaşık ${MODEL_SIZES[config.model_name] || '1.5GB'}). Lütfen bekleyiniz...`
                          : <><span className="font-semibold text-slate-700">{queue.length}</span> dosyadan <span className="font-semibold text-[var(--color-primary)]">{currentIndex + 1}.</span> işleniyor</>
                        }
                      </p>

                      {/* Progress Bar Container */}
                      <div className="w-80 lg:w-96">
                        <div className="flex justify-between text-[10px] font-bold text-slate-400 mb-2 uppercase tracking-widest">
                          <span>{isDownloading ? 'İNDİRİLİYOR' : 'İŞLENİYOR'}</span>
                          <span>{currentPercent}%</span>
                        </div>
                        <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden border border-slate-200/50 p-[1px]">
                          <motion.div
                            className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-600 rounded-full"
                            initial={{ width: 0 }}
                            animate={{ width: `${currentPercent}%` }}
                            transition={{ duration: 0.5 }}
                          />
                        </div>
                        <p className="text-[10px] text-slate-400 mt-3 font-medium italic">
                          {isDownloading
                            ? 'Bu işlem internet hızınıza bağlı olarak birkaç dakika sürebilir.'
                            : 'İşlem sırasında pencereyi kapatmayınız.'}
                        </p>
                      </div>
                    </div>

                    <div className="flex flex-col items-center gap-3">
                      <div className="flex items-center gap-2 text-sm text-[#64748B] font-mono bg-white px-4 py-2 rounded-full border border-[var(--color-border-light)] shadow-sm">
                        <span className={`w-2 h-2 rounded-full ${isDownloading ? 'bg-amber-400' : 'bg-[var(--color-primary)]'} animate-ping`} />
                        {isDownloading ? 'Kaynaklar indiriliyor...' : `Aktif dosya: ${queue[currentIndex]?.name}`}
                      </div>
                    </div>
                  </motion.div>
                )}

                {appState === 'READY' && completedSessions.length > 0 && (
                  <motion.div
                    key="ready"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="w-full max-w-[1400px] flex gap-8 h-full min-h-0 px-8"
                  >
                    {/* Left: Tab list for completed files */}
                    <div className="w-72 flex flex-col gap-3 min-h-0">
                      <h3 className="font-semibold text-sm uppercase tracking-wider text-slate-500 mb-2 pl-1">İşlenen Dosyalar</h3>
                      <div className="flex-1 overflow-y-auto space-y-3 p-1 pb-4 [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-slate-300/50 hover:[&::-webkit-scrollbar-thumb]:bg-slate-400 [&::-webkit-scrollbar-thumb]:rounded-full">
                        {completedSessions.map((session, idx) => (
                          <button
                            key={idx}
                            onClick={() => setActiveResultIndex(idx)}
                            className={`w-full text-left p-4 rounded-2xl border transition-all ${activeResultIndex === idx
                              ? 'bg-white border-[var(--color-primary)] shadow-md ring-1 ring-[var(--color-primary)]'
                              : 'bg-white/40 backdrop-blur-md border-white/60 hover:bg-white/70 text-slate-700 shadow-sm'
                              }`}
                          >
                            <p className="font-semibold text-sm truncate" title={session.file.name}>{session.file.name}</p>
                            <p className="text-xs mt-1 opacity-70">
                              {formatDuration(session.transcript?.duration || 0)} • {formatBytes(session.file.size)}
                            </p>
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Right: Transcript Canvas and Actions */}
                    <div className="flex-1 flex flex-col gap-4 relative z-10 min-w-0" style={{ width: 'calc(100% - 320px)' }}>
                      <div className="flex-1 bg-white rounded-3xl border border-[var(--color-border-light)] shadow-sm overflow-hidden flex flex-col min-w-0">
                        <div className="p-6 border-b border-[var(--color-border-light)] flex flex-wrap items-center justify-between bg-slate-50/50 gap-4">
                          <div className="flex-1 min-w-0 max-w-full">
                            <h3 className="font-semibold text-lg truncate" title={completedSessions[activeResultIndex].file.name}>
                              {completedSessions[activeResultIndex].file.name}
                            </h3>
                            <div className="flex items-center gap-4 mt-1">
                              <p className="text-xs text-[#64748B]">
                                Süre: {formatDuration(completedSessions[activeResultIndex].transcript?.duration || 0)}
                              </p>
                              <div className="h-3 w-px bg-slate-200" />
                              <div className="relative flex items-center">
                                <Search className="w-3 h-3 absolute left-3 text-slate-400" />
                                <input
                                  type="text"
                                  placeholder="Metin içinde ara..."
                                  value={searchTerm}
                                  onChange={(e) => setSearchTerm(e.target.value)}
                                  className="pl-8 pr-4 py-1.5 bg-white border border-slate-200 rounded-full text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500/20 w-48 transition-all focus:w-64"
                                />
                              </div>
                            </div>
                          </div>
                          <div className="flex gap-2 shrink-0">
                            <button
                              onClick={exportToWord}
                              className="flex items-center gap-2 text-sm font-medium bg-[#4F46E5] text-white hover:bg-indigo-700 px-4 py-2.5 rounded-xl transition-all shadow-md shadow-indigo-200 active:scale-95"
                              title="Word Olarak Dışa Aktar"
                            >
                              <FileText className="w-4 h-4" /> <span>Word</span>
                            </button>
                            <div className="w-px h-10 bg-slate-200 mx-1" />
                            <button
                              onClick={resetToNew}
                              className="flex items-center gap-2 text-sm font-medium bg-white border border-[#CBD5E1] hover:bg-slate-50 px-4 py-2.5 rounded-xl transition-colors shadow-sm text-slate-700"
                            >
                              <Plus className="w-4 h-4" /> Yeni Analiz
                            </button>
                            <button
                              onClick={openOutputFolder}
                              className="flex items-center gap-2 text-sm font-medium bg-[#0F172A] text-white hover:bg-[#1E293B] px-4 py-2.5 rounded-xl transition-colors shadow-sm"
                            >
                              <FolderOpen className="w-4 h-4" /> Çıktılar
                            </button>
                          </div>
                        </div>

                        <div className="p-8 overflow-y-auto flex-1 space-y-8 [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-slate-200 hover:[&::-webkit-scrollbar-thumb]:bg-slate-300 [&::-webkit-scrollbar-thumb]:rounded-full">
                          {completedSessions[activeResultIndex].transcript?.blocks
                            ? completedSessions[activeResultIndex].transcript.blocks
                              .filter((b: any) => b.text.toLowerCase().includes(searchTerm.toLowerCase()))
                              .map((block: any, idx: number) => {
                                const fileObj = completedSessions[activeResultIndex].file;
                                const isThisSegmentPlaying = playingFile?.name === fileObj.name && isPlaying &&
                                  playingBlock?.start === block.start_time;

                                return (
                                  <div key={block.id} className={`group relative p-4 rounded-[1.5rem] transition-all duration-300 ${isThisSegmentPlaying ? 'bg-indigo-50/40 ring-1 ring-indigo-500/20 shadow-sm' : 'hover:bg-slate-50/50'}`}>
                                    <div className={`absolute -left-8 top-5 transition-all duration-300 ${isThisSegmentPlaying ? 'opacity-100 scale-100' : 'opacity-0 scale-90 group-hover:opacity-100 group-hover:scale-100'}`}>
                                      <button
                                        onClick={() => playTranscriptSegment(fileObj, block.start_time, block.end_time)}
                                        className={`p-2 rounded-lg shadow-lg transition-all
                                    ${isThisSegmentPlaying
                                            ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                                            : 'bg-white text-indigo-600 hover:text-white hover:bg-indigo-600 border border-indigo-100'}`}
                                      >
                                        {isThisSegmentPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                                      </button>
                                    </div>
                                    <div className="flex items-baseline gap-3 mb-3">
                                      <span className="font-bold text-xs uppercase tracking-widest text-slate-400">{block.speaker || `KONUŞMACI ${(idx % 2) + 1}`}</span>
                                      <span className="text-[10px] text-indigo-500 font-bold bg-indigo-50 px-2 py-0.5 rounded-full cursor-pointer hover:bg-indigo-100 transition-colors" onClick={() => playTranscriptSegment(fileObj, block.start_time, block.end_time)}>
                                        {new Date(block.start_time * 1000).toISOString().substr(11, 8)}
                                      </span>
                                    </div>
                                    <div className="text-slate-700 leading-relaxed text-[15px] w-full break-words" style={{ overflowWrap: 'anywhere', wordBreak: 'break-word' }}>
                                      {block.words && block.words.length > 0 ? (
                                        <div className="flex flex-wrap gap-x-1.5 gap-y-2 w-full max-w-full">
                                          {block.words.map((word: any, wIdx: number) => {
                                            const isWordActive = isThisSegmentPlaying &&
                                              currentTime >= word.start &&
                                              currentTime <= word.end;

                                            return (
                                              <span
                                                key={wIdx}
                                                className={`transition-all duration-200 rounded-md px-0.5 inline-block
                                              ${isWordActive
                                                    ? 'bg-indigo-600 text-white scale-110 shadow-md font-medium'
                                                    : 'text-slate-700'}`}
                                              >
                                                {word.word}
                                              </span>
                                            );
                                          })}
                                        </div>
                                      ) : (
                                        <p className="break-words w-full">{block.text}</p>
                                      )}
                                    </div>
                                  </div>
                                );
                              }) : (
                              <p className="text-[#64748B] text-center mt-10">Transkript bulunamadı.</p>
                            )}
                        </div>
                      </div>
                    </div>
                  </motion.div>

                )}
              </AnimatePresence>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
