from Tkinter import *

WELCOME_DURATION = 2000
INFO = '''ImageCapturePy must be initialized before you can use it for the first time.'''

def init():
    top = Toplevel()
    top.title('ImageCapturePy')
    Message(top, text=WELCOME_MSG, padx=20, pady=20).pack()
    top.after(WELCOME_DURATION, top.destroy)

window = Tk()
window.geometry("150x150") 
window.resizable(0,0)
window.title('ImageCapturePy')

msg   = Frame(window)
msg.pack(side=TOP)
Message(msg, text=INFO, padx=20, pady=20).pack()

bttns = Frame(window)
bttns.pack(side=BOTTOM, fill=BOTH, expand=True)

Button(bttns, text="OK", fg="Green", command=init).pack(side=LEFT, fill=BOTH, expand=True)
Button(bttns, text="Cancel", fg="Red", command=init).pack(side=RIGHT, fill=BOTH, expand=True)

window.mainloop()
