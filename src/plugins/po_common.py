import pcbnew
import wx

def handle_get_footprints_list(dialog, event):
    board = pcbnew.GetBoard()
    design_settings = board.GetDesignSettings()
    drill_origin = design_settings.GetAuxOrigin()
    fp_list = board.GetFootprints()
    
    dialog.resize_rows(len(fp_list))

    for fp_id, fp in enumerate(fp_list, start=0):
        pos = fp.GetPosition()
        orient = fp.GetOrientation()
        
        dialog.grid.SetCellValue(fp_id, 1, fp.GetReference())
        dialog.grid.SetCellValue(fp_id, 2, fp.GetValue())
        dialog.grid.SetCellValue(fp_id, 3, str((pos.x - drill_origin.x)/1e6))
        dialog.grid.SetCellValue(fp_id, 4, str((pos.y - drill_origin.y)/1e6))
        dialog.grid.SetCellValue(fp_id, 5, str(orient.AsDegrees()))
        
    dialog.clear_modifications()
    dialog.activate_or_sort_grid_by_column(1)
    dialog.log.AppendText(f"Updated the List\n")

def handle_orient(dialog, event):
    board = pcbnew.GetBoard()
    
    if board is not None:
        for row in range(dialog.grid.GetNumberRows()):
            active_flag = dialog.grid.GetCellValue(row, 0).strip()
            if not active_flag:
                continue

            ref = dialog.grid.GetCellValue(row, 1)
            fp = board.FindFootprintByReference(ref)

            if fp is not None:
                try:
                    x = 1e6 * float(dialog.grid.GetCellValue(row, 3).replace(',', '.'))
                    y = 1e6 * float(dialog.grid.GetCellValue(row, 4).replace(',', '.'))
                    rot = float(dialog.grid.GetCellValue(row, 5).replace(',', '.'))
                    
                    design_settings = board.GetDesignSettings()
                    drill_origin = design_settings.GetAuxOrigin()
                    pos = fp.GetPosition()
                    pos.x = drill_origin.x + int(x)
                    pos.y = drill_origin.y + int(y)
                    fp.SetPosition(pos)
                    fp.SetOrientationDegrees(rot)
                except ValueError:
                    dialog.log.AppendText("Error: Cell value is not a valid number.")
            else:
                dialog.log.AppendText(f"Footprint {ref} not found on the board!")

        board.BuildListOfNets()
        pcbnew.Refresh()
        dialog.clear_modifications()
        dialog.log.AppendText(f"Set Positions and Orientations\n")
    else:
        dialog.log.AppendText(f"Board not found!!!")

def color_cells(dialog):
    for row in range(dialog.grid.GetNumberRows()):
        active_flag = dialog.grid.GetCellValue(row, 0).strip()
        for col in range(3, dialog.grid.GetNumberCols()):
            cell_color = dialog.grid.GetCellBackgroundColour(row, col)

            if active_flag == "1":  # active row
                if cell_color == wx.Colour(235, 235, 235):  # grey
                    dialog.grid.SetCellBackgroundColour(row, col, wx.Colour(247, 247, 247))  # white
                elif cell_color == wx.Colour(240, 240, 180):  # light yellow
                    dialog.grid.SetCellBackgroundColour(row, col, wx.Colour(255, 255, 50))  # yellow
                else:
                    print(f"Unrecognised color at ({row},{col}): {cell_color}")
            else:  # inactive row
                if cell_color == wx.Colour(247, 247, 247):  # white
                    dialog.grid.SetCellBackgroundColour(row, col, wx.Colour(235, 235, 235))  # grey
                elif cell_color == wx.Colour(255, 255, 50):  # yellow
                    dialog.grid.SetCellBackgroundColour(row, col, wx.Colour(240, 240, 180))  # light yellow
                else:
                    print(f"Unrecognised color at ({row},{col}): {cell_color}")

    dialog.grid.Refresh()
    dialog.grid.Update()