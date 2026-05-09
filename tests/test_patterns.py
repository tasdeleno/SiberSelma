"""
SAST ve secret tarama regex pattern testleri.
Çalıştır: pytest tests/
"""
import re
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import DANGEROUS_PATTERNS, SECRET_PATTERNS


def _match_any(line: str, patterns):
    return any(re.search(rgx, line) for rgx, *_ in patterns)


# --- DANGEROUS_PATTERNS .py ---

class TestPythonDangerousPatterns:
    PY = DANGEROUS_PATTERNS[".py"]

    def test_eval_detected(self):
        assert _match_any('result = eval(user_input)', self.PY)

    def test_exec_detected(self):
        assert _match_any('exec("import os")', self.PY)

    def test_os_system_detected(self):
        assert _match_any('os.system("ls " + name)', self.PY)

    def test_subprocess_shell_true_detected(self):
        assert _match_any('subprocess.run(cmd, shell=True)', self.PY)

    def test_pickle_load_detected(self):
        assert _match_any('data = pickle.loads(payload)', self.PY)

    def test_yaml_load_unsafe_detected(self):
        assert _match_any('cfg = yaml.load(f)', self.PY)

    def test_yaml_safeload_not_flagged(self):
        assert not _match_any('cfg = yaml.load(f, Loader=yaml.SafeLoader)', self.PY)

    def test_hardcoded_password_detected(self):
        assert _match_any('password = "hunter2"', self.PY)

    def test_clean_code_not_flagged(self):
        assert not _match_any('x = 1 + 2', self.PY)
        assert not _match_any('return user.name', self.PY)


# --- DANGEROUS_PATTERNS .js ---

class TestJsDangerousPatterns:
    JS = DANGEROUS_PATTERNS[".js"]

    def test_innerhtml_detected(self):
        assert _match_any('el.innerHTML = userInput', self.JS)

    def test_document_write_detected(self):
        assert _match_any('document.write(html)', self.JS)

    def test_child_process_exec_detected(self):
        assert _match_any('child_process.exec(cmd)', self.JS)

    def test_clean_code_not_flagged(self):
        assert not _match_any('const x = 5;', self.JS)


# --- SECRET_PATTERNS ---

class TestSecretPatterns:
    def test_aws_access_key(self):
        assert _match_any('aws_access_key_id = "AKIAIOSFODNN7EXAMPLE"', SECRET_PATTERNS)

    def test_github_token(self):
        assert _match_any('token = "ghp_abcdefghijklmnopqrstuvwxyz0123456789"', SECRET_PATTERNS)

    def test_private_key(self):
        assert _match_any('-----BEGIN RSA PRIVATE KEY-----', SECRET_PATTERNS)

    def test_db_connection_string(self):
        assert _match_any('DB = "postgres://admin:s3cret@db.host:5432/app"', SECRET_PATTERNS)

    def test_short_password_not_flagged(self):
        # 3 karakterden az değer eşleşmemeli
        assert not _match_any('password = "ab"', SECRET_PATTERNS)

    def test_clean_code_not_flagged(self):
        assert not _match_any('username = "john"', SECRET_PATTERNS)
