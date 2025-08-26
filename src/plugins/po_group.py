import wx

def handle_revers_y(dialog, event):
    for row in range(dialog.grid.GetNumberRows()):
        try:
            y = float(dialog.grid.GetCellValue(row, 4).replace(',', '.'))
            dialog.grid.SetCellValue(row, 4, str(-y))
        
            cell_color = dialog.grid.GetCellBackgroundColour(row, 4)

            if cell_color == wx.Colour(247, 247, 247) or cell_color == wx.Colour(255, 255, 50):  # default white or yellow
                dialog.grid.SetCellBackgroundColour(row, 4, wx.Colour(255, 255, 50)) # yellow
            elif cell_color == wx.Colour(235, 235, 235) or cell_color == wx.Colour(240, 240, 180):  # grey or light gray
                dialog.grid.SetCellBackgroundColour(row, 4, wx.Colour(240, 240, 180)) # light yellow
            else:
                print("Urecognised color")
        except ValueError:
            dialog.log.AppendText("Error: Cell value is not a valid number.")

    dialog.grid.Refresh()
    dialog.grid.Update()