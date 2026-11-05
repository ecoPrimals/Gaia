#!/usr/bin/env python3
"""Generate self-signed TLS cert for all three Gaia faces."""
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime, ipaddress, os

cert_dir = os.path.join(os.path.dirname(__file__), "..", "certs")
key_file = os.path.join(cert_dir, "gate-key.pem")
cert_file = os.path.join(cert_dir, "gate-cert.pem")

key = rsa.generate_private_key(65537, 2048)
name = x509.Name([
    x509.NameAttribute(NameOID.COMMON_NAME, "nestgate.io"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ecoPrimals"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Michigan"),
    x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
])

cert = (x509.CertificateBuilder()
    .subject_name(name).issuer_name(name)
    .public_key(key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.datetime.utcnow())
    .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=3650))
    .add_extension(x509.SubjectAlternativeName([
        x509.DNSName("nestgate.io"), x509.DNSName("*.nestgate.io"),
        x509.DNSName("primals.eco"), x509.DNSName("*.primals.eco"),
        x509.DNSName("gaia"), x509.DNSName("localhost"),
        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        # ZK — no LAN IPs in cert SANs
    ]), critical=False)
    .sign(key, hashes.SHA256()))

with open(key_file, "wb") as f:
    f.write(key.private_bytes(serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption()))

with open(cert_file, "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print(f"CERT: {cert_file}")
print(f"KEY:  {key_file}")
print(f"SANs: nestgate.io, *.nestgate.io, primals.eco, *.primals.eco, gaia, localhost, 127.0.0.1")
