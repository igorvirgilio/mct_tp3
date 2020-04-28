from nfstream import NFStreamer


# or network interface (source="eth0")
my_awesome_streamer = NFStreamer(source="./skype-matheus.pcapng")

my_dataframe = NFStreamer(source='./skype-matheus.pcapng').to_pandas()
my_dataframe.head()

for flow in my_awesome_streamer:
    print(flow)
    print("")

print(my_dataframe)
