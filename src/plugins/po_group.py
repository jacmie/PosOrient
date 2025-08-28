import wx

class ShiftDialog(wx.Dialog):
    def __init__(self, parent, axis_name, ask_value=True):
        title = f"Shift {axis_name}" if ask_value else f"Reverse {axis_name}"
        super().__init__(parent, title=title)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.ask_value = ask_value
        self.value_ctrl = None

        if ask_value:
            # Label + text field
            hbox1 = wx.BoxSizer(wx.HORIZONTAL)
            label = wx.StaticText(self, label=f"{axis_name}:")
            self.value_ctrl = wx.TextCtrl(self, value="0")
            hbox1.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
            hbox1.Add(self.value_ctrl, 1, wx.ALL | wx.EXPAND, 5)
            main_sizer.Add(hbox1, 0, wx.EXPAND)

        # Checkbox
        self.ignore_active_cb = wx.CheckBox(self, label="Ignore Active")
        main_sizer.Add(self.ignore_active_cb, 0, wx.ALL, 5)

        # OK / Cancel buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(self, wx.ID_OK, label="OK", size=(70, 25))
        cancel_btn = wx.Button(self, wx.ID_CANCEL, label="Cancel", size=(70, 25))
        btn_sizer.AddStretchSpacer(1)
        btn_sizer.Add(ok_btn, 0, wx.ALL, 5)
        btn_sizer.Add(cancel_btn, 0, wx.ALL, 5)
        btn_sizer.AddStretchSpacer(1)
        main_sizer.Add(btn_sizer, 0, wx.EXPAND)

        # Outer sizer for margins around all content
        outer_sizer = wx.BoxSizer(wx.VERTICAL)
        outer_sizer.Add(main_sizer, 1, wx.ALL | wx.EXPAND, 8)

        self.SetSizer(outer_sizer)
        self.Fit()
        self.Centre()

    def get_values(self):
        """Returns (shift_value, ignore_active)."""
        ignore_active = self.ignore_active_cb.IsChecked()
        if self.ask_value:
            try:
                shift_value = float(self.value_ctrl.GetValue().replace(',', '.'))
            except ValueError:
                wx.MessageBox("Invalid number entered.", "Error", wx.OK | wx.ICON_ERROR)
                return None, None
        else:
            shift_value = None
        return shift_value, ignore_active

def update_cell_color(dialog, row, col):
    cell_color = dialog.grid.GetCellBackgroundColour(row, col)

    if cell_color in (wx.Colour(247, 247, 247), wx.Colour(255, 255, 50)):  # default white or yellow
        dialog.grid.SetCellBackgroundColour(row, col, wx.Colour(255, 255, 50))  # yellow
    elif cell_color in (wx.Colour(235, 235, 235), wx.Colour(240, 240, 180)):  # grey or light gray
        dialog.grid.SetCellBackgroundColour(row, col, wx.Colour(240, 240, 180))  # light yellow
    else:
        print("Unrecognised color")

def shift_or_reverse(parent, axis_name, ask_value=True):
    """Show dialog for shift (ask_value=True) or reverse (ask_value=False)."""
    dlg = ShiftDialog(parent, axis_name, ask_value=ask_value)
    if dlg.ShowModal() == wx.ID_OK:
        shift_value, ignore_active = dlg.get_values()
        dlg.Destroy()
        if ask_value:
            return shift_value, ignore_active
        else:
            return ignore_active
    dlg.Destroy()
    return (None, None) if ask_value else None

def handle_column_update(dialog, col_index, operation, ignore_active=False):
    for row in range(dialog.grid.GetNumberRows()):
        if not ignore_active:
            active_value = str(dialog.grid.GetCellValue(row, 0)).strip().lower()
            if active_value not in ("1", "true", "yes", "checked"):
                continue

        try:
            value = float(dialog.grid.GetCellValue(row, col_index).replace(',', '.'))
            new_value = operation(value)
            dialog.grid.SetCellValue(row, col_index, str(new_value))
            update_cell_color(dialog, row, col_index)
        except ValueError:
            dialog.log.AppendText(
                f"Error: Cell value in row {row+1}, col {col_index+1} is not a valid number.\n"
            )

    dialog.grid.Refresh()
    dialog.grid.Update()

def handle_reverse_column(dialog, col_index, ignore_active=False):
    handle_column_update(dialog, col_index, lambda v: -v, ignore_active)

def handle_shift_column(dialog, col_index, shift_value, ignore_active=False):
    handle_column_update(dialog, col_index, lambda v: v + shift_value, ignore_active)

def handle_revers_y(dialog, event):
    ignore_active = shift_or_reverse(dialog, "Y", ask_value=False)
    if ignore_active is not None:
        handle_reverse_column(dialog, 4, ignore_active)

def handle_revers_x(dialog, event):
    ignore_active = shift_or_reverse(dialog, "X", ask_value=False)
    if ignore_active is not None:
        handle_reverse_column(dialog, 3, ignore_active)

def handle_shift_dx(dialog, event):
    shift_value, ignore_active = shift_or_reverse(dialog, "dX", ask_value=True)
    if shift_value is not None:
        handle_shift_column(dialog, 3, shift_value, ignore_active)

def handle_shift_dy(dialog, event):
    shift_value, ignore_active = shift_or_reverse(dialog, "dY", ask_value=True)
    if shift_value is not None:
        handle_shift_column(dialog, 4, shift_value, ignore_active)
