import { useCallback, useEffect, useRef, useState } from "react";
import config from "../../../../contract/config.json";

export const canRecord = (): boolean => typeof navigator !== "undefined" && !!navigator.mediaDevices?.getUserMedia && typeof MediaRecorder !== "undefined";

/** Records up to audioMaxSeconds as opus/webm and keeps the blob locally until it is sent. */
export function useRecorder() {
  const [recording, setRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [level, setLevel] = useState(0);
  const [blob, setBlob] = useState<Blob | null>(null);
  const rec = useRef<MediaRecorder | null>(null);
  const chunks = useRef<Blob[]>([]);
  const stopAll = useRef<() => void>(() => undefined);

  const stop = useCallback(() => { rec.current?.state === "recording" && rec.current.stop(); }, []);

  const start = useCallback(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true }); // denied -> caller hides the mic
    const mime = MediaRecorder.isTypeSupported("audio/webm;codecs=opus") ? "audio/webm;codecs=opus" : undefined;
    const r = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined);
    chunks.current = [];
    r.ondataavailable = (e) => { if (e.data.size) chunks.current.push(e.data); };
    const ctx = new AudioContext();
    const analyser = ctx.createAnalyser();
    ctx.createMediaStreamSource(stream).connect(analyser);
    const buf = new Uint8Array(analyser.fftSize);
    const started = Date.now();
    const tick = setInterval(() => {
      analyser.getByteTimeDomainData(buf);
      let peak = 0;
      for (const v of buf) peak = Math.max(peak, Math.abs(v - 128));
      setLevel(Math.min(1, peak / 64));
      const s = Math.floor((Date.now() - started) / 1000);
      setSeconds(s);
      if (s >= config.audioMaxSeconds) stop();
    }, 100);
    stopAll.current = () => { clearInterval(tick); stream.getTracks().forEach((t) => t.stop()); void ctx.close(); setLevel(0); };
    r.onstop = () => { stopAll.current(); setBlob(new Blob(chunks.current, { type: r.mimeType || "audio/webm" })); setRecording(false); };
    rec.current = r;
    r.start();
    setSeconds(0); setBlob(null); setRecording(true);
  }, [stop]);

  useEffect(() => () => { stop(); stopAll.current(); }, [stop]);
  return { recording, seconds, level, blob, start, stop, clear: () => setBlob(null) };
}
