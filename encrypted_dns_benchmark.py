import encrypted_dns_measurement as edm
import csv
import math
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

tools = ['dnspython', 'pydig', 'dig_timelib', 'dig_awk']
protocols = ['do53'] # TODO: ADD DOH/DOT LATER
resolvers = [x[0] for x in edm.get_main_resolvers('do53')]
top10_domains = edm.get_tranco_top_x_domains(10)

# Queries
# unfiltered: 'Protocol/Tool == "{p/t}"'
# no Timeout: '& `Response Time` < 3000'
# google domain: '& Domain == google.com'
# top 10 domains: '& Domain in @top10_domains'
# failure rate: '& (`Response Time` > 3000 | `Response Status` != 1 | (RCODE != "NOERROR" & ~RCODE.isnull()) | ~Error.isnull())'

def benchmark_tools(df):
    """
    query, plot and save charts to compare tools (1 for each protocol)
        Y axis = Mean Response Times (ms)
        X axis = Main resolvers
    """
    for p in protocols:
        # Select and reshape data
        df2 = df.query(f'Protocol == "{p}" & `Response Time` < 3000 & Domain == "google.com"')[["Tool", "Response Time", "Resolver"]]
        #print(df2)
        df2_pivot = pd.pivot_table(
            df2,
            values="Response Time",
            index="Resolver",
            columns="Tool",
            aggfunc=('count','mean','std')
        )

        # TODO: Confidence Interval
        df2_pivot = df2_pivot.join(pd.DataFrame(
             np.random.rand(6,4),
             columns=pd.MultiIndex.from_product([['ci95_range'], tools]),
             index=df2_pivot.index))

        for t in tools:
            #ci95_hi = []
            #ci95_lo = []
            ci95_range = []
            for i in df2_pivot.index:    
                c = df2_pivot.loc[i, 'count'][t]
                m = df2_pivot.loc[i, 'mean'][t]
                s = df2_pivot.loc[i, 'std'][t]
                #ci_hi = m + 1.96*s/math.sqrt(c)
                ci_lo = m - 1.96*s/math.sqrt(c)
                ci_range = m - ci_lo
                #ci95_hi.append(ci_hi)
                #ci95_lo.append(ci_lo)
                ci95_range.append(ci_range)
            #df2_pivot[('ci95_hi', t)] = ci95_hi
            #df2_pivot[('ci95_lo', t)] = ci95_lo
            df2_pivot[('ci95_range', t)] = ci95_range

        #print(df2_pivot)

        # Format and plot chart
        colors=['darkgray','gray','dimgray','lightgray']
        ax = df2_pivot['mean'].plot(kind="bar", color=colors, yerr=df2_pivot['ci95_range'], capsize=4)
        f = ax.get_figure()
        #f.tight_layout()
        ax.set_xlabel("Resolvers")
        ax.set_ylabel("Response Time (ms)")

        plt.subplots_adjust(bottom=0.3)
        #plt.show()
        f.savefig(f'analysis/tool_benchmark_{p}.pdf', bbox_inches='tight', dpi=300)

def benchmark_protocols(df):
    """
    query, plot and save charts to compare protocols (1 for each tool)
        Y axis = Mean Response Times (ms)
        X axis = Main Resolvers
    """
    for t in tools:
        # Select and reshape data
        df2 = df.query(f'Tool == "{t}" & (`Response Time` < 3000 & `Response Status` == 1 & (RCODE == "NOERROR" | RCODE.isnull()) | Error.isnull()) & Domain == "google.com"')[["Protocol", "Response Time", "Resolver"]]
        df2_pivot = pd.pivot_table(
            df2,
            values="Response Time",
            index="Resolver",
            columns="Protocol",
            aggfunc=np.mean
        )
        print(df2_pivot)

        # Format and plot chart
        ax = df2_pivot.plot(kind="bar")
        f = ax.get_figure()
        #f.tight_layout()
        ax.set_xlabel("Resolvers")
        ax.set_ylabel("Response Time (ms)")

        plt.subplots_adjust(bottom=0.3)
        #plt.show()
        f.savefig(f'analysis/protocol_benchmark_{t}.pdf', bbox_inches='tight', dpi=300)

def benchmark_top10_domains(df):
    """
    query, plot and save charts to compare response times of different resolvers in resolving the top 10 domains (1 for each tool/protocol combination)
        Y axis = Mean Response Times (ms)
        X axis = Main Resolvers
    """
    for t in tools:
        for p in protocols:
            # Select and reshape data
            df2 = df.query(f'Tool == "{t}" & Protocol == "{p}" & `Response Time` < 3000 & `Response Status` == 1 & Domain in @top10_domains')[["Protocol", "Response Time", "Domain", "Resolver"]]
            df2_pivot = pd.pivot_table(
                df2,
                values="Response Time",
                index="Resolver",
                columns="Domain",
                aggfunc=np.mean
            )
            print(df2_pivot)

            # Format and plot chart
            ax = df2_pivot.plot(kind="bar")
            #f.tight_layout()
            ax.set_xlabel("Resolvers")
            ax.set_ylabel("Response Time (ms)")
            ax.legend(bbox_to_anchor=(1.0, 1.0))
            f = ax.get_figure()

            plt.subplots_adjust(bottom=0.3)
            #plt.show()
            f.savefig(f'analysis/top10domains_benchmark_{t}_{p}.pdf', bbox_inches='tight', dpi=300)

def failure_rate(df):
    """
    query, plot and save charts to compare failure rates of different protocols for each resolver (1 for each tool)
        failure = (Status == -1 OR RCODE != NOERRROR OR RCODE != NaN OR Error != NaN)
        Y axis = Mean Response Times (ms)
        X axis = Main Resolvers
    """
    #for t in tools:
    # Select and reshape data
    #Tool == "{t}" & 
    df2 = df.query(f'(`Response Time` > 3000 | `Response Status` != 1 | (RCODE != "NOERROR" & ~RCODE.isnull()) | ~Error.isnull())')[["Tool", "Protocol", "Resolver"]]
    #print(df2.groupby(["Tool", "Protocol", "Resolver"]).size())
    print(df2.groupby(["Tool", "Protocol", "Resolver"]).agg({'Count':'count'}))

    #df2 = df2.eval(f'FailureRate = {len(df2.index) / len(df.index)}')
    #print(df2)
    #print(df.count(1) / df2.count(1))
    '''
    df2_pivot = pd.pivot_table(
        df2,
        values="FailureRate",
        index="Resolver",
        columns="Protocol",
        aggfunc=np.mean
    )
    print(df2_pivot)

    # Format and plot chart
    ax = df2_pivot.plot(kind="bar")
    #f.tight_layout()
    ax.set_xlabel("Resolvers")
    ax.set_ylabel("Failure Rate")
    ax.legend(bbox_to_anchor=(1.0, 1.0))
    f = ax.get_figure()

    plt.subplots_adjust(bottom=0.3)
    #plt.show()
    f.savefig(f'analysis/failure_rates_{t}.pdf', bbox_inches='tight', dpi=300)
    '''
    
    def print_stats(df):
        df2 = df.query(f'Protocol == "{p}" & `Response Time` < 3000 & Domain == "google.com"')[["Tool", "Response Time", "Resolver"]]
        print(df2)
        df2.describe()
        df2_pivot = pd.pivot_table(
            df2,
            values="Response Time",
            index="Resolver",
            columns="Tool",
            aggfunc=('count','mean','std')
        )
        print(df2_pivot)
        df2_pivot.describe()
        
if __name__ == "__main__":
    # Read data into DataFrame list
    dfs = list()
    for t in tools:
        for p in protocols:
            for r in resolvers:
                csv_file = f'./results/{t}-{p}-{r}.csv'
                #print(csv_file)
                
                # Read the CSV file into a pandas DataFrame
                try:
                    data = pd.read_csv(csv_file)

                    # Add columns for tool, protocol and resolver
                    data['Tool'] = t
                    data['Protocol'] = p
                    data['Resolver'] = r

                    # Convert the timestamp column to datetime format
                    data['Timestamp'] = pd.to_datetime(data['Timestamp'])

                    # Add to DataFrame list
                    dfs.append(data)

                    #print(data)
                except:
                    pass
    # Concat data in single DataFrame
    df = pd.concat(dfs, ignore_index=True)

    # Print Descriptive Statistics
    #print_stats(df)

    # COMPARING TOOLS
    benchmark_tools(df)

    # COMPARING PROTOCOLS
    #benchmark_protocols(df)

    # COMPARING TOP 10 DOMAINS
    #benchmark_top10_domains(df)

    # TODO: TERMINAR FUNCAO FAILURE RATES
    #failure_rate(df)