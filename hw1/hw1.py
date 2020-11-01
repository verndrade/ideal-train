import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats

client = pd.read_csv(sys.argv[2], sep=' ', header=None)
client.columns = ['Source', 'Dest']
server = pd.read_csv(sys.argv[3], sep=' ', header=None)
server.columns = ['Source', 'Dest']

client_dfs = [0]
for i in range(1, 21):
    df = pd.read_csv(sys.argv[1] + '\client' + str(i) + '.txt', sep='\t', header=None)
    df.columns = ['Time', 'Source', 'Dest', 'Seq', 'Ack']
    df = df.loc[(df['Dest'] == client.iloc[i - 1]['Source']) & (df['Source'] == client.iloc[i - 1]['Dest'])]
    if i == 1:
        df['Time'] = pd.to_datetime(df['Time'], format='%M:%S.%f')
    else:
        df['Time'] = pd.to_datetime(df['Time'])
    df['Time'] = df['Time'].astype(np.int64) // 10 ** 6
    df['Time'] = df['Time'] - df['Time'].iloc[0]
    df = df.drop(columns=['Source', 'Dest', 'Ack'])
    df = df.dropna()
    client_dfs.append(df)

server_dfs = [0]
for i in range(1, 21):
    df = pd.read_csv(sys.argv[1] + '\server' + str(i) + '.txt', sep='\t', header=None)
    df.columns = ['Time', 'Source', 'Dest', 'Seq', 'Ack']
    df = df.loc[(df['Dest'] == server.iloc[i - 1]['Source']) & (df['Source'] == server.iloc[i - 1]['Dest'])]
    df['Time'] = pd.to_datetime(df['Time'])
    df['Time'] = df['Time'].astype(np.int64) // 10 ** 6
    df['Time'] = df['Time'] - df['Time'].iloc[0]
    df = df.drop(columns=['Source', 'Dest', 'Seq'])
    df = df.dropna()
    server_dfs.append(df)

aggre = 2000
noise = 20
count = 0
output = open('output.txt', 'w')
for q in range(1, 21):
    client_df = client_dfs[q]
    client_df.columns = ['Time', 'Bytes']
    client_df = client_df.astype(float)
    client_df = client_df[len(client_df) // noise:-len(client_df) // noise]
    client_df['col'] = (client_df['Time'] // aggre).astype(int)
    client_df = client_df.groupby(client_df['col'], as_index=False).mean()
    client_df = client_df.drop_duplicates()

    correlations = []
    for j in range(1, 21):
        server_df = server_dfs[j]
        server_df.columns = ['Time', 'Bytes']
        server_df = server_df.astype(float)
        server_df = server_df[len(server_df) // noise:-len(server_df) // noise]
        server_df['col'] = (server_df['Time'] // aggre).astype(int)
        server_df = server_df.groupby(server_df['col'], as_index=False).mean()
        server_df = server_df.drop_duplicates()

        temp = (len(client_df) if len(client_df) < len(server_df) else len(server_df))

        new_client_df = client_df.iloc[:temp]
        new_server_df = server_df.iloc[:temp]
        correlations.append(stats.pearsonr(new_client_df['Bytes'], new_server_df['Bytes']))
    maxc = max(correlations)
    indexc = correlations.index(maxc) + 1
    output.write(str(q) + ' ' + str(indexc) + '\n')
    if q == indexc:
        count += 1
        
output.write(str(count))
output.close()

""" client_df = client_dfs[5]
client_df.columns = ['Time', 'Bytes']
client_df = client_df.astype(float)
client_df = client_df[len(client_df) // 10:-len(client_df) // 10]

server_df = server_dfs[5]
server_df.columns = ['Time', 'Bytes']
server_df = server_df.astype(float)
plt.plot(client_df['Time'], client_df['Bytes'], label='Client 5')
plt.plot(server_df['Time'], server_df['Bytes'], label='Server 5')
plt.xlabel('Relative Time from Start of Connection (ms)', fontsize=10)
plt.ylabel('Bytes Sent/Recieved', fontsize=10)
plt.legend(loc=2)
plt.title('Correlated Traces')
plt.show()

server_df = server_dfs[6]
server_df.columns = ['Time', 'Bytes']
server_df = server_df.astype(float)
plt.plot(client_df['Time'], client_df['Bytes'], label='Client 5')
plt.plot(server_df['Time'], server_df['Bytes'], label='Server 6')
plt.xlabel('Relative Time from Start of Connection (ms)', fontsize=10)
plt.ylabel('Bytes Sent/Recieved', fontsize=10)
plt.legend(loc=2)
plt.title('Uncorrelated Traces')
plt.show() """
