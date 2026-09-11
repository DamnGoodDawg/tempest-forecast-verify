/* dawg_crypto.js — decrypts the private Dawg journal blob published by the Mac (tempest-local,
   alerts/journal.py encrypt_payload): AES-256-GCM under a PBKDF2-HMAC-SHA256 key (200k iters),
   16-byte salt, 12-byte nonce, GCM tag appended to ct. Same file runs in the browser (WebCrypto)
   and in the Node interop test (tests/dawg_crypto.test.mjs). No dependencies. */
(function (root, factory) {
  const api = factory();
  root.DawgCrypto = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  const subtle = () => (globalThis.crypto && globalThis.crypto.subtle) ? globalThis.crypto.subtle : null;
  function b64(s) {
    const bin = atob(s); const out = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
    return out;
  }
  async function deriveKey(pass, salt, iter) {
    const km = await subtle().importKey("raw", new TextEncoder().encode(pass), "PBKDF2", false, ["deriveKey"]);
    return subtle().deriveKey({ name: "PBKDF2", salt, iterations: iter, hash: "SHA-256" }, km,
                              { name: "AES-GCM", length: 256 }, false, ["decrypt"]);
  }
  async function decrypt(blob, pass) {
    if (!subtle()) throw new Error("WebCrypto unavailable (needs HTTPS)");
    if (!blob || blob.v !== 1 || !blob.ct) throw new Error("unrecognized journal blob");
    const key = await deriveKey(String(pass || ""), b64(blob.salt), Number(blob.iter) || 200000);
    const pt = await subtle().decrypt({ name: "AES-GCM", iv: b64(blob.nonce) }, key, b64(blob.ct));
    return JSON.parse(new TextDecoder().decode(pt));
  }
  return { decrypt, deriveKey, b64 };
});
