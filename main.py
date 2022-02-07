from nebuleco import Nebuleco
from connection import Connect
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import tkinter
import sys
from lib import getshutingvoltage, getDate, getFilterValues, getGoodTimestamp, getdailystd, getTime


class E(tkinter.Tk):
    def __init__(self, parent):
        tkinter.Tk.__init__(self, parent)
        self.connection = Connect()
        self.option = self.connection.nebulecolist
        #self.fig = plt.figure(figsize=(16, 4))
        #self.fig2 = plt.figure(figsize=(16, 4))

        self.fig, (self.ax, self.ax2) = plt.subplots(2, 1, figsize=(9, 9))
        #self.ax2 = self.fig2.add_subplot(211)
        self.locator = mdates.AutoDateLocator()
        self.formatter = mdates.ConciseDateFormatter(self.locator)
        self.frame = tkinter.Frame(self)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas2 = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.variable = tkinter.StringVar(self)

        self.parent = parent
        self.protocol("WM_DELETE_WINDOW", self.dest)
        self.main()

    def main(self):
        plt.close()
        self.toolbar.update()
        self.toolbar.pack()
        self.option = tkinter.OptionMenu(self, self.variable, *self.option)
        self.option.config(width=14, font=('Calibri', 15))
        self.option.pack(ipadx=0)
        #print(f'token={self.connection.getToken()}')
        self.variable.trace('w', self.callback)

    def dest(self):
        self.destroy()
        sys.exit()

    def callback(self, *args):
        plt.close()
        plt.axis([0, 80, 0, 1])
        self.ax.cla()
        self.ax2.cla()
        self.ax.xaxis.set_major_locator(self.locator)
        self.ax.xaxis.set_major_formatter(self.formatter)
        self.ax2.xaxis.set_major_locator(self.locator)
        self.ax2.xaxis.set_major_formatter(self.formatter)
        name = self.variable.get()
        passedmonth = 20
        Neb = Nebuleco(name, self.connection)
        pwmvalues, pwmtime = Neb.getPWM()
        voltage, voltageDate = Neb.getVoltage()
        # brkdate = Neb.getBreakdowndate()

        voltageFig = self.ax.plot(voltageDate, voltage, color='blue', label='voltage')
        pwmFig = self.ax2.step(pwmtime, pwmvalues, label='pww')
        #v = self.ax.scatter(voltageDate, voltage, color='blue', label='voltage')

        #time, voltage = Neb.getrawVoltage()
        #time = getGoodTimestamp(time)
        #stdv, stdt = getdailystd(voltage, time)
        #date = getDate(time)
        #voltage, date = getFilterValues(voltage, date)
        print(Neb.getLastlog())
        data = Neb.getBreakdown()
        print(data)
        brkdate = data[1]

        #av = getshutingvoltage(brkdate)
        #print('av:'+str(av))
        #self.ax.plot(date, voltage, color='blue', label='voltage')

        #d = self.ax2.hist(voltage, density=1, bins=10)
        #a = self.ax2
        #a = self.ax2.plot(date, voltage, color='red', label='raw voltage')
        #b = self.ax.plot(stdt, stdv, color='red', label='ecart_type')

        #panne = self.ax.axvline(brkdate, color='red', linestyle='--', label='panne 62 %')
        #chute = self.ax.axvline(av, color='green', linestyle='--', label='chute')
        #self.ax2.legend()


        self.frame.pack(padx=15, pady=15)

        self.canvas.get_tk_widget().pack(side='bottom', fill='both')
        self.canvas.tkcanvas.pack(side='bottom', fill='both', expand=1)
        self.canvas2.tkcanvas.pack(side='bottom', fill='both', expand=1)

        self.toolbar.update()
        self.toolbar.pack()

        self.option.config(width=14, font=('Calibri', 15))
        self.option.pack(ipadx=0)

        self.canvas2.draw()
        self.canvas.draw()


if __name__ == "__main__":
    app = E(None)
    app.title('Embedding in TK')
    app.mainloop()

    print("hello")
