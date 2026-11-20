#!/usr/bin/env python3
"""Isolated behavioral probes for strictly bounded TLS/no_log edits.

Reference-control success validates the harness, not model-generated repair quality.
The Docker worker has no network, host source, Docker socket, or real credentials.
"""
from __future__ import annotations

import argparse
import copy
import datetime
import hashlib
import http.server
import json
import os
from pathlib import Path
import ssl
import subprocess
import sys
import tempfile
import threading

IMAGE = "ansibleguard-study-runtime:20261114"
SENTINEL = "SYNTHETIC_STUDY_SECRET_7ae149"


def bounded_task(before, after, family):
    """Reject arbitrary executable YAML even inside the disposable container."""
    import yaml
    def parse(value):
        task = yaml.safe_load(value)
        if not isinstance(task, list) or len(task) != 1 or not isinstance(task[0], dict):
            raise ValueError("one leaf task required")
        return task[0]
    first, second = parse(before), parse(after)
    permitted = {"name", "tags", "changed_when", "register", "no_log"}
    if first.get("changed_when", False) is not False or first.get("register", "deployment_result") != "deployment_result":
        raise ValueError("unexpected executable task control")
    if family == "missing-validate-certs":
        module = "ansible.builtin.get_url"
        permitted.add(module)
        args = first.get(module)
        if not isinstance(args, dict) or set(args) != {"url", "dest", "mode", "validate_certs"} \
                or args["url"] != "https://localhost:4443/artifact" \
                or args["dest"] not in {f"/tmp/artifact-{i}" for i in range(6)} \
                or args["mode"] != "0644" or args["validate_certs"] is not False:
            raise ValueError("unexpected TLS fixture")
        expected = copy.deepcopy(first)
        expected[module]["validate_certs"] = True
    elif family == "credential-log-exposure":
        module = "ansible.builtin.debug"
        permitted.add(module)
        if first.get(module) != {"msg": "{{ service_password }}"} or first.get("no_log") is not False:
            raise ValueError("unexpected logging fixture")
        expected = {**first, "no_log": True}
    else:
        raise ValueError("unsupported repair family")
    if set(first) - permitted or second != expected:
        raise ValueError("edit exceeds allowed boundary")
    return first, second


def certificates(root):
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
    now = datetime.datetime.now(datetime.timezone.utc)
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Study fixture CA")])
    ca = (x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
          .serial_number(x509.random_serial_number()).not_valid_before(now - datetime.timedelta(days=1))
          .not_valid_after(now + datetime.timedelta(days=2)).add_extension(x509.BasicConstraints(ca=True, path_length=None), True)
          .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), False)
          .add_extension(x509.KeyUsage(digital_signature=True, content_commitment=False, key_encipherment=False,
                         data_encipherment=False, key_agreement=False, key_cert_sign=True, crl_sign=True,
                         encipher_only=False, decipher_only=False), True)
          .sign(key, hashes.SHA256()))
    server_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    server = (x509.CertificateBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")]))
              .issuer_name(name).public_key(server_key.public_key()).serial_number(x509.random_serial_number())
              .not_valid_before(now - datetime.timedelta(days=1)).not_valid_after(now + datetime.timedelta(days=2))
              .add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost")]), False)
              .add_extension(x509.BasicConstraints(ca=False, path_length=None), True)
              .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(key.public_key()), False)
              .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), False).sign(key, hashes.SHA256()))
    (root / "ca.pem").write_bytes(ca.public_bytes(serialization.Encoding.PEM))
    (root / "server.pem").write_bytes(server.public_bytes(serialization.Encoding.PEM))
    (root / "server.key").write_bytes(server_key.private_bytes(serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))


def execute(task, root, *, trusted=False, failure=False, logging=False):
    import yaml
    task = copy.deepcopy(task)
    if trusted:
        task["environment"] = {"SSL_CERT_FILE": str(root / "ca.pem")}
    # Harness-only instrumentation; never counted as part of a suggested edit.
    if logging:
        task["register"] = "deployment_result"
        if failure:
            task["failed_when"] = True
            task["ignore_errors"] = True
        after = [{"name": "Check task result remains usable", "ansible.builtin.assert": {
            "that": ["deployment_result.msg == service_password"], "quiet": True}, "no_log": True}]
    else:
        after = []
    play = [{"name": "Disposable study behavior probe", "hosts": "localhost", "gather_facts": False,
             "tasks": [task] + after}]
    # Model a runtime credential, not a literal next to the task in error excerpts.
    variables = root / "private-vars.yml"
    variables.write_text(yaml.safe_dump({"service_password": SENTINEL,
                                       "ansible_python_interpreter": sys.executable}))
    path = root / "play.yml"
    path.write_text(yaml.safe_dump(play, sort_keys=False))
    config = root / "ansible.cfg"
    config.write_text(f"[defaults]\nretry_files_enabled = False\nhost_key_checking = False\nremote_tmp = {root}/remote-tmp\n")
    env = {**os.environ, "HOME": str(root), "ANSIBLE_HOME": str(root / "ansible"),
           "ANSIBLE_LOCAL_TEMP": str(root / "ansible/tmp"), "ANSIBLE_CONFIG": str(config),
           "ANSIBLE_NOCOLOR": "1", "ANSIBLE_STDOUT_CALLBACK": "default"}
    result = subprocess.run([sys.executable, "-m", "ansible.cli.playbook", "-i", "localhost,", "-c", "local",
                             "--extra-vars", "@" + str(variables), str(path)],
                            cwd=root, env=env, capture_output=True, text=True, timeout=45)
    output = result.stdout + result.stderr
    artifact = root / "artifact"
    return {"returncode": result.returncode, "sentinel_visible": SENTINEL in output,
            "output": output, "artifact_content": artifact.read_text() if artifact.exists() else None}


def worker(payload):
    before, after = bounded_task(payload["before"], payload["after"], payload["family"])
    with tempfile.TemporaryDirectory(prefix="behavior-") as temporary:
        root = Path(temporary)
        if payload["family"] == "missing-validate-certs":
            certificates(root)
            class Handler(http.server.BaseHTTPRequestHandler):
                def do_GET(self):
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"expected-study-artifact")
                def log_message(self, *_args):
                    pass
            server = http.server.HTTPServer(("127.0.0.1", 4443), Handler)
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(root / "server.pem", root / "server.key")
            server.socket = context.wrap_socket(server.socket, server_side=True)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            # Normalize only fixture destination to this container's disposable root.
            for task in (before, after):
                task["ansible.builtin.get_url"]["dest"] = str(root / "artifact")
            try:
                insecure = execute(before, root)
                (root / "artifact").unlink(missing_ok=True)
                rejected = execute(after, root)
                (root / "artifact").unlink(missing_ok=True)
                trusted = execute(after, root, trusted=True)
                checks = {"before_accepts_untrusted": insecure["returncode"] == 0 and insecure["artifact_content"] == "expected-study-artifact",
                          "after_rejects_untrusted": rejected["returncode"] != 0 and rejected["artifact_content"] is None
                              and ("CERTIFICATE_VERIFY_FAILED" in rejected["output"] or "certificate verify failed" in rejected["output"]),
                          "after_accepts_trusted_same_artifact": trusted["returncode"] == 0 and trusted["artifact_content"] == "expected-study-artifact"}
                attempts = {"before_untrusted": insecure, "after_untrusted": rejected, "after_trusted": trusted}
            finally:
                server.shutdown()
                server.server_close()
        else:
            normal_before = execute(before, root, logging=True)
            normal_after = execute(after, root, logging=True)
            failed_before = execute(before, root, failure=True, logging=True)
            failed_after = execute(after, root, failure=True, logging=True)
            checks = {"before_normal_exposes_sentinel": normal_before["sentinel_visible"],
                      "after_normal_hides_sentinel": not normal_after["sentinel_visible"],
                      "before_failure_exposes_sentinel": failed_before["sentinel_visible"],
                      "after_failure_hides_sentinel": not failed_after["sentinel_visible"],
                      "task_result_preserved": all(r["returncode"] == 0 for r in
                          (normal_before, normal_after, failed_before, failed_after))}
            attempts = {"normal_before": normal_before, "normal_after": normal_after,
                        "failure_before": failed_before, "failure_after": failed_after}
        return {"checks": checks, "passed": all(checks.values()), "attempts": attempts,
                "limitation": "Bounded synthetic scenario, not general deployment equivalence."}


def container_check(payload, image=IMAGE):
    bounded_task(payload["before"], payload["after"], payload["family"])
    with tempfile.TemporaryDirectory(prefix="behavior-input-") as directory:
        path = Path(directory) / "input.json"
        path.write_text(json.dumps(payload))
        result = subprocess.run(["docker", "run", "--rm", "--network", "none", "--read-only",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges", "--pids-limit", "128",
            "--memory", "768m", "--cpus", "1", "--user", "65534:65534",
            "--tmpfs", "/tmp:rw,exec,size=256m,mode=1777", "-v", f"{path}:/input.json:ro",
            image, "python", "/worker.py", "--worker", "/input.json"],
            capture_output=True, text=True, timeout=240)
        if result.returncode:
            return {"passed": False, "status": "container-error", "stdout": result.stdout, "stderr": result.stderr}
        return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", type=Path)
    parser.add_argument("--reference-controls", action="store_true")
    parser.add_argument("--package", type=Path)
    parser.add_argument("--run", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--image", default=IMAGE)
    args = parser.parse_args()
    if args.worker:
        print(json.dumps(worker(json.loads(args.worker.read_text()))))
        return
    from scripts.llm_quality_study import repair_cases, save, load, records_for, validated_source
    import yaml
    if not args.output:
        parser.error("--output is required")
    if args.output.exists():
        parser.error("refusing to overwrite behavioral results")
    image_id = subprocess.run(["docker", "image", "inspect", args.image, "--format", "{{.Id}}"],
                              capture_output=True, text=True, check=True).stdout.strip()
    results = []
    if args.reference_controls:
        selected = [case for case in repair_cases() if case["repair_stratum"] == "eligible"]
        for case in selected:
            before = case["files"]["tasks.yml"]
            task = yaml.safe_load(before)[0]
            if case["family"] == "missing-validate-certs":
                task["ansible.builtin.get_url"]["validate_certs"] = True
            else:
                task["no_log"] = True
            payload = {"before": before, "after": yaml.safe_dump([task], sort_keys=False), "family": case["family"]}
            results.append({"case_id": case["case_id"], "producer": "authored-reference-control",
                            **container_check(payload, image_id)})
    else:
        if not args.package or not args.run:
            parser.error("--package and --run are required for generated suggestions")
        cases, records = records_for(args.package, args.run)
        validated_source(args.package, list(cases))
        for record in records:
            case = cases[record["case_id"]]
            snippet = record["result"].get("llm_fixed_code_snippet")
            if not snippet:
                results.append({"case_id": case["case_id"], "status": "not-proposed", "passed": None})
                continue
            try:
                result = container_check({"before": case["files"]["tasks.yml"], "after": snippet, "family": case["family"]}, image_id)
            except (ValueError, KeyError) as exc:
                result = {"status": "boundary-rejected", "passed": False, "reason": str(exc)}
            results.append({"case_id": case["case_id"], "producer": "delivered-model-suggestion", **result})
    save(args.output, {"image_id": image_id, "worker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         "reference_controls_only": args.reference_controls, "human_fix_review": "pending", "results": results})
    print(json.dumps({"cases": len(results), "passed": sum(r["passed"] is True for r in results),
                      "reference_controls_only": args.reference_controls, "output": str(args.output)}))


if __name__ == "__main__":
    # Docker worker runs as a standalone script; host CLI imports sibling scripts.
    if "--worker" not in sys.argv:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    main()
