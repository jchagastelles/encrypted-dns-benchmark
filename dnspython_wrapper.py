import httpx
import dns.message
import dns.query
import dns.rdatatype

import time

def query(protocol, domain, resolver):
    if protocol == 'do53':
        return do53_query(domain, resolver)
    elif protocol == 'doh':
        return doh_query(domain, resolver)
    elif protocol == 'dot':
        return dot_query(domain, resolver)
    else:
        return 'INVALID PROTOCOL'

def do53_query(domain, resolver):
    # TODO: Do53 query
    return -1

def doh_query(domain, resolver):
    res_timestamp = 0
    res_time = 0
    res_status = 0
    res_addresses = []

    where = resolver
    qname = domain
    with httpx.Client() as client:

        mq = dns.message.make_query(qname, dns.rdatatype.A)

        try:
            res_timestamp = time.time()
            q = dns.query.https(mq, where, session=client)
            end_time = time.time()
            res_status = 1
            for answer in q.answer:
                res_addresses.append(answer[0])
        except Exception as e:
            end_time = time.time()
            res_status = -1
            res_addresses = []

            ## TODO: error handling
            print(f'Error: {e}')
    
    res_time = end_time*1000 - res_timestamp*1000
    return [res_timestamp, domain, res_time, res_status, res_addresses]

def dot_query(domain, resolver):
    ## TODO: DoT query
    return -1