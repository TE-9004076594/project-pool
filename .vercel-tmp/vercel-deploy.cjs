#!/usr/bin/env node
const { spawnSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');
const isWindows = os.platform() === 'win32';
const ALLOWED_COMMANDS = new Set(['vercel', 'npm', 'pnpm', 'yarn']);
function log(msg) { console.error(msg); }
function commandExists(cmd) {
if (!ALLOWED_COMMANDS.has(cmd)) { throw new Error(`Command not in whitelist: ${cmd}`); }
try {
if (isWindows) { const result = spawnSync('where', [cmd], { stdio: 'ignore' }); return result.status === 0; }
else { const result = spawnSync('sh', ['-c', `command -v "$1"`, '--', cmd], { stdio: 'ignore' }); return result.status === 0; }
} catch { return false; }
}
function getCommandOutput(cmd, args) {
try {
const result = spawnSync(cmd, args, { encoding: 'utf8', stdio: ['pipe', 'pipe', 'ignore'], shell: isWindows });
return result.status === 0 ? (result.stdout || '').trim() : null;
} catch { return null; }
}
function checkVercelInstalled() {
if (!commandExists('vercel')) { log('Error: Vercel CLI is not installed'); process.exit(1); }
const version = getCommandOutput('vercel', ['--version']) || 'unknown'; log(`Vercel CLI version: ${version}`);
}
function checkLoginStatus() {
log('Checking login status...');
try {
const result = spawnSync('vercel', ['whoami'], { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'], shell: isWindows });
const output = (result.stdout || '').trim();
if (result.status === 0 && output && !output.includes('Error') && !output.includes('not logged in')) { log(`Logged in as: ${output}`); return true; }
} catch { }
return false;
}
function doDeploy(projectPath, options) {
log(''); log('Starting deployment...'); log('');
const args = ['deploy'];
if (options.yes) args.push('--yes');
if (options.prod) { args.push('--prod'); log('Deployment environment: Production'); } else { log('Deployment environment: Preview'); }
log(`Executing: vercel ${args.join(' ')}`); log('');
try {
const result = spawnSync('vercel', args, { cwd: projectPath, encoding: 'utf8', stdio: ['inherit', 'pipe', 'pipe'], timeout: 300000, shell: isWindows });
const output = (result.stdout || '') + (result.stderr || '');
log(output);
if (result.status !== 0) { throw new Error('Deployment failed'); }
const aliasedMatch = output.match(/Aliased:\s*(https:\/\/[a-zA-Z0-9.-]+\.vercel\.app)/i);
const deploymentMatch = output.match(/Production:\s*(https:\/\/[a-zA-Z0-9.-]+\.vercel\.app)/i);
const finalUrl = (aliasedMatch ? aliasedMatch[1] : null) || (deploymentMatch ? deploymentMatch[1] : null);
log(''); log('========================================'); log('Deployment successful!'); log('========================================'); log('');
if (finalUrl) { log(`Your site is live! Visit: ${finalUrl}`); log(''); console.log(JSON.stringify({ status: 'success', url: finalUrl })); }
else { console.log(JSON.stringify({ status: 'success', message: 'Deployment successful' })); }
} catch (error) { log(error.message || ''); log(''); log('Deployment failed'); process.exit(1); }
}
function main() {
log('========================================'); log('Vercel Deployment'); log('========================================'); log('');
const projectPath = process.argv[2] || '.';
checkVercelInstalled(); log('');
if (!checkLoginStatus()) { log(''); log('Error: Not logged in'); process.exit(1); }
log('');
const absPath = path.resolve(projectPath);
log(`Project path: ${absPath}`);
doDeploy(absPath, { prod: true, yes: true });
}
main();
