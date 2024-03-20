import argparse
import os
import encrypted_dns_measurement as edm
import csv
import math
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

master_df = None
results_folder = './results/'

tools = set()
protocols = set()
resolvers = set()

def benchmark_tools(df):
    """
    query, plot and save charts to compare tools (1 for each protocol)
        Y axis = Mean Response Times (ms)
        X axis = Main resolvers
    """
    for p in protocols:
        # Select and reshape data
        df2 = df.query(f'Protocol == "{p}" & `Response Time` < 3000')[["Tool", "Response Time", "Resolver"]]
        df2_pivot = pd.pivot_table(
            df2,
            values="Response Time",
            index="Resolver",
            columns="Tool",
            aggfunc=('count','mean','std')
        )

        # Add Confidence Interval
        df2_pivot = df2_pivot.join(pd.DataFrame(
             np.random.rand(5,4),
             columns=pd.MultiIndex.from_product([['ci95_range'], tools]),
             index=df2_pivot.index))

        for t in tools:
            ci95_range = []
            for i in df2_pivot.index:    
                c = df2_pivot.loc[i, 'count'][t]
                m = df2_pivot.loc[i, 'mean'][t]
                s = df2_pivot.loc[i, 'std'][t]
                ci_lo = m - 1.96*s/math.sqrt(c)
                ci_range = m - ci_lo
                ci95_range.append(ci_range)
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
        f.savefig(f'results/tool_benchmark_{p}.pdf', bbox_inches='tight', dpi=300)
        print(f'Saved results/tool_benchmark_{p}.pdf')

def benchmark_protocols(df):
    """
    query, plot and save charts to compare protocols (1 for each tool)
        Y axis = Mean Response Times (ms)
        X axis = Main Resolvers
    """
    
    # aggregated
    df2 = df.query(f'(`Response Time` < 3000 & `Response Status` == 1 & (RCODE == "NOERROR" | RCODE.isnull()) | Error.isnull())')[["Protocol", "Response Time", "Resolver"]]
    df2_pivot = pd.pivot_table(
        df2,
        values="Response Time",
        index="Resolver",
        columns="Protocol",
        aggfunc=('count','mean','std')
    )

    # Add Confidence Interval
    df2_pivot = df2_pivot.join(pd.DataFrame(
            np.random.rand(5,3),
            columns=pd.MultiIndex.from_product([['ci95_range'], protocols]),
            index=df2_pivot.index))

    for p in protocols:
        ci95_range = []
        for i in df2_pivot.index:    
            c = df2_pivot.loc[i, 'count'][p]
            m = df2_pivot.loc[i, 'mean'][p]
            s = df2_pivot.loc[i, 'std'][p]
            ci_lo = m - 1.96*s/math.sqrt(c)
            ci_range = m - ci_lo
            ci95_range.append(ci_range)
        df2_pivot[('ci95_range', p)] = ci95_range

    #print(df2_pivot)

    # Format and plot chart
    colors=['darkgray','gray','dimgray','lightgray']
    ax = df2_pivot['mean'].plot(kind="bar", color=colors, yerr=df2_pivot['ci95_range'], capsize=4)
    f = ax.get_figure()
    ax.set_xlabel("Resolvers")
    ax.set_ylabel("Response Time (ms)")

    plt.subplots_adjust(bottom=0.3)
    f.savefig(f'results/protocol_benchmark_aggr.pdf', bbox_inches='tight', dpi=300)
    print(f'Saved results/protocol_benchmark_aggr.pdf')

    # by tool
    for t in tools:
        # Select and reshape data
        df2 = df.query(f'Tool == "{t}" & (`Response Time` < 3000 & `Response Status` == 1 & (RCODE == "NOERROR" | RCODE.isnull()) | Error.isnull())')[["Protocol", "Response Time", "Resolver"]]
        df2_pivot = pd.pivot_table(
            df2,
            values="Response Time",
            index="Resolver",
            columns="Protocol",
            aggfunc=('count','mean','std')
        )

        # Add Confidence Interval
        df2_pivot = df2_pivot.join(pd.DataFrame(
             np.random.rand(5,3),
             columns=pd.MultiIndex.from_product([['ci95_range'], protocols]),
             index=df2_pivot.index))

        for p in protocols:
            ci95_range = []
            for i in df2_pivot.index:    
                c = df2_pivot.loc[i, 'count'][p]
                m = df2_pivot.loc[i, 'mean'][p]
                s = df2_pivot.loc[i, 'std'][p]
                ci_lo = m - 1.96*s/math.sqrt(c)
                ci_range = m - ci_lo
                ci95_range.append(ci_range)
            df2_pivot[('ci95_range', p)] = ci95_range

        #print(df2_pivot)

        # Format and plot chart
        colors=['darkgray','gray','dimgray','lightgray']
        ax = df2_pivot['mean'].plot(kind="bar", color=colors, yerr=df2_pivot['ci95_range'],capsize=4)
        f = ax.get_figure()
        #f.tight_layout()
        ax.set_xlabel("Resolvers")
        ax.set_ylabel("Response Time (ms)")

        plt.subplots_adjust(bottom=0.3)
        #plt.show()
        f.savefig(f'results/protocol_benchmark_{t}.pdf', bbox_inches='tight', dpi=300)
        print(f'Saved results/protocol_benchmark_{t}.pdf')

    
def print_stats(df):
    df2 = df.query(f'Protocol == "{p}" & `Response Time` < 3000')[["Tool", "Response Time", "Resolver"]]
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
    #python3 encrypted_dns_benchmark.py [protocol_benchmark] [tool_benchmark]
    parser = argparse.ArgumentParser(
                    prog='Encrypted DNS Benchmark',
                    description='Analyzes measurement results and plots charts (https://github.com/jchagastelles/encrypted-dns-benchmark)')
    parser.add_argument('-p', action='store_true',
                    default=False,
                    help='Protocol Benchmark')
    parser.add_argument('-t', action='store_true',
                    default=False,
                    help='Tool Benchmark')
    parser.add_argument('-f', action='store_true',
                    default=False,
                    help='Failure Rate Benchmark')
    parser.add_argument('-d', action='store',
                    default='./results/',
                    help='Output path (default: "results/")')
    args = parser.parse_args()

    for filename in os.listdir(results_folder):
        if filename.endswith(".csv"):
            # Extract tool, protocol, and resolver from filename
            parts = filename.split("-")
            t = parts[0]
            tools.add(t)
            p = parts[1]
            protocols.add(p)
            r = parts[2].replace(".csv", "")
            resolvers.add(r)

            # Read CSV file
            df = pd.read_csv(os.path.join(results_folder, filename))

            # Add new columns and assign values
            df["Tool"] = t
            df["Protocol"] = p
            df["Resolver"] = r

            # Concatenate to master DataFrame (handling first iteration)
            if master_df is None:
                master_df = df.copy()
            else:
                master_df = pd.concat([master_df, df], ignore_index=True)


    #print_stats(master_df)

    if args.t:
        benchmark_tools(master_df)

    if args.p:
        benchmark_protocols(master_df)