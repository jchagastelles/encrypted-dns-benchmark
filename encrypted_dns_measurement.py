import dnspython_wrapper
import pydig_wrapper
import dig_subprocess

from urllib.parse import urlparse
import csv
from pathlib import Path
import time

from tranco import Tranco

import subprocess

latest_list = ''
# TODO: get tranco top x .br domains + automate for any country code
#with open('datasets/tranco_W9Z49-1m.csv/top-1m.csv', 'r') as dl:
    #topXdomains = [next(dl).strip().split(',')[1] for _ in range(y) if next(dl).endswith('.br')]
    #print(f'Tranco top {x} .br:\n{topXdomains}\n')'''

# download latest tranco list
def download_tranco_list():
    global latest_list
    t = Tranco(cache=True, cache_dir='./datasets/domains/')
    latest_list = t.list()
    #date_list = t.list(date='2023-07-19')

# get top x domains from tranco list
def get_tranco_top_x_domains(x):
    download_tranco_list()
    return latest_list.top(x)

# get main public resolvers
def get_main_resolvers(protocol):
    ret = ''
    with open(f'./datasets/resolvers/main-resolvers-{protocol}.txt', 'r') as mrf:
        ret = [line.strip().split(',') for line in mrf]
    return ret

# get first x resolvers from curl list (created with scrape_curl_doh_providers.py script)
def get_curl_first_x_resolvers(x):
    # TODO: import scricpt & automate getting list + creating file
    with open('./datasets/resolvers/curl-doh-resolvers-19072023.txt', 'r') as crf:
        first_x_resolvers = [next(crf).strip() for _ in range(y)]
    return first_x_resolvers

# write results to .csv
def export_results(tool, protocol, resolver, results):
    csv_path = Path(f'./results/{tool}-{protocol}-{resolver}.csv')
    write_or_append = 'a'

    print(f'WRITING TO {csv_path}.....')
    if not csv_path.exists():
        with open(f'./results/{tool}-{protocol}-{resolver}.csv', 'w', newline='') as csvfile:
            # write header (query_result dictionary keys)
            fieldnames = ['Domain', 'Timestamp', 'Response Status', 'Response Time', 'RCODE', 'TTL', 'Addresses', 'Error']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, restval='')
            writer.writeheader()

            for i, r in enumerate(results):
                # stringify & format fields
                r['Timestamp'] = f'{r["Timestamp"]:.3f}'
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
                r['Timestamp'] = f'{r["Timestamp"]:.3f}'
                r['Response Time'] = f'{r["Response Time"]:.3f}'
                # write row
                writer.writerow(r)
        return
        

if __name__ == "__main__":
    download_tranco_list()

    start_time = time.time()

    do53_resolvers = get_main_resolvers('do53')
    print(f'Do53 Resolvers: {do53_resolvers}')

    #doh_resolvers = get_main_resolvers('doh')

    domains = get_tranco_top_x_domains(1)
    print(f'Tranco top 100 domains: {domains}')

    for i in range(100):
        # loop
        print(f'LOOP {i}:\n')

        # PYDIG DO53
        print('\n##### PYDIG DO53 QUERIES..... #####')
        for r in do53_resolvers:
            results = []
            for d in domains:
                q = pydig_wrapper.query('do53',d,r[1])
                #print(q) # DEBUGGING PRINT
                results.append(q)
            export_results('pydig','do53',r[0],results)
        
        # DNSPYTHON DO53
        print('\n##### DNSPYTHON DO53 QUERIES..... #####')
        for r in do53_resolvers:
            results = []
            for d in domains:
                q = dnspython_wrapper.query('do53',d,r[1])
                #print(q) # DEBUGGING PRINT
                results.append(q)
            export_results('dnspython','do53',r[0],results)

        # DIG_SUBPROCESS DO53
        print('\n##### DIG_SUBPROCESS DO53 QUERIES..... #####')
        for r in do53_resolvers:
            results_timelib = []
            results_awk = []
            o = urlparse(r[1])
            for d in domains:
                q = dig_subprocess.query('do53',d,o[2])
                #print(q) # DEBUGGING PRINT
                results_timelib.append(q[0])
                results_awk.append(q[1])

            export_results('dig_timelib','do53',r[0],results_timelib)
            export_results('dig_awk','do53',r[0],results_awk)
        '''
        # PYDIG DOH
        print('\n##### PYDIG DOH QUERIES..... #####')
        for r in doh_resolvers:
            results = []
            o = urlparse(r[1])
            for d in domains:
                q = pydig_wrapper.query('doh',d,o[1],o[2])
                #print(q) # DEBUGGING PRINT
                results.append(q)
            export_results('pydig','doh',r[0],results)

        # DNSPYTHON DOH
        print('\n##### DNSPYTHON DOH QUERIES..... #####')
        for r in doh_resolvers:
            results = []
            for d in domains:
                q = dnspython_wrapper.query('doh',d,r[1])
                #print(q) # DEBUGGING PRINT
                results.append(q)
            export_results('dnspython','doh',r[0],results)

        '''

    end_time = time.time()
    total_time = end_time - start_time
    print(f'\nTOTAL_TIME = {total_time}\n')