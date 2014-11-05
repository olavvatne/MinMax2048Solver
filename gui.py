from tkinter import *
from tkinter import ttk, filedialog, messagebox
from display import Game2048Display
from model import GameState, Direction
from controller import GameController
import threading

class AppUI(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master, relief=SUNKEN, bd=2, highlightthickness=0)
        self.grid(sticky=N+S+E+W)
        
        self.menubar = Menu(self)
        menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Game", menu=menu)
        
        menu.add_command(label="Start", command=lambda: start_solver(), accelerator="Ctrl+A")
        master.bind("<Control-a>", lambda event: start_solver())

        menu.add_command(label="Stop", command=lambda: stop_solver(), accelerator="Ctrl+S")
        master.bind("<Control-s>", lambda event: stop_solver())
        
        menu.add_command(label="Restart", command=lambda: callback(), accelerator="Ctrl+R")
        master.bind("<Control-r>", lambda event: callback())

        def callback():
                restart()
        try:
            self.master.config(menu=self.menubar)
        except AttributeError:
            self.master.tk.call(master, "config", "-menu", self.menubar)

        self.visualizer = Game2048Display(self)
        self.visualizer.grid(row=1, column=1, sticky=N+S+E+W)
        #For resizing purposes. Display can be dynamically resized
        self.visualizer.bind("<Configure>", self.visualizer.on_resize)
        self.visualizer.addtag_all("all")
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

def start_solver(*args):
    #Run algorithm in it's own thread
    #The algorithm send events that is put in a display queue.
    #This UI and algorithm can work on seperate threads
    def callback():
       app.controller.start_solving()
    t = threading.Thread(target=callback)
    t.daemon = True
    t.start()

def stop_solver(*args):
    app.controller.stop_solving()

def onExit(*args):
        print("TEST_EXIT")
        root.quit()

def left_action(*args):
    print("LEFT")
    app.controller.action(Direction.LEFT)

def right_action(*args):
    app.controller.action(Direction.RIGHT)
    print("RIGHT")

def up_action(*args):
    app.controller.action(Direction.UP)
    print("UP")

def down_action(*args):
    app.controller.action(Direction.DOWN)
    print("Down")

root = Tk()
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.title("2048")
app = AppUI(root)
app.controller = GameController(app.visualizer)
app.visualizer.set_model(app.controller.model)
app.visualizer.start()
#root.bind('<Return>', solve)
root.bind('<Left>', left_action)
root.bind('<Right>', right_action)
root.bind('<Up>', up_action)
root.bind('<Down>', down_action)
root.mainloop()