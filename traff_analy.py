from nfstream import NFStreamer
import pandas as pd


class Traff_Analy():
    def __init__(self):
        self.data = []
        self.cat_name = []
        self.app_name = []
        self.app_prot = []
        self.data_short = []


    def capture(self):
        captura = NFStreamer(source='/home/igor/UMinho/MCT/captura/webex-matheus.pcapng').to_pandas()
        #captura = NFStreamer(source='/home/igor/UMinho/MCT/mct_tp3/test.pcap').to_pandas()
        self.data = pd.DataFrame(captura) # converte em dataframe
        pd.set_option('display.max_rows',320)
        print("\nA dimensão do arquivo é: ")
        print(self.data.shape)


    def filtering(self):
        self.cat_name = self.data['category_name'].unique()
        self.app_name = self.data['application_name'].unique()
        self.app_prot = self.data['app_protocol'].unique()

        self.data_short = self.data.loc[0:,[#'src_ip','dst_ip',
                'bidirectional_ip_bytes',
                #'src2dst_ip_bytes','dst2src_ip_bytes','app_protocol',
                'bidirectional_duration_ms','app_protocol','application_name','category_name',
                'client_info','server_info','j3a_client' ]]#,30,31,32]]
        # filtra por aplicações contidas na lista app_name
        #data_webex = (self.data_short['app_protocol'].isin(self.app_prot[1]))
        # filtra por aplicações que contenha a string 'Webex'
        #data_webex = (self.data_short['application_name'].str.contains('Webex'))


    def print_table(self):
        for x in self.app_prot:
            print('\n')
            data_new = (self.data_short['app_protocol'] == x)
            # imprime a tabela com um tamanho máxima definido
            print(self.data_short.loc[data_new].head(1000))


def main():
    traff = Traff_Analy()

    traff.capture()
    traff.filtering()
    traff.print_table()

if __name__ == '__main__':
    main() 

