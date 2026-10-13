// DOM smoke test for the standalone browser calculator (Node.js, no dependencies).
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');

const html = fs.readFileSync(path.join(__dirname, '..', 'web', 'index.html'), 'utf8');
const script = html.split('<script>', 2)[1]?.split('</script>', 1)[0];
assert.ok(script, 'Inline browser application script should exist');
new vm.Script(script);

const ids = ['gcs-eye', 'gcs-verbal', 'gcs-motor', 'gcs-pupils',
             'gcs-intubated', 'gcs-pediatric', 'gcs-total', 'gcs-detail'];
const nodes = Object.fromEntries(ids.map(id => [id, {
    value: '', checked: false, textContent: '', disabled: false,
    addEventListener() {}
}]));
nodes['gcs-eye'].value = '4';
nodes['gcs-verbal'].value = '5';
nodes['gcs-motor'].value = '6';
nodes['gcs-verbal'].options = [1, 2, 3, 4, 5].map(i => ({
    value: String(i), textContent: ''
}));
const context = {document: {getElementById: id => nodes[id]}};
vm.runInNewContext(script, context);
assert.match(nodes['gcs-total'].textContent, /GCS 15 \/ 15/);
nodes['gcs-pupils'].value = '2';
context.updateScore();
assert.match(nodes['gcs-total'].textContent, /GCS-P 13/);
nodes['gcs-intubated'].checked = true;
context.updateScore();
assert.equal(nodes['gcs-total'].textContent, 'Total GCS unavailable');
assert.match(nodes['gcs-detail'].textContent, /V-NT/);
assert.doesNotMatch(nodes['gcs-detail'].textContent, /GCS-P [0-9]/);
assert.equal(nodes['gcs-verbal'].disabled, true);
nodes['gcs-intubated'].checked = false;
nodes['gcs-pediatric'].checked = true;
nodes['gcs-pupils'].value = '';
context.updateScore();
assert.match(nodes['gcs-verbal'].options[4].textContent, /coos\/babbles/);
assert.equal(nodes['gcs-verbal'].disabled, false);
console.log('Browser scoring smoke test passed');
