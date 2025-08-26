import os
import pcbnew
import wx
import wx.grid as gridlib

from .po_dialog import PosOrientDialog

class PosOrientPlugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "PosOrient"
        self.category = "Design Automation"
        self.description = "Positioning & Orientation of footprints in the PCB Editor"
        self.pcbnew_icon_support = hasattr(self, "show_toolbar_button")
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'icon.png')
        self.dark_icon_file_name = os.path.join(os.path.dirname(__file__), 'icon.png')
        self.is_running = False

    def Run(self):
        if self.is_running:
            return  # Exit if already running

        self.is_running = True

        dialog = PosOrientDialog(None)
        dialog.Bind(wx.EVT_CLOSE, self.onDialogClose)
        dialog.Show()

    def onDialogClose(self, event):
        self.is_running = False
        dialog = event.GetEventObject()
        dialog.Destroy()

