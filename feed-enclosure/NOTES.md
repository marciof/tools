# Rewrite as a PWA?

## Pros

- Available anywhere, no installation, always up to date on the browser.
- Also available as a CLI via Nodejs.

## Cons

- Need to potentially write/rewrite a lot (feed parsing, HTTP caching, feed checking intervals, database, downloader, resumable downloads, download jobs, UI/UX).

- Can't write videos to a folder automatically (yet?).
  - Can use Chrome on desktop?
  - See: https://web.dev/file-system-access/ 
  - See: https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/webkitdirectory 
  - See: https://github.com/GoogleChromeLabs/browser-fs-access 
  - See: https://bugs.chromium.org/p/chromium/issues/detail?id=1011535 

- Needs a web server to serve the app.
  - Can use static GitHub pages?

- Needs a web server to sidestep CROSS.
  - Can use Heroku?
  - Can use a localhost proxy for privacy and reduced latency?
    - Python proxy web server packaged via Python for Android.

- Conflict resolution may be tricky when syncing multiple installations.
  - Can Syncthing?

## Prototyping?

1. QR code reader PWA (camera).
   - Feature recent history (storage).
   - Feature P2P syncing (WebRTC).

2. "Sup" PWA.
   - Feature notifications (web workers, background, notifications, sound, vibration).
   - Feature QR code for linking (image generation).

3. Video downloader PWA.
   - Feature YouTube support (CORS).
   - Feature audio/video merging on device (ffmpeg WASM).
