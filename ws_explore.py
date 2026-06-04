#!/usr/bin/env python3
"""
ws_explore.py - one-off WebSocket menu probe (stdlib only). Manual/diagnostic, NOT in
the daily capture path. Connects to the Tempest WebSocket, subscribes to observations,
rapid wind, and events, listens ~75s, and records which message types arrive plus one
sample payload of each into ws_sample.json. Answers "what can we actually pull from the
WebSocket with a personal token?" (Spoiler from earlier testing: device_status/hub_status
are NOT delivered to personal tokens; this enumerates what IS.)

Env: TEMPEST_TOKEN, TEMPEST_STATION_ID.
"""
import json, os, sys, socket, ssl, base64, struct, time, urllib.request, urllib.parse

UA = "tempest-forecast-verify/1.0 (tkb5047@gmail.com)"
LISTEN_SECONDS = 75


def get(url, params=None):
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def discover_device_id(station, token):
    st = get("https://swd.weatherflow.com/swd/rest/stations", {"token": token})
    for s in st.get("stations", []):
        if str(s.get("station_id")) == str(station):
            for d in s.get("devices", []):
                if d.get("device_type") == "ST":
                    return d.get("device_id")
    return None


def ws_send(sock, opcode, payload=b""):
    mask = os.urandom(4)
    n = len(payload)
    hdr = bytearray([0x80 | opcode])
    if n < 126:
        hdr.append(0x80 | n)
    elif n < 65536:
        hdr.append(0x80 | 126); hdr += struct.pack(">H", n)
    else:
        hdr.append(0x80 | 127); hdr += struct.pack(">Q", n)
    hdr += mask
    sock.sendall(bytes(hdr) + bytes(b ^ mask[i % 4] for i, b in enumerate(payload)))


class Reader:
    def __init__(self, sock, leftover=b""):
        self.s, self.buf = sock, leftover

    def _need(self, n):
        while len(self.buf) < n:
            chunk = self.s.recv(4096)
            if not chunk:
                raise RuntimeError("ws closed")
            self.buf += chunk

    def frame(self):
        self._need(2)
        b0, b1 = self.buf[0], self.buf[1]
        opcode, masked, ln, idx = b0 & 0x0F, b1 & 0x80, b1 & 0x7F, 2
        if ln == 126:
            self._need(4); ln = struct.unpack(">H", self.buf[2:4])[0]; idx = 4
        elif ln == 127:
            self._need(10); ln = struct.unpack(">Q", self.buf[2:10])[0]; idx = 10
        mask = b""
        if masked:
            self._need(idx + 4); mask = self.buf[idx:idx + 4]; idx += 4
        self._need(idx + ln)
        payload = self.buf[idx:idx + ln]; self.buf = self.buf[idx + ln:]
        if masked:
            payload = bytes(c ^ mask[i % 4] for i, c in enumerate(payload))
        return opcode, payload


def main():
    token, station = os.environ.get("TEMPEST_TOKEN"), os.environ.get("TEMPEST_STATION_ID")
    if not token or not station:
        print("TEMPEST_TOKEN/TEMPEST_STATION_ID not set", file=sys.stderr); sys.exit(1)
    device_id = discover_device_id(station, token)
    if not device_id:
        print("could not discover device_id", file=sys.stderr); sys.exit(1)

    host = "ws.weatherflow.com"
    path = "/swd/data?token=" + urllib.parse.quote(token, safe="")
    raw = socket.create_connection((host, 443), timeout=20)
    s = ssl.create_default_context().wrap_socket(raw, server_hostname=host)
    key = base64.b64encode(os.urandom(16)).decode()
    s.sendall((f"GET {path} HTTP/1.1\r\nHost: {host}\r\nUpgrade: websocket\r\n"
               f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n"
               f"Sec-WebSocket-Version: 13\r\n\r\n").encode())
    buf = b""
    while b"\r\n\r\n" not in buf:
        buf += s.recv(1024)
    rdr = Reader(s, buf.split(b"\r\n\r\n", 1)[1])

    for t in ("listen_start", "listen_rapid_start", "listen_start_events"):
        ws_send(s, 0x1, json.dumps({"type": t, "device_id": int(device_id), "id": t}).encode())

    s.settimeout(LISTEN_SECONDS)
    samples, counts, end = {}, {}, time.time() + LISTEN_SECONDS
    while time.time() < end:
        try:
            opcode, payload = rdr.frame()
        except (socket.timeout, RuntimeError):
            break
        if opcode == 0x8:
            break
        if opcode == 0x9:
            ws_send(s, 0xA, payload); continue
        if opcode != 0x1:
            continue
        try:
            m = json.loads(payload.decode())
        except Exception:
            continue
        t = m.get("type", "?")
        counts[t] = counts.get(t, 0) + 1
        if t not in samples:
            samples[t] = m            # keep the first example of each type
    try:
        s.close()
    except Exception:
        pass

    out = {"device_id": device_id, "listened_seconds": LISTEN_SECONDS,
           "types_seen": sorted(counts), "counts": counts, "samples": samples}
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ws_sample.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("types seen:", out["types_seen"])
    print("counts:", counts)


if __name__ == "__main__":
    main()
