import json
from pathlib import Path

root = Path(__file__).parent
fixtures = [
    {'requestId': 'demo-1', 'name': ' Ana Demo ', 'email': 'ANA@example.test'},
    {'requestId': 'demo-1', 'name': ' Ana Demo ', 'email': 'ANA@example.test'},
    {'requestId': 'demo-2', 'name': 'Luis Example', 'email': 'luis@example.test'},
    {'requestId': 'invalid-3', 'name': 'Invalid Example', 'email': 'not-an-email'},
]
logic = (root / 'normalize.cjs').read_text().split('module.exports')[0]
nodes = [
    {'id': 'start', 'name': 'Manual demo', 'type': 'n8n-nodes-base.manualTrigger', 'typeVersion': 1, 'position': [0,0], 'parameters': {}},
    {'id': 'fixtures', 'name': 'Synthetic form submissions', 'type': 'n8n-nodes-base.code', 'typeVersion': 2, 'position': [240,0], 'parameters': {'jsCode': 'return '+json.dumps(fixtures)+'.map(json => ({json}));'}},
    {'id': 'validate', 'name': 'Validate and deduplicate', 'type': 'n8n-nodes-base.code', 'typeVersion': 2, 'position': [480,0], 'parameters': {'jsCode': logic+'\nconst result = normalize($input.all().map(item => item.json));\nconsole.log(JSON.stringify({accepted:result.accepted.length,rejected:result.rejected}));\nreturn result.accepted.map(json => ({json}));'}},
    {'id': 'crm', 'name': 'Upsert into MOCK CRM', 'type': 'n8n-nodes-base.httpRequest', 'typeVersion': 4.2, 'position': [720,0], 'parameters': {'method': 'PUT', 'url': '=http://autobusiness-n8n-crm:8080/leads/{{ $json.externalId }}', 'sendBody': True, 'specifyBody': 'json', 'jsonBody': '={{ JSON.stringify($json) }}', 'options': {'timeout': 5000}}},
]
connections = {a['name']: {'main': [[{'node': b['name'], 'type':'main', 'index':0}]]} for a,b in zip(nodes,nodes[1:])}
workflow = {'id':'cdrxrxLeadIntakeDemo','name':'CDRXRX — lead intake, synthetic CRM demo','active':False,'nodes':nodes,'connections':connections,'settings':{'executionOrder':'v1'}}
(root/'workflow.json').write_text(json.dumps(workflow,indent=2,ensure_ascii=False)+'\n')
