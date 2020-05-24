from nfstream import NFStreamer
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import display, HTML
from tkinter import *
from tabulate import tabulate
import tkinter as tk					 
from tkinter import ttk 

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
        #captura = NFStreamer(source='./Pcap_Files/webex-matheus.pcapng').to_pandas()
        captura = NFStreamer(source='/home/igor/UMinho/MCT/captura/blackboard_03-04.pcapng').to_pandas()
        #captura = NFStreamer(source='/home/igor/UMinho/MCT/mct_tp3/test.pcap').to_pandas()
        self.data = pd.DataFrame(captura) # converte em dataframe


    def filtering(self):
        self.cat_name = self.data['category_name'].unique()
        self.app_name = self.data['application_name'].unique()
        self.app_prot = self.data['app_protocol'].unique()

        self.data_short = self.data.loc[0:,['src_ip','dst_ip','src_port','dst_port',
                                            'bidirectional_ip_bytes','bidirectional_packets',
                                            #'src2dst_ip_bytes','dst2src_ip_bytes','app_protocol',
                                            #'protocol',#'client_info',
                                            'server_info',
                                            #'bidirectional_duration_ms',
                                            'app_protocol','application_name','category_name',
                                            ]]
        # Renomeando Colunas
        self.data_short.index.name = 'Flow'
        self.data_short.rename(columns={'src_ip':'Source IP','dst_ip':'Destin. IP',
                                        'src_port':'Src Port','dst_port':'Dst Port',
                                        'bidirectional_ip_bytes':'Total Bytes','server_info':'Servers info',
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

        data_grouped = self.data.groupby(self.data_short.category_name)
        
        # Cria novo dicionario com a estrutuda do novo DataFrame
        data_cat = {'categoria':[],'total_bytes':[],'(%) do total':[],'Applicações':[],'# of Apps':[],'Most used server':[],} 
        self.df_cat_stat = pd.DataFrame(data_cat) # converte em DF pandas
        

        columns = list(self.df_cat_stat)
        data_dict = []

        i=0
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
        
        #patches, texts = plt.pie(sizes, shadow=True, startangle=90)
        #plt.legend(patches, labels, loc="best")
        #plt.tight_layout()

        plt.axis('equal')
        plt.title('TP - QoS / Category Graph')
        plt.show()

    def plot_graphs2(self):
        fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))

        recipe = self.df_cat_stat['categoria'].to_list()

        data = self.df_cat_stat['total_bytes'].to_list()

        wedges, texts = ax.pie(data, wedgeprops=dict(width=0.5), startangle=-40)

        bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
        kw = dict(arrowprops=dict(arrowstyle="-"),
                bbox=bbox_props, zorder=0, va="center")

        for i, p in enumerate(wedges):
            ang = (p.theta2 - p.theta1)/2. + p.theta1
            y = np.sin(np.deg2rad(ang))
            x = np.cos(np.deg2rad(ang))
            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            connectionstyle = "angle,angleA=0,angleB={}".format(ang)
            kw["arrowprops"].update({"connectionstyle": connectionstyle})
            ax.annotate(recipe[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
                        horizontalalignment=horizontalalignment, **kw)

        ax.set_title("Matplotlib bakery: A donut")

        plt.show(block=FALSE)   
    
    def plot_graphs_barh(self):
        labels = self.df_cat_stat['categoria'].to_list()
        sizes = self.df_cat_stat['%% do total'].to_list()

        df = pd.DataFrame({'Total Bytes': sizes}, index=labels)
        ax = df.plot.barh(y='Total Bytes')

        plt.show(block=FALSE) 
    
    def win_table(self):
        win = Tk()
        win.title('TP - QOS / Full Category Table')
        
        pdtabulate=lambda df:tabulate(self.df_cat_stat.set_index('categoria'),headers='keys',tablefmt='psql')

        print(pdtabulate(self.df_cat_stat))

        table1 = Label(win, text=pdtabulate(self.df_cat_stat),font=('Consolas', 10), justify=LEFT, anchor='nw').grid(sticky='ewns')    
        #table2 = Label(win, text=self.df_cat_stat['total_bytes']).grid(column=1, row=0)
        win.mainloop()

    def win_tabs(self):

        root = tk.Tk() 
        root.title("Relatório resumo - Categorias") 
        tabControl = ttk.Notebook(root) 

        num_of_tabs = len(self.cat_name)

        tabControl.pack(expand = 1, fill ="both") 

        
        print(self.df_dict[self.cat_name[0]])
        i=0
        for x in range(len(self.cat_name)):
            
            globals()[self.cat_name[i]] = ttk.Frame(tabControl)
            #tab2 = ttk.Frame(tabControl)
            tabControl.add(globals()[self.cat_name[i]], text =self.cat_name[i])
            pdtabulate=lambda df:tabulate(self.df_dict[self.cat_name[i]],headers='keys',tablefmt='psql')
            ttk.Label(globals()[self.cat_name[i]],text=pdtabulate(self.df_dict[self.cat_name[i]]),font=('Consolas', 10), justify=LEFT, anchor='nw').grid(sticky='ewns')
            i += 1

        root.mainloop()

    def win_tabs_scroll(self):

        root = tk.Tk() 
        root.title("Relatório resumo - Categorias") 
         
        
        container = ttk.Frame(root) ####
        canvas = tk.Canvas(container) #### 
        scrollable_frame = ttk.Frame(canvas)      
        tabControl = ttk.Notebook(scrollable_frame)

        yscrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview) ####
        xscrollbar = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview) ####

        num_of_tabs = len(self.cat_name)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=yscrollbar.set)
        canvas.configure(xscrollcommand=xscrollbar.set)

        tab1 = ttk.Frame(tabControl)
        #canvas = tk.Canvas(tab1)        ######
        #scrollable_frame = ttk.Frame(canvas)       #####
        tabControl.add(tab1, text ='Tab 1') 
        pdtabulate=lambda df:tabulate(self.df_cat_stat.set_index('categoria'),headers='keys',tablefmt='psql')
        ttk.Label(tab1,text=pdtabulate(self.df_cat_stat),font=('Consolas', 10), justify=LEFT, anchor='nw').grid(sticky='ewns') 
        
        print(self.df_dict[self.cat_name[0]])
        tab2 = ttk.Frame(tabControl)
        tabControl.add(tab2, text =self.cat_name[0])
        pdtabulate=lambda df:tabulate(self.df_dict[self.cat_name[0]],headers='keys',tablefmt='psql')
        ttk.Label(scrollable_frame, text=pdtabulate(self.df_dict[self.cat_name[0]]),font=('Consolas', 10), justify=LEFT, anchor='nw').grid(sticky='ewns')
        ttk.Label(tab2, text=pdtabulate(self.df_dict[self.cat_name[0]]),font=('Consolas', 10), justify=LEFT, anchor='nw').grid(sticky='ewns')

        tab3 = ttk.Frame(tabControl)
        tabControl.add(tab3, text ='Tab 3')
        ttk.Label(tab3,                 text =len(self.cat_name)).grid(column = 0, 
                                            row = 0, 
                                            padx = 30, 
                                            pady = 30) 

        tabControl.pack(expand = 1, fill ="both") 

        root.mainloop()

    def win_scroll(self):
        root = tk.Tk() ####
        container = ttk.Frame(root) ####
        canvas = tk.Canvas(container) ####
        yscrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview) ####
        xscrollbar = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview) ####
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=yscrollbar.set)
        canvas.configure(xscrollcommand=xscrollbar.set)

        pdtabulate=lambda df:tabulate(self.df_dict[self.cat_name[0]],headers='keys',tablefmt='psql')
        ttk.Label(scrollable_frame, text=pdtabulate(self.df_dict[self.cat_name[0]]),font=('Consolas', 10), justify=LEFT, anchor='nw').grid(sticky='ewns')

        container.pack(expand = 1, fill ="both")
        canvas.pack(side="left", fill="both", expand=True)
        yscrollbar.pack(side="right", fill="y")
        xscrollbar.pack(side="bottom", fill="x")

        root.mainloop()


    """
    def main(self):
        #traff = Traff_Analy()

        self.capture()
        self.filtering()
        self.statistic()
        self.print_table()
        #self.plot_graphs_barh()
        self.plot_graphs()
        
        self.win_table()
        #self.plot_graphs2()
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


if __name__ == '__main__':
    main() 

