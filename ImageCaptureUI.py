#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

class ImageCaptureUI:

  def hello(self, widget, data=None):
    print "Hello World!"

  def is_checked(self, widget, data=None):
    checked = str(widget.get_active())
    print "Auto Start Enabled!"

  def delete_event(self, widget, event, data=None):
    print "Delete event occured."
    return False

  def destroy(self, widget, data=None):
    gtk.main_quit()

  def __init__(self):
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.connect("delete_event", self.delete_event)
    self.window.connect("destroy", self.destroy)
    self.window.set_title("ImageCapture")
    self.window.set_border_width(10)

    table    = gtk.Table(10, 10, True)
    button   = gtk.Button("Hello World")
    checkbox = gtk.CheckButton(label='Auto Start', use_underline=False)

    self.window.add(table)
    table.attach(button, 0, 1, 0, 1)
    table.attach(checkbox, 0, 1, 1, 2)

    button.connect("clicked", self.hello, None)
    button.connect_object("clicked", gtk.Widget.destroy, self.window)
    checkbox.connect("toggled", self.is_checked, None)
  
    table.show()
    button.show()
    checkbox.show()
    self.window.show()

  def main(self):
    gtk.main()

if __name__ == "__main__":
  hello = ImageCaptureUI()
  hello.main()
