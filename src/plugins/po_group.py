import pcbnew
import wx

from .po_common import color_cells


class ActionDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Select Action")

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.radio_buttons = []
        actions = [
            "Activate selected",
            "Deactivate selected",
            "Add activated selected",
            "Subtract activated selected",
        ]
        for i, label in enumerate(actions):
            rb = wx.RadioButton(self, label=label, style=wx.RB_GROUP if i == 0 else 0)
            self.radio_buttons.append(rb)
            main_sizer.Add(rb, 0, wx.ALL, 5)

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

    def get_choice(self):
        for i, rb in enumerate(self.radio_buttons):
            if rb.GetValue():
                return i
        return None


def handle_selected_group_footprints(dialog, event):
    board = pcbnew.GetBoard()
    footprints = board.GetFootprints()
    selected_footprints = [fp for fp in footprints if fp.IsSelected()]

    if not selected_footprints:
        wx.MessageBox("No footprint selected.", "Error", wx.OK | wx.ICON_ERROR)
        return

    action_dlg = ActionDialog(dialog)
    if action_dlg.ShowModal() != wx.ID_OK:
        action_dlg.Destroy()
        return

    choice_idx = action_dlg.get_choice()
    action_dlg.Destroy()

    action_map = {
        0: "Activate selected",
        1: "Deactivate selected",
        2: "Add activated selected",
        3: "Subtract activated selected",
    }
    action = action_map.get(choice_idx)

    selected_refs = {fp.GetReference() for fp in selected_footprints}

    if action == "Activate selected":
        # Selected get 1, others get 0
        for row in range(dialog.grid.GetNumberRows()):
            ref = dialog.grid.GetCellValue(row, 1)
            dialog.grid.SetCellValue(row, 0, "1" if ref in selected_refs else "0")

    elif action == "Deactivate selected":
        # Selected get 0, others get 1
        for row in range(dialog.grid.GetNumberRows()):
            ref = dialog.grid.GetCellValue(row, 1)
            dialog.grid.SetCellValue(row, 0, "0" if ref in selected_refs else "1")

    elif action == "Add activated selected":
        for row in range(dialog.grid.GetNumberRows()):
            ref = dialog.grid.GetCellValue(row, 1)
            if ref in selected_refs:
                try:
                    val = int(dialog.grid.GetCellValue(row, 0))
                except ValueError:
                    val = 0
                dialog.grid.SetCellValue(row, 0, str(val + 1))

    elif action == "Subtract activated selected":
        for row in range(dialog.grid.GetNumberRows()):
            ref = dialog.grid.GetCellValue(row, 1)
            if ref in selected_refs:
                try:
                    val = int(dialog.grid.GetCellValue(row, 0))
                except ValueError:
                    val = 0
                dialog.grid.SetCellValue(row, 0, str(max(val - 1, 0)))

    color_cells(dialog)


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
                shift_value = float(self.value_ctrl.GetValue().replace(",", "."))
            except ValueError:
                wx.MessageBox("Invalid number entered.", "Error", wx.OK | wx.ICON_ERROR)
                return None, None
        else:
            shift_value = None
        return shift_value, ignore_active


def update_cell_color(dialog, row, col):
    cell_color = dialog.grid.GetCellBackgroundColour(row, col)

    if cell_color in (
        wx.Colour(247, 247, 247),
        wx.Colour(255, 255, 50),
    ):  # default white or yellow
        dialog.grid.SetCellBackgroundColour(row, col, wx.Colour(255, 255, 50))  # yellow
    elif cell_color in (
        wx.Colour(235, 235, 235),
        wx.Colour(240, 240, 180),
    ):  # grey or light gray
        dialog.grid.SetCellBackgroundColour(
            row, col, wx.Colour(240, 240, 180)
        )  # light yellow
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
            value = float(dialog.grid.GetCellValue(row, col_index).replace(",", "."))
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


def handle_rotate_column(dialog, col_index, rotate_value, ignore_active=False):
    handle_column_update(dialog, col_index, lambda v: v + rotate_value, ignore_active)


def handle_shift_dx(dialog, event):
    shift_value, ignore_active = shift_or_reverse(dialog, "dX", ask_value=True)
    dialog.log.AppendText(f"Shift all dX = {shift_value}\n")
    if shift_value is not None:
        handle_shift_column(dialog, 3, shift_value, ignore_active)


def handle_shift_dy(dialog, event):
    shift_value, ignore_active = shift_or_reverse(dialog, "dY", ask_value=True)
    dialog.log.AppendText(f"Shift all dY = {shift_value}\n")
    if shift_value is not None:
        handle_shift_column(dialog, 4, shift_value, ignore_active)


def handle_revers_x(dialog, event):
    ignore_active = shift_or_reverse(dialog, "X", ask_value=False)
    dialog.log.AppendText(f"Revers all X\n")
    if ignore_active is not None:
        handle_reverse_column(dialog, 3, ignore_active)


def handle_revers_y(dialog, event):
    ignore_active = shift_or_reverse(dialog, "Y", ask_value=False)
    dialog.log.AppendText(f"Revers all Y\n")
    if ignore_active is not None:
        handle_reverse_column(dialog, 4, ignore_active)


def handle_rotate(dialog, event):
    rotate_value, ignore_active = shift_or_reverse(dialog, "dRot", ask_value=True)
    dialog.log.AppendText(f"Rotate all dRot = {rotate_value}\n")
    if rotate_value is not None:
        handle_rotate_column(dialog, 5, rotate_value, ignore_active)
