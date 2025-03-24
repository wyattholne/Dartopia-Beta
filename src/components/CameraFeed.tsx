import React, { useEffect, useRef, useState } from 'react';

export function CameraFeed({ onFrameCapture }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [devices, setDevices] = useState<MediaDeviceInfo[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<string>('');
  const [resolution, setResolution] = useState({ width: 1280, height: 720 });

  useEffect(() => {
    navigator.mediaDevices.enumerateDevices().then(devices => {
      const videoDevices = devices.filter(device => device.kind === 'videoinput');
      setDevices(videoDevices);
      if (videoDevices.length > 0) {
        setSelectedDevice(videoDevices[0].deviceId);
      }
    });
  }, []);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { deviceId: selectedDevice, width: resolution.width, height: resolution.height },
        audio: false,
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
        setIsStreaming(true);
      }
    } catch (err) {
      setError('Failed to access camera: ' + err.message);
      setIsStreaming(false);
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      const tracks = stream.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
      setIsStreaming(false);
    }
  };

  const captureFrame = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
      const imageData = canvas.toDataURL('image/jpeg');
      if (onFrameCapture) {
        onFrameCapture(imageData);
      }
    }
  };

  useEffect(() => {
    if (selectedDevice) {
      startCamera();
    }
    return () => stopCamera();
  }, [selectedDevice, resolution]);

  return (
    <div className="camera-feed">
      <h2>Live Dartboard Feed</h2>
      {error && <p className="text-red-500">{error}</p>}
      <div>
        <label>Camera: </label>
        <select onChange={(e) => setSelectedDevice(e.target.value)} value={selectedDevice}>
          {devices.map(device => (
            <option key={device.deviceId} value={device.deviceId}>
              {device.label || `Camera ${devices.indexOf(device) + 1}`}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label>Resolution: </label>
        <select onChange={(e) => {
          const [width, height] = e.target.value.split('x').map(Number);
          setResolution({ width, height });
        }}>
          <option value="640x480">640x480</option>
          <option value="1280x720">1280x720</option>
          <option value="1920x1080">1920x1080</option>
        </select>
      </div>
      <video ref={videoRef} className="w-full max-w-[1280px]" />
      <div className="controls mt-2 flex gap-2">
        <button onClick={startCamera} disabled={isStreaming} className="btn btn-primary">
          Start Camera
        </button>
        <button onClick={stopCamera} disabled={!isStreaming} className="btn btn-secondary">
          Stop Camera
        </button>
        <button onClick={captureFrame} disabled={!isStreaming} className="btn btn-accent">
          Capture Frame
        </button>
      </div>
    </div>
  );
}
