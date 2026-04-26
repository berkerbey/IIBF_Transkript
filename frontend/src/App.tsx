import { useState, useRef, useEffect, useMemo } from 'react';
import { UploadCloud, Settings, Database, ArrowRight, Play, Home, HelpCircle, Info, FolderOpen, CheckCircle, X, Sparkles, Plus, Trash2, Pause, Clock } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

type AppState = 'WELCOME' | 'EMPTY' | 'STAGING' | 'PROCESSING' | 'READY';
type TabState = 'MAIN' | 'HISTORY' | 'SETTINGS' | 'HELP' | 'ABOUT';

function formatDuration(seconds: number) {
  if (!seconds) return "0s";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}s ${m}dk`;
  if (m > 0) return `${m}dk ${s}sn`;
  return `${s}sn`;
}

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
  const fileInputRef = useRef<HTMLInputElement>(null);
  const addMoreInputRef = useRef<HTMLInputElement>(null);

  // Batch Processing State
  const [queue, setQueue] = useState<File[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [completedSessions, setCompletedSessions] = useState<any[]>([]);
  const [activeResultIndex, setActiveResultIndex] = useState(0);
  const [showToast, setShowToast] = useState(false);

  // Audio Playback State
  const audioRef = useRef<HTMLAudioElement>(null);
  const [playingFile, setPlayingFile] = useState<File | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playingBlock, setPlayingBlock] = useState<{ start: number, end: number } | null>(null);

  // History State
  const [historyItems, setHistoryItems] = useState<any[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);

  useEffect(() => {
    if (activeTab === 'HISTORY') {
      setIsLoadingHistory(true);
      fetch('http://127.0.0.1:8000/history')
        .then(res => res.json())
        .then(data => setHistoryItems(data))
        .catch(console.error)
        .finally(() => setIsLoadingHistory(false));
    }
  }, [activeTab]);

  const loadFromHistory = (item: any) => {
    const reconstructedSession = {
      session_id: item.session_id,
      file: { name: item.filename, size: item.file_size || 0 },
      transcript: item.transcript
    };
    setCompletedSessions([reconstructedSession]);
    setActiveResultIndex(0);
    setAppState('READY');
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
    stopAudio();
    setCurrentIndex(0);
    setCompletedSessions([]);
    setAppState('PROCESSING');

    await processNextFile(0, queue);
  };

  const processNextFile = async (index: number, allFiles: File[]) => {
    if (index >= allFiles.length) {
      // Batch complete
      setAppState('READY');
      setActiveResultIndex(0);
      setShowToast(true);
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
      alert(`${file.name} sunucuya yüklenemedi.`);
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
        processNextFile(index + 1, allFiles);
      } else if (data.state === 'ERROR') {
        alert(`${allFiles[index].name} işlenirken hata oluştu: ` + data.error);
        setCurrentIndex(index + 1);
        processNextFile(index + 1, allFiles);
      } else {
        setTimeout(() => pollStatus(sid, index, allFiles), 2000);
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

    if (playingFile?.name !== file.name) {
      if (audioRef.current.src) URL.revokeObjectURL(audioRef.current.src);
      const url = URL.createObjectURL(file);
      audioRef.current.src = url;
      setPlayingFile(file);
    }

    audioRef.current.currentTime = startTime;
    audioRef.current.play();
    setIsPlaying(true);
    setPlayingBlock({ start: startTime, end: endTime });
  };

  const handleTimeUpdate = () => {
    if (!audioRef.current || !playingBlock) return;
    if (audioRef.current.currentTime >= playingBlock.end) {
      audioRef.current.pause();
      setIsPlaying(false);
      setPlayingBlock(null);
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

  const navItems = [
    { id: 'MAIN', label: 'Ana İşlem', icon: Home },
    { id: 'HISTORY', label: 'Geçmiş', icon: Clock },
    { id: 'SETTINGS', label: 'Ayarlar', icon: Settings },
    { id: 'HELP', label: 'Yardım', icon: HelpCircle },
    { id: 'ABOUT', label: 'Hakkında', icon: Info },
  ] as const;

  return (
    <div className="h-screen w-full flex bg-[var(--color-surface-bg)] text-[#0F172A] font-sans relative overflow-hidden">
      {/* Electron Titlebar Drag Region */}
      <div className="absolute top-0 left-0 w-full h-6 z-[9999]" style={{ WebkitAppRegion: 'drag' } as any} />

      {/* Hidden Global Audio Player */}
      <audio
        ref={audioRef}
        onEnded={() => { setIsPlaying(false); setPlayingBlock(null); }}
        onPause={() => setIsPlaying(false)}
        onPlay={() => setIsPlaying(true)}
        onTimeUpdate={handleTimeUpdate}
        className="hidden"
      />

      {/* Full Screen Completion Popup */}
      <AnimatePresence>
        {showToast && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[9999] bg-[#0F172A]/60 backdrop-blur-md flex items-center justify-center p-4"
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
              <p className="text-slate-500 mb-8 text-sm">Tüm dosyalarınız başarıyla MAXQDA formatına çevrildi ve analiz için hazırlandı.</p>
              <button
                onClick={() => setShowToast(false)}
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
            <img src="/assets/Pamukkale_University_logo.svg" alt="PAU" className="h-20 w-auto filter brightness-0 invert opacity-90" />
            <img src="/assets/iibf_logo.png" alt="IIBF" className="h-20 w-auto filter brightness-0 invert opacity-90" />
          </div>
          <h1 className="text-[#F8FAFC] font-semibold text-sm tracking-wide">Pamukkale Üniversitesi İktisadi ve İdari Bilimler Fakültesi</h1>
          <p className="text-[#64748B] text-xs mt-1">Sesten Metne Döküm Aracı</p>
          <p className="text-[#64748B] text-xs mt-1">Versiyon: Alpha 1.0</p>
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
          <div className="flex-1 overflow-y-auto p-12">
            <div className="max-w-3xl mx-auto space-y-8">
              <div>
                <h2 className="text-2xl font-semibold mb-1">Ayarlar</h2>
                <p className="text-[#64748B] text-sm">Transkripsiyon motorunun davranışını ve donanım kullanımını yapılandırın.</p>
              </div>

              <div className="bg-white rounded-3xl border border-[var(--color-border-light)] shadow-sm p-8 space-y-8">
                <div>
                  <label className="block text-sm font-semibold mb-3">Yapay Zeka Modeli</label>
                  <div className="grid grid-cols-2 gap-4">
                    {['faster-whisper-tiny', 'faster-whisper-base', 'faster-whisper-medium', 'faster-whisper-large-v2'].map(model => (
                      <div
                        key={model}
                        onClick={() => saveConfig({ ...config, model_name: model })}
                        className={`p-4 rounded-xl border cursor-pointer bg-[#F8FAFC] transition-colors
                          ${config.model_name === model ? 'border-[var(--color-primary)] ring-1 ring-[var(--color-primary)]' : 'border-[var(--color-border-light)] hover:border-[var(--color-primary)]'}`}
                      >
                        <div className="flex justify-between items-center mb-1">
                          <span className="font-medium text-sm">{model.split('-').pop()?.toUpperCase()}</span>
                          {model === 'faster-whisper-medium' && <span className="bg-[var(--color-primary)]/10 text-[var(--color-primary)] text-[10px] px-2 py-0.5 rounded-full font-bold">ÖNERİLEN</span>}
                        </div>
                        <p className="text-xs text-[#64748B]">Hız ve doğruluk dengesi</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-8">
                  <div>
                    <label className="block text-sm font-semibold mb-3">Donanım (Hardware)</label>
                    <select
                      value={config.device}
                      onChange={(e) => saveConfig({ ...config, device: e.target.value })}
                      className="w-full p-3 rounded-xl border border-[var(--color-border-light)] bg-[#F8FAFC] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/20"
                    >
                      <option value="auto">Otomatik Algıla</option>
                      <option value="cuda">NVIDIA GPU (CUDA)</option>
                      <option value="cpu">Sadece CPU</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold mb-3">Kaynak Dil</label>
                    <select
                      value={config.default_language}
                      onChange={(e) => saveConfig({ ...config, default_language: e.target.value })}
                      className="w-full p-3 rounded-xl border border-[var(--color-border-light)] bg-[#F8FAFC] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/20"
                    >
                      <option value="auto">Otomatik Algıla</option>
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
          <div className="flex-1 overflow-y-auto p-12">
            <div className="max-w-3xl mx-auto space-y-8">
              <div>
                <h2 className="text-2xl font-semibold mb-1">Yardım & Kılavuz</h2>
                <p className="text-[#64748B] text-sm">Sistemi en verimli şekilde nasıl kullanacağınızı öğrenin.</p>
              </div>

              <div className="bg-white rounded-3xl border border-[var(--color-border-light)] shadow-sm p-8 space-y-6">
                <div className="space-y-2">
                  <h3 className="font-semibold text-lg text-[var(--color-primary)]">1. Modeller Arası Farklar Nelerdir?</h3>
                  <p className="text-sm text-[#334155] leading-relaxed">
                    Sistem 4 farklı model destekler. <strong>Tiny</strong> ve <strong>Base</strong> modelleri çok hızlı çalışır ancak kelime hataları yapabilir. Akademik kullanımlar için <strong>Medium</strong> modeli ideal hız-doğruluk dengesini sunar.
                  </p>
                </div>
                <hr className="border-[var(--color-border-light)]" />
                <div className="space-y-2">
                  <h3 className="font-semibold text-lg text-[var(--color-primary)]">2. Sistem Verilerimi İnternete Gönderiyor mu?</h3>
                  <p className="text-sm text-[#334155] leading-relaxed">
                    <strong>Hayır.</strong> Tüm ses dosyaları bilgisayarınızda (yerel olarak) işlenir. İnternet bağlantısı sadece ilk kullanımda seçtiğiniz modeli indirmek için kullanılır. Veri gizliliği akademik etiğe uygun şekilde korunur.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'ABOUT' && (
          <div className="flex-1 flex items-center justify-center p-12">
            <div className="max-w-md w-full bg-white p-10 rounded-3xl border border-[var(--color-border-light)] shadow-sm text-center">
              <div className="flex justify-center gap-4 mb-8">
                <img src="/assets/Pamukkale_University_logo.svg" alt="PAU" className="h-20 w-auto" />
                <img src="/assets/iibf_logo.png" alt="IIBF" className="h-20 w-auto" />
              </div>
              <h2 className="text-2xl font-bold mb-2">PAÜ İİBF Transkripsiyon</h2>
              <p className="text-sm text-[#64748B] mb-6">Versiyon 2.0.0-alpha • Modern SaaS Sürümü</p>
              <div className="bg-[#F8FAFC] p-4 rounded-xl border border-[var(--color-border-light)] text-sm text-left space-y-3">
                <p><strong>Geliştirici:</strong> PAÜ İİBF Yapay Zeka ve Dijital Uygulamalar Koordinatörlüğü</p>
                <p><strong>Mimari:</strong> React, Electron, FastAPI, faster-whisper</p>
                <p className="text-xs text-[#94A3B8] mt-4 pt-4 border-t border-[var(--color-border-light)]">
                  Bu yazılım, akademik araştırmalardaki deşifre süreçlerini hızlandırmak amacıyla tamamen ücretsiz ve açık kaynak olarak geliştirilmiştir.
                </p>
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
                          <img src="/assets/iibf_transkript.png" alt="IIBF Logo" className="w-56 lg:w-72 h-auto object-contain drop-shadow-[0_0_30px_rgba(99,102,241,0.3)]" />
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
                      <div className={`relative w-[22rem] h-[22rem] rounded-full flex flex-col items-center justify-center text-center p-8 transition-all duration-500 overflow-hidden shadow-2xl
                      ${dragActive
                          ? 'bg-blue-50/60 backdrop-blur-2xl border border-blue-300 scale-105 shadow-blue-500/20'
                          : 'bg-white/50 backdrop-blur-xl border border-white/80 hover:bg-white/60 hover:scale-[1.02]'}`}
                      >
                        {/* Inner Glow */}
                        <div className={`absolute inset-0 bg-gradient-to-b from-white/60 to-transparent pointer-events-none transition-opacity ${dragActive ? 'opacity-0' : 'opacity-100'}`} />
                        <div className={`absolute inset-0 bg-gradient-to-b from-blue-400/20 to-indigo-500/20 pointer-events-none transition-opacity duration-500 ${dragActive ? 'opacity-100' : 'opacity-0'}`} />

                        {/* Content inside Portal */}
                        <motion.div
                          className={`mb-6 flex items-center justify-center transition-all duration-500 relative z-10
                          ${dragActive ? 'scale-110' : 'opacity-90 hover:opacity-100 hover:scale-105'}`}
                          animate={dragActive ? { y: [0, -5, 0] } : { y: 0 }}
                          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                        >
                          <img src="/assets/iibf_transkript.png" alt="IIBF Logo" className={`h-24 w-auto object-contain transition-all duration-500 ${dragActive ? 'drop-shadow-[0_0_25px_rgba(79,70,229,0.6)]' : 'drop-shadow-lg'}`} />
                        </motion.div>

                        <h2 className={`text-2xl font-bold tracking-tight mb-2 relative z-10 transition-colors ${dragActive ? 'text-indigo-900' : 'text-slate-800'}`}>
                          {dragActive ? 'Verileri Bırakın' : 'Ses veya Video Dosyası Yükleyin'}
                        </h2>

                        <p className="text-sm text-slate-500 relative z-10 max-w-[16rem]">
                          {dragActive
                            ? 'İşlem anında başlayacaktır...'
                            : 'Ses ve video kayıtlarınızı bu alana sürükleyip bırakabilir ya da bu alana tıklayarak dosya seçebilirsiniz.'}
                        </p>

                        {!dragActive && (
                          <div className="flex gap-2 mt-6 relative z-10">
                            {['MP3', 'MP4', 'WAV'].map(ext => (
                              <span key={ext} className="px-3 py-1 bg-white/60 border border-white/80 rounded-full text-[10px] font-bold text-slate-400 shadow-sm">
                                {ext}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </motion.div>

                    {/* Security Badge */}
                    <div className="absolute bottom-8 flex items-center justify-center w-full pointer-events-none z-10">
                      <div className="flex items-center gap-2 text-xs font-medium text-slate-500 px-4 py-2 bg-white/60 backdrop-blur-md rounded-full border border-white/80 shadow-sm">
                        <CheckCircle className="w-4 h-4 text-emerald-500" />
                        Tamamen yerel donanımda, internet bağımsız çalışır.
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
                    className="w-full max-w-4xl bg-white/70 backdrop-blur-2xl rounded-[2rem] border border-white shadow-2xl flex flex-col overflow-hidden max-h-full relative"
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
                        <img src="/assets/iibf_transkript.png" alt="Logo" className="w-full h-full object-contain drop-shadow-xl animate-[pulse_3s_ease-in-out_infinite]" />
                      </motion.div>
                    </div>

                    <div className="text-center mb-6">
                      <h2 className="text-2xl font-bold tracking-tight mb-2">
                        Sinyaller Çözümleniyor
                      </h2>
                      <p className="text-[#64748B]">
                        <span className="font-semibold text-slate-700">{queue.length}</span> dosyadan <span className="font-semibold text-[var(--color-primary)]">{currentIndex + 1}.</span> işleniyor
                      </p>
                    </div>

                    <div className="flex flex-col items-center gap-3">
                      <div className="flex items-center gap-2 text-sm text-[#64748B] font-mono bg-white px-4 py-2 rounded-full border border-[var(--color-border-light)] shadow-sm">
                        <span className="w-2 h-2 rounded-full bg-[var(--color-primary)] animate-ping" />
                        Aktif dosya: {queue[currentIndex]?.name}
                      </div>
                    </div>
                  </motion.div>
                )}

                {appState === 'READY' && completedSessions.length > 0 && (
                  <motion.div
                    key="ready"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="w-full max-w-5xl flex gap-8 h-full min-h-0"
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
                    <div className="flex-1 flex flex-col gap-4 relative z-10">
                      <div className="flex-1 bg-white rounded-3xl border border-[var(--color-border-light)] shadow-sm overflow-hidden flex flex-col">
                        <div className="p-6 border-b border-[var(--color-border-light)] flex items-center justify-between bg-slate-50/50">
                          <div>
                            <h3 className="font-semibold text-lg">{completedSessions[activeResultIndex].file.name}</h3>
                            <p className="text-xs text-[#64748B]">
                              Süre: {formatDuration(completedSessions[activeResultIndex].transcript?.duration || 0)}
                            </p>
                          </div>
                          <div className="flex gap-2">
                            <button
                              onClick={resetToNew}
                              className="flex items-center gap-2 text-sm font-medium bg-white border border-[#CBD5E1] hover:bg-slate-50 px-4 py-2.5 rounded-xl transition-colors shadow-sm"
                            >
                              <Plus className="w-4 h-4" /> Yeni Analiz
                            </button>
                            <button
                              onClick={openOutputFolder}
                              className="flex items-center gap-2 text-sm font-medium bg-[#0F172A] text-white hover:bg-[#1E293B] px-4 py-2.5 rounded-xl transition-colors shadow-sm"
                            >
                              <FolderOpen className="w-4 h-4" /> Çıktıları Aç
                            </button>
                          </div>
                        </div>

                        <div className="p-8 overflow-y-auto flex-1 space-y-8 [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-slate-200 hover:[&::-webkit-scrollbar-thumb]:bg-slate-300 [&::-webkit-scrollbar-thumb]:rounded-full">
                          {completedSessions[activeResultIndex].transcript?.blocks ? completedSessions[activeResultIndex].transcript.blocks.map((block: any, idx: number) => {
                            const fileObj = completedSessions[activeResultIndex].file;
                            const isThisSegmentPlaying = playingFile?.name === fileObj.name && isPlaying &&
                              playingBlock?.start === block.start_time;
                            return (
                              <div key={block.id} className={`group relative p-2 rounded-xl transition-colors ${isThisSegmentPlaying ? 'bg-blue-50/50 ring-1 ring-[var(--color-primary)]/20' : 'hover:bg-slate-50/50'}`}>
                                <div className={`absolute -left-6 top-3 transition-opacity ${isThisSegmentPlaying ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}`}>
                                  <button
                                    onClick={() => playTranscriptSegment(fileObj, block.start_time, block.end_time)}
                                    className={`p-1.5 rounded-md shadow-sm transition-colors
                                    ${isThisSegmentPlaying
                                        ? 'bg-[var(--color-primary)] text-white hover:bg-[#0F172A]'
                                        : 'bg-blue-50 text-[var(--color-primary)] hover:text-white hover:bg-[var(--color-primary)]'}`}
                                    title={isThisSegmentPlaying ? "Duraklat" : "Sadece bu cümleyi dinle"}
                                  >
                                    {isThisSegmentPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
                                  </button>
                                </div>
                                <div className="flex items-baseline gap-3 mb-1">
                                  <span className="font-semibold text-sm">{block.speaker || `KONUŞMACI_${(idx % 2) + 1}`}</span>
                                  <span className="text-xs text-[var(--color-primary)] font-mono bg-blue-50 px-1.5 py-0.5 rounded cursor-pointer hover:bg-blue-100" onClick={() => playTranscriptSegment(fileObj, block.start_time, block.end_time)}>
                                    {new Date(block.start_time * 1000).toISOString().substr(11, 8)}
                                  </span>
                                </div>
                                <p className="text-base leading-relaxed text-[#1E293B]">
                                  {block.text}
                                </p>
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
