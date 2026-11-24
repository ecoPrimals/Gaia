#!/usr/bin/env python3
"""hands - knock on the phones wired to this body, introduce myself, and try to shake hands.

    python scripts/hands.py            knock: who is on the wire, what each will say, whether we have shaken before
    python scripts/hands.py pair       ask the iPhone to trust this body (it shows "Trust This Computer?");
                                       waits for the answer on its screen and keeps the record where Apple's
                                       service keeps them. This is a key exchange: it is run on Kevin's word,
                                       and the tap on the phone is the consent.

A knock is a read. Android answers through adb: "device" means it already holds my key, "unauthorized" means it
is asking its owner. An iPhone answers through Apple's device service on 127.0.0.1:27015 (a loopback door): before
trust it gives its name, model and iOS; after trust it opens a session.

Nothing here holds a key. A pairing's keys are made with the openssl already on this body, live only in a
temporary folder while the phone is asked, and end up in the service's own store (ProgramData/Apple/Lockdown).
Nothing is read from a phone's storage here, and no key or record is ever printed.
"""
import json, os, plistlib, shutil, socket, ssl, struct, subprocess, sys, tempfile, time, uuid

MUX = ("127.0.0.1", 27015)
LOCKDOWN_PORT = 62078
LABEL = "gaia-hands"
MODELS = {"iPhone10,1": "iPhone 8", "iPhone10,4": "iPhone 8", "iPhone10,3": "iPhone X", "iPhone10,6": "iPhone X",
          "iPhone11,2": "iPhone XS", "iPhone11,4": "iPhone XS Max", "iPhone11,6": "iPhone XS Max", "iPhone11,8": "iPhone XR",
          "iPhone12,1": "iPhone 11", "iPhone12,3": "iPhone 11 Pro", "iPhone12,5": "iPhone 11 Pro Max", "iPhone12,8": "iPhone SE (2nd)",
          "iPhone13,1": "iPhone 12 mini", "iPhone13,2": "iPhone 12", "iPhone13,3": "iPhone 12 Pro", "iPhone13,4": "iPhone 12 Pro Max",
          "iPhone14,4": "iPhone 13 mini", "iPhone14,5": "iPhone 13", "iPhone14,2": "iPhone 13 Pro", "iPhone14,3": "iPhone 13 Pro Max",
          "iPhone14,6": "iPhone SE (3rd)", "iPhone14,7": "iPhone 14", "iPhone14,8": "iPhone 14 Plus"}
CHIPS = {"8015": "A11 (8 / X)", "8020": "A12 (XS / XS Max / XR)", "8030": "A13 (11 family)", "8101": "A14 (12 family)",
         "8110": "A15 (13 family / 14 / SE 3rd)", "8120": "A16", "8130": "A17 Pro", "8140": "A18"}


class Said(Exception):
    """The other side answered, and the answer was no (or not yet)."""


def short(udid):
    return ("…" + udid[-4:]) if udid else "?"


# ── Apple's device service: the usbmux door ─────────────────────────────────────────────────────────────────────

class Mux:
    def __init__(self):
        self.s = socket.create_connection(MUX, timeout=6)
        self.tag = 0

    def ask(self, msg):
        self.tag += 1
        body = plistlib.dumps(dict(msg, ClientVersionString=LABEL, ProgName=LABEL, kLibUSBMuxVersion=3))
        self.s.sendall(struct.pack("<IIII", len(body) + 16, 1, 8, self.tag) + body)
        head = self._read(16)
        size = struct.unpack("<I", head[:4])[0]
        return plistlib.loads(self._read(size - 16))

    def _read(self, n):
        buf = b""
        while len(buf) < n:
            part = self.s.recv(n - len(buf))
            if not part:
                raise ConnectionError("the device service closed the door")
            buf += part
        return buf

    def close(self):
        try:
            self.s.close()
        except Exception:
            pass


def mux_devices():
    m = Mux()
    try:
        out = []
        for d in m.ask({"MessageType": "ListDevices"}).get("DeviceList", []):
            p = d.get("Properties", {})
            udid = p.get("SerialNumber", "")
            if len(udid) == 24 and "-" not in udid:        # newer phones: records are kept under 8-16 with a dash
                udid = udid[:8] + "-" + udid[8:]
            out.append({"id": p.get("DeviceID", d.get("DeviceID")), "udid": udid, "wire": p.get("ConnectionType", "?")})
        return out
    finally:
        m.close()


