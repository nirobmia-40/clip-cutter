const API = 'http://127.0.0.1:8765/api';
const analyzeForm = document.querySelector('#analyze-form');
const statusText = document.querySelector('#status');
const editor = document.querySelector('#editor');
const downloadButton = document.querySelector('#download-button');
const startTime = document.querySelector('#start-time');
const endTime = document.querySelector('#end-time');
const startSlider = document.querySelector('#start-slider');
const endSlider = document.querySelector('#end-slider');
const qualitySelect = document.querySelector('#quality-select');
const formatSelect = document.querySelector('#format-select');
const saveLocation = document.querySelector('#save-location');
let mediaInfo = null;
let mode = 'video';

function formatTime(seconds) {
  const whole = Math.max(0, Math.floor(Number(seconds) || 0));
  return `${String(Math.floor(whole / 60)).padStart(2, '0')}:${String(whole % 60).padStart(2, '0')}`;
}

function parseTime(value) {
  const match = value.trim().match(/^(\d{1,4}):(\d{2})$/);
  if (!match || Number(match[2]) > 59) throw new Error('Use minutes:seconds, for example 02:15.');
  return Number(match[1]) * 60 + Number(match[2]);
}

function setStatus(message, isError = false) {
  statusText.textContent = message;
  statusText.classList.toggle('error', isError);
}

function syncRange(source) {
  const duration = Math.floor(mediaInfo.duration);
  if (source === 'start-slider') startTime.value = formatTime(startSlider.value);
  if (source === 'end-slider') endTime.value = formatTime(endSlider.value);
  if (source === 'start-time') startSlider.value = Math.min(duration, parseTime(startTime.value));
  if (source === 'end-time') endSlider.value = Math.min(duration, parseTime(endTime.value));
  if (Number(startSlider.value) >= Number(endSlider.value)) {
    if (source.startsWith('start')) {
      endSlider.value = Math.min(duration, Number(startSlider.value) + 1);
      endTime.value = formatTime(endSlider.value);
    } else {
      startSlider.value = Math.max(0, Number(endSlider.value) - 1);
      startTime.value = formatTime(startSlider.value);
    }
  }
}

function updateOptions() {
  qualitySelect.replaceChildren();
  formatSelect.replaceChildren();
  if (mode === 'video') {
    const heights = [...new Set(mediaInfo.qualities)].sort((a, b) => b - a);
    for (const height of heights) qualitySelect.add(new Option(`${height}p`, String(height)));
    if (!heights.length) qualitySelect.add(new Option('Best available', 'best'));
    formatSelect.add(new Option('MP4', 'mp4'));
    formatSelect.add(new Option('MOV', 'mov'));
  } else {
    for (const bitrate of [320, 256, 192, 128]) qualitySelect.add(new Option(`${bitrate} kbps`, String(bitrate)));
    formatSelect.add(new Option('MP3', 'mp3'));
  }
  document.querySelector('#quality-field').firstChild.textContent = mode === 'video' ? 'Quality' : 'Bitrate';
}

analyzeForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  editor.hidden = true;
  downloadButton.disabled = true;
  setStatus('Reading media information…');
  try {
    const response = await fetch(`${API}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: document.querySelector('#source-url').value.trim() }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Could not analyze this source.');
    mediaInfo = data;
    const duration = Math.floor(data.duration);
    document.querySelector('#duration-label').textContent = formatTime(duration);
    document.querySelector('#timeline-end').textContent = formatTime(duration);
    startSlider.max = String(duration);
    endSlider.max = String(duration);
    startSlider.value = '0';
    endSlider.value = String(duration);
    startTime.value = '00:00';
    endTime.value = formatTime(duration);
    document.querySelector('#quality-summary').textContent = data.qualities.length ? `${data.qualities.join(' / ')}p` : 'Best available';
    mode = 'video';
    document.querySelectorAll('.mode-button').forEach((button) => {
      const active = button.dataset.mode === mode;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    updateOptions();
    editor.hidden = false;
    downloadButton.disabled = false;
    setStatus('Ready to prepare a clip.');
  } catch (error) {
    setStatus(error.message.includes('Failed to fetch') ? 'Start the local backend, then analyze again.' : error.message, true);
  }
});

startSlider.addEventListener('input', () => syncRange('start-slider'));
endSlider.addEventListener('input', () => syncRange('end-slider'));
for (const [field, source] of [[startTime, 'start-time'], [endTime, 'end-time']]) {
  field.addEventListener('change', () => {
    try { syncRange(source); } catch (error) { setStatus(error.message, true); }
  });
}

document.querySelector('#full-range').addEventListener('click', () => {
  if (!mediaInfo) return;
  startSlider.value = '0';
  endSlider.value = String(Math.floor(mediaInfo.duration));
  startTime.value = '00:00';
  endTime.value = formatTime(mediaInfo.duration);
});

document.querySelectorAll('.mode-button').forEach((button) => {
  button.addEventListener('click', () => {
    mode = button.dataset.mode;
    document.querySelectorAll('.mode-button').forEach((item) => {
      const active = item === button;
      item.classList.toggle('active', active);
      item.setAttribute('aria-pressed', String(active));
    });
    updateOptions();
  });
});

downloadButton.addEventListener('click', async () => {
  try {
    syncRange('start-time');
    syncRange('end-time');
    const start = parseTime(startTime.value);
    const end = parseTime(endTime.value);
    if (end <= start) throw new Error('End time must be after start time.');
    downloadButton.disabled = true;
    downloadButton.innerHTML = '<span aria-hidden="true">…</span> Processing clip';
    setStatus('Processing locally. Longer clips may take a little while.');
    const response = await fetch(`${API}/download`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: document.querySelector('#source-url').value.trim(),
        start,
        end,
        mode,
        quality: qualitySelect.value,
        format: formatSelect.value,
      }),
    });
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || 'Download processing failed.');
    }
    const blobUrl = URL.createObjectURL(await response.blob());
    await chrome.downloads.download({
      url: blobUrl,
      filename: `clip.${formatSelect.value}`,
      saveAs: saveLocation.checked,
    });
    setTimeout(() => URL.revokeObjectURL(blobUrl), 30_000);
    setStatus(saveLocation.checked ? 'Choose a folder in the Save As dialog.' : 'Download started.');
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    downloadButton.disabled = false;
    downloadButton.innerHTML = '<span aria-hidden="true">↓</span> Prepare download';
  }
});