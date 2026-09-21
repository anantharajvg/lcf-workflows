#!/usr/bin/env python3
"""Explicit, human-operated Riker workflow. Remote actions default to preview."""
import argparse
import hashlib
import json
import re
import shlex
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAYLOAD = ('src/smoke.sh', 'hpc/job.sbatch', 'configs/riker.json')
SSH = ['ssh', '-o', 'ControlMaster=no', '-o', 'ControlPath=none', '-o',
       'PreferredAuthentications=keyboard-interactive,password']

def run(cmd):
    return subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE).stdout

def prepare(run_id):
    dest = ROOT / 'runs' / run_id
    if dest.exists():
        raise ValueError('Run already exists; use a new run ID.')
    dest.mkdir(parents=True)
    hashes = {}
    for name in PAYLOAD:
        target = dest / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
        hashes[name] = hashlib.sha256(target.read_bytes()).hexdigest()
    probe = subprocess.run(
        ['git', '-C', str(ROOT), 'rev-parse', '--verify', 'HEAD'],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    commit = probe.stdout.strip() if probe.returncode == 0 else None
    (dest / 'manifest.json').write_text(json.dumps(
        {'run_id': run_id, 'git_commit': commit, 'sha256': hashes}, indent=2) + '\n')
    return dest

def verify(dest):
    manifest = json.loads((dest / 'manifest.json').read_text())
    for name in PAYLOAD:
        if hashlib.sha256((dest / name).read_bytes()).hexdigest() != manifest['sha256'][name]:
            raise ValueError('Prepared payload changed; prepare a new run.')

def commands(action, dest, cfg, job_id=None):
    remote = cfg['remote_root'] + '/' + dest.name
    host = cfg['host']
    q = shlex.quote
    ssh = SSH + [host]
    transport = shlex.join(SSH)
    if action == 'stage':
        return [ssh + ['mkdir -p -- ' + q(remote)],
                ['rsync', '-av', '-e', transport, '--exclude=results/',
                 '--exclude=job-id.txt', '--exclude=submission-attempted',
                 str(dest) + '/', host + ':' + remote + '/']]
    if action == 'submit':
        return [ssh + ['cd ' + q(remote) + ' && sbatch --parsable --account=' +
                       q(cfg['account']) + ' hpc/job.sbatch']]
    if action == 'status':
        return [ssh + ['squeue -j ' + job_id],
                ssh + ['sacct -j ' + job_id + ' --format=JobID,State,ExitCode,Elapsed -P']]
    if action == 'fetch':
        return [['rsync', '-av', '-e', transport, host + ':' + remote + '/',
                 str(dest / 'retrieved') + '/']]
    raise ValueError(action)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'stage', 'submit', 'status', 'fetch', 'check'])
    parser.add_argument('run_id')
    parser.add_argument('--execute', action='store_true', help='Actually run remote commands; authenticate in your terminal')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', args.run_id):
        parser.error('Use a run ID with letters, numbers, underscores or hyphens.')
    dest = ROOT / 'runs' / args.run_id
    if args.action == 'prepare':
        print(prepare(args.run_id))
        return
    verify(dest)
    cfg = json.loads((dest / 'configs/riker.json').read_text())
    if not re.fullmatch(r'[A-Za-z0-9_.-]+@[A-Za-z0-9.-]+', cfg['host']):
        raise ValueError('Invalid host')
    if not re.fullmatch(r'/[A-Za-z0-9_./-]+', cfg['remote_root']) or '..' in cfg['remote_root'].split('/'):
        raise ValueError('Invalid remote root')
    if args.action == 'check':
        data = json.loads((dest / 'retrieved/results/result.json').read_text())
        if data != {'sum_of_squares': 333383335000, 'terms': 10000}:
            raise ValueError('Unexpected numerical result')
        print('Numerical result verified. Also confirm COMPLETED and ExitCode 0:0 with status.')
        return
    job = None
    if args.action == 'status':
        job = (dest / 'job-id.txt').read_text().strip()
        if not re.fullmatch(r'[0-9]+', job):
            raise ValueError('Invalid job ID')
    cmds = commands(args.action, dest, cfg, job)
    for cmd in cmds:
        print(shlex.join(cmd), flush=True)
    if not args.execute:
        print('Preview only. Add --execute in your terminal to run.')
        return
    if args.action == 'submit':
        # Never automatically retry an ambiguous submission (e.g. dropped SSH).
        with (dest / 'submission-attempted').open('x') as marker:
            marker.write('Check remote squeue/sacct before any manual retry.\n')
    for cmd in cmds:
        output = run(cmd)
        print(output, end='')
    if args.action == 'submit':
        value = output.strip()
        if not re.fullmatch(r'[0-9]+(?:;[A-Za-z0-9_.-]+)?', value):
            raise ValueError('Submission response unclear; inspect remote queue before retrying.')
        (dest / 'job-id.txt').write_text(value.split(';')[0] + '\n')

if __name__ == '__main__':
    main()