def mux_buid():
    m = Mux()
    try:
        return m.ask({"MessageType": "ReadBUID"}).get("BUID")
    finally:
        m.close()


def mux_record(udid):
    m = Mux()
    try:
        data = m.ask({"MessageType": "ReadPairRecord", "PairRecordID": udid}).get("PairRecordData")
        return plistlib.loads(data) if data else None
    finally:
        m.close()


def mux_save_record(udid, device_id, record):
    m = Mux()
    try:
        r = m.ask({"MessageType": "SavePairRecord", "PairRecordID": udid, "DeviceID": device_id,
                   "PairRecordData": plistlib.dumps(record)})
        return r.get("Number", 0) == 0
    finally:
        m.close()


class Lockdown:
    """One conversation with the phone's front desk, through the service's tunnel."""

    def __init__(self, device_id):
        self.m = Mux()
        port = socket.htons(LOCKDOWN_PORT)
        r = self.m.ask({"MessageType": "Connect", "DeviceID": device_id, "PortNumber": port})
        if r.get("Number", 0) != 0:
            self.m.close()
            raise Said("the phone would not open its front desk (code %s)" % r.get("Number"))
        self.s = self.m.s
        self.s.settimeout(12)

    def ask(self, **msg):
        body = plistlib.dumps(dict(msg, Label=LABEL))
        self.s.sendall(struct.pack(">I", len(body)) + body)
        n = struct.unpack(">I", self._read(4))[0]
        return plistlib.loads(self._read(n))

    def _read(self, n):
        buf = b""
        while len(buf) < n:
            part = self.s.recv(n - len(buf))
            if not part:
                raise ConnectionError("the phone hung up")
            buf += part
        return buf

    def value(self, key=None, domain=None):
        q = {"Request": "GetValue"}
        if key:
            q["Key"] = key
        if domain:
            q["Domain"] = domain
        r = self.ask(**q)
        if "Error" in r:
            raise Said(r["Error"])
        return r.get("Value")

    def session(self, record):
        """Shake hands with a record we already hold. After this the line is private."""
        r = self.ask(Request="StartSession", HostID=record["HostID"], SystemBUID=record["SystemBUID"])
        if "Error" in r:
            raise Said(r["Error"])
        if r.get("EnableSessionSSL"):
            d = tempfile.mkdtemp(prefix="gaia-hands-")
            try:
                pem = os.path.join(d, "h.pem")
                with open(pem, "wb") as fh:
                    fh.write(record["HostCertificate"] + b"\n" + record["HostPrivateKey"])
                ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                try:
                    ctx.set_ciphers("ALL:@SECLEVEL=0")
                    ctx.minimum_version = ssl.TLSVersion.TLSv1
                except Exception:
                    pass
                ctx.load_cert_chain(pem)
            finally:
                shutil.rmtree(d, ignore_errors=True)
            self.s = ctx.wrap_socket(self.s)
        return r.get("SessionID")

    def close(self):
        try:
            self.s.close()
        except Exception:
            pass
        self.m.close()


# ── knock ───────────────────────────────────────────────────────────────────────────────────────────────────────

def knock_iphone(dev):
    out = {"hand": "iphone", "wire": dev["wire"], "udid": short(dev["udid"])}
    bare = dev["udid"].replace("-", "")
    chip = bare[4:8] if len(bare) == 24 and bare.startswith("0000") else ""
    if chip in CHIPS:
        out["chip"] = CHIPS[chip]
    try:
        ld = Lockdown(dev["id"])
    except (Said, OSError) as e:
        out["front_desk"] = str(e)
        return out
    try:
        said = {}
        for key in ("DeviceName", "ProductType", "ProductVersion", "DeviceClass"):
            try:
                said[key] = ld.value(key)
            except Said as e:
                said[key] = "(would not say: %s)" % e
        out["name"] = said["DeviceName"]
        out["model"] = MODELS.get(said["ProductType"], said["ProductType"])
        out["ios"] = said["ProductVersion"]
        record = mux_record(dev["udid"])
        if not record:
            out["handshake"] = "none yet: this body holds no record for it"
            return out
        try:
            ld.session(record)
            out["handshake"] = "yes: it remembers us"
            for label, key, domain in (("battery", "BatteryCurrentCapacity", "com.apple.mobile.battery"),
                                       ("charging", "BatteryIsCharging", "com.apple.mobile.battery"),
                                       ("locked", "PasswordProtected", None)):
                try:
                    out[label] = ld.value(key, domain)
                except Said:
                    pass
        except Said as e:
            out["handshake"] = "no: I hold a record but the phone said %s" % e
        except (ssl.SSLError, OSError) as e:
            out["handshake"] = "the phone accepted the record, then the private line failed (%s)" % type(e).__name__
    finally:
        ld.close()
    return out


