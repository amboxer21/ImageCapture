from Tkinter import *

WELCOME_DURATION = 2000
INFO = '''ImageCapturePy must be initialized before you can use it for the first time.'''

class init():

    def result(self,bool_val, window):
        return bool_val and window.destroy

    def ui():
        window = Tk()
        window.geometry("150x150") 
        window.resizable(0,0)
        window.title('ImageCapturePy')

        msg   = Frame(window)
        msg.pack(side=TOP)
        Message(msg, text=INFO, padx=20, pady=20).pack()

        bttns = Frame(window)
        bttns.pack(side=BOTTOM, fill=BOTH, expand=True)

        Button(bttns, text="OK", fg="Green", command=result(True,window)).pack(side=LEFT, fill=BOTH, expand=True)
        Button(bttns, text="Cancel", fg="Red", command=result(False,window)).pack(side=RIGHT, fill=BOTH, expand=True)

        window.mainloop()

if __name__ == '__main__':
    init.ui()
