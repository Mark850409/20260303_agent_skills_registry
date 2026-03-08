const { spawnSync } = require('child_process');
const path = require('path');

const isWin = process.platform === 'win32';
const pythonExe = isWin ? 'python' : 'python3';

console.log('Installing Python dependencies for agentskills CLI...');

// Ensure pip is available
const pipCheck = spawnSync(pythonExe, ['-m', 'pip', '--version']);
if (pipCheck.status !== 0) {
    console.error(`Error: Could not find pip. Please ensure Python and pip are installed and accessible via '${pythonExe}'.`);
    process.exit(1);
}

// Install requirements into a local "vendor" directory
const args = ['-m', 'pip', 'install', '-r', 'requirements.txt', '--target', 'vendor'];
const result = spawnSync(pythonExe, args, { stdio: 'inherit' });

if (result.status !== 0) {
    console.error('Failed to install Python dependencies.');
    process.exit(result.status);
}

console.log('Dependencies installed successfully.');
