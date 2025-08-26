import wx

def handle_open(dialog, event):
    with wx.FileDialog(dialog, "Open file", wildcard="(*.cpf)|*.cpf|(*.txt)|*.txt|(*.dat)|*.dat|(All *.*)|*.*",
                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

        if fileDialog.ShowModal() == wx.ID_CANCEL:
            return

        dialog.file_path = fileDialog.GetPath()
        lines = []

        with open(dialog.file_path, 'r') as file:
            data_line_corrupted = False
            for line_number, line in enumerate(file, start=1):
                # Skip comments and empty lines
                if not line.strip() or line.startswith('#'):
                    continue

                # Check if the line has 6 values
                values = line.strip().split()
                if len(values) == 6:
                    lines.append(values)
                else:
                    dialog.log.AppendText(f"Data corrupted in line {line_number}:\n{line.strip()}\n")
                    data_line_corrupted = True

            if data_line_corrupted:
                wx.MessageBox(f"Expected 6 data entries in a single line, divided with spaces!\nWrong number of the data entries!\n\nReading data for these lines ommited!\nSee plugin's log for details.",
                "Data Line Corrupted", wx.OK | wx.ICON_ERROR)

            dialog.status_bar.SetStatusText(f"Work file: {dialog.file_path}", 0)

        # Process the data
        dialog.resize_rows(len(lines))

        for line_id, line in enumerate(lines, start=0):
            active, designator, footprint, x, y, rotation = line
            if active == '1':
                dialog.grid.SetCellValue(line_id, 0, str(1))
            else:
                dialog.grid.SetCellValue(line_id, 0, "")
            dialog.grid.SetCellValue(line_id, 1, designator)
            dialog.grid.SetCellValue(line_id, 2, footprint)
            dialog.grid.SetCellValue(line_id, 3, x)
            dialog.grid.SetCellValue(line_id, 4, y)
            dialog.grid.SetCellValue(line_id, 5, rotation)

            # Set colors
            if active == '1':
                for i in range(3, 6):
                    dialog.grid.SetCellBackgroundColour(line_id, i, wx.Colour(255, 255, 50)) # yellow
            else:
                for i in range(3, 6):
                    dialog.grid.SetCellBackgroundColour(line_id, i, wx.Colour(240, 240, 180)) # light yellow
        
        dialog.grid.Refresh()
        dialog.grid.Update()
        dialog.log.AppendText(f"Open:  {dialog.file_path}\n")

def save(dialog):
    with open(dialog.file_path, 'w', newline='') as file:
        # Write header
        file.write("# Component Placement File\n")
        file.write(f"{'# Active':<10}{'Designator':<20}{'Footprint':<40}{'X[mm]':<15}{'Y[mm]':<15}{'Rotation[deg]':<15}\n")

        designator_too_long = False
        footprint_name_too_long = False
        footprint_name_has_spaces = False

        # Write data
        for row in range(dialog.grid.GetNumberRows()):
            row_data = [dialog.grid.GetCellValue(row, col) for col in range(dialog.grid.GetNumberCols())]
            formatted_row = ""

            for idx, value in enumerate(row_data):
                if idx == 0:
                    formatted_row += f"{value:<10}"
                elif idx == 1:
                    if len(value) > 20:
                        dialog.log.AppendText(f"Too long Designator name:  {value}\n")
                        designator_too_long = True
                    else:
                        formatted_row += f"{value:<20}"
                elif idx == 2:
                    if " " in value:
                        value = value.replace(" ", "_")
                        dialog.log.AppendText(f"Footprint name spaces converted to underscores:  {value}\n")                            
                        footprint_name_has_spaces = True
                    if len(value) > 40:
                        dialog.log.AppendText(f"Too long Footprint name:  {value}\n")
                        footprint_name_too_long = True
                    formatted_row += f"{value:<40}"
                else:
                    try:
                        number_value = float(value.replace(',', '.'))  # Convert to float
                        formatted_row += f"{number_value:<15.4f}"
                    except ValueError:
                        # If conversion fails (e.g., if the cell is empty or non-numeric), add the raw value
                        formatted_row += f"{value:<15}"
            
            file.write(f"{formatted_row}\n")

        if designator_too_long:
            wx.MessageBox(f"Too long Designator name!\n\nData for these Designators isn't saved!\nSee plugin's log for details.",
            "Too Long Designator", wx.OK | wx.ICON_ERROR)
        if footprint_name_too_long:
            wx.MessageBox(f"Too long Footprint name.\n\nThay are for information purposes only and don't critically affect data.\nLonger Footprint names will be truncated to 40 characters.\nSee plugin's log for details.",
            "Too Long Footprint name", wx.OK | wx.ICON_WARNING)
        if footprint_name_has_spaces:
            wx.MessageBox(f"Footprint names contain spaces.\n\nThay are for information purposes only and don't critically affect data.\nSpaces are converted to underscores.\nSee plugin's log for details.",
            "Space to Underscore Conversion", wx.OK | wx.ICON_WARNING)

        dialog.status_bar.SetStatusText(f"Work file: {dialog.file_path}", 0)

def handle_save_as(dialog, event):
    with wx.FileDialog(dialog, "Save file", wildcard="(*.cpf)|*.cpf|(*.txt)|*.txt|(*.dat)|*.dat|(All *.*)|*.*",
                       style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

        if fileDialog.ShowModal() == wx.ID_CANCEL:
            return

        dialog.file_path = fileDialog.GetPath()

        # Automatically add extension if missing
        valid_extensions = [".cpf", ".txt", ".dat"]
        if not any(dialog.file_path.lower().endswith(ext) for ext in valid_extensions):
            dialog.file_path += valid_extensions[0]  # Appending the first valid extension

        save(dialog)
        dialog.log.AppendText(f"Save As:  {dialog.file_path}\n")

def handle_save(dialog, event):
    if not dialog.file_path:
        dialog.on_save_as(event)
    else:
        save(dialog)
        dialog.log.AppendText(f"Save:  {dialog.file_path}\n")