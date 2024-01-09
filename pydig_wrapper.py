import pydig

import time

def get_query_result_dict():
    return {'Domain': None, 
            'Timestamp': None, 
            'Response Status': None, 
            'Response Time': None, 
            'RCODE': None, 
            'TTL': None, 
            'Addresses': [], 
            'Error': None}

def query(protocol, domain, resolver, endpoint=''):
    if protocol == 'do53':
        return do53_query(domain, resolver)
    elif protocol == 'doh':
        return doh_query(domain, resolver, endpoint)
    elif protocol == 'dot':
        return dot_query(domain, resolver)

def do53_query(domain, resolver):
    query_result = get_query_result_dict()
    query_result['Domain'] = domain

    resolver = pydig.Resolver(
        executable='/usr/bin/dig',
        nameservers=[
            resolver
        ],
        additional_args=[
            '+tries=1',
            '+timeout=3'
        ]
    )

    try:
        query_result['Timestamp'] = start_time = time.time()
        q = resolver.query(domain, 'A')
        end_time = time.time()

        query_result['Response Status'] = 1
        query_result['Addresses'] = q
        
    except Exception as e:
        end_time = time.time()

        query_result['Response Status'] = -1
        query_result['Addresses'] = []
        query_result['Error'] = e

        ## TODO: ERROR HANDLING
        #if e.returncode == 9:
        #    print(f'No reply from server')
        #print(f'Error: {e}')

    res_time = end_time*1000 - start_time*1000
    query_result['Response Time'] = res_time
    return query_result

def doh_query(domain, resolver, endpoint):
    query_result = get_query_result_dict()
    query_result['Domain'] = domain
    
    resolver = pydig.Resolver(
        executable='/usr/bin/dig',
        nameservers=[
            resolver
        ],
        additional_args=[
            f'+https={endpoint}',
            '+tries=1',
            '+timeout=3'
        ]
    )

    try:
        query_result['Timestamp'] = start_time = time.time()
        q = resolver.query(domain, 'A')
        end_time = time.time()

        query_result['Response Status'] = 1
        query_result['Addresses'] = q
        
    except Exception as e:
        end_time = time.time()

        query_result['Response Status'] = -1
        query_result['Addresses'] = []
        query_result['Error'] = e

        ## TODO: ERROR HANDLING
        #if e.returncode == 9:
        #    print(f'No reply from server')
        #print(f'Error: {e}')

    res_time = end_time*1000 - start_time*1000
    query_result['Response Time'] = res_time
    return query_result

def dot_query(domain, resolver):
    query_result = get_query_result_dict()
    query_result['Domain'] = domain
    
    resolver = pydig.Resolver(
        executable='/usr/local/bin/dig', # change this to '/usr/bin/dig' in case of default bind/dig installation
        nameservers=[
            resolver
        ],
        additional_args=[
            f'+tls',
            '+tries=1',
            '+timeout=3'
        ]
    )

    try:
        query_result['Timestamp'] = start_time = time.time()
        q = resolver.query(domain, 'A')
        end_time = time.time()

        query_result['Response Status'] = 1
        query_result['Addresses'] = q
        
    except Exception as e:
        end_time = time.time()

        query_result['Response Status'] = -1
        query_result['Addresses'] = []
        query_result['Error'] = e

        ## TODO: ERROR HANDLING
        #if e.returncode == 9:
        #    print(f'No reply from server')
        #print(f'Error: {e}')

    res_time = end_time*1000 - start_time*1000
    query_result['Response Time'] = res_time
    return query_result

if __name__ == "__main__":
    pass
    # Do53 example query
    #q = query('do53','inf.ufrgs.br','1.1.1.1')
    #print(q)

    # DoH example query
    #q = query('doh','inf.ufrgs.br','dns.google', '/dns-query')
    #print(q)

    # DoT example query
    #q = query('dot','inf.ufrgs.br','8.8.8.8')
    #print(q)