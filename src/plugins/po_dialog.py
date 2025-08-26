import pcbnew
import wx
import wx.grid as gridlib

from .po_common import handle_orient, handle_get_footprints_list
from .po_file import handle_open, handle_save_as, handle_save
from .po_single import handle_selected_footprint
from .po_group import handle_revers_y

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
        
        # Set the text colour to black
        self.grid.SetDefaultCellTextColour(wx.Colour(20, 20, 20))

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
        self.list_button = wx.Button(self.panel, label="List", size=(70, 25))
        self.list_button.SetToolTip(wx.ToolTip("Click to update list of the footprints and data from the KiCad PCB Editor"))
        self.list_button.Bind(wx.EVT_BUTTON, self.on_get_footprints_list)

        self.selected_button = wx.Button(self.panel, label="Selected", size=(70, 25))
        self.selected_button.SetToolTip(wx.ToolTip("Go on the list to the selected footprint"))
        self.selected_button.Bind(wx.EVT_BUTTON, self.on_selected_footprint)
        
        self.revers_button = wx.Button(self.panel, label="Revers Y", size=(70, 25))
        self.revers_button.SetToolTip(wx.ToolTip("Revers Y position of a footprint"))
        self.revers_button.Bind(wx.EVT_BUTTON, self.on_revers_y)

        self.open_button = wx.Button(self.panel, label="Open", size=(70, 25))
        self.open_button.SetToolTip(wx.ToolTip("Open data file with footprints position and orientation"))
        self.open_button.Bind(wx.EVT_BUTTON, self.on_open)

        self.save_as_button = wx.Button(self.panel, label="Save As", size=(70, 25))
        self.save_as_button.SetToolTip(wx.ToolTip("Save As data file with footprints position and orientation"))
        self.save_as_button.Bind(wx.EVT_BUTTON, self.on_save_as)

        self.save_button = wx.Button(self.panel, label="Save", size=(70, 25))
        self.save_button.SetToolTip(wx.ToolTip("Save data file with footprints position and orientation"))
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save)

        self.orient_button = wx.Button(self.panel, label="Orient", size=(70, 25))
        self.orient_button.SetToolTip(wx.ToolTip("Click to set position and orientation of the footprints in the KiCad PCB Editor"))
        self.orient_button.Bind(wx.EVT_BUTTON, self.on_orient)

        self.cancel_button = wx.Button(self.panel, label="Close", size=(70, 25))
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)

        # Buttons panel        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.list_button, 0, wx.ALL, 4)
        button_sizer.Add(self.selected_button, 0, wx.ALL, 4)
        button_sizer.Add(self.revers_button, 0, wx.ALL, 4)
        button_sizer.Add(self.open_button, 0, wx.ALL, 4)
        button_sizer.Add(self.save_as_button, 0, wx.ALL, 4)
        button_sizer.Add(self.save_button, 0, wx.ALL, 4)
        button_sizer.Add(self.orient_button, 0, wx.ALL, 4)
        button_sizer.Add(self.cancel_button, 0, wx.ALL, 4)

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

        board = pcbnew.GetBoard()
        design_settings = board.GetDesignSettings()
        drill_origin = design_settings.GetAuxOrigin()
        drill_x_mm = drill_origin.x / 1e6
        drill_y_mm = drill_origin.y / 1e6
        self.log.AppendText(f"Footprints position reference is the Drill Origin ({drill_x_mm:.4f}, {drill_y_mm:.4f}) mm\n")

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
        handle_get_footprints_list(self, event)
    
    def on_selected_footprint(self, event):
        handle_selected_footprint(self, event)

    def on_revers_y(self, event):
        handle_revers_y(self, event)

    def on_open(self, event):
        handle_open(self, event)
    
    def on_save_as(self, event):
        handle_save_as(self, event)
    
    def on_save(self, event):
        handle_save(self, event)
        
    def on_orient(self, event):
        handle_orient(self, event)

    def on_cancel(self, event):
        self.Close(wx.ID_CANCEL)
