import React, { useRef, useState, useEffect } from 'react';
import { loadPlayer } from 'rtsp-relay/browser';


const SERVER_ADDRESS = process.env.REACT_APP_SERVER_ADDRESS || 'localhost:2000';

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
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!visible || !canvasRef.current) return;

    loadPlayer({
      url: `ws://${SERVER_ADDRESS}/api/stream`,
      canvas: canvasRef.current,
    });
  }, [visible]);

  if (!visible) return null;

  return (
    <div id="video">
      <h1>RTSP Stream</h1>
      <canvas
        ref={canvasRef}
        id="canvas"
        style={{ width: '640px', height: '480px' }}
      />
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

    fetch(`http://${SERVER_ADDRESS}/api/set-rtsp`, {
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

  const startInterpreter = () => {
    const img = document.getElementById('canvas');
    const prompt = document.getElementById('input').value;
    if (!img || !prompt) {
      alert('Please ensure the canvas and prompt are set');
      return;
    }

    const payload = {
      prompt: prompt,
      image64: img.toDataURL('image/jpeg').split(',')[1]
    };

    fetch('http://localhost:5000/interpreter', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(response => response.json())
      .then(data => {
        if (data.success === true) {
          document.getElementById('output').value = data.response;
          startInterpreter();
        }
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Failed to start interpreter');
      });
  }

  return (
    <div style={{ display: 'flex', width: '100%' }}>
      <div style={{ float: 'left', width: '60%', marginLeft: '10px' }}>
        <h1>RTSP Stream Viewer</h1>
        <LinkField onConnect={handleConnect} />
        <VideoPlayer visible={videoVisible} />
        <input type='text' id='input' placeholder='Enter prompt here' hidden={!videoVisible} />
        <button onClick={startInterpreter} hidden={!videoVisible}>Start interpretor</button>
      </div>
      <div style={{ float: 'right', width: '32%', marginLeft: '10px', marginRight: '10px', marginTop: '30px' }} hidden={!videoVisible}>
        <label htmlFor='output'>Response</label>
        <br/>
        <textarea id='output' rows='10' cols='50' readOnly></textarea>
      </div>
    </div>
  );
}
