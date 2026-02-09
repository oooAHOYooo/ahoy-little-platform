<template>
  <div class="focus-container focus-strava">
    <section class="podcasts-hero focus-page-header">
      <div class="podcasts-hero-inner">
        <h1><i class="fas fa-headphones" aria-hidden="true"></i> Focus</h1>
        <p>Timer · Music · Progress</p>
      </div>
    </section>

    <div class="focus-content">
      <section class="focus-step focus-dial-section">
        <div class="focus-dial-wrap">
          <svg class="focus-dial-svg" viewBox="0 0 220 220" aria-hidden="true">
            <defs>
              <linearGradient id="focus-ring-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#FC4C02"/>
                <stop offset="100%" stop-color="#FF6B35"/>
              </linearGradient>
            </defs>
            <circle class="focus-dial-track" cx="110" cy="110" r="95" fill="none" stroke-width="8"/>
            <line x1="110" y1="22" x2="110" y2="30" class="focus-dial-tick"/>
            <line x1="198" y1="110" x2="190" y2="110" class="focus-dial-tick"/>
            <line x1="110" y1="198" x2="110" y2="190" class="focus-dial-tick"/>
            <line x1="22" y1="110" x2="30" y2="110" class="focus-dial-tick"/>
            <circle
              class="focus-dial-ring"
              cx="110" cy="110" r="95" fill="none" stroke="url(#focus-ring-gradient)"
              stroke-width="8" stroke-linecap="round" stroke-dasharray="597"
              :stroke-dashoffset="strokeDashOffset"
              transform="rotate(-90 110 110)"
            />
          </svg>
          <div class="focus-dial-center">
            <span class="focus-dial-time">{{ displayTime }}</span>
            <span class="focus-dial-label">{{ timerRunning ? 'remaining' : 'set timer' }}</span>
          </div>
        </div>
        <div class="focus-presets">
          <button
            v-for="mins in [15, 25, 45]"
            :key="mins"
            type="button"
            class="focus-preset-btn"
            :class="{ active: timerMinutes === mins }"
            :disabled="timerRunning"
            @click="setTimerMinutes(mins)"
          >
            {{ mins }}
          </button>
        </div>
        <div class="focus-dial-actions">
          <button v-if="!timerRunning && remainingSeconds > 0" type="button" class="focus-btn focus-btn-start" @click="startTimer">Start</button>
          <button v-if="timerRunning" type="button" class="focus-btn focus-btn-pause" @click="pauseTimer">Pause</button>
          <button v-if="!timerRunning && remainingSeconds > 0" type="button" class="focus-btn focus-btn-reset" @click="resetTimer">Reset</button>
        </div>
      </section>

      <section class="focus-step focus-music-section">
        <span class="focus-step-num">2</span>
        <select v-model="selectedMusicId" class="focus-music-select" aria-label="Choose focus music" @change="onMusicChange">
          <option v-for="opt in musicOptions" :key="opt.id" :value="opt.id">{{ opt.name }}</option>
        </select>
      </section>

      <section class="focus-step focus-activity-section">
        <div class="focus-activity-header">
          <span class="focus-step-num">3</span>
          <p class="focus-activity-title">Today</p>
        </div>
        <div class="focus-activity-rings" role="progressbar" :aria-valuenow="pomodorosToday" :aria-valuemax="pomodoroGoal">
          <div v-for="i in pomodoroGoal" :key="i" class="focus-ring-dot" :class="{ filled: i <= pomodorosToday }"></div>
        </div>
        <p class="focus-activity-count">{{ pomodorosToday }} / {{ pomodoroGoal }} pomodoros</p>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const POMODORO_KEY = 'focus_pomodoros'
const POMODORO_GOAL = 4
const CIRCUMFERENCE = 597

function todayKey() {
  const d = new Date()
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0')
}

