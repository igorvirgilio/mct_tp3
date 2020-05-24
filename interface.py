from tkinter import *
from tkinter import messagebox
from traff_analy_mct_v2 import *
import tkinter
import time
import traff_analy_mct_v2
import network_capture


class Gui():
    def __init__(self, root):
        # Interface structure start here.
        btn_capture = Button(root, text='Nova Captura', command=self.btncapture)

        btn_nfstream = Button(root, text='Captura Existente', command=self.btnnfstream)

        btn_capture.grid(column=0, row=0)
        btn_nfstream.grid(column=3, row=0)

        self.frame = Frame(root).grid(columnspan=4)
        #self.txtArea = Text(self.frame, width=80, height=25)
        #self.txtArea.grid(columnspan=4)

        root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def btncapture(self):
        try:
            messagebox.showinfo("Information","A captura será incializada. Para acompanhá-la verifique o Terminal.\n\nPara finalizar a captura pressione 'Ctrl+C' em seu teclado")
            #self.txtArea.delete(1.0, END)
            fncapture = network_capture.network_capture()
            fncapture.main()
            #self.txtArea.insert(END, 'End capture packet.')
        
            messagebox.showinfo("Information","O arquivo 'network_capture_test.pcap' foi gerado.\n\nSelecione-o na próxima janela")
            fnstream = Traff_Analy()
            fnstream.main()
        
        except:
            messagebox.showerror("Error", "Algo deu errado com a captura, tente novamente.")
            print("ERRO!")
            pass
            #self.txtArea.delete(1.0, END)
            #self.txtArea.insert(END, 'Error!')
        
    def on_closing(self):
        root.destroy()
        # if messagebox.askokcancel("Quit", "Do you want to quit?"):
        #    root.destroy()

    def btnnfstream(self):
        #self.txtArea.delete(1.0, END)

        fnstream = Traff_Analy()
        fnstream.main()

    """
    def onOpen(self):

        filename = fd.askopenfilename()
        print(len(filename))
        ftypes = [('Capture Files', '*.pcapng'), ('All files', '*')]
        dlg = tkFileDialog.Open(self, filetypes = ftypes)
        fl = dlg.show()


        if fl != '':
            text = self.readFile(fl)
            self.txt.insert(END, text)

    def readFile(self, filename):

        f = open(filename, "r")
        text = f.read()
        return text
    """
# def newwindowtest():
#    nextwindow = Toplevel(root)
#    nextwindow.geometry('300x50')
#    btn_window = Button(nextwindow, text='Ping', command= lambda: btnping(nextwindow))
#    btn_window.grid(column=0, row=0)
#    label_ping = Label(nextwindow, text = 'What\'s the server do you want to ping?')
#    label_ping.grid(column=1, row=1)
#    entry_ping = Entry(nextwindow)
#    entry_ping.grid(column=1, row=0)
#    return nextwindow


if __name__ == '__main__':
    # Program start here
    root = Tk()
    root.title('TP - MCT')
    Gui(root)
    root.mainloop()
