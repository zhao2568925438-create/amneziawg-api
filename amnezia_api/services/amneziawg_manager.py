from __future__ import annotations

import base64
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from amnezia_api.core.terminal import clean_terminal_output


class AmneziaWGError(RuntimeError):
    pass


@dataclass(slots=True)
class SSHConfig:
    host: str
    user: str = "root"
    port: int = 22
    identity_file: str | None = None
    strict_host_key_checking: str = "accept-new"


class AmneziaWGManager:
    def __init__(
        self,
        ssh: SSHConfig,
        manage_script_path: str = "/root/awg/manage_amneziawg.sh",
        timeout: int = 60,
    ) -> None:
        self.ssh = ssh
        self.manage_script_path = manage_script_path
        self.timeout = timeout

    def add_client(self, name: str, expires: str | None = None) -> str:
        args = ["add", name]
        if expires:
            args.append(f"--expires={expires}")
        return self._run_manage(args)

    def remove_client(self, name: str) -> str:
        remote_command = self._build_remote_command(["remove", name])
        return self._run_remote_text(f"printf 'y\\n' | {remote_command}")

    def extend_client(self, name: str, duration: str) -> str:
        return self._run_manage(["extend", name, duration])

    def get_client_expiry(self, name: str) -> int | None:
        command = (
            "bash -lc "
            + shlex.quote(
                f"source /root/awg/awg_common.sh >/dev/null 2>&1 && get_client_expiry {shlex.quote(name)}"
            )
        )
        output = self._run_remote_text(command)
        if not output:
            return None
        if output.isdigit():
            return int(output)
        raise AmneziaWGError(f"Некорректный expiry для клиента '{name}': {output}")

    def fetch_client_bundle(self, name: str, output_dir: str | Path) -> tuple[Path, Path]:
        remote_config_path = self.find_client_config_path(name)
        config_text = self.read_remote_file(remote_config_path)

        output_path = Path(output_dir).expanduser().resolve()
        output_path.mkdir(parents=True, exist_ok=True)

        config_file = output_path / f"{name}.conf"
        qr_file = output_path / f"{name}.png"
        config_file.write_text(config_text, encoding="utf-8")
        qr_file.write_bytes(self.generate_remote_qr_png(remote_config_path))
        return config_file, qr_file

    def list_clients(self) -> str:
        return self._run_manage(["list"])

    def list_clients_structured(self) -> dict[str, object]:
        clients = self._parse_clients_table(self.list_clients())
        return {"clients": clients, "count": len(clients)}

    def check_connectivity(self, timeout: int = 5) -> dict[str, str | bool]:
        process = subprocess.run(
            self._build_ssh_command("exit 0"),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if process.returncode == 0:
            return {"is_reachable": True, "status": "online", "status_label": "Доступен"}

        error_text = clean_terminal_output(process.stderr) or clean_terminal_output(process.stdout) or "SSH connection failed"
        return {"is_reachable": False, "status": "offline", "status_label": error_text}

    def find_client_config_path(self, name: str) -> str:
        exact_pattern = shlex.quote(f"{name}.conf")
        fuzzy_pattern = shlex.quote(f"*{name}*.conf")
        command = (
            "find /root/awg -type f "
            f"\\( -name {exact_pattern} -o -name {fuzzy_pattern} \\) "
            "| sort | head -n 1"
        )
        result = self._run_remote_text(command)
        if not result:
            raise AmneziaWGError(f"Client config for {name!r} was not found on the server")
        return result

    def read_remote_file(self, remote_path: str) -> str:
        return self._run_remote_text(f"cat {shlex.quote(remote_path)}")

    def generate_remote_qr_png(self, remote_path: str) -> bytes:
        encoded = self._run_remote_text(f"qrencode -t PNG -o - < {shlex.quote(remote_path)} | base64")
        return base64.b64decode(encoded)

    def _run_manage(self, args: Sequence[str]) -> str:
        return self._run_remote_text(self._build_remote_command(args))

    def _run_remote_text(self, remote_command: str) -> str:
        process = subprocess.run(
            self._build_ssh_command(remote_command),
            capture_output=True,
            text=True,
            timeout=self.timeout,
        )
        if process.returncode != 0:
            error_text = clean_terminal_output(process.stderr) or clean_terminal_output(process.stdout) or "Unknown SSH error"
            raise AmneziaWGError(error_text)
        return clean_terminal_output(process.stdout)

    def _build_remote_command(self, args: Sequence[str]) -> str:
        command_parts = ["sudo", "bash", self.manage_script_path, *args]
        return " ".join(shlex.quote(part) for part in command_parts)

    def _build_ssh_command(self, remote_command: str) -> list[str]:
        command = [
            "ssh",
            "-p",
            str(self.ssh.port),
            "-o",
            f"StrictHostKeyChecking={self.ssh.strict_host_key_checking}",
        ]
        if self.ssh.identity_file:
            command.extend(["-i", self.ssh.identity_file])
        command.append(f"{self.ssh.user}@{self.ssh.host}")
        command.append(remote_command)
        return command

    def _parse_clients_table(self, raw_output: str) -> list[dict[str, str | bool | None]]:
        clients: list[dict[str, str | bool | None]] = []
        for line in raw_output.splitlines():
            cleaned = line.strip()
            if not cleaned or cleaned.startswith("[") or cleaned.startswith("Имя клиента"):
                continue
            if set(cleaned) <= {"-", "="} or cleaned.startswith("INFO:") or "|" not in cleaned:
                continue

            parts = [part.strip() for part in cleaned.split("|")]
            if len(parts) < 4:
                continue

            name, conf, qr, status = parts[:4]
            status_value, status_label, expires_in = self._normalize_status(status)
            clients.append(
                {
                    "name": name,
                    "has_conf": conf == "+",
                    "has_qr": qr == "+",
                    "status": status_value,
                    "status_label": status_label,
                    "expires_in": expires_in,
                }
            )
        return clients

    def _normalize_status(self, status: str) -> tuple[str, str, str | None]:
        cleaned = status.strip()
        expires_in = None
        if "[" in cleaned and cleaned.endswith("]"):
            base, suffix = cleaned.rsplit("[", 1)
            cleaned = base.strip()
            expires_in = suffix[:-1].strip() or None

        status_map = {"Активен": "active", "Недавно": "recent", "Нет handshake": "no_handshake"}
        return status_map.get(cleaned, "unknown"), cleaned, expires_in