const timerMinutes = ref(25)
const remainingSeconds = ref(25 * 60)
const timerRunning = ref(false)
const timerId = ref(null)
const musicOptions = ref([{ id: 'masters-remastered', name: 'Masters Remastered' }])
const ambientModes = ref([])
const selectedMusicId = ref('masters-remastered')
const pomodorosTodayCount = ref(0)

const pomodoroGoal = POMODORO_GOAL
const pomodorosToday = computed(() => pomodorosTodayCount.value)

const displayTime = computed(() => {
  const m = Math.floor(remainingSeconds.value / 60)
  const s = remainingSeconds.value % 60
  return String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0')
})

const strokeDashOffset = computed(() => {
  const total = timerMinutes.value * 60
  return CIRCUMFERENCE - (remainingSeconds.value / total) * CIRCUMFERENCE
})

function loadPomodoroCount() {
  try {
    const raw = localStorage.getItem(POMODORO_KEY)
    const data = raw ? JSON.parse(raw) : {}
    pomodorosTodayCount.value = data[todayKey()] || 0
  } catch {
    pomodorosTodayCount.value = 0
  }
}

function setTimerMinutes(mins) {
  if (timerRunning.value) return
  timerMinutes.value = mins
  remainingSeconds.value = mins * 60
}

function tick() {
  if (remainingSeconds.value <= 0) {
    timerRunning.value = false
    if (timerId.value) clearTimeout(timerId.value)
    completePomodoro()
    return
  }
  remainingSeconds.value--
  timerId.value = setTimeout(tick, 1000)
}

function startTimer() {
  if (timerRunning.value) return
  timerRunning.value = true
  onMusicChange()
  tick()
}

function pauseTimer() {
  timerRunning.value = false
  if (timerId.value) {
    clearTimeout(timerId.value)
    timerId.value = null
  }
}

function resetTimer() {
  pauseTimer()
  remainingSeconds.value = timerMinutes.value * 60
}

function completePomodoro() {
  try {
    const raw = localStorage.getItem(POMODORO_KEY)
    const data = raw ? JSON.parse(raw) : {}
    const key = todayKey()
    data[key] = (data[key] || 0) + 1
    localStorage.setItem(POMODORO_KEY, JSON.stringify(data))
    pomodorosTodayCount.value = data[key]
  } catch {}
  remainingSeconds.value = timerMinutes.value * 60
  window.dispatchEvent(new CustomEvent('ahoy:toast', { detail: { message: 'Pomodoro done!', type: 'success' } }))
}

function onMusicChange() {
  const ctrl = window.backgroundAudioController
  if (!ctrl) return
  const mode = selectedMusicId.value === 'masters-remastered'
    ? (ambientModes.value && ambientModes.value[0]) || null
    : (ambientModes.value || []).find(m => m.id === selectedMusicId.value)
  if (mode) ctrl.play(mode)
}

onMounted(() => {
  remainingSeconds.value = timerMinutes.value * 60
  loadPomodoroCount()
  fetch('/static/data/ambient-modes.json')
    .then(r => r.json())
    .then(data => {
      ambientModes.value = data || []
      musicOptions.value = [{ id: 'masters-remastered', name: 'Masters Remastered' }].concat(
        (ambientModes.value || []).map(m => ({ id: m.id, name: m.name }))
      )
    })
    .catch(() => {})
})

onUnmounted(() => {
  if (timerId.value) clearTimeout(timerId.value)
})
</script>

<style scoped>
.focus-container.focus-strava {
  min-height: 100vh;
  padding-bottom: 120px;
  background: #0d0d0d;
}
.focus-content { max-width: 400px; margin: 0 auto; padding: 20px 16px; }
.focus-page-header.podcasts-hero .podcasts-hero-inner h1 { margin: 0 0 6px 0; font-size: 28px; font-weight: 700; }
.focus-page-header.podcasts-hero .podcasts-hero-inner p { margin: 0; color: rgba(255,255,255,0.68); }

