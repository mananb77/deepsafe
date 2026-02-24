#!/usr/bin/env node
/**
 * DeepSafe Google Meet Browser Controller
 *
 * Puppeteer-based headless browser that joins Google Meet calls,
 * captures audio/video streams, and forwards them to the Python
 * orchestrator via a local WebSocket connection.
 *
 * Usage:
 *   node browser_controller.js --meeting-url <url> --ws-port <port> [--bot-name <name>]
 *
 * The Python process starts a WebSocket server on --ws-port.
 * This script connects to it and sends:
 *   - { type: "audio_frame", data: <base64>, sample_rate, channels, participant_id }
 *   - { type: "video_frame", data: <base64>, width, height, format, participant_id }
 *   - { type: "participant_joined", participant: { id, name, ... } }
 *   - { type: "participant_left", participant_id }
 *   - { type: "meeting_ended" }
 *   - { type: "status", status: "connected" | "error", message? }
 */

const puppeteer = require('puppeteer');
const WebSocket = require('ws');

// ─── CLI Arguments ──────────────────────────────────────────────────────────

function parseArgs() {
  const args = {};
  const argv = process.argv.slice(2);
  for (let i = 0; i < argv.length; i++) {
    switch (argv[i]) {
      case '--meeting-url': args.meetingUrl = argv[++i]; break;
      case '--ws-port': args.wsPort = parseInt(argv[++i], 10); break;
      case '--bot-name': args.botName = argv[++i]; break;
      case '--headless': args.headless = true; break;
      case '--executable': args.executablePath = argv[++i]; break;
      case '--video-fps': args.videoFps = parseInt(argv[++i], 10); break;
    }
  }
  args.botName = args.botName || 'DeepSafe Bot';
  args.videoFps = args.videoFps || 5;
  args.headless = args.headless !== false;
  return args;
}

const config = parseArgs();
if (!config.meetingUrl || !config.wsPort) {
  console.error('Usage: node browser_controller.js --meeting-url <url> --ws-port <port>');
  process.exit(1);
}

// ─── WebSocket Connection to Python Orchestrator ────────────────────────────

let ws = null;
let wsReady = false;

function connectWebSocket() {
  return new Promise((resolve, reject) => {
    ws = new WebSocket(`ws://127.0.0.1:${config.wsPort}`);

    ws.on('open', () => {
      wsReady = true;
      sendMessage({ type: 'status', status: 'connecting', message: 'WebSocket connected' });
      resolve();
    });

    ws.on('message', (data) => {
      try {
        const msg = JSON.parse(data.toString());
        handleCommand(msg);
      } catch (e) {
        console.error('Invalid message from orchestrator:', e.message);
      }
    });

    ws.on('close', () => {
      wsReady = false;
      console.log('WebSocket closed, shutting down...');
      cleanup();
    });

    ws.on('error', (err) => {
      console.error('WebSocket error:', err.message);
      reject(err);
    });
  });
}

function sendMessage(msg) {
  if (ws && wsReady) {
    ws.send(JSON.stringify(msg));
  }
}

function sendBinary(type, buffer, metadata) {
  if (ws && wsReady) {
    // Send metadata first, then binary
    sendMessage({ type, ...metadata, size: buffer.length });
    ws.send(buffer);
  }
}

// ─── Command Handler (from Python) ──────────────────────────────────────────

async function handleCommand(msg) {
  switch (msg.command) {
    case 'disconnect':
      await leaveMeeting();
      break;
    case 'send_chat':
      await sendChatMessage(msg.message);
      break;
    case 'inject_overlay':
      await injectOverlay(msg.html, msg.position);
      break;
    case 'remove_overlay':
      await removeOverlay(msg.overlay_id);
      break;
  }
}

// ─── Browser & Meeting Logic ────────────────────────────────────────────────

let browser = null;
let page = null;
let captureInterval = null;
let participantObserver = null;
let knownParticipants = new Map();

const SELECTORS = {
  nameInput: "input[aria-label='Your name']",
  joinButton: "button[data-idom-class*='join'], button[jsname='Qx7uuf']",
  askToJoinButton: "button[jsname='Qx7uuf']",
  leaveButton: "button[aria-label='Leave call']",
  muteButton: "button[aria-label*='microphone']",
  cameraButton: "button[aria-label*='camera']",
  chatButton: "button[aria-label*='chat']",
  chatInput: "textarea[aria-label*='message']",
  chatSend: "button[aria-label='Send']",
  participantList: "div[aria-label='Participants']",
  participantItem: "div[data-participant-id]",
  endCallIndicator: "div[data-call-ended='true']",
};

async function launchBrowser() {
  const launchOptions = {
    headless: config.headless ? 'new' : false,
    args: [
      '--use-fake-ui-for-media-stream',
      '--use-fake-device-for-media-stream',
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-gpu',
      '--disable-dev-shm-usage',
      '--autoplay-policy=no-user-gesture-required',
      '--disable-features=TranslateUI',
    ],
  };

  if (config.executablePath) {
    launchOptions.executablePath = config.executablePath;
  }

  browser = await puppeteer.launch(launchOptions);
  page = await browser.newPage();

  // Grant permissions for mic/camera
  const context = browser.defaultBrowserContext();
  await context.overridePermissions('https://meet.google.com', [
    'microphone',
    'camera',
    'notifications',
  ]);

  await page.setViewport({ width: 1920, height: 1080 });

  // Listen for page errors
  page.on('error', (err) => {
    console.error('Page error:', err.message);
    sendMessage({ type: 'status', status: 'error', message: err.message });
  });
}

async function joinMeeting() {
  console.log(`Navigating to: ${config.meetingUrl}`);
  await page.goto(config.meetingUrl, { waitUntil: 'networkidle2', timeout: 30000 });

  // Wait for the join flow to load
  await page.waitForTimeout(3000);

  // Try to set bot name
  try {
    await page.waitForSelector(SELECTORS.nameInput, { timeout: 5000 });
    await page.click(SELECTORS.nameInput, { clickCount: 3 });
    await page.type(SELECTORS.nameInput, config.botName);
  } catch {
    console.log('Name input not found (may already be set)');
  }

  // Turn off camera and mic before joining
  try {
    const cameraBtn = await page.$(SELECTORS.cameraButton);
    if (cameraBtn) await cameraBtn.click();
  } catch { /* ignore */ }

  try {
    const muteBtn = await page.$(SELECTORS.muteButton);
    if (muteBtn) await muteBtn.click();
  } catch { /* ignore */ }

  // Click join / ask to join
  try {
    await page.waitForSelector(SELECTORS.joinButton, { timeout: 10000 });
    await page.click(SELECTORS.joinButton);
  } catch {
    console.error('Could not find join button');
    sendMessage({ type: 'status', status: 'error', message: 'Join button not found' });
    return false;
  }

  // Wait for meeting to load (check for leave button as indicator)
  try {
    await page.waitForSelector(SELECTORS.leaveButton, { timeout: 60000 });
  } catch {
    console.error('Never entered meeting (timeout waiting for leave button)');
    sendMessage({ type: 'status', status: 'error', message: 'Failed to join meeting' });
    return false;
  }

  console.log('Successfully joined meeting');
  sendMessage({ type: 'status', status: 'connected', message: 'Joined meeting' });
  return true;
}

// ─── Stream Capture ─────────────────────────────────────────────────────────

async function startCapture() {
  const intervalMs = Math.round(1000 / config.videoFps);

  // Inject audio capture script via Web Audio API
  await page.evaluate(() => {
    window.__deepsafe_audioChunks = [];

    navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
      const ctx = new AudioContext({ sampleRate: 16000 });
      const source = ctx.createMediaStreamSource(stream);
      const processor = ctx.createScriptProcessor(4096, 1, 1);

      processor.onaudioprocess = (e) => {
        const pcm = e.inputBuffer.getChannelData(0);
        // Convert Float32 to Int16
        const int16 = new Int16Array(pcm.length);
        for (let i = 0; i < pcm.length; i++) {
          int16[i] = Math.max(-32768, Math.min(32767, Math.round(pcm[i] * 32768)));
        }
        window.__deepsafe_audioChunks.push(Array.from(int16));
      };

      source.connect(processor);
      processor.connect(ctx.destination);
      window.__deepsafe_audioCtx = ctx;
    }).catch(() => {
      // No audio available
    });
  });

  // Periodic frame capture loop
  captureInterval = setInterval(async () => {
    try {
      // Capture video frame from the page
      const screenshot = await page.screenshot({
        type: 'jpeg',
        quality: 60,
        encoding: 'base64',
      });

      sendMessage({
        type: 'video_frame',
        data: screenshot,
        width: 1920,
        height: 1080,
        format: 'jpeg',
        participant_id: 'mixed', // Full page capture
        timestamp: Date.now(),
      });

      // Collect audio chunks
      const audioChunks = await page.evaluate(() => {
        const chunks = window.__deepsafe_audioChunks || [];
        window.__deepsafe_audioChunks = [];
        return chunks;
      });

      if (audioChunks.length > 0) {
        // Flatten into single buffer
        const flat = audioChunks.flat();
        sendMessage({
          type: 'audio_frame',
          data: Buffer.from(new Int16Array(flat).buffer).toString('base64'),
          sample_rate: 16000,
          channels: 1,
          duration_ms: Math.round((flat.length / 16000) * 1000),
          participant_id: 'mixed',
          timestamp: Date.now(),
        });
      }
    } catch (err) {
      // Page might be navigating
      console.error('Capture error:', err.message);
    }
  }, intervalMs);
}

