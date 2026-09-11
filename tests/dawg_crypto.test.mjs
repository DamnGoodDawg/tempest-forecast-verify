// node tests/dawg_crypto.test.mjs — proves the browser decrypt path matches the Mac's encryption.
// Fixtures are produced by tempest-local's alerts.journal.encrypt_payload with passphrase "test-pass-only".
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const DawgCrypto = require("../dawg_crypto.js");
const blob = JSON.parse(readFileSync(new URL("./fixtures/dawg_journal.enc.json", import.meta.url)));
const plain = JSON.parse(readFileSync(new URL("./fixtures/dawg_journal.plain.json", import.meta.url)));
const out = await DawgCrypto.decrypt(blob, "test-pass-only");
assert.deepEqual(out, plain);
let failed = false;
try { await DawgCrypto.decrypt(blob, "wrong-pass"); } catch (e) { failed = true; }
assert.ok(failed, "wrong passphrase must fail");
console.log(`dawg_crypto: decrypt interop OK (${blob.plain_bytes} plaintext bytes, iter ${blob.iter})`);