.focus-dial-section { text-align: center; margin-bottom: 32px; }
.focus-dial-wrap { position: relative; width: 280px; height: 280px; margin: 0 auto 20px; }
.focus-dial-svg { width: 100%; height: 100%; }
.focus-dial-track { stroke: rgba(255, 255, 255, 0.08); }
.focus-dial-tick { stroke: rgba(255, 255, 255, 0.2); stroke-width: 2; }
.focus-dial-ring { transition: stroke-dashoffset 1s linear; }
.focus-dial-center {
  position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%);
  display: flex; flex-direction: column; align-items: center; pointer-events: none;
}
.focus-dial-time { font-size: 48px; font-weight: 800; color: #fff; font-variant-numeric: tabular-nums; line-height: 1.1; letter-spacing: -0.02em; }
.focus-dial-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.12em; color: rgba(255,255,255,0.45); margin-top: 4px; }

.focus-presets { display: flex; justify-content: center; gap: 12px; margin-bottom: 16px; }
.focus-preset-btn {
  width: 48px; height: 48px; border-radius: 50%; border: 2px solid rgba(255,255,255,0.15);
  background: transparent; color: rgba(255,255,255,0.6); font-size: 14px; font-weight: 700; cursor: pointer; transition: all 0.2s ease;
}
.focus-preset-btn:hover:not(:disabled) { border-color: rgba(255,255,255,0.35); color: #fff; }
.focus-preset-btn.active { border-color: #FC4C02; background: rgba(252,76,2,0.15); color: #FC4C02; }
.focus-preset-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.focus-dial-actions { display: flex; align-items: center; justify-content: center; gap: 10px; flex-wrap: wrap; }
.focus-btn {
  padding: 12px 24px; border-radius: 24px; font-size: 14px; font-weight: 700; cursor: pointer; border: none;
  transition: all 0.2s ease; text-transform: uppercase; letter-spacing: 0.04em;
}
.focus-btn-start { background: #FC4C02; color: #fff; }
.focus-btn-start:hover { background: #ff5c1a; transform: scale(1.02); box-shadow: 0 4px 24px rgba(252,76,2,0.4); }
.focus-btn-pause { background: rgba(255,255,255,0.12); color: #fff; border: 1px solid rgba(255,255,255,0.2); }
.focus-btn-reset { background: transparent; color: rgba(255,255,255,0.5); }
.focus-btn-reset:hover { color: rgba(255,255,255,0.9); }

.focus-music-section, .focus-activity-section {
  display: flex; align-items: center; gap: 14px; padding: 16px 0; border-top: 1px solid rgba(255,255,255,0.06);
}
.focus-step-num {
  width: 28px; height: 28px; border-radius: 50%; background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.5);
  font-size: 12px; font-weight: 700; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.focus-music-select {
  flex: 1; padding: 12px 14px; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px;
  background: rgba(255,255,255,0.04); color: #fff; font-size: 15px; font-weight: 500; cursor: pointer;
}
.focus-music-select:focus { outline: none; border-color: rgba(252,76,2,0.5); }

.focus-activity-section { flex-direction: column; align-items: flex-start; gap: 0; }
.focus-activity-header { display: flex; align-items: center; gap: 14px; margin-bottom: 12px; }
.focus-activity-title { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(255,255,255,0.45); margin: 0; }
.focus-activity-rings { display: flex; gap: 10px; align-items: center; }
.focus-ring-dot {
  width: 14px; height: 14px; border-radius: 50%; background: rgba(255,255,255,0.1); border: 2px solid rgba(255,255,255,0.15); transition: all 0.25s ease;
}
.focus-ring-dot.filled { background: #FC4C02; border-color: #FC4C02; box-shadow: 0 0 12px rgba(252,76,2,0.5); }
.focus-activity-count { font-size: 14px; font-weight: 600; color: rgba(255,255,255,0.7); margin: 0; }

@media (max-width: 768px) {
  .focus-dial-wrap { width: 260px; height: 260px; }
  .focus-dial-time { font-size: 42px; }
}
</style>
