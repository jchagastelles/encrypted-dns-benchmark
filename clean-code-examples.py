import time
import dns
import httpx
import pydig
import subprocess
domain = ''
resolver = ''
protocols = ''
tools = ''
query_result = {}
df = []
df_pivot = []
plt = []

# QUERIES
## DIG PYTHON QUERY CODE
cmd = f"dig +multiline +answer @{resolver} {domain} +tries=1 +timeout=3" + "| awk '/Query/{t=$4}END{print t}'"
result = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)

## PYDIG PYTHON DO53 QUERY CODE
resolver = pydig.Resolver(
        executable='/usr/bin/dig',
        nameservers=[
            '1.1.1.1'
        ],
        additional_args=[
            '+tries=1',
            '+timeout=3'
        ]
    )
result = resolver.query(domain, 'A')

## DNSPYTHON PYTHON QUERY CODE
mq = dns.message.make_query('inf.ufrgs.br', dns.rdatatype.NS)
q = dns.query.udp(mq, '1.1.1.1', timeout=3)


# MEASUREMENTS (ALL COMBINATIONS OF RESOLVER+DOMAIN FOR PYDIG DO53)
for resolver in do53_resolvers:
    results = []
    for domain in domains:
        q = pydig_wrapper.query('do53',domain,resolver)
        results.append(q)
    export_results('pydig','do53',resolver,results)


# READING AND UNIFYING ALL THE DATA
dfs = list()
for t in tools:
    for p in protocols:
        for r in resolvers:
            csv_file = f'./results/{t}-{p}-{r}.csv'
            data = pd.read_csv(csv_file)
            data['Tool'] = t
            data['Protocol'] = p
            data['Resolver'] = r
            data['Timestamp'] = pandas.to_datetime(data['Timestamp'])
            dfs.append(data)
df = pandas.concat(dfs, ignore_index=True)


# DATA ANALYSIS QUERY EXAMPLES

for p in protocols:
    df2 = df.query(f'Protocol == "{p}" & {query_success_conditions}')[["Tool", "Response Time", "Resolver"]]
    final_df = pd.pivot_table(
        df2,
        values="Response Time",
        index="Resolver",
        columns="Tool",
        aggfunc=('count','mean','std')
    )



## EXCLUDING FAILURES FOR MEAN RT BENCHMARK
success_conditions = '(`Response Time` < 3000 & `Response Status` == 1 & (RCODE == "NOERROR" | RCODE.isnull()) | Error.isnull())'

## TOOL BENCHMARK: 1 CHART PER PROTOCOL
for p in protocols:
    df.query(f'Protocol == "{p}" & `Response Status` == 1)[["Tool", "Response Time", "Resolver"]]

## PROTOCOL BENCHMARK: 1 CHART PER TOOL
for t in tools:
    df.query(f'Tool == "{t}" & `Response Status` == 1')[["Protocol", "Response Time", "Resolver"]]


# 95% CONFIDENCE INTERVAL
ci95_range = []
for i in df.index:    
    c = df.loc[i, 'count'][t]
    m = df.loc[i, 'mean'][t]
    s = df.loc[i, 'std'][t]
    ci_lo = m - 1.96*s/math.sqrt(c)
    ci_range = m - ci_lo
    ci95_range.append(ci_range)
df[('ci95_range', t)] = ci95_range


# DATAVIZ EXAMPLE (TOOL BENCHMARK): Format + Plot + Save
colors=['darkgray','gray','dimgray','lightgray']
ax = df_pivot['mean'].plot(kind="bar", color=colors, yerr=df_pivot['ci95_range'], capsize=4)
f = ax.get_figure()
ax.set_xlabel("Resolvers")
ax.set_ylabel("Response Time (ms)")
plt.subplots_adjust(bottom=0.3)
plt.show()
f.savefig(f'results/tool_benchmark_{protocol}.pdf', bbox_inches='tight', dpi=300)



# WRAPPER EXAMPLE
def get_query_result_dict():
    return {'Domain': None, 
            'Timestamp': None, 
            'Response Status': None, 
            'Response Time': None, 
            'RCODE': None, 
            'TTL': None, 
            'Addresses': [], 
            'Error': None
        }

def query(protocol, domain, resolver, endpoint=''):
    if protocol == 'do53':
        return do53_query(domain, resolver)
    elif protocol == 'doh':
        return doh_query(domain, resolver, endpoint)
    elif protocol == 'dot':
        return dot_query(domain, resolver)

def do53_query(domain, resolver):
    result = get_query_result_dict()
    # QUERY AND BUILD RESULT DICTIONARY
    return result

def doh_query(domain, resolver, endpoint):
    result = get_query_result_dict()
    # QUERY AND BUILD RESULT DICTIONARY
    return result

def dot_query(domain, resolver):
    result = get_query_result_dict()
    # QUERY AND BUILD RESULT DICTIONARY
    return result

if __name__ == "__main__":
    pass