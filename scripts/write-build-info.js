const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

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
} catch (_) { }

let commits = [];
try {
  const commitData = execSync('git log -n 5 --pretty=format:"%h|%an|%at|%s"', { encoding: 'utf8' });
  commits = commitData.split('\n').map(line => {
    const [hash, author, timestamp, message] = line.split('|');
    return { hash, author, timestamp: parseInt(timestamp) * 1000, message };
  });
} catch (e) {
  console.warn('Could not fetch git commits:', e.message);
}

const buildInfo = {
  version,
  buildDate,
  buildTime,
  buildTimestamp,
  buildLabel: `${version} (${buildDate} ${buildTime})`,
  commits,
};

fs.writeFileSync(outPath, JSON.stringify(buildInfo, null, 2), 'utf8');
console.log('Build info:', buildInfo.buildLabel);
if (commits.length > 0) {
  console.log(`Included ${commits.length} recent commits.`);
}
