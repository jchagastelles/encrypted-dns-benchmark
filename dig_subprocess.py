import subprocess

def query(protocol, domain, resolver='', endpoint=''):
    if protocol == 'do53':
        return do53_query(domain, resolver)
    elif protocol == 'doh':
        return doh_query(domain, resolver, endpoint)
    elif protocol == 'dot':
        return dot_query(domain, resolver, endpoint)

def do53_query(domain, resolver):
    # TODO: ESTENDER AWK SCRIPT PRA PEGAR RESTO DAS METRICAS
    # awk '/^;; ANSWER SECTION:$/,/^$/ {if ($0 != ";; ANSWER SECTION:" && $0 != "") print $NF}'
    #cmd = ['dig', 'multiline', 'answer', f'@{resolver}', f'{domain}', 'timeout=3']
    cmd = f"dig +multiline +answer @{resolver} {domain} +timeout=3 | awk '/^;; ANSWER SECTION:$/,/^$/ {{if ($0 != \";; ANSWER SECTION:\" && $0 != \"\") print $NF}}'"
    try:
        #result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        #return result.stdout
        return str(output)
    except subprocess.CalledProcessError as e:
        return f'Command execution failed: {e}'

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