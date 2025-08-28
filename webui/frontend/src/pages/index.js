import React, { useRef, useState, useEffect } from 'react';
import { loadPlayer } from 'rtsp-relay/browser';


const SERVER_ADDRESS = process.env.NEXT_PUBLIC_SERVER_ADDRESS || 'stream-server:2000';
const BACKEND_ADDRESS = process.env.NEXT_PUBLIC_BACKEND_SERVER_ADDRESS || 'processing:5000';

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
  const [isInterpreting, setIsInterpreting] = useState(false);
  const [prompt, setPrompt] = useState('');
  const [debouncedPrompt, setDebouncedPrompt] = useState('');
  const [lastProcessedPrompt, setLastProcessedPrompt] = useState('');

  // Debounce effect for prompt changes
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedPrompt(prompt);
    }, 500);

    return () => {
      clearTimeout(handler);
    };
  }, [prompt]);

  // Automatically start interpreter when debounced prompt changes
  useEffect(() => {
    if (debouncedPrompt && videoVisible && debouncedPrompt !== lastProcessedPrompt) {
      setLastProcessedPrompt(debouncedPrompt);
      startInterpreter(debouncedPrompt);
    }
  }, [debouncedPrompt, videoVisible, lastProcessedPrompt]);

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

  const startInterpreter = async (prompt) => {
    if (isInterpreting) return;
    
    setIsInterpreting(true);
    
    try {
      const img = document.getElementById('canvas');
      if (!img) {
        alert('Please ensure the canvas is set');
        setIsInterpreting(false);
        return;
      }

      const payload = {
        prompt: prompt,
        image64: img.toDataURL('image/png').split(',')[1]
      };

      // Send request to backend
      const response = await fetch(`http://${BACKEND_ADDRESS}/interpreter`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (data.success === true) {
        // Start polling for results
        const requestId = data.request_id;
        let result = null;
        let attempts = 0;
        const maxAttempts = 100; // Timeout after 100 attempts (10 seconds with 100ms interval)
        
        while (attempts < maxAttempts) {
          const resultResponse = await fetch(`http://${BACKEND_ADDRESS}/result?id=${requestId}`);
          const resultData = await resultResponse.json();
          
          if (resultData.response) {
            result = resultData.response;
            break;
          }
          
          attempts++;
          await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        if (result) {
          document.getElementById('output').value = result;
        } else {
          throw new Error('Timeout waiting for result');
        }
      } else {
        throw new Error(data.error || 'Server returned success: false');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to start interpreter: ' + error.message);
    } finally {
      // Reset interpreting state after completion
      setIsInterpreting(false);
    }
  }

  return (
    <div style={{ display: 'flex', width: '100%' }}>
      <div style={{ float: 'left', width: '60%', marginLeft: '10px' }}>
        <h1>RTSP Stream Viewer</h1>
        <LinkField onConnect={handleConnect} />
        <VideoPlayer visible={videoVisible} />
        <input 
          type='text' 
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder='Enter prompt here' 
          hidden={!videoVisible} 
        />
      </div>
      <div style={{ float: 'right', width: '32%', marginLeft: '10px', marginRight: '10px', marginTop: '30px' }} hidden={!videoVisible}>
        <label htmlFor='output'>Response</label>
        <br />
        <textarea id='output' rows='10' cols='50' readOnly></textarea>
      </div>
    </div>
  )
}
