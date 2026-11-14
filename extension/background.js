// SVG to Slides — service worker.
// Its only job: when an existing install updates across a release with
// something worth announcing, leave a flag for the content script, which
// shows a one-time "What's new" card inside Slides. New installs get
// nothing (the store listing already told them what it does).
const ANNOUNCE = '1.2.0'; // bump when a release deserves the card again

function older(a, b) {
  const pa = String(a).split('.').map(Number);
  const pb = String(b).split('.').map(Number);
  for (let i = 0; i < Math.max(pa.length, pb.length); i++) {
    const d = (pa[i] || 0) - (pb[i] || 0);
    if (d) return d < 0;
  }
  return false;
}

chrome.runtime.onInstalled.addListener(({ reason, previousVersion }) => {
  if (reason === 'update' && previousVersion && older(previousVersion, ANNOUNCE)) {
    chrome.storage.local.set({ whatsNew: ANNOUNCE });
  }
});
