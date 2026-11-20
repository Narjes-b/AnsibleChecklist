"""Resume exact-SHA corpus acquisition, reusing clean existing checkouts."""
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'study/manifests/github-v2-final-eligible.csv'
OLD = ROOT / 'study/manifests/github-v2-final-frozen.csv'
REPOS = ROOT / 'study/repositories'
OUT = ROOT / 'study/manifests/github-207-local-frozen.csv'


def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args],
                                   text=True, stderr=subprocess.PIPE, timeout=600).strip()


def run():
    old_hash = hashlib.sha256(OLD.read_bytes()).hexdigest()
    with MANIFEST.open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == len({r['project'].lower() for r in rows}) == 207
    for row in rows:
        assert re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', row['project'])
        assert all(p not in {'.', '..'} for p in row['project'].split('/'))
        assert re.fullmatch(r'[0-9a-f]{40}', row['commit_sha'])
    with OLD.open(newline='') as stream:
        old = {r['project'] for r in csv.DictReader(stream)}
    assert len(old) == 149
    print(json.dumps({'repositories': 207, 'overlap_with_old': sum(r['project'] in old for r in rows),
                      'existing_clones': sum((REPOS / r['project'] / '.git').is_dir() for r in rows),
                      'old_manifest_sha256': old_hash}), flush=True)
    if '--check' in sys.argv:
        return
    results = []
    for i, row in enumerate(rows, 1):
        project, sha = row['project'], row['commit_sha']
        dest = REPOS / project
        result = dict(row, repository_path=str(dest), status='failed', error='')
        try:
            assert dest.resolve().is_relative_to(REPOS.resolve()) and not dest.is_symlink()
            existing = (dest / '.git').is_dir()
            if existing:
                if git(dest, 'status', '--porcelain', '--untracked-files=all'):
                    dest = ROOT / 'study/repositories-207' / project
                    result['repository_path'] = str(dest)
                    assert dest.resolve().is_relative_to((ROOT / 'study/repositories-207').resolve())
                    existing = (dest / '.git').is_dir()
                    if existing and git(dest, 'status', '--porcelain', '--untracked-files=all'):
                        raise RuntimeError('Local changes in both checkouts; preserved')
            if not existing:
                if dest.exists() and any(dest.iterdir()):
                    raise RuntimeError('Nonempty destination is not a Git clone')
                dest.mkdir(parents=True, exist_ok=True)
                git(dest, 'init')
                git(dest, 'remote', 'add', 'origin', 'https://github.com/' + project + '.git')
            try:
                git(dest, 'cat-file', '-e', sha + '^{commit}')
            except subprocess.CalledProcessError:
                if shutil.disk_usage(REPOS).free < 1024**3:
                    raise RuntimeError('Less than 1 GiB free; acquisition paused')
                # Explicit URL avoids relying on a stale or unrelated local remote.
                git(dest, 'fetch', '--depth=1', '--no-tags',
                    'https://github.com/' + project + '.git', sha)
            git(dest, 'checkout', '--detach', sha)
            actual = git(dest, 'rev-parse', 'HEAD')
            if actual != sha:
                raise RuntimeError('Checkout SHA mismatch')
            result.update(status='collected', acquisition='reused' if existing else 'new',
                          actual_commit_sha=actual)
        except Exception as exc:
            detail = getattr(exc, 'stderr', '') or str(exc)
            result.update(error=detail[-1500:], acquisition='failed', actual_commit_sha='')
        results.append(result)
        fields = list(rows[0]) + ['acquisition', 'actual_commit_sha']
        temporary = OUT.with_suffix('.tmp')
        with temporary.open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(results)
        temporary.replace(OUT)
        print(f"[{i}/207] {project}: {result['status']} {result['acquisition']} {result['error']}", flush=True)
        if 'Less than 1 GiB' in result['error']:
            break
    assert hashlib.sha256(OLD.read_bytes()).hexdigest() == old_hash
    failures = sum(r['status'] != 'collected' for r in results)
    print(f'Verified {len(results)-failures}/207; failures={failures}; old manifest unchanged', flush=True)
    if failures or len(results) != 207:
        raise SystemExit(1)


if __name__ == '__main__':
    run()
