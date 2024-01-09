import httpx
import dns.message
import dns.query
import dns.rdataclass
import dns.rdatatype

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
    query_result = get_query_result_dict()
    query_result['Domain'] = domain

    where = resolver
    qname = domain
    mq = dns.message.make_query(qname, dns.rdatatype.NS)

    try:
        query_result['Timestamp'] = start_time = time.time()
        q = dns.query.udp(mq, where, timeout=3)
        end_time = time.time()

        query_result['Response Status'] = 1

        #print(f'q.answer={q.answer}')
        #print(f'q.to_text()={q.to_text()}')
        #print(f'q.rcode={dns.rcode.to_text(q.rcode())}')

        query_result['RCODE'] = dns.rcode.to_text(q.rcode())

        for a in q.answer:
            query_result['TTL'] = int(a.to_text().split(" ")[1])
            for addr in a:
                #print(f'addr={addr}')
                query_result['Addresses'].append(addr.to_text())
    except Exception as e:
        end_time = time.time()

        query_result['Response Status'] = -1
        query_result['Addresses'] = []
        query_result['Error'] = e
        
        ## TODO: error handling
        #print(f'Error: {e}')
    
    res_time = end_time*1000 - start_time*1000
    query_result['Response Time'] = res_time
    return query_result

def doh_query(domain, resolver):
    query_result = get_query_result_dict()
    query_result['Domain'] = domain

    where = resolver
    qname = domain
    with httpx.Client() as client:

        mq = dns.message.make_query(qname, dns.rdatatype.A)

        try:
            query_result['Timestamp'] = start_time = time.time()

            q = dns.query.https(mq, where, session=client, timeout=3)
            end_time = time.time()

            query_result['Response Status'] = 1

            #print(f'q.answer={q.answer}')
            #print(f'q.to_text()={q.to_text()}')
            #print(f'q.rcode={dns.rcode.to_text(q.rcode())}')

            query_result['RCODE'] = dns.rcode.to_text(q.rcode())

            for a in q.answer:
                query_result['TTL'] = int(a.to_text().split(" ")[1])
                for addr in a:
                    #print(f'addr={addr}')
                    query_result['Addresses'].append(addr.to_text())
        except Exception as e:
            end_time = time.time()

            query_result['Response Status'] = -1
            query_result['Addresses'] = []
            query_result['Error'] = e

            ## TODO: error handling
            #print(f'Error: {e}')
    
    res_time = end_time*1000 - start_time*1000
    query_result['Response Time'] = res_time
    return query_result

def dot_query(domain, resolver):
    ## TODO: DoT query
    query_result = get_query_result_dict()
    query_result['Domain'] = domain

    where = resolver
    qname = domain
    with httpx.Client() as client:

        mq = dns.message.make_query(qname, dns.rdatatype.A)

        try:
            query_result['Timestamp'] = start_time = time.time()

            q = dns.query.tls(mq, where, session=client, timeout=3)
            end_time = time.time()

            query_result['Response Status'] = 1

            #print(f'q.answer={q.answer}')
            #print(f'q.to_text()={q.to_text()}')
            #print(f'q.rcode={dns.rcode.to_text(q.rcode())}')

            query_result['RCODE'] = dns.rcode.to_text(q.rcode())

            for a in q.answer:
                query_result['TTL'] = int(a.to_text().split(" ")[1])
                for addr in a:
                    #print(f'addr={addr}')
                    query_result['Addresses'].append(addr.to_text())
        except Exception as e:
            end_time = time.time()

            query_result['Response Status'] = -1
            query_result['Addresses'] = []
            query_result['Error'] = e

            ## TODO: error handling
            #print(f'Error: {e}')
    
    res_time = end_time*1000 - start_time*1000
    query_result['Response Time'] = res_time
    return query_result