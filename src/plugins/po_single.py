import pcbnew
import wx

def handle_selected_footprint(dialog, event):
    board = pcbnew.GetBoard()
    footprints = board.GetFootprints()
    selected_footprints = [fp for fp in footprints if fp.IsSelected()]

    if not selected_footprints:
        wx.MessageBox("No footprint selected.", "Error", wx.OK | wx.ICON_ERROR)
        return

    if len(selected_footprints) > 1:
        wx.MessageBox("Multiple footprints selected. Please select only one.", "Error", wx.OK | wx.ICON_ERROR)
        return

    selected_ref = selected_footprints[0].GetReference()
    for row in range(dialog.grid.GetNumberRows()):
        cell_value = dialog.grid.GetCellValue(row, 1)
        if cell_value == selected_ref:
            dialog.grid.MakeCellVisible(row, 1)
            dialog.grid.SelectRow(row)
            return
    
    wx.MessageBox(f"Footprint {selected_ref} not found in the list.", "Not Found", wx.OK | wx.ICON_INFORMATION)
