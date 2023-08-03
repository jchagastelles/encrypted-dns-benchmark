import pydig

import time

def query(protocol, domain, resolver, endpoint):
    if protocol == 'do53':
        return do53_query(domain, resolver, endpoint)
    elif protocol == 'doh':
        return doh_query(domain, resolver, endpoint)
    elif protocol == 'dot':
        return dot_query(domain, resolver, endpoint)

def do53_query(domain, resolver, endpoint):
    ## TODO: Do53 query
    return -1

def doh_query(domain, resolver, endpoint):
    resolver = pydig.Resolver(
        executable='/usr/bin/dig',
        nameservers=[
            resolver
        ],
        additional_args=[
            f'+https={endpoint}',
        ]
    )

    res_timestamp = 0
    res_time = 0
    res_status = 0
    res_addresses = []
    try:
        res_timestamp = time.time()

        q = resolver.query(domain, 'A')
        
        end_time = time.time()

        res_status = 1
        res_addresses = q
        
    except Exception as e:
        end_time = time.time()
        res_status = -1
        res_addresses = []

        ## TODO: ERROR HANDLING
        #if e.returncode == 9:
        #    print(f'No reply from server')
        print(f'Error: {e}')

    res_time = end_time*1000 - res_timestamp*1000
    return [res_timestamp, domain, res_time, res_status, res_addresses]

def dot_query(domain, resolver, endpoint):
    ## TODO: DoT query
    return -1