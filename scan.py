import requests
from requests import RequestException, Timeout
from multiprocessing.dummy import Pool as ThreadPool
import ipaddress
import re
import json
from tabulate import tabulate
from pathlib import Path

def filter_private_ip(ip_lst) -> set:
    print("FILTERING PRIVATE IPs")
    public_ips = set()
    for ip in ip_lst:
        if not ipaddress.ip_address(ip).is_private:
            public_ips.add(ip)
    return public_ips

def write_to_file(file_name_: str, write_this, mode: str = "a"):
    with open(file_name_, mode) as file_:
        if type(write_this) is list or type(write_this) is set:
            file_.write("\n".join(write_this))
        else:
            file_.write(write_this)

def request_get(url_: str):
    headers_ = {"accept": "application/json"}
    try:
        req = requests.get(url=url_, headers=headers_, timeout=provider_timeout)
        if req.status_code == 200:
            return req.text

    except (RequestException, Timeout, Exception) as connectErr:
        return "request_get error"

def get_peers_via_rpc(provider_url_: str):
    new_rpc_ = set()
    try:
        peers = request_get(f'{provider_url_}/net_info')
        if "error" in str(peers):
            return ''
        peers = json.loads(peers)["result"]["peers"]

        for p in peers:
            try:
                rpc_port  = p["node_info"]["other"]["rpc_address"].split(":")[2] or 26657
                remote_ip = p["remote_ip"]
                new_rpc_.add(f'http://{remote_ip}:{rpc_port}')

            except Exception as get_peers_err:
                continue
        return new_rpc_

    except Exception as peer_conn_err:
        return ''

def get_vuln_validators(validator_url_: str):
    try:
        node_data = request_get(f'{validator_url_}/status')
        node_data = json.loads(node_data)

        if 'error' not in str(node_data) and 'jsonrpc' not in str(node_data):
            print(f'{validator_url_} is available, but method /status not supported')

        if 'error' not in str(node_data) and 'jsonrpc' in str(node_data):
            node_data    = node_data["result"]

            voting_power = int(node_data["validator_info"]["voting_power"])
            peer_id      = str(node_data["node_info"]["id"])
            moniker      = str(node_data["node_info"]["moniker"])
            network      = str(node_data["node_info"]["network"])
            block_height = int(node_data["sync_info"]["latest_block_height"])
            sync_status  = str(node_data["sync_info"]["catching_up"])

            return f'{moniker},{validator_url_},{network},{peer_id},{block_height},{sync_status},{voting_power}'

        else:
            return 'rpc_not_available'
    except:
        return 'rpc_not_available'


print("Version: 0.2")

CSV_HEADER_STR    = 'moniker,validator_url_,network,peer_id,block_height,syncing?,voting_power'
rpc_file_name     = 'rpc_urls.txt'  # Manual RPC URL file
genesis_file_name = 'genesis_ips.txt'  # Not used in this version
threads_count     = 10
provider_timeout  = 10

rpc_provider_lst  = set(open(rpc_file_name, "r").read().split("\n"))
rpc_provider_lst.discard('')

# Commented out the genesis fetching logic
# rpc_provider_lst = get_genesis_ips() | rpc_provider_lst

# getting all rpc urls
print(f'--> SEARCHING FOR PEER IPs AND THEIR RPC PORTs')
pool = ThreadPool(threads_count)
new_rpc = pool.map(get_peers_via_rpc, rpc_provider_lst)
new_rpc = set([item for sublist in new_rpc for item in sublist])
new_rpc.discard('')

new_peers_found = (new_rpc | rpc_provider_lst) - rpc_provider_lst
rpc_provider_lst = new_rpc | rpc_provider_lst

while len(new_peers_found) > 0:
    new_rpc = pool.map(get_peers_via_rpc, new_peers_found)
    new_rpc = set([item for sublist in new_rpc for item in sublist])
    new_rpc.discard('')

    new_peers_found = (new_rpc | rpc_provider_lst) - rpc_provider_lst
    rpc_provider_lst = new_rpc | rpc_provider_lst

print(f'Found {len(rpc_provider_lst)} peers')
print(f'---> SEARCHING FOR VULNERABLE VALIDATORS (where RPC port is opened and voting power > 0)')
valid_rpc = set(pool.map(get_vuln_validators, rpc_provider_lst))
valid_rpc.discard('rpc_not_available')

# WRITE CSV HEADERS
Path("results").mkdir(parents=True, exist_ok=True)
write_to_file('results/valid_rpc.csv', CSV_HEADER_STR + "\n", 'w')
write_to_file('results/vulnerable_validators.csv', CSV_HEADER_STR + "\n", 'w')

# SEARCHING FOR VULN VALIDATORS
AFFECTED_STAKE = 0
VULN_VALIDATORS = []

for node in valid_rpc:
    moniker_ = node.split(",")[0]
    voting_power_ = int(node.split(",")[-1])

    if voting_power_ > 0:
        VULN_VALIDATORS.append(node.split(","))
        AFFECTED_STAKE += voting_power_

if len(VULN_VALIDATORS) > 0:
    print(tabulate(VULN_VALIDATORS, tablefmt="grid", headers=CSV_HEADER_STR.split(",")))
    VULN_VALIDATORS = [",".join(i) for i in VULN_VALIDATORS]
    write_to_file('results/vulnerable_validators.csv', VULN_VALIDATORS, 'a')
    print(f'TOTAL VULNERABLE VALIDATORS: {len(VULN_VALIDATORS)} | TOTAL AFFECTED STAKE: {AFFECTED_STAKE}\n'
          f'Check file: vulnerable_validators.csv')
else:
    print("Vulnerable validators not found")

write_to_file('results/valid_rpc.csv', valid_rpc, 'a')
print("DONE")
