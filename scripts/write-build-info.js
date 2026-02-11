#!/usr/bin/env node
/**
 * Writes electron/build-info.json with version and compile date/time.
 * Run before electron-builder so the packed app knows its build identity.
 */
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const pkgPath = path.join(root, 'package.json');
const outPath = path.join(root, 'electron', 'build-info.json');

const now = new Date();
const buildDate = now.toISOString().slice(0, 10); // YYYY-MM-DD
const buildTime = now.toTimeString().slice(0, 8); // HH:mm:ss
const buildTimestamp = now.toISOString(); // full ISO

let version = '0.0.0';
try {
  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
  version = pkg.version || version;
} catch (_) {}

const buildInfo = {
  version,
  buildDate,
  buildTime,
  buildTimestamp,
  buildLabel: `${version} (${buildDate} ${buildTime})`,
};

fs.writeFileSync(outPath, JSON.stringify(buildInfo, null, 2), 'utf8');
console.log('Build info:', buildInfo.buildLabel);
