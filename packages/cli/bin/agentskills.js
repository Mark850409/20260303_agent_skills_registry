#!/usr/bin/env node
const { spawnSync } = require('child_process');
const path = require('path');

const isWin = process.platform === 'win32';
const pythonExe = isWin ? 'python' : 'python3';

const mainScript = path.join(__dirname, '..', 'agentskills', 'main.py');
const vendorDir = path.join(__dirname, '..', 'vendor');
const rootDir = path.join(__dirname, '..');

// Set PYTHONPATH so python can find the vendor packages and the agentskills package itself
const env = Object.assign({}, process.env);
env.PYTHONPATH = env.PYTHONPATH
    ? `${vendorDir}${path.delimiter}${rootDir}${path.delimiter}${env.PYTHONPATH}`
    : `${vendorDir}${path.delimiter}${rootDir}`;

const args = [mainScript, ...process.argv.slice(2)];

const result = spawnSync(pythonExe, args, {
    stdio: 'inherit',
    env: env
});

process.exit(result.status !== null ? result.status : 1);
