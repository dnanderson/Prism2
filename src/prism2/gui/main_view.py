import customtkinter as ctk

class MainView(ctk.CTkFrame):
    def __init__(self, parent, view_model):
        super().__init__(parent)
        self.view_model = view_model

        self.grid_columnconfigure(0, weight=0)  # Column for controls
        self.grid_columnconfigure(1, weight=1)  # Column for history/details
        self.grid_rowconfigure(0, weight=1)      # Main content row
        self.grid_rowconfigure(1, weight=0)      # Breakdown row (fixed height)


        # --- Create a container for the left-side controls ---
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=0, column=0, rowspan=2, padx=0, pady=0, sticky="nsew")
        self.controls_frame.grid_columnconfigure(0, weight=1)
        self.controls_frame.grid_rowconfigure(1, weight=0) # Let the SPI frame have fixed height

        # --- Create Device Connection Frame ---
        self.device_frame = ctk.CTkFrame(self.controls_frame)
        self.device_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.device_frame.grid_columnconfigure(1, weight=1)

        self.device_label = ctk.CTkLabel(self.device_frame, text="NI-845x Device")
        self.device_label.grid(row=0, column=0, padx=10, pady=10)

        self.device_combobox = ctk.CTkComboBox(
            self.device_frame,
            variable=self.view_model.selected_device,
            values=self.view_model.device_list.get(),
            state="readonly"
        )
        self.device_combobox.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.refresh_button = ctk.CTkButton(
            self.device_frame,
            text="Refresh",
            command=self.view_model.refresh_devices
        )
        self.refresh_button.grid(row=0, column=2, padx=10, pady=10)

        self.connect_button = ctk.CTkButton(
            self.device_frame,
            text="Connect",
            command=self.view_model.connect_device
        )
        self.connect_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.disconnect_button = ctk.CTkButton(
            self.device_frame,
            text="Disconnect",
            command=self.view_model.disconnect_device
        )
        self.disconnect_button.grid(row=1, column=2, padx=10, pady=10)

        # --- Bindings and Traces ---
        # Update the combobox when the device list changes
        self.view_model.device_list.trace_add("write", self._update_device_combobox)
        # Update button states when connection status changes
        self.view_model.is_connected.trace_add("write", self._update_widget_states)

        # Set initial states
        self._update_widget_states()

        # --- Create SPI Command Frame ---
        self.spi_frame = ctk.CTkFrame(self.controls_frame)
        self.spi_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.spi_frame.grid_columnconfigure(0, weight=1)

        self.spi_label = ctk.CTkLabel(self.spi_frame, text="SPI Command")
        self.spi_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # Predefined commands
        self.predefined_commands = ["Read Status: 0100", "Write Enable: 06", "Chip Erase: C7"]
        self.predefined_cmd_var = ctk.StringVar(value=self.predefined_commands[0])
        self.predefined_cmd_menu = ctk.CTkOptionMenu(
            self.spi_frame,
            variable=self.predefined_cmd_var,
            values=self.predefined_commands,
            command=self._on_predefined_cmd_select
        )
        self.predefined_cmd_menu.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # Custom command entry
        self.custom_cmd_entry = ctk.CTkEntry(
            self.spi_frame,
            placeholder_text="Enter custom command (e.g., DEADBEEF)"
        )
        self.custom_cmd_entry.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        # Send button
        self.send_button = ctk.CTkButton(
            self.spi_frame,
            text="Send Command",
            command=self._send_command
        )
        self.send_button.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        # --- Create Command History Frame ---
        self.history_frame = ctk.CTkScrollableFrame(self, label_text="Command History")
        self.history_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # --- Create Breakdown View Frame ---
        self.breakdown_textbox = ctk.CTkTextbox(
            self,
            height=150,
            font=("monospace", 12),
            state="disabled" # Start as disabled, will be enabled to set text
        )
        self.breakdown_textbox.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # --- Bindings and Traces for History & Breakdown ---
        self.view_model.command_history.trace_add("write", self._render_command_history)
        self.view_model.breakdown_text.trace_add("write", self._update_breakdown_view)


    def _on_predefined_cmd_select(self, selected_command):
        """Callback when a predefined command is selected."""
        # Extracts the hex part of the command string
        hex_value = selected_command.split(": ")[-1]
        self.custom_cmd_entry.delete(0, "end")
        self.custom_cmd_entry.insert(0, hex_value)

    def _send_command(self):
        """Wrapper to send the command from the entry field."""
        command_to_send = self.custom_cmd_entry.get()
        if command_to_send:
            self.view_model.send_spi_command(command_to_send)
        else:
            print("Custom command field is empty.")

    def _update_device_combobox(self, *args):
        """Callback to update the device combobox."""
        devices = self.view_model.device_list.get()
        self.device_combobox.configure(values=devices)
        if not devices:
            self.device_combobox.set("")

    def _update_widget_states(self, *args):
        """Callback to enable/disable widgets based on connection state."""
        is_connected = self.view_model.is_connected.get()

        # Device Frame widgets
        if is_connected:
            self.connect_button.configure(state="disabled")
            self.disconnect_button.configure(state="normal")
            self.device_combobox.configure(state="disabled")
            self.refresh_button.configure(state="disabled")
        else:
            self.connect_button.configure(state="normal")
            self.disconnect_button.configure(state="disabled")
            self.device_combobox.configure(state="readonly")
            self.refresh_button.configure(state="normal")

        # SPI Frame widgets
        spi_state = "normal" if is_connected else "disabled"
        self.predefined_cmd_menu.configure(state=spi_state)
        self.custom_cmd_entry.configure(state=spi_state)
        self.send_button.configure(state=spi_state)

    def _render_command_history(self, *args):
        """Clears and rebuilds the command history view."""
        # Clear existing widgets
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        history = self.view_model.command_history.get()

        for i, item in enumerate(history):
            cmd_str = f"CMD: {item['command']}"
            resp_str = f"RSP: {item['response']}"

            entry_text = f"{i+1:03d} | {cmd_str.ljust(25)} | {resp_str}"

            button = ctk.CTkButton(
                self.history_frame,
                text=entry_text,
                font=("monospace", 12),
                anchor="w",
                command=lambda i=item: self.view_model.select_history_item(i)
            )
            button.pack(fill="x", padx=5, pady=2)

    def _update_breakdown_view(self, *args):
        """Updates the breakdown textbox with new content."""
        self.breakdown_textbox.configure(state="normal")
        self.breakdown_textbox.delete("1.0", "end")
        self.breakdown_textbox.insert("1.0", self.view_model.breakdown_text.get())
        self.breakdown_textbox.configure(state="disabled")