def knock_android():
    adb = shutil.which("adb")
    if not adb:
        return [{"hand": "android", "state": "no adb on this body"}]
    r = subprocess.run([adb, "devices"], capture_output=True, text=True, timeout=30)
    out = []
    for line in r.stdout.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 2:
            continue
        serial, state = parts[0], parts[1]
        d = {"hand": "android", "serial": short(serial)}
        if state == "device":
            d["handshake"] = "yes: it remembers us"
            for label, prop in (("model", "ro.product.model"), ("android", "ro.build.version.release"),
                                ("patch", "ro.build.version.security_patch")):
                p = subprocess.run([adb, "-s", serial, "shell", "getprop", prop], capture_output=True, text=True, timeout=15)
                d[label] = p.stdout.strip()
            b = subprocess.run([adb, "-s", serial, "shell", "dumpsys", "battery"], capture_output=True, text=True, timeout=15)
            for ln in b.stdout.splitlines():
                if ln.strip().startswith("level:"):
                    d["battery"] = int(ln.split(":")[1])
        elif state == "unauthorized":
            d["handshake"] = "not yet: it is asking its owner on its screen"
        else:
            d["handshake"] = "state: " + state
        out.append(d)
    return out


def knock():
    hands = knock_android()
    try:
        devs = mux_devices()
        service = "up"
    except OSError:
        devs, service = [], "not answering on 127.0.0.1:27015"
    for dev in devs:
        hands.append(knock_iphone(dev))
    return {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "apple_service": service, "on_the_wire": len(hands), "hands": hands}


# ── pair: ask the iPhone to trust this body ─────────────────────────────────────────────────────────────────────

EXT = """[root]
basicConstraints = critical, CA:TRUE
[leaf]
basicConstraints = critical, CA:FALSE
keyUsage = critical, digitalSignature, keyEncipherment
subjectKeyIdentifier = hash
[req]
distinguished_name = dn
prompt = no
[dn]
O = Gaia
"""


def find_openssl():
    for p in (shutil.which("openssl"), r"C:\Program Files\Git\usr\bin\openssl.exe", r"C:\Program Files\Git\mingw64\bin\openssl.exe"):
        if p and os.path.isfile(p):
            return p
    raise Said("no openssl on this body to make the certificates with")


def make_certs(device_pub_pkcs1, workdir):
    """Root, host and device certificates the way a phone expects them. -> dict of PEM bytes."""
    o = find_openssl()
    f = lambda n: os.path.join(workdir, n)
    with open(f("ext.cnf"), "w") as fh:
        fh.write(EXT)
    with open(f("dev1.pem"), "wb") as fh:
        fh.write(device_pub_pkcs1)

    def run(*args):
        r = subprocess.run([o] + list(args), capture_output=True, text=True, cwd=workdir,
                           env=dict(os.environ, OPENSSL_CONF=f("ext.cnf")))
        if r.returncode != 0:
            raise Said("openssl %s failed: %s" % (args[0], (r.stderr or "").strip().splitlines()[-1:] or "?"))

    run("genrsa", "-traditional", "-out", "root.key", "2048")
    run("genrsa", "-traditional", "-out", "host.key", "2048")
    run("req", "-new", "-key", "root.key", "-out", "any.csr", "-config", "ext.cnf")
    run("x509", "-req", "-in", "any.csr", "-signkey", "root.key", "-set_serial", "0", "-days", "3650", "-sha256",
        "-extfile", "ext.cnf", "-extensions", "root", "-out", "root.pem")
    run("rsa", "-in", "host.key", "-pubout", "-out", "host.pub")
    run("x509", "-req", "-in", "any.csr", "-force_pubkey", "host.pub", "-CA", "root.pem", "-CAkey", "root.key",
        "-set_serial", "0", "-days", "3650", "-sha256", "-extfile", "ext.cnf", "-extensions", "leaf", "-out", "host.pem")
    run("rsa", "-RSAPublicKey_in", "-in", "dev1.pem", "-pubout", "-out", "dev.pub")
    run("x509", "-req", "-in", "any.csr", "-force_pubkey", "dev.pub", "-CA", "root.pem", "-CAkey", "root.key",
        "-set_serial", "0", "-days", "3650", "-sha256", "-extfile", "ext.cnf", "-extensions", "leaf", "-out", "device.pem")
    run("verify", "-CAfile", "root.pem", "host.pem", "device.pem")
    return {n: open(f(n), "rb").read() for n in ("root.pem", "root.key", "host.pem", "host.key", "device.pem")}