// ─── Participant Tracking ───────────────────────────────────────────────────

async function startParticipantObserver() {
  // Poll participant list every 5 seconds
  participantObserver = setInterval(async () => {
    try {
      const participants = await page.evaluate((sel) => {
        const items = document.querySelectorAll(sel);
        return Array.from(items).map((el) => ({
          id: el.getAttribute('data-participant-id') || el.textContent,
          name: el.textContent?.trim() || 'Unknown',
        }));
      }, SELECTORS.participantItem);

      const currentIds = new Set(participants.map((p) => p.id));

      // Detect joins
      for (const p of participants) {
        if (!knownParticipants.has(p.id)) {
          knownParticipants.set(p.id, p);
          sendMessage({ type: 'participant_joined', participant: p });
        }
      }

      // Detect leaves
      for (const [id] of knownParticipants) {
        if (!currentIds.has(id)) {
          knownParticipants.delete(id);
          sendMessage({ type: 'participant_left', participant_id: id });
        }
      }
    } catch {
      // Participant list may not be visible
    }

    // Check for meeting end
    try {
      const ended = await page.$(SELECTORS.endCallIndicator);
      if (ended) {
        sendMessage({ type: 'meeting_ended' });
        await cleanup();
      }
    } catch { /* ignore */ }
  }, 5000);
}

// ─── Meeting Actions ────────────────────────────────────────────────────────

async function leaveMeeting() {
  try {
    const leaveBtn = await page.$(SELECTORS.leaveButton);
    if (leaveBtn) {
      await leaveBtn.click();
      await page.waitForTimeout(1000);
    }
  } catch { /* ignore */ }
  sendMessage({ type: 'status', status: 'disconnected', message: 'Left meeting' });
  await cleanup();
}

async function sendChatMessage(message) {
  try {
    // Open chat
    const chatBtn = await page.$(SELECTORS.chatButton);
    if (chatBtn) await chatBtn.click();
    await page.waitForTimeout(500);

    // Type and send
    await page.waitForSelector(SELECTORS.chatInput, { timeout: 3000 });
    await page.type(SELECTORS.chatInput, message);
    const sendBtn = await page.$(SELECTORS.chatSend);
    if (sendBtn) await sendBtn.click();
  } catch (err) {
    console.error('Failed to send chat:', err.message);
  }
}

async function injectOverlay(html, position) {
  try {
    await page.evaluate((htmlContent, pos) => {
      let overlay = document.getElementById('deepsafe-overlay');
      if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'deepsafe-overlay';
        overlay.style.cssText = `
          position: fixed; z-index: 99999; pointer-events: none;
          ${pos === 'top-right' ? 'top: 16px; right: 16px;' : 'bottom: 16px; left: 16px;'}
        `;
        document.body.appendChild(overlay);
      }
      overlay.innerHTML = htmlContent;
    }, html, position || 'top-right');
  } catch { /* ignore */ }
}

async function removeOverlay(overlayId) {
  try {
    await page.evaluate((id) => {
      const el = document.getElementById(id || 'deepsafe-overlay');
      if (el) el.remove();
    }, overlayId);
  } catch { /* ignore */ }
}

// ─── Cleanup ────────────────────────────────────────────────────────────────

async function cleanup() {
  if (captureInterval) {
    clearInterval(captureInterval);
    captureInterval = null;
  }
  if (participantObserver) {
    clearInterval(participantObserver);
    participantObserver = null;
  }
  if (browser) {
    try { await browser.close(); } catch { /* ignore */ }
    browser = null;
  }
  process.exit(0);
}

process.on('SIGTERM', cleanup);
process.on('SIGINT', cleanup);

// ─── Main ───────────────────────────────────────────────────────────────────

async function main() {
  try {
    await connectWebSocket();
    await launchBrowser();

    const joined = await joinMeeting();
    if (!joined) {
      await cleanup();
      return;
    }

    await startCapture();
    await startParticipantObserver();

    console.log('Bot running. Capturing streams...');
  } catch (err) {
    console.error('Fatal error:', err);
    sendMessage({ type: 'status', status: 'error', message: err.message });
    await cleanup();
  }
}

main();
