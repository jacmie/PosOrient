import os
import pcbnew
import wx
import wx.grid as gridlib

class PosOrientDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title="Position & Orientation", size=(600, 400), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        self.file_path = ""

        self.panel = wx.Panel(self)

        self.table_label = wx.StaticText(self.panel, label="Footprints list:")
        self.log_label = wx.StaticText(self.panel, label="Log:")
        self.log = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 200))

        self.grid = gridlib.Grid(self.panel, size=(-1, 400))
        self.num_cols = 6
        self.num_rows = 7
        self.grid.CreateGrid(self.num_rows, self.num_cols)
        self.grid.DisableDragRowSize()
        self.Bind(gridlib.EVT_GRID_CELL_CHANGED, self.on_cell_changed)
        #self.grid.Bind(gridlib.EVT_GRID_LABEL_LEFT_CLICK, self.on_column_header_click)
        self.Bind(gridlib.EVT_GRID_LABEL_LEFT_CLICK, self.on_column_header_click)

        # Set headers labels
        self.grid.SetColLabelSize(25)  
        self.grid.SetRowLabelSize(50)

        self.grid.SetColLabelValue(0, f"Active")
        self.grid.SetColLabelValue(1, f"Designator")
        self.grid.SetColLabelValue(2, f"Footprint")
        self.grid.SetColLabelValue(3, f"X [mm]")
        self.grid.SetColLabelValue(4, f"Y [mm]")
        self.grid.SetColLabelValue(5, f"Rot [deg]")

        for i in range(self.num_rows):
            self.grid.SetRowLabelValue(i, f"{i+1}")

        attr = gridlib.GridCellAttr()
        attr.SetAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self.grid.SetColAttr(0, attr)

        # Set chosen colums width
        self.grid.SetColSize(0, 50)
        self.grid.SetColSize(2, 200)
        
        # Use GridCellFloatRenderer for the last three columns
        for i in range(3, 6):
            self.grid.SetColFormatFloat(i, width=-1, precision=4)

        # Set the checkbox column format
        self.grid.SetColFormatBool(0)
        for i in range(self.num_rows):
            self.grid.SetCellValue(i, 0, str(1))

        for i in range(self.num_rows):
            for j in range(1, 3):
                # Make the first two columns read-only
                self.grid.SetReadOnly(i, j)

                # Set background color to light gray for the first three columns
                self.grid.SetCellBackgroundColour(i, j, wx.Colour(235, 235, 235))

                # Set data
                data = f"({i+1}, {j+1})"
                self.grid.SetCellValue(i, j, data)
        
        # Create buttons
        self.list_button = wx.Button(self.panel, label="List", size=(80, 25))
        self.list_button.SetToolTip(wx.ToolTip("Click to update list of the footprints and data from the KiCad PCB Editor"))
        self.list_button.Bind(wx.EVT_BUTTON, self.on_get_footprints_list)
        
        self.open_button = wx.Button(self.panel, label="Open", size=(80, 25))
        self.open_button.SetToolTip(wx.ToolTip("Open data file with footprints position and orientation"))
        self.open_button.Bind(wx.EVT_BUTTON, self.on_open)

        self.save_as_button = wx.Button(self.panel, label="Save As", size=(80, 25))
        self.save_as_button.SetToolTip(wx.ToolTip("Save As data file with footprints position and orientation"))
        self.save_as_button.Bind(wx.EVT_BUTTON, self.on_save_as)

        self.save_button = wx.Button(self.panel, label="Save", size=(80, 25))
        self.save_button.SetToolTip(wx.ToolTip("Save data file with footprints position and orientation"))
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save)

        self.orient_button = wx.Button(self.panel, label="Orient", size=(80, 25))
        self.orient_button.SetToolTip(wx.ToolTip("Click to set position and orientation of the footprints in the KiCad PCB Editor"))
        self.orient_button.Bind(wx.EVT_BUTTON, self.on_orient)

        self.cancel_button = wx.Button(self.panel, label="Close", size=(80, 25))
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)

        # Shortcuts for buttons supported only on Windows?
        accel_tbl = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, ord('l'), self.list_button.GetId()),
            (wx.ACCEL_CTRL, ord('o'), self.open_button.GetId()),
            (wx.ACCEL_CTRL, ord('s'), self.save_button.GetId()),
            (wx.ACCEL_CTRL, ord('p'), self.orient_button.GetId())
        ])
        self.panel.SetAcceleratorTable(accel_tbl)

        # Buttons panel        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.list_button, 0, wx.ALL, 5)
        button_sizer.Add(self.open_button, 0, wx.ALL, 5)
        button_sizer.Add(self.save_as_button, 0, wx.ALL, 5)
        button_sizer.Add(self.save_button, 0, wx.ALL, 5)
        button_sizer.Add(self.orient_button, 0, wx.ALL, 5)
        button_sizer.Add(self.cancel_button, 0, wx.ALL, 5)

        # Status bar
        self.status_bar = wx.StatusBar(self.panel)
        self.status_bar.SetStatusText("Click \'List\' to update footprints list with parameters", 0)
        
        # Add all widgets to the layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.table_label, 0, wx.ALL | wx.EXPAND, 2)
        sizer.Add(self.grid, 1, wx.ALL | wx.EXPAND, 2)
        sizer.Add(self.log_label, 0, wx.ALL | wx.EXPAND, 2)
        sizer.Add(self.log, proportion=0, flag=wx.EXPAND | wx.ALL, border=2)
        sizer.Add(button_sizer, 0, wx.ALL | wx.ALIGN_CENTER, 2)
        sizer.Add(self.status_bar, 0, wx.ALL | wx.EXPAND, 2)
        
        self.panel.SetSizer(sizer)
        sizer.Fit(self)

        # Simulate the button_list event and get the list
        event = wx.CommandEvent(wx.EVT_BUTTON.typeId, self.list_button.GetId())
        wx.PostEvent(self.list_button, event)

    def resize_rows(self, new_rows):
        current_rows = self.grid.GetNumberRows()

        if new_rows > current_rows:
            self.grid.AppendRows(new_rows - current_rows)
        elif new_rows < current_rows:
            self.grid.DeleteRows(new_rows, current_rows - new_rows)

        for i in range(new_rows):
            self.grid.SetCellValue(i, 0, str(1))
            for j in range(1, 3):
                # Make the columns read-only
                self.grid.SetReadOnly(i, j)
                # Set background color to light gray
                self.grid.SetCellBackgroundColour(i, j, wx.Colour(235, 235, 235))

    def on_cell_changed(self, event):
        row = event.GetRow()
        col = event.GetCol()

        if(col == 0):
            if self.grid.GetCellValue(row, col) == '1':  # Marked Checked
                for i in range(3, 6):
                    cell_color = self.grid.GetCellBackgroundColour(row, i)
                    print(f"{cell_color}")

                    if cell_color == wx.Colour(235, 235, 235):  # grey
                        self.grid.SetCellBackgroundColour(row, i, wx.Colour(247, 247, 247)) # default white
                    elif cell_color == wx.Colour(240, 240, 180):  # light yellow
                        self.grid.SetCellBackgroundColour(row, i, wx.Colour(255, 255, 50)) # yellow
                    else:
                        print("Urecognised color")
            else: # Marked Unchecked
                for i in range(3, 6):
                    cell_color = self.grid.GetCellBackgroundColour(row, i)
                    print(f"{cell_color}")

                    if cell_color == wx.Colour(247, 247, 247):  # default white
                        self.grid.SetCellBackgroundColour(row, i, wx.Colour(235, 235, 235)) # gray
                    elif cell_color == wx.Colour(255, 255, 50):  # yellow
                        self.grid.SetCellBackgroundColour(row, i, wx.Colour(240, 240, 180)) # light yellow
                    else:
                        print("Urecognised color")

        if(col >= 3):
            if(col == 3):
                self.log.AppendText(f"{row+1}: {self.grid.GetCellValue(row, 1)} X =  {self.grid.GetCellValue(row, col)}\n")
            elif(col == 4):
                self.log.AppendText(f"{row+1}: {self.grid.GetCellValue(row, 1)} Y =  {self.grid.GetCellValue(row, col)}\n")
            elif(col == 5):
                self.log.AppendText(f"{row+1}: {self.grid.GetCellValue(row, 1)} Rot =  {self.grid.GetCellValue(row, col)}\n")

            cell_color = self.grid.GetCellBackgroundColour(row, col)
            #print(f"{cell_color}")
            
            if cell_color == wx.Colour(247, 247, 247) or cell_color == wx.Colour(255, 255, 50):  # default white or yellow
                self.grid.SetCellBackgroundColour(row, col, wx.Colour(255, 255, 50)) # yellow
            elif cell_color == wx.Colour(235, 235, 235) or cell_color == wx.Colour(240, 240, 180):  # grey or light gray
                self.grid.SetCellBackgroundColour(row, col, wx.Colour(240, 240, 180)) # light yellow
            else:
                print("Urecognised color")

        self.grid.Refresh()
        self.grid.Update()

    def clear_modifications(self):
        for row in range(self.grid.GetNumberRows()):
            if self.grid.GetCellValue(row, 0) == '1':  # Marked Checked
                for col in range(3, 6):
                    self.grid.SetCellBackgroundColour(row, col, wx.Colour(247, 247, 247)) # default white
            else: # Marked Unchecked
                for col in range(3, 6):
                    self.grid.SetCellBackgroundColour(row, col, wx.Colour(235, 235, 235)) # gray
            
        self.grid.Refresh()
        self.grid.Update()

    def sort_grid_by_column(self, column_idx):
        # Extract data from the grid into a list of tuples
        data = []
        for row in range(self.grid.GetNumberRows()):
            row_data = []
            for col in range(self.grid.GetNumberCols()):
                row_data.append(self.grid.GetCellValue(row, col))
            data.append(tuple(row_data))
    
        # Sort the list of tuples by the specified column
        if column_idx in [3, 4, 5]:     # columns with pure numbers
            sorted_data = sorted(data, key=lambda x: float(x[column_idx]))
        else:                           # columns with strings
            sorted_data = sorted(data, key=lambda x: x[column_idx])
    
        # Clear the existing grid data
        self.grid.ClearGrid()
    
        # Repopulate the grid with sorted data
        for row_idx, row_data in enumerate(sorted_data):
            for col_idx, value in enumerate(row_data):
                self.grid.SetCellValue(row_idx, col_idx, value)
    
    def on_column_header_click(self, event):
        column_idx = event.GetCol()
        self.sort_grid_by_column(column_idx)
        event.Skip() # Skip the event to allow the grid to process it further

    def on_get_footprints_list(self, event):
        board = pcbnew.GetBoard()
        fp_list = board.GetFootprints()
        
        self.resize_rows(len(fp_list))

        for fp_id, fp in enumerate(fp_list, start=0):
            pos = fp.GetPosition()
            orient = fp.GetOrientation()
            
            self.grid.SetCellValue(fp_id, 1, fp.GetReference())
            self.grid.SetCellValue(fp_id, 2, fp.GetValue())
            self.grid.SetCellValue(fp_id, 3, str(pos.x/1e6))
            self.grid.SetCellValue(fp_id, 4, str(pos.y/1e6))
            self.grid.SetCellValue(fp_id, 5, str(orient.AsDegrees()))
            
        self.clear_modifications()
        self.sort_grid_by_column(1)
        self.log.AppendText(f"Update the List\n")
        
    def on_open(self, event):
        with wx.FileDialog(self, "Open file", wildcard="(*.cpf)|*.cpf|(*.txt)|*.txt|(*.dat)|*.dat|(All *.*)|*.*",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            self.file_path = fileDialog.GetPath()
            lines = []

            with open(self.file_path, 'r') as file:
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
                        self.log.AppendText(f"Data corrupted in line {line_number}:\n{line.strip()}\n")
                        data_line_corrupted = True

                if data_line_corrupted:
                    wx.MessageBox(f"Expected 6 data entries in a single line, divided with spaces!\nWrong number of the data entries!\n\nReading data for these lines ommited!\nSee plugin's log for details.",
                    "Data Line Corrupted", wx.OK | wx.ICON_ERROR)

                self.status_bar.SetStatusText(f"Work file: {self.file_path}", 0)

            # Process the data
            self.resize_rows(len(lines))

            for line_id, line in enumerate(lines, start=0):
                active, designator, footprint, x, y, rotation = line
                if active == '1':
                    self.grid.SetCellValue(line_id, 0, str(1))
                else:
                    self.grid.SetCellValue(line_id, 0, "")
                self.grid.SetCellValue(line_id, 1, designator)
                self.grid.SetCellValue(line_id, 2, footprint)
                self.grid.SetCellValue(line_id, 3, x)
                self.grid.SetCellValue(line_id, 4, y)
                self.grid.SetCellValue(line_id, 5, rotation)

                # Set colors
                if active == '1':
                    for i in range(3, 6):
                        self.grid.SetCellBackgroundColour(line_id, i, wx.Colour(255, 255, 50)) # yellow
                else:
                    for i in range(3, 6):
                        self.grid.SetCellBackgroundColour(line_id, i, wx.Colour(240, 240, 180)) # light yellow
            
            self.grid.Refresh()
            self.grid.Update()
            self.log.AppendText(f"Open:  {self.file_path}\n")

    def save(self):
        with open(self.file_path, 'w', newline='') as file:
            # Write header
            file.write("# Component Placement File\n")
            file.write(f"{'# Active':<10}{'Designator':<20}{'Footprint':<40}{'X[mm]':<15}{'Y[mm]':<15}{'Rotation[deg]':<15}\n")

            designator_too_long = False
            footprint_name_too_long = False
            footprint_name_has_spaces = False

            # Write data
            for row in range(self.grid.GetNumberRows()):
                row_data = [self.grid.GetCellValue(row, col) for col in range(self.grid.GetNumberCols())]
                formatted_row = ""

                for idx, value in enumerate(row_data):
                    if idx == 0:
                        formatted_row += f"{value:<10}"
                    elif idx == 1:
                        if len(value) > 20:
                            self.log.AppendText(f"Too long Designator name:  {value}\n")
                            designator_too_long = True
                        else:
                            formatted_row += f"{value:<20}"
                    elif idx == 2:
                        if " " in value:
                            value = value.replace(" ", "_")
                            self.log.AppendText(f"Footprint name spaces converted to underscores:  {value}\n")                            
                            footprint_name_has_spaces = True
                        if len(value) > 40:
                            self.log.AppendText(f"Too long Footprint name:  {value}\n")
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

            self.status_bar.SetStatusText(f"Work file: {self.file_path}", 0)

    def on_save_as(self, event):
        with wx.FileDialog(self, "Save file", wildcard="(*.cpf)|*.cpf|(*.txt)|*.txt|(*.dat)|*.dat|(All *.*)|*.*",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            self.file_path = fileDialog.GetPath()

            # Automatically add extension if missing
            valid_extensions = [".cpf", ".txt", ".dat"]
            if not any(self.file_path.lower().endswith(ext) for ext in valid_extensions):
                self.file_path += valid_extensions[0]  # Appending the first valid extension
            
            self.save()
            self.log.AppendText(f"Save As:  {self.file_path}\n")
    
    def on_save(self, event):
        if not self.file_path:
            self.on_save_as(event)
        else:
            self.save()
            self.log.AppendText(f"Save:  {self.file_path}\n")
        
    def on_orient(self, event):
        board = pcbnew.GetBoard()
        
        if board is not None:
            for row in range(self.grid.GetNumberRows()):
                ref = self.grid.GetCellValue(row, 1)
                fp = board.FindFootprintByReference(ref)

                if fp is not None:
                    try:
                        x = 1e6 * float(self.grid.GetCellValue(row, 3).replace(',', '.'))
                        y = 1e6 * float(self.grid.GetCellValue(row, 4).replace(',', '.'))
                        rot = float(self.grid.GetCellValue(row, 5).replace(',', '.'))
                        
                        pos = fp.GetPosition()
                        pos.x = int(x)
                        pos.y = int(y)
                        fp.SetPosition(pos)
                        fp.SetOrientationDegrees(rot)
                    except ValueError:
                        self.log.AppendText("Error: Cell value is not a valid number.")
                else:
                    self.log.AppendText(f"Footprint {ref} not found on the board!")

            board.BuildListOfNets()
            pcbnew.Refresh()
            self.clear_modifications()
            self.log.AppendText(f"Set Positions and Orientations\n")
        else:
            self.log.AppendText(f"Board not found!!!")

    def on_cancel(self, event):
        self.Close(wx.ID_CANCEL)

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

# Register the plugin
PosOrientPlugin().register()
