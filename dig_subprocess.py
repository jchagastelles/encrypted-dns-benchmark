import time
import subprocess

def get_query_result_dict():
    return {'Domain': None, 
            'Timestamp': None, 
            'Response Status': None, 
            'Response Time': None, 
            'RCODE': None, 
            'TTL': None, 
            'Addresses': [], 
            'Error': None}

def query(protocol, domain, resolver='', endpoint=''):
    if protocol == 'do53':
        return do53_query(domain, resolver)
    elif protocol == 'doh':
        return doh_query(domain, resolver, endpoint)
    elif protocol == 'dot':
        return dot_query(domain, resolver, endpoint)

def do53_query(domain, resolver):
    # TODO: ESTENDER AWK SCRIPT PRA PEGAR E FORMATAR RESTO DAS METRICAS
    # awk '/^;; ANSWER SECTION:$/,/^$/ {if ($0 != ";; ANSWER SECTION:" && $0 != "") print $NF}'

    query_result_timelib = get_query_result_dict()
    query_result_awk = get_query_result_dict()

    query_result_timelib['Domain'] = domain
    query_result_awk['Domain'] = domain
    
    cmd = f"dig +multiline +answer @{resolver} {domain} +tries=1 +timeout=3" + "| awk '/Query/{t=$4}END{print t}'"

    try:
        query_result_timelib['Timestamp'] = start_time = time.time()
        query_result_awk['Timestamp'] = start_time
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)
        end_time = time.time()

        query_result_awk['Response Time'] = float(result.stdout)

        query_result_timelib['Response Status'] = 1
        query_result_awk['Response Status'] = 1

        #output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        #return str(output)
    except Exception as e:
        end_time = time.time()

        query_result_awk['Response Time'] = 3001 # test

        query_result_timelib['Response Status'] = -1
        query_result_awk['Response Status'] = -1

        query_result_timelib['Addresses'] = []
        query_result_awk['Addresses'] = []

        query_result_timelib['Error'] = e
        query_result_awk['Error'] = e
    
    res_time = end_time*1000 - start_time*1000
    query_result_timelib['Response Time'] = res_time
    return [query_result_timelib, query_result_awk]
    

def doh_query(domain, resolver, endpoint):
    # TODO: ESTENDER AWK SCRIPT PRA PEGAR RESTO DAS METRICAS
    #cmd = ['dig', 'multiline', 'answer', f'@{resolver}', f'{domain}', f'https={endpoint}', 'timeout=3']
    cmd = f"dig +multiline +answer @{resolver} +https={endpoint} {domain} +timeout=3"

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)
        #output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        return result.stdout
        #return str(output)
    except subprocess.CalledProcessError as e:
        return f'Command execution failed: {e}'

def dot_query(domain, resolver, endpoint):
    ## TODO: DoT query
    return -1

if __name__ == "__main__":
    q = query('do53','inf.ufrgs.br','1.1.1.1')
    print(q)

    #q = query('doh','inf.ufrgs.br','dns.google', '/dns-query')
    #print(q)