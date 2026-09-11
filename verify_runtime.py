"""Run two real n8n executions against a private mock CRM, then remove containers."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IMAGE = 'docker.n8n.io/n8nio/n8n@sha256:a8c95f75c6fdf65f5f2b7a7b354744eaa1c62bb911b5c00af6499c3f38e4cd32'
NETWORK = 'autobusiness-n8n-proof'
MOCK = 'autobusiness-n8n-crm'

def run(*args):
    return subprocess.run(['docker', *args], check=True, text=True, capture_output=True).stdout

network_created = mock_created = False
try:
    run('network', 'create', '--internal', NETWORK)
    network_created = True
    run('run', '-d', '--rm', '--name', MOCK, '--network', NETWORK,
        '--mount', f'type=bind,source={ROOT},target=/work,readonly',
        'python:3.12-alpine', 'python', '/work/mock_crm.py')
    mock_created = True
    for attempt in (1, 2):
        print(f'Executing n8n pass {attempt}', flush=True)
        proc = subprocess.run(['docker', 'run', '--rm', '--network', NETWORK,
            '--mount', f'type=bind,source={ROOT},target=/work,readonly',
            '-e', 'N8N_DIAGNOSTICS_ENABLED=false', '-e', 'N8N_VERSION_NOTIFICATIONS_ENABLED=false',
            '--entrypoint', '/bin/sh', IMAGE, '-c',
            'n8n import:workflow --input=/work/workflow.json && n8n execute --id=cdrxrxLeadIntakeDemo'], text=True, capture_output=True)
        (ROOT / f'runtime-{attempt}.log').write_text(proc.stdout + proc.stderr)
        if proc.returncode:
            raise RuntimeError(f'n8n pass {attempt} exited {proc.returncode}; inspect runtime-{attempt}.log')
    state = json.loads(run('exec', MOCK, 'python', '-c',
        "import urllib.request; print(urllib.request.urlopen('http://localhost:8080/').read().decode())"))
    assert set(state['records']) == {'demo-1', 'demo-2'}, state
    assert state['calls'] == 4, state
    assert state['records']['demo-1']['email'] == 'ana@example.test', state
    result = {'status':'passed', 'executions':2, 'http_writes':4, 'unique_mock_crm_records':2,
              'replay_created_duplicates':False, 'image':IMAGE,
              'limitations':['Synthetic manual-trigger input', 'In-memory mock CRM, no real vendor integration',
                             'Source validation only; email ownership not verified',
                             'No webhook authentication, durable rejection queue, or notification integration in this sample']}
    (ROOT/'verification.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result), flush=True)
finally:
    if mock_created:
        run('stop', MOCK)
    if network_created:
        run('network', 'rm', NETWORK)
