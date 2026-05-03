const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const { execFile } = require('child_process');

let statusBar;
let lastLineCount = {};
let lastPlayTime = 0;
const COOLDOWN_MS = 80;

function log(msg) {
  console.log('[SlapVSCode] ' + msg);
}

function playSound(context) {
  const now = Date.now();
  if (now - lastPlayTime < COOLDOWN_MS) return;
  lastPlayTime = now;

  try {
    const cfg = vscode.workspace.getConfiguration('slapvscode');
    if (!cfg.get('enabled')) return;
    const pack = cfg.get('soundPack') || 'slap';
    const volume = String(cfg.get('volume') || 0.8);
    const dir = path.join(context.extensionPath, 'sounds', pack);
    if (!fs.existsSync(dir)) { log('No existe: ' + dir); return; }
    const files = fs.readdirSync(dir).filter(f => /\.(mp3|wav|aiff)$/i.test(f));
    if (!files.length) { log('Sin sonidos en: ' + dir); return; }
    const file = path.join(dir, files[Math.floor(Math.random() * files.length)]);
    log('Reproduciendo: ' + file);
    execFile('afplay', ['-v', volume, file], err => {
      if (err) log('afplay error: ' + err.message);
    });
  } catch(e) { log('playSound error: ' + e.message); }
}

function updateBar(context) {
  try {
    const cfg = vscode.workspace.getConfiguration('slapvscode');
    const on = cfg.get('enabled');
    const pack = cfg.get('soundPack') || 'slap';
    const dir = path.join(context.extensionPath, 'sounds', pack);
    const count = fs.existsSync(dir)
      ? fs.readdirSync(dir).filter(f => /\.(mp3|wav|aiff)$/i.test(f)).length
      : 0;
    statusBar.text = on ? ('$(unmute) Slap [' + pack + ' ' + count + ']') : '$(mute) Slap OFF';
    statusBar.tooltip = on ? ('Pack: ' + pack + ' | ' + count + ' sonidos') : 'SlapVSCode desactivado';
    statusBar.color = on ? undefined : '#888';
  } catch(e) { log('updateBar error: ' + e.message); }
}

function activate(context) {
  log('Activando...');

  statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 200);
  statusBar.command = 'slapvscode.toggle';
  updateBar(context);
  statusBar.show();
  context.subscriptions.push(statusBar);

  context.subscriptions.push(
    vscode.commands.registerCommand('slapvscode.toggle', () => {
      const cfg = vscode.workspace.getConfiguration('slapvscode');
      const now = cfg.get('enabled');
      cfg.update('enabled', !now, vscode.ConfigurationTarget.Global);
      updateBar(context);
      vscode.window.showInformationMessage('SlapVSCode: ' + (!now ? 'ON 🔊' : 'OFF 🔇'));
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('slapvscode.testSound', () => {
      playSound(context);
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('slapvscode.nextPack', async () => {
      const packs = [
        { label: '👋 Slap', value: 'slap' },
        { label: '🎪 Cartoon', value: 'cartoon' },
        { label: '🕹 Retro', value: 'retro' },
      ];
      const sel = await vscode.window.showQuickPick(packs, { placeHolder: 'Elige pack' });
      if (sel) {
        await vscode.workspace.getConfiguration('slapvscode')
          .update('soundPack', sel.value, vscode.ConfigurationTarget.Global);
        updateBar(context);
      }
    })
  );

  // Trigger: Enter (nueva línea) O Space
  context.subscriptions.push(
    vscode.workspace.onDidChangeTextDocument(e => {
      const cfg = vscode.workspace.getConfiguration('slapvscode');
      if (!cfg.get('enabled')) return;

      for (const change of e.contentChanges) {
        const text = change.text;
        // Enter
        if (text === '\n' || text === '\r\n' || text === '\r') {
          playSound(context);
          return;
        }
        // Space
        if (text === ' ') {
          playSound(context);
          return;
        }
      }

      // Fallback: detectar Enter por cambio de líneas
      const uri = e.document.uri.toString();
      const prev = lastLineCount[uri] || e.document.lineCount;
      const curr = e.document.lineCount;
      if (curr > prev) {
        playSound(context);
      }
      lastLineCount[uri] = curr;
    })
  );

  context.subscriptions.push(
    vscode.workspace.onDidChangeConfiguration(e => {
      if (e.affectsConfiguration('slapvscode')) updateBar(context);
    })
  );

  log('Extension activa. Sonidos en: ' + path.join(context.extensionPath, 'sounds'));
}

function deactivate() { log('Desactivada'); }
module.exports = { activate, deactivate };
