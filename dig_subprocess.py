import subprocess

def query(protocol, domain, resolver, endpoint):
    if protocol == 'do53':
        return do53_query(domain, resolver, endpoint)
    elif protocol == 'doh':
        return doh_query(domain, resolver, endpoint)
    elif protocol == 'dot':
        return dot_query(domain, resolver, endpoint)

def do53_query(domain, resolver):
    ## TODO: Do53 query
    return -1

def doh_query(domain, resolver, endpoint):
    # TODO: TENTAR AWK PRA PEGAR TTL
    # awk '/^;; ANSWER SECTION:$/,/^$/ {if ($0 != ";; ANSWER SECTION:" && $0 != "") print $NF}'
    cmd = ["dig", "multiline", "answer", f"@{resolver}", f"{domain}", f"https={endpoint}", ""]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f'Command execution failed: {e}'

def dot_query(domain, resolver, endpoint):
    ## TODO: DoT query
    return -1

if __name__ == "__main__":
    doh_query('inf.ufrgs.br', '1.1.1.1')
