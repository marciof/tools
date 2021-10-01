# Rewrite as a PWA?

## Pros

- Available anywhere, no installation, always up to date on the browser.
- Also available as a CLI via Nodejs.

## Cons

- Need to potentially write/rewrite a lot (feed parsing, HTTP caching, feed checking intervals, database, downloader, resumable downloads, download jobs, UI/UX).

- Can't write videos to a folder automatically (yet?).
  - Can use Chrome on desktop?
  - See: https://web.dev/file-system-access/ 
  - See: https://googlechromelabs.github.io/text-editor/ 
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
  - Can use Syncthing?

## Prototyping?

1. QR code reader PWA (camera).
   - Feature recent history (storage).
     - See: https://github.com/pubkey/rxdb 
   - Feature P2P syncing (WebRTC).
     - See: https://github.com/szimek/sharedrop 
     - See: conflict-free replicated data type (CRDT)
     - See: https://github.com/automerge/automerge 
     - See: https://github.com/yjs/yjs 
     - See: https://github.com/josephg/diamond-types
     - See: https://josephg.com/blog/crdts-go-brrr/ 
   - Feature offline availability. 
     - See: https://www.inkandswitch.com/local-first.html 
     - See: https://rxdb.info/offline-first.html 
     - See: https://rxdb.info/downsides-of-offline-first.html 
     - See: https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Offline_Service_workers

2. "Sup" PWA.
   - Feature notifications (web workers, background, notifications, sound, vibration).
     See: https://developer.mozilla.org/en-US/docs/Web/API/Web_Periodic_Background_Synchronization_API 
   - Feature QR code for linking (image generation).

3. Video downloader PWA.
   - Feature YouTube support (CORS).
   - Feature audio/video merging on device (ffmpeg WASM).
