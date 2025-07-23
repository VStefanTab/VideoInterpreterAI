import React, { useRef, useState, useEffect } from 'react';

function LinkField({ onConnect }) {
  const inputRef = useRef();

  const handleClick = () => {
    const rtspUrl = inputRef.current.value;
    onConnect(rtspUrl);
  };

  return (
    <div>
      <label>Insert RTSP link</label>
      <br />
      <input ref={inputRef} type="text" placeholder="rtsp://example.com/stream" />
      <button onClick={handleClick}>Connect</button>
    </div>
  );
}

function VideoPlayer({ visible }) {
  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'http://localhost:2000/script.js';
    script.async = true;
    document.body.appendChild(script);
    return () => {
      document.body.removeChild(script);
    };
  }, []);

  if (!visible) return null;

  return (
    <div id="video">
      <h1>RTSP Stream</h1>
      <canvas id="canvas" style={{ width: '640px', height: '480px', background: '#000' }} />
    </div>
  );
}

export default function HomePage() {
  const [videoVisible, setVideoVisible] = useState(false);

  const handleConnect = (rtspUrl) => {
    if (!rtspUrl) {
      alert('Please enter a valid RTSP URL');
      return;
    }

    fetch('/api/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rtspUrl })
    })
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          alert(data.error);
        } else {
          alert(data.message);
          setVideoVisible(true);
        }
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Failed to set RTSP URL');
      });
  };

  return (
    <div>
      <h1>RTSP Stream Viewer</h1>
      <LinkField onConnect={handleConnect} />
      <VideoPlayer visible={videoVisible} />
    </div>
  );
}