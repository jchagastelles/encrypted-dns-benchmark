import encrypted_dns_measurement as edm
import csv
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

tools = ['dnspython', 'pydig']
protocols = ['do53', 'doh']
resolvers = [x[0] for x in edm.get_main_resolvers('do53')]
top10_domains = edm.get_tranco_top_x_domains(10)

# Queries
# unfiltered: 'Protocol/Tool == "{p/t}"'
# no Timeout: '& `Response Time` < 3000'
# google domain: '& Domain == google.com'
# top 10 domains: '& Domain in @top10_domains'


def benchmark_tools(df):
    """
    query, plot and save charts to compare tools (1 for each protocol)
        Y axis = Mean Response Times (ms)
        X axis = Main resolvers
    """
    for p in protocols:
        # Select and reshape data
        df2 = df.query(f'Protocol == "{p}" & `Response Time` < 3000 & `Response Status` == 1 & Domain == "google.com"')[["Tool", "Response Time", "Resolver"]]
        df2_pivot = pd.pivot_table(
            df2,
            values="Response Time",
            index="Resolver",
            columns="Tool",
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
        f.savefig(f'analysis/tool_benchmark_{p}.pdf', bbox_inches='tight', dpi=300)

def benchmark_protocols(df):
    """
    query, plot and save charts to compare protocols (1 for each tool)
        Y axis = Mean Response Times (ms)
        X axis = Main Resolvers
    """
    for t in tools:
        # Select and reshape data
        df2 = df.query(f'Tool == "{t}" & `Response Time` < 3000 & `Response Status` == 1 & Domain == "google.com"')[["Protocol", "Response Time", "Resolver"]]
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

if __name__ == "__main__":
    # TODO: BETTER PARAMETRIZATION
    tools = ['dnspython', 'pydig']
    protocols = ['do53', 'doh']
    resolvers = [x[0] for x in edm.get_main_resolvers('do53')]

    # Read data into DataFrame list
    dfs = list()
    for t in tools:
        for p in protocols:
            for r in resolvers:
                csv_file = f'./results/17.08/{t}-{p}-{r}.csv'
                #print(csv_file)
                
                # Read the CSV file into a pandas DataFrame
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
    # Concat data in single DataFrame
    df = pd.concat(dfs, ignore_index=True)

    # COMPARING TOOLS
    benchmark_tools(df)

    # COMPARING PROTOCOLS
    benchmark_protocols(df)

    # COMPARING TOP 10 DOMAINS
    benchmark_top10_domains(df)