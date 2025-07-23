const express = require('express');
const expressWs = require('express-ws');
const bodyParser = require('body-parser');
const { proxy, scriptUrl } = require('rtsp-relay')(express());

const app = express();
expressWs(app);
app.use(bodyParser.json());

let rtspUrl = null;

// Endpoint to receive RTSP link
app.post('/api/set-rtsp', (req, res) => {
  rtspUrl = req.body.rtspUrl;
  if (!rtspUrl) {
    return res.status(400).json({ error: 'RTSP URL required' });
  }
  res.json({ message: 'RTSP URL set' });
});

// WebSocket stream endpoint
app.ws('/api/stream', (ws, req) => {
  if (!rtspUrl) {
    ws.close();
    return;
  }
  proxy({
    url: rtspUrl,
    verbose: false
  })(ws, req);
});

app.get('/script.js', (req, res) => {
  res.type('text/javascript');
  res.send(`
    const canvas = document.getElementById('canvas');
    const ws = new WebSocket('ws://' + location.hostname + ':2000/api/stream');
    const player = new window.JSMpeg.Player(ws, { canvas: canvas });
  `);
});

const PORT = 2000;
app.listen(PORT, () => console.log(`RTSP relay standby on http://localhost:${PORT}`));