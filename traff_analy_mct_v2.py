from nfstream import NFStreamer
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import display, HTML
from tabulate import tabulate
from tkinter import *
import tkinter as tk					 
from tkinter import ttk 
from tkinter import filedialog as fd

class Traff_Analy():
    def __init__(self):
        self.data = []
        self.cat_name = []
        self.app_name = []
        self.app_prot = []
        self.data_short = []
        self.data_dict = {}
        self.df_dict = []
        self.df_dict_stat = []
        self.df_cat_stat = []
        self.serv_info = []


    def capture(self):
        """
        Função abre filedialog para escolher o arquivo de 
        captura que será utilizado. É definido que os formatos
        .pcap e .pcapng serão os formatos padrões
        """
        filetypes=(("Capturas", "*.pcap .pcapng"), ("All files", "*.*")) 
        cap_file = fd.askopenfilename(filetypes=filetypes)
        print(cap_file)
        answer = messagebox.askokcancel("Análise de Captura","A captura será analisada e levará alguns segundos. \n\nPor favor aguarde. \n\nPressione 'OK' para continuar.")
        #captura = NFStreamer(source='./Pcap_Files/webex-matheus.pcapng').to_pandas()
        if answer == True:

            captura = NFStreamer(source=str(cap_file)).to_pandas()
            #captura = NFStreamer(source='/home/igor/UMinho/MCT/mct_tp3/test.pcap').to_pandas()
            self.data = pd.DataFrame(captura) # converte em dataframe
        
        else:
            return


    def filtering(self):
        """
        Função faz o primeiro tratamento dos dados,
        selecionando as colunas mais significantes para 
        esta análise

        É também atribuído os valores de certas colunas do
        DataFrame Pandas para listas para que possam ser 
        manipuladas.
        """
        self.cat_name = self.data['category_name'].unique()
        self.app_name = self.data['application_name'].unique()
        self.app_prot = self.data['app_protocol'].unique()

        self.data_short = self.data.loc[0:,['src_ip','dst_ip','src_port','dst_port',
                                            'bidirectional_ip_bytes','bidirectional_packets',
                                            #'src2dst_ip_bytes','dst2src_ip_bytes','app_protocol',
                                            #'protocol',#'client_info',
                                            'server_info','client_info',
                                            #'bidirectional_duration_ms',
                                            'app_protocol','application_name','category_name',
                                            ]]
        # Renomeando Colunas
        self.data_short.index.name = 'Flow'
        self.data_short.rename(columns={'src_ip':'Source IP','dst_ip':'Destin. IP',
                                        'src_port':'Src Port','dst_port':'Dst Port',
                                        'bidirectional_ip_bytes':'Total Bytes',
                                        'client_info':'Client info','server_info':'Servers info',
                                        'bidirectional_packets':'Total Packets'}, inplace = True)

        # cria vários um dicionario com todas as tabelas separadas pela list criada em cat_name
        self.df_dict = {elem : pd.DataFrame for elem in self.cat_name}
        for key in self.df_dict.keys():
            self.df_dict[key] = self.data_short[:][self.data_short.category_name == key]
        

    def statistic(self):
        self.total_bi_bytes = (self.data_short['Total Bytes'].sum())/1000
        total_bi_packets = self.data_short['Total Packets'].sum()
        total_flows = len(self.data_short.index)
        print('Total de bytes da captura: '+str(self.total_bi_bytes))
        print('Total de pacotes da captura: '+str(total_bi_packets))
        print('Total de fluxos da captura: '+str(total_flows))

        # Agrupa em os dados do dataframe original baseados na coluna 'category_name'
        data_grouped = self.data.groupby(self.data_short.category_name)
        
        # Cria novo dicionario com a estrutuda do novo DataFrame
        data_cat = {'categoria':[],'total_bytes':[],'(%) do total':[],'Applicações':[],'# of Apps':[],'Most used server':[],} 
        self.df_cat_stat = pd.DataFrame(data_cat) # converte em DF pandas
        
        # Adiciona o 
        columns = list(self.df_cat_stat)
        data_dict = []

        i=0
        """Separação dos DataFrame em multiplos DataFrames por categoria""" 
        for x in self.cat_name:
            
            group_x = data_grouped.get_group(str(self.cat_name[i]))
            group_x_name = group_x.iloc[0]['category_name']
                      
            all_bytes = (group_x['bidirectional_ip_bytes'].sum())/1000
            print(all_bytes)
            percent_of = round(((all_bytes/self.total_bi_bytes)*100 ),2)

            app_per_cat = group_x['application_name'].unique()
            num_app = len(app_per_cat)
            group_x = group_x.sort_values(by='bidirectional_raw_bytes', ascending=False)

            # Coletando informação dos principais servidores da categoria
            server_freq = group_x['server_info'].value_counts()[:1].index.tolist()

            server_freq = list(filter(None,group_x['server_info']))

            df_graphlist = []
            j = 0
            for x in server_freq:
                if server_freq[j]:
                    df_graphlist.extend(x.split(","))
                    j+=1  
                else:
                    pass
            
            # Os servers que tiverem valor zero é colocado "-"
            if len(df_graphlist) == 0:
                df_graphlist = ['-']  
            
            # remove os endereços 
            for word in df_graphlist[:]:
                if word.startswith('*'):
                    df_graphlist.remove(word)
            print(df_graphlist[0])
            
            values = [group_x_name, all_bytes, percent_of, app_per_cat, num_app, df_graphlist[0]]
            zipped = zip(columns,values)

            dici = dict(zipped)
            data_dict.append(dici)

            i += 1

        # Faz o append do dicitionário no DataFrame e ordena descendentemente a partir do total de Bytes
        self.df_cat_stat = self.df_cat_stat.append(data_dict, True).sort_values(by='total_bytes', ascending=False)
        

    def print_table(self):
        i = 0
        
        for x in self.app_prot:

            filt = (self.data_short['app_protocol'] == x) # Cria filtro p/ imprimir somente linhas que contenham o 'app_prot' x
            data_filt = self.data_short.loc[filt] # criar novo DataFrame com somente dados do app_prot x
 
            sum = data_filt['Total Bytes'].sum()
            self.data_dict.update({ self.app_name[i]: sum})
            i += 1  

        
        '''
            Imprime a table de uma categoria específica ou imprime 
            a tabela de todas as categorias.
        '''
        # Imprime uma tabela para cada categoria
        #i = 0
        #for x in self.cat_name:
        #    print(self.cat_name[i])
        #    print(self.df_dict[self.cat_name[i]])
        #    i += 1     
        #for key, value in mydic.items() :
        #    print (key, value)

        # Imprime tabela de estatísticas
        print(self.df_cat_stat)
        print ("Dataframe 1:")
        display(self.df_cat_stat.set_index('categoria'))

    
    def plot_graphs(self):

        # soma todos os bytes das categorias que possuem valor <= 1
        sum_of_other = self.df_cat_stat.loc[self.df_cat_stat['(%) do total'] <= 1, 'total_bytes'].sum()

        # Elimina as categorias de pouco relevantes
        df_graph = self.df_cat_stat.loc[self.df_cat_stat['(%) do total'] >= 1]
        # Cria um novo Dataframe reduzido com os dados para plotagem do gráfico
        df_graph = df_graph[['categoria', 'total_bytes']].copy()
        
        # Adiciona uma linha com a categoria 'Others' e com o valor da soma dos bytes daquelas categorias pouco relevantes
        df_graph = df_graph.append({'categoria':'Others','total_bytes':sum_of_other}, ignore_index=True)
        print(df_graph)
        print ("Dataframe 3:")
        display(self.df_cat_stat.set_index('categoria'))
        
        labels = df_graph['categoria'].to_list()
        sizes = df_graph['total_bytes'].to_list()

        # Plot
        plt.pie(sizes, labels=labels, #xplode=0.1, #colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=140)

        plt.axis('equal')
        plt.title('TP - MCT / Category Graph')
        plt.show()


    def win_tabs_scroll(self):

        """ 
        Função para criar uma janela com abas, sendo a primeira com o
        resumo das categorias que foram identificadas na captura e
        as demais aba com as respetivas categorias com seus respetivos 
        detalhes
        """
        root = tk.Tk() 
        root.title("Relatório resumo - Categorias") 
        tabControl = ttk.Notebook(root) 

        num_of_tabs = len(self.cat_name)

        tabControl.pack(expand = 1, fill ="both") 

        # Cria a primeira aba resumo
        cat_tab = ttk.Frame(tabControl)
        h = Scrollbar(cat_tab, orient = 'horizontal')
        h.pack(side = BOTTOM, fill = X)
        v = Scrollbar(cat_tab)
        v.pack(side = RIGHT, fill = Y)

        tabControl.add(cat_tab, text ='CATEGORIAS')
        pdtabulate=lambda df:tabulate(self.df_cat_stat,headers='keys',tablefmt='psql')
        #ttk.Label(cat_tab,text=pdtabulate(self.df_cat_stat),font=('Consolas', 10), justify=LEFT, anchor='nw').grid(sticky='ewns')
        t1 = Text(cat_tab,width = 300, height = 100, wrap = NONE,
                xscrollcommand = h.set,  
                yscrollcommand = v.set)
        t1.insert(END,pdtabulate(self.df_cat_stat))
        t1.pack(side=TOP, fill=X)
        h.config(command=t1.xview)
        v.config(command=t1.yview)
        
        
        i=0
        for x in range(len(self.cat_name)):
            
            globals()[self.cat_name[i]] = ttk.Frame(tabControl)
            #tab2 = ttk.Frame(tabControl)
            h = Scrollbar(globals()[self.cat_name[i]], orient = 'horizontal')
            h.pack(side = BOTTOM, fill = X)
            v = Scrollbar(globals()[self.cat_name[i]])
            v.pack(side = RIGHT, fill = Y)

            tabControl.add(globals()[self.cat_name[i]], text =self.cat_name[i])
            pdtabulate=lambda df:tabulate(self.df_dict[self.cat_name[i]],headers='keys',tablefmt='psql')
            globals()["t" + str(i)] = Text(globals()[self.cat_name[i]],width = 300, height = 100, wrap = NONE,xscrollcommand = h.set,yscrollcommand = v.set)
            
            globals()["t" + str(i)].insert(END, pdtabulate(self.df_dict[self.cat_name[i]]))#,
                                    #font=('Consolas', 10), justify=LEFT, anchor='nw',
                                    #xscrollcommand = h.set,
                                    #yscrollcommand = v.set)#.grid(sticky='ewns')
            globals()["t" + str(i)].pack(side=TOP, fill=X)
            h.config(command=globals()["t" + str(i)].xview)
            v.config(command=globals()["t" + str(i)].yview)
                         
            #ttk.Label(globals()[self.cat_name[i]],text=pdtabulate(self.df_dict[self.cat_name[i]]),
            #                                    font=('Consolas', 10), justify=LEFT, anchor='nw').grid(sticky='ewns')
                                                #xscrollcommand = h.set,
                                                #yscrollcommand = v.set)#.grid(sticky='ewns')
            
            i += 1

        root.mainloop()

    
    def main(self):

        self.capture()
        self.filtering()
        self.statistic()
        #self.print_table()
        self.plot_graphs()
        self.win_tabs_scroll()
        

"""
def main():
    traff = Traff_Analy()

    traff.capture()
    traff.filtering()
    traff.statistic()
    traff.print_table()
    #traff.plot_graphs_barh()
    traff.plot_graphs()
    traff.win_tabs()    
    #traff.win_scroll()
    #traff.plot_graphs2()
"""

if __name__ == '__main__':
    main() 

