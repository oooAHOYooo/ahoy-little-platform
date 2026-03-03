# Preview & Refine the Mobile Live TV Experience

## Quick preview (same machine)

1. **Start the app**
   ```bash
   python help.py start
   # or: npm run start:dev
   ```
   This builds the SPA and starts Flask (e.g. http://127.0.0.1:5002).

2. **Chrome DevTools device mode**
   - Open http://127.0.0.1:5002 (or your port) in Chrome.
   - Go to **Live TV** (nav or `/live-tv`).
   - Press **Cmd+Shift+M** (Mac) or **Ctrl+Shift+M** (Windows) to toggle the device toolbar.
   - Pick a device (e.g. iPhone 14 Pro, Pixel 7) or set a custom width (e.g. 390px).
   - Reload and interact: tap play, channel up/down, fullscreen, etc.

3. **Throttling (optional)**  
   In DevTools → Network, set "Slow 3G" to approximate mobile networks.

---

## Preview on a real phone (same Wi‑Fi)

1. **Allow network access**
   ```bash
   AHOY_HOST=0.0.0.0 python app.py
   ```
   Or with a specific port:
   ```bash
   PORT=5002 AHOY_HOST=0.0.0.0 python app.py
   ```
   (If you use `python help.py start`, it may use gunicorn, which already binds `0.0.0.0`; check the script. With `dev.py` and Flask only, use the env vars above or run `app.py` directly.)

2. **Find your machine’s IP**
   - Mac: System Settings → Network, or run `ipconfig getifaddr en0` (or your interface).
   - Example: `192.168.1.42`.

3. **On the phone**
   - Same Wi‑Fi as the dev machine.
   - Open: `http://192.168.1.42:5002/live-tv` (replace with your IP and port).

4. **If the app is in Capacitor**  
   The packaged app loads from the **deployed** URL (e.g. `app.ahoy.ooo`), not your laptop. To test **local** changes on the device:
   - Use the phone’s **browser** with the URL above, or
   - Use a tunnel (e.g. ngrok: `ngrok http 5002`) and temporarily point the app at that URL for testing.

---

## What’s different on mobile today

- **Hero video + remote only**  
  The full TV guide is hidden at `max-width: 768px` so the screen isn’t crowded. Users change channels only via **Channel Up** / **Channel Down** on the remote.
- **Right dashboard**  
  “Now / Next / Suggested” panel is hidden on mobile (`hidden-mobile`).
- **Touch targets**  
  Remote buttons are 44px on mobile; spacing and typography are tuned at 768px and 480px.

---

## Refinement ideas

1. **Mobile channel switcher**  
   Add a “Channels” control that opens a drawer/sheet listing channels (reuse `channels` and `selectChannel`). The SPA already has `mobileDrawerOpen` and `ltv-overlay`; add a visible **Channels** button (e.g. next to the remote or below the player) that sets `mobileDrawerOpen = true` and shows a list of channel names. Tapping a channel calls `selectChannel(rowIdx)` and closes the drawer.

2. **Channel strip (optional)**  
   Reuse the Home view pattern: a horizontal strip of channel pills below the remote (e.g. “Channel 01 — Misc”, “Channel 02 — …”) so users can tap a channel without opening a drawer.

3. **Show a compact “now” line on mobile**  
   Optionally show a single line under the player: “Now: &lt;title&gt; • Channel X” and “Up next: …” so users know what’s on without the full guide.

4. **Breakpoints and touch**  
   - Adjust `@media (max-width: 768px)` and `480px` in `spa/src/views/LiveTVView.vue` for spacing, font sizes, and control layout.
   - Ensure no `touch-action: none` or `preventDefault()` on touch that would block scroll (see CLAUDE.md mobile scroll notes).

5. **Fullscreen and orientation**  
   Test fullscreen on device (e.g. `toggleFullscreen` and native fullscreen APIs) and lock/orientation if you want landscape-only for video.

---

## Files to edit

| Goal                     | File |
|--------------------------|------|
| Mobile layout, guide visibility, remote size | `spa/src/views/LiveTVView.vue` (template + scoped styles) |
| Mobile channel drawer / Channels button     | `spa/src/views/LiveTVView.vue` (template + script: `mobileDrawerOpen`, `channels`, `selectChannel`) |
| Global mobile nav (e.g. Live TV tab)        | `spa/src/components/AppNavbar.vue` |

After edits, rebuild the SPA (e.g. `cd spa && npm run build`) or rely on your existing dev flow so Flask serves the updated `spa-dist`.
