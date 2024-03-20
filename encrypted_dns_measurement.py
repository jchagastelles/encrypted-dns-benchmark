import dnspython_wrapper
import pydig_wrapper
import dig_wrapper

import argparse
from urllib.parse import urlparse
import csv
from pathlib import Path
import time

from tranco import Tranco

# download latest tranco list
def download_tranco_list():
    t = Tranco(cache=True, cache_dir='./datasets/domains/')
    return t.list()

# get resolver dataset
def get_resolver_list(path):
    ret = []
    with open(path, 'r') as mrf:
        ret = [line.strip().split(',') for line in mrf]
    return ret

# get domain dataset
def get_domain_list(path):
    ret = []
    if path == '':
        try:
            tranco_list = download_tranco_list()
        except:
            print('Error downloading latest Tranco list: defaulting to 2024.01.15 list')
            with open('./datasets/domains/tranco-20240115.csv', newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                for row in reader:
                    ret.append(row[1])
    else:
        with open(path, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                ret.append(row[1])
    return ret

# get tool dataset
def get_tool_list(path):
    ret = []
    with open(path, 'r') as mrf:
        ret = [line.strip().strip(',') for line in mrf]
    return ret

# get protocol dataset
def get_protocol_list(path):
    ret = []
    with open(path, 'r') as mrf:
        ret = [line.strip().strip(',') for line in mrf]
    return ret

# get first x resolvers from curl list (created with scrape_curl_doh_providers.py script)
def get_curl_first_x_resolvers(x):
    # TODO: import scricpt & automate getting list + creating file
    with open('./datasets/resolvers/curl-doh-resolvers-19072023.csv', 'r') as crf:
        first_x_resolvers = [next(crf).strip() for _ in range(y)]
    return first_x_resolvers

# write results to .csv
def export_results(tool, protocol, resolver, results):
    csv_path = Path(f'./results/{tool}-{protocol}-{resolver}.csv')
    write_or_append = 'a'

    #print(f'WRITING TO {csv_path}.....')
    if not csv_path.exists():
        with open(f'./results/{tool}-{protocol}-{resolver}.csv', 'w', newline='') as csvfile:
            # write header (query_result dictionary keys)
            fieldnames = ['Domain', 'Timestamp', 'Response Status', 'Response Time', 'RCODE', 'TTL', 'Addresses', 'Error']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, restval='')
            writer.writeheader()

            for i, r in enumerate(results):
                # stringify & format fields
                if (r['Timestamp'] != None):
                    r['Timestamp'] = f'{r["Timestamp"]:.3f}'
                if (r['Response Time']  != None):
                    r['Response Time'] = f'{r["Response Time"]:.3f}'
                # write row
                writer.writerow(r)
        return
    else:
        with open(f'./results/{tool}-{protocol}-{resolver}.csv', 'a', newline='') as csvfile:
            fieldnames = ['Domain', 'Timestamp', 'Response Status', 'Response Time', 'RCODE', 'TTL', 'Addresses', 'Error']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, restval='')

            for i, r in enumerate(results):
                # stringify & format fields
                if (r['Timestamp'] != None):
                    r['Timestamp'] = f'{r["Timestamp"]:.3f}'
                if (r['Response Time']  != None):
                    r['Response Time'] = f'{r["Response Time"]:.3f}'
                # write row
                writer.writerow(r)
        return
    
def measure(tools, protocols, resolvers, domains):
    for t in tools:
        query_func = getattr(globals()[f'{t}_wrapper'], 'query')
        for p in protocols:
            protocol_resolvers = resolvers[p]
            for r in protocol_resolvers:
                results = []
                for d in domains:
                    result = query_func(p,d,r[1])
                    #print(result)
                    results.append(result)

                if (t == 'dig'): # split into dig_awk and dig_timelib
                    for pair in results:
                        export_results('dig_timelib',p,r[0],[pair[0]])
                        export_results('dig_awk',p,r[0],[pair[1]])
                else:
                    export_results(t,p,r[0],results)
    return

if __name__ == "__main__":
    #python3 encrypted_dns_measurement.py [tools] [domains] [resolvers-do53] [resolvers-doh] [resolvers-dot] [query_amount]
    parser = argparse.ArgumentParser(
                    prog='Encrypted DNS Measurement',
                    description='Issues DNS queries and stores results (https://github.com/jchagastelles/encrypted-dns-benchmark)')
    parser.add_argument('-i', action='store', type=int,
                    default=500,
                    help='Query Sample Amount (default: "500")')
    parser.add_argument('-t', action='store',
                    default='./datasets/tools/main-tools.csv',
                    help='Lookup Tool List (default: "./datasets/tools/main-tools.csv")')
    parser.add_argument('-d', action='store',
                    default='./datasets/domains/tranco-20240115.csv',
                    help='Domain List (default: "./datasets/domains/tranco-20240115.csv")')
    parser.add_argument('-p', action='store',
                    default='./datasets/protocols/protocols.csv',
                    help='Protocol List (default: "./datasets/protocols/protocols.csv")')
    parser.add_argument('-rdo53', action='store',
                    default='./datasets/resolvers/main-resolvers-do53.csv',
                    help='Do53 Resolver List (default: "./datasets/resolvers/main-resolvers-do53.csv")')
    parser.add_argument('-rdoh', action='store',
                    default='./datasets/resolvers/main-resolvers-doh.csv',
                    help='DoH Resolver List (default: "./datasets/resolvers/main-resolvers-doh.csv")')
    parser.add_argument('-rdot', action='store',
                    default='./datasets/resolvers/main-resolvers-dot.csv',
                    help='DoT Resolver List (default: "./datasets/resolvers/main-resolvers-dot.csv")')
    args = parser.parse_args()


    do53_resolvers = get_resolver_list(args.rdo53)
    print(f'Do53 Resolvers: {do53_resolvers}')

    doh_resolvers = get_resolver_list(args.rdoh)
    print(f'DoH Resolvers: {doh_resolvers}')

    dot_resolvers = get_resolver_list(args.rdot)
    print(f'DoT Resolvers: {dot_resolvers}')

    resolvers = {
        'do53': do53_resolvers,
        'doh': doh_resolvers,
        'dot': dot_resolvers
    }

    tools = get_tool_list(args.t)
    #print(f'Lookup Tool List: {tools}')

    domains = get_domain_list(args.d)
    #print(f'Domain List: {domains}')

    protocols = get_protocol_list(args.p)
    #print(f'Protocol List: {protocols}')

    i = args.i
    print(f'Query sample required: {i}')

    start_time = time.time()

    for i in range(args.i):
        print(f'Sample #{i}:')

        measure(tools,protocols,resolvers,domains)

    end_time = time.time()
    total_time = end_time - start_time
    print(f'\nTOTAL_TIME = {total_time}\n')