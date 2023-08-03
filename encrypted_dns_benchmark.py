import dnspython_wrapper
import pydig_wrapper
import dig_subprocess

from urllib.parse import urlparse
import csv

from tranco import Tranco

import subprocess

# TODO: get tranco top x .br domains + automate for any country code
#with open('datasets/tranco_W9Z49-1m.csv/top-1m.csv', 'r') as dl:
    #topXdomains = [next(dl).strip().split(',')[1] for _ in range(y) if next(dl).endswith('.br')]
    #print(f'Tranco top {x} .br:\n{topXdomains}\n')'''

# domains with tranco package
t = Tranco(cache=True, cache_dir='./datasets/domains/')
latest_list = t.list()
#date_list = t.list(date='2023-07-19')

# get top x domains
def get_top_x_domains(x):
    return latest_list.top(x)

# get main public resolvers
def get_main_resolvers(protocol):
    ret = ''
    with open(f'./datasets/resolvers/main-resolvers-{protocol}.txt', 'r') as mrf:
        ret = [line.strip() for line in mrf]
    return ret

# get first x resolvers from curl list (created with scrape_curl_doh_providers.py script)
def get_curl_first_x_resolvers(x):
    # TODO: import scricpt & automate getting list + creating file
    with open('./datasets/resolvers/curl-doh-resolvers-19072023.txt', 'r') as crf:
        first_x_resolvers = [next(crf).strip() for _ in range(y)]
    return first_x_resolvers

def export_results(tool, protocol, resolver, results):
    with open(f'./results/{tool}-{protocol}-{resolver[8:][:-10]}.csv', 'w', newline='') as csvfile:
        fieldnames = ['Domain', 'Timestamp', 'Response Status', 'Response Time', 'Addresses']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for i, r in enumerate(results):
            writer.writerow({'Domain': r[0], 
                             'Timestamp': r[1],
                             'Response Status': r[2], 
                             'Response Time': f'{int(r[3])}', 
                             'Addresses': r[4]})

if __name__ == "__main__":

    resolvers = get_main_resolvers('doh')
    domains = get_top_x_domains(10)

    # PYDIG
    print('\n##### PYDIG #####')
    for r in resolvers:
        results = []
        o = urlparse(r)
        for d in domains:
            q = pydig_wrapper.query('doh', d, o[1], o[2])
            print(q)
            results.append(q)
        export_results('pydig','doh',r,results)
    
    # DNSPYTHON (TODO: FORMATAR 'ANSWERS' FIELD)
    print('\n##### DNSPYTHON #####')
    for r in resolvers:
        results = []
        for d in domains:
            q = dnspython_wrapper.query('doh', d, r)
            print(q)
            results.append(q)
        export_results('dnspython','doh',r,results)

    # DIG_SUBPROCESS (TODO: FORMATAR RESPOSTA & TENTAR PEGAR TTL)
    print('\n##### DIG_SUBPROCESS #####')
    for r in resolvers:
        results = []
        o = urlparse(r)
        for d in domains:
            q = dig_subprocess.query('doh', d[0],o[1],o[2])
            print(q)
            results.append(q)
        #export_results('dig_subprocess','doh',r,results)