import React, { useState } from 'react';
import { Camera, RotateCcw, Play, Pause, Video, Eye, Crosshair, AlertCircle } from 'lucide-react';

export default function VideoFeed({ onReset }) {
  const [isPlaying, setIsPlaying] = useState(true);
  const [streamKey, setStreamKey] = useState(Date.now());
  const [isResetting, setIsResetting] = useState(false);

  const handleTogglePlay = () => {
    setIsPlaying(!isPlaying);
    if (!isPlaying) {
      setStreamKey(Date.now());
    }
  };

  const handleSnapshot = () => {
    const link = document.createElement('a');
    link.href = `/api/stream/snapshot?t=${Date.now()}`;
    link.download = `sortstream-conveyor-snapshot-${Date.now()}.jpg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleResetClick = async () => {
    if (window.confirm("Are you sure you want to reset current conveyor session counters?")) {
      setIsResetting(true);
      await onReset();
      setStreamKey(Date.now());
      setIsResetting(false);
    }
  };

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-950/80 shadow-2xl overflow-hidden flex flex-col">
      {/* Header Bar */}
      <div className="px-4 py-3 border-b border-zinc-800/80 flex items-center justify-between bg-zinc-900/50">
        <div className="flex items-center space-x-2">
          <div className="p-1 rounded bg-emerald-500/10 border border-emerald-500/30">
            <Video className="w-4 h-4 text-emerald-400" />
          </div>
          <span className="font-semibold text-sm text-zinc-100 flex items-center gap-2">
            CONVEYOR FEED 01
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-emerald-400 font-mono-code">20 FPS • MJPEG</span>
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleTogglePlay}
            className={`p-1.5 rounded-lg border text-xs transition-colors flex items-center gap-1.5 px-2.5 font-medium ${
              isPlaying
                ? 'bg-amber-500/10 text-amber-300 border-amber-500/30 hover:bg-amber-500/20'
                : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30 hover:bg-emerald-500/20'
            }`}
          >
            {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            <span>{isPlaying ? 'PAUSE' : 'RESUME'}</span>
          </button>

          <button
            onClick={handleSnapshot}
            className="p-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border border-zinc-700 transition-colors flex items-center gap-1.5 px-2.5 text-xs font-medium"
            title="Download full-resolution diagnostic snapshot"
          >
            <Camera className="w-3.5 h-3.5 text-sky-400" />
            <span className="hidden sm:inline">SNAPSHOT</span>
          </button>

          <button
            onClick={handleResetClick}
            disabled={isResetting}
            className="p-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 transition-colors flex items-center gap-1.5 px-2.5 text-xs font-medium"
            title="Reset telemetry and ByteTrack IDs"
          >
            <RotateCcw className={`w-3.5 h-3.5 ${isResetting ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">RESET</span>
          </button>
        </div>
      </div>

      {/* Main Video Viewport */}
      <div className="relative aspect-[4/3] w-full bg-zinc-950 flex items-center justify-center overflow-hidden group">
        {isPlaying ? (
          <img
            key={streamKey}
            src={`/api/stream/feed?t=${streamKey}`}
            alt="SortStream AI Conveyor Stream"
            className="w-full h-full object-contain select-none"
            onError={(e) => {
              // Retry on connection transient
              setTimeout(() => setStreamKey(Date.now()), 2000);
            }}
          />
        ) : (
          <div className="text-center p-8 text-zinc-500">
            <Pause className="w-12 h-12 mx-auto mb-3 text-zinc-600" />
            <p className="text-sm font-medium text-zinc-400">Stream Paused</p>
            <p className="text-xs text-zinc-600 mt-1">Click RESUME to continue live conveyor inspection</p>
          </div>
        )}

        {/* Live Tracking Crosshair Overlay */}
        <div className="absolute bottom-3 left-3 px-2.5 py-1 rounded bg-black/70 backdrop-blur-md border border-zinc-700/60 text-[11px] font-mono-code text-zinc-300 flex items-center space-x-2">
          <Crosshair className="w-3.5 h-3.5 text-emerald-400 animate-spin" style={{ animationDuration: '8s' }} />
          <span>VIRTUAL TRIPWIRE ACTIVE: Y=240px</span>
        </div>

        <div className="absolute bottom-3 right-3 px-2 py-0.5 rounded bg-black/60 text-[10px] font-mono-code text-zinc-400">
          640x480 • IEEE 754 ACCUMULATOR
        </div>
      </div>

      {/* Footer Info Strip */}
      <div className="p-3 bg-zinc-900/60 border-t border-zinc-800/80 text-xs text-zinc-400 flex flex-wrap items-center justify-between gap-2">
        <span className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
          <span>ByteTrack Kalman Filter: Multi-Object IoU + Centroid Re-identification</span>
        </span>
        <span className="font-mono-code text-zinc-500">EPA FACTOR: $\Delta E = M \cdot (EF_L - EF_R)$</span>
      </div>
    </div>
  );
}
