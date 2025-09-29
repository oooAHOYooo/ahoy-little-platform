// static/js/guest-bootstrap.js
// Provide safe defaults so pages work when not logged in.

window.LOGGED_IN = !!window.LOGGED_IN;            // from base.html if set
window.isLoggedIn = typeof window.isLoggedIn !== "undefined" ? window.isLoggedIn : window.LOGGED_IN;
window.userProfile = window.userProfile || {
  display_name: "Guest",
  username: "guest",
  email: "",
  avatar: "/static/img/default-avatar.png"
};

// Minimal player shims so Alpine bindings don't explode when no audio yet
window.globalPlayer = window.globalPlayer || (() => ({
  play() {}, pause() {}, next() {}, prev() {}, toggle() {},
}));
window.currentTrack   = typeof window.currentTrack !== "undefined" ? window.currentTrack : null;
window.isPlaying      = typeof window.isPlaying !== "undefined" ? window.isPlaying : false;
window.isShuffled     = typeof window.isShuffled !== "undefined" ? window.isShuffled : false;
window.isRepeated     = typeof window.isRepeated !== "undefined" ? window.isRepeated : false;
window.currentTime    = typeof window.currentTime !== "undefined" ? window.currentTime : 0;
window.progressPercent= typeof window.progressPercent !== "undefined" ? window.progressPercent : 0;
window.formatTime     = window.formatTime || (s => {
  s = Math.max(0, Math.floor(s||0)); const m = Math.floor(s/60), ss = String(s%60).padStart(2,"0"); return `${m}:${ss}`;
});
