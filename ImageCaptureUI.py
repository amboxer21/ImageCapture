#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

class ImageCaptureUI:

  def clicked(self, widget, data=None):
    print "Clicked!"

  def is_checked(self, widget, data=None):
    if widget.get_active():
      print str(data) + " enabled!"
      return str(data)

  def button_clicked(self, widget, data=None):
    print str(data) + " clicked!"

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
    self.window.set_default_size(150,250)

    table            = gtk.Table(5, 5, True)
    button           = gtk.Button("Start")
    buttonClearLogin = gtk.Button("Clear Login")
    checkboxCam      = gtk.CheckButton(label='Enable Cam', use_underline=False)
    checkboxLogin    = gtk.CheckButton(label='Auto Login', use_underline=False)
    checkboxSuccess  = gtk.CheckButton(label='Allow Successful', use_underline=False)

    self.window.add(table)
    table.attach(button, 4, 5, 4, 5)
    table.attach(checkboxCam, 0, 1, 4, 5)
    table.attach(checkboxLogin, 1, 2, 4, 5)
    table.attach(checkboxSuccess, 2, 3, 4, 5)
    table.attach(buttonClearLogin, 4, 5, 3, 4)

    button.connect("clicked", self.button_clicked, "start")
    #button.connect_object("clicked", gtk.Widget.destroy, self.window)
    checkboxCam.connect("toggled", self.is_checked, "enable_cam")
    checkboxLogin.connect("toggled", self.is_checked, "auto_login")
    checkboxSuccess.connect("toggled", self.is_checked, "allow_success")
    buttonClearLogin.connect("clicked", self.button_clicked, "clear_login")
  
    table.show()
    button.show()
    checkboxCam.show()
    checkboxLogin.show()
    checkboxSuccess.show()
    buttonClearLogin.show()
    self.window.show()

  def main(self):
    gtk.main()

if __name__ == "__main__":
  hello = ImageCaptureUI()
  hello.main()
