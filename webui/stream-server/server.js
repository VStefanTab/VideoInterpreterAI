const express = require('express');
const expressWs = require('express-ws');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
expressWs(app);
const { proxy, scriptUrl } = require('rtsp-relay')(app);

app.use(cors());
app.use(bodyParser.json());

let rtspUrl = null;

// Endpoint to receive RTSP link
app.post('/api/set-rtsp', (req, res) => {
  rtspUrl = req.body.rtspUrl;
  if (!rtspUrl) {
    return res.status(400).json({ error: 'RTSP URL required' });
  }
  console.log(`RTSP URL set to: ${rtspUrl}`);
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
    transport: "tcp",
    verbose: true,
    additionalFlags: ['-an', '-fflags', 'nobuffer', '-s', '1280x720']
  })(ws, req);
});

app.get('/', (req, res) =>
  res.send(`
  <canvas id='canvas'></canvas>

  <script src='${scriptUrl}'></script>
  <script>
    loadPlayer({
      url: 'ws://' + location.host + '/api/stream',
      canvas: document.getElementById('canvas')
    });
  </script>
`),
);

const PORT = 2000;
app.listen(PORT, '0.0.0.0', () => console.log(`RTSP relay standby on http://0.0.0.0:${PORT}`));