def pair(wait=120):
    devs = [d for d in mux_devices() if d["wire"] == "USB"]
    if not devs:
        return {"state": "no iPhone on the wire"}
    dev = devs[0]
    res = {"hand": "iphone", "udid": short(dev["udid"])}
    if mux_record(dev["udid"]):
        ld = Lockdown(dev["id"])
        try:
            ld.session(mux_record(dev["udid"]))
            res["state"] = "already shaken: it remembers us"
            return res
        except Said as e:
            res["old_record"] = "the phone no longer honours the record this body holds (%s); asking again" % e
        finally:
            ld.close()
    workdir = tempfile.mkdtemp(prefix="gaia-hands-")
    ld = Lockdown(dev["id"])
    try:
        res["name"] = ld.value("DeviceName")
        certs = make_certs(ld.value("DevicePublicKey"), workdir)
        try:
            wifi = ld.value("WiFiAddress")
        except Said:
            wifi = None
        buid = mux_buid()
        host_id = str(uuid.uuid4()).upper()
        offer = {"DeviceCertificate": certs["device.pem"], "HostCertificate": certs["host.pem"],
                 "RootCertificate": certs["root.pem"], "HostID": host_id, "SystemBUID": buid}
        deadline = time.time() + wait
        asked = False
        while True:
            r = ld.ask(Request="Pair", PairRecord=offer, ProtocolVersion="2", PairingOptions={"ExtendedPairingErrors": True})
            err = r.get("Error")
            if not err:
                record = dict(offer, HostPrivateKey=certs["host.key"], RootPrivateKey=certs["root.key"])
                if r.get("EscrowBag"):
                    record["EscrowBag"] = r["EscrowBag"]
                if wifi:
                    record["WiFiMACAddress"] = wifi
                res["kept"] = mux_save_record(dev["udid"], dev["id"], record)
                res["state"] = "shaken: the phone trusts this body" if res["kept"] else "the phone said yes but the service would not keep the record"
                return res
            if err == "PairingDialogResponsePending":
                if not asked:
                    print("the phone is asking on its screen: Trust This Computer?  (waiting up to %d s)" % wait, flush=True)
                    asked = True
            elif err == "PasswordProtected":
                if not asked:
                    print("the phone is locked: it will ask once it is unlocked  (waiting up to %d s)" % wait, flush=True)
                    asked = True
            elif err == "UserDeniedPairing":
                res["state"] = "the answer on the phone was no"
                return res
            else:
                res["state"] = "the phone said: %s" % err
                return res
            if time.time() > deadline:
                res["state"] = "no answer on the phone within %d s; nothing was kept" % wait
                return res
            time.sleep(2)
    finally:
        ld.close()
        shutil.rmtree(workdir, ignore_errors=True)


def main(argv):
    cmd = argv[0] if argv else "knock"
    try:
        if cmd == "knock":
            out = knock()
        elif cmd == "pair":
            out = pair(int(argv[1]) if len(argv) > 1 else 120)
        else:
            print(__doc__)
            return 2
    except Said as e:
        out = {"state": str(e)}
    except OSError as e:
        out = {"state": "the device service is not answering (%s)" % type(e).__name__}
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
