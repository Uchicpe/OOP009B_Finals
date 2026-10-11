import sys
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QLabel, QLineEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QComboBox, QSpinBox, QMessageBox, QGridLayout, 
    QFrame, QTextEdit
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush

# --- DYNAMIC VECTOR VEHICLE COMPONENT ---
class ParkingSlotWidget(QWidget):
    def __init__(self, is_occupied, spot_label, parent=None):
        super().__init__(parent)
        self.is_occupied = is_occupied
        self.spot_label = spot_label
        self.setMinimumSize(80, 110)
        
    def set_occupied(self, state):
        self.is_occupied = state
        self.update() # Triggers paint repaint loop

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Color coding logic matching dashboard rules
        color = QColor("#e74c3c") if self.is_occupied else QColor("#2ecc71")

        ## UCHI'S EDIT: REMODEL OF VEHICLE
        pen = QPen(color, 2)
        brush = QBrush()
        
        # Body Outline
        painter.setPen(pen)
        painter.drawRoundedRect(26, 15, 42, 69, 30, 12)

        # Trunk Outline
        painter.setPen(pen)
        painter.drawRoundedRect(25, 70, 44, 20, 10, 10)

        # Hood Outline
        painter.setPen(pen)
        painter.drawRoundedRect(25, 5, 44, 30, 15, 15)

        # Side Rear Mirror (Left) Outline
        painter.setPen(pen)
        painter.drawLine(QPoint(20, 32), QPoint(25, 28))

        # Side Rear Mirror (Right) Outline
        painter.setPen(pen)
        painter.drawLine(QPoint(74, 32), QPoint(68, 28))

        # "Inner" Roof Outline
        painter.setPen(pen)
        brush.setColor(QColor("#2d2d30"))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)
        painter.drawRoundedRect(32, 27, 30, 48, 30, 5)
        
        # Bottom text indicator for space coordinate
        painter.setPen(QColor("#ffffff"))
        painter.setFont(painter.font())
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, self.spot_label)


# --- MAIN INTEGRATED APP ARCHITECTURE ---
class ParkingSystemApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Automated Parking Management System")
        self.resize(1000, 680)
        self.setStyleSheet("background-color: #2d2d30;")

        # Core Backend State: Stores live data for 12 core grid spots (Matching original 2x6 design image)
        self.parking_slots = {f"Spot {i}": None for i in range(1, 13)}
        
        # Tracks current dynamic visual visibility filters ("All", "Available", "Occupied")
        self.current_filter = "All"
        
        # Storage dictionary mapping spot labels directly to target container blocks and vector objects
        self.slot_ui_elements = {}

        # Layout Root Core Configuration
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)

        # Tab Layout Interface Setup
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #555; background: #2d2d30; }
            QTabBar::tab { background: #3e3e42; color: #aaa; padding: 8px 16px; border-top-left-radius: 4px; border-top-right-radius: 4px; margin-right: 2px;}
            QTabBar::tab:selected { background: #555; color: white; font-weight: bold; }
        """)
        self.main_layout.addWidget(self.tabs)

        # Build Sub-Sections Panels
        self.init_dashboard_tab()
        self.init_time_tracking_tab()
        self.init_ticket_management_tab()

        # Initial UI synchronization state check
        self.update_ui_state()

    # --- TAB 1: MODERNISED DASHBOARD VIEWPORT WITH LIVE GRIDS ---
    def init_dashboard_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)

        # 1. TOP STATS OVERVIEW BANNER BANNER BLOCK
        banner = QFrame()
        banner.setStyleSheet("background-color: #3e3e42; border-radius: 4px;")
        banner.setFixedHeight(75)
        banner_layout = QHBoxLayout(banner)
        banner_layout.setContentsMargins(15, 0, 15, 0)
        
        p_logo = QLabel("P")
        p_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        p_logo.setFixedSize(45, 45)
        p_logo.setStyleSheet("background-color: #1e1e1e; color: #f1c40f; font-size: 22px; font-weight: bold; border-radius: 4px;")
        banner_layout.addWidget(p_logo)
        
        title = QLabel("TIP QC Parking Area")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold; background: transparent;")
        banner_layout.addWidget(title)
        banner_layout.addStretch()
        
        # Metric Track Panels
        self.lbl_total_stat = QLabel("12")
        self.lbl_vacant_stat = QLabel("12")
        self.lbl_occupied_stat = QLabel("0")
        
        stats_configurations = [
            ("Total:", self.lbl_total_stat, "white"),
            ("Vacant:", self.lbl_vacant_stat, "#2ecc71"),
            ("Occupied:", self.lbl_occupied_stat, "#e74c3c")
        ]
        for text, metric_widget, font_color in stats_configurations:
            box = QFrame()
            box.setFixedSize(90, 55)
            box.setStyleSheet("background-color: #1e1e1e; border: 1px solid #555; border-radius: 4px;")
            box_vbox = QVBoxLayout(box)
            box_vbox.setContentsMargins(0, 4, 0, 4)
            box_vbox.setSpacing(2)
            
            lbl = QLabel(text)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: #aaa; font-size: 11px; background: transparent;")
            
            metric_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            metric_widget.setStyleSheet(f"color: {font_color}; font-size: 15px; font-weight: bold; background: transparent;")
            
            box_vbox.addWidget(lbl)
            box_vbox.addWidget(metric_widget)
            banner_layout.addWidget(box)
            
        layout.addWidget(banner)

        # 2. CONTROL INPUT AND GRID FLEX SPACE LAYER
        lower_layout = QHBoxLayout()
        lower_layout.setSpacing(15)
        
        left_panel = QVBoxLayout()
        
        # User input fields mapping layout configuration row
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        
        vbox_name = QVBoxLayout()
        lbl_name = QLabel("Customer Name / Plate:")
        lbl_name.setStyleSheet("color: #aaa; font-size: 11px;")
        self.customer_name_input = QLineEdit()
        self.customer_name_input.setFixedWidth(160)
        self.customer_name_input.setStyleSheet("background-color: #555; color: white; border: 1px solid #777; padding: 4px; border-radius: 2px;")
        vbox_name.addWidget(lbl_name)
        vbox_name.addWidget(self.customer_name_input)
        controls_layout.addLayout(vbox_name)
        
        vbox_slot = QVBoxLayout()
        lbl_slot = QLabel("Selected Space Target:")
        lbl_slot.setStyleSheet("color: #aaa; font-size: 11px;")
        self.spot_selector = QComboBox()
        self.spot_selector.setFixedWidth(120)
        self.spot_selector.setStyleSheet("background-color: #555; color: white; border: 1px solid #777; padding: 4px; border-radius: 2px;")
        vbox_slot.addWidget(lbl_slot)
        vbox_slot.addWidget(self.spot_selector)
        controls_layout.addLayout(vbox_slot)
        
        btn_assign = QPushButton("Assign & Check-In")
        btn_assign.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; padding: 6px 12px; border-radius: 2px; margin-bottom: 2px;")
        btn_assign.clicked.connect(self.assign_spot)
        controls_layout.addWidget(btn_assign, alignment=Qt.AlignmentFlag.AlignBottom)
        
        controls_layout.addStretch()
        
        # Toggle Layout Filtering Buttons Block
        btn_avail = QPushButton("Available")
        btn_avail.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; padding: 6px 12px; border-radius: 2px;")
        btn_avail.clicked.connect(lambda: self.set_grid_filter("Available"))
        
        btn_occ = QPushButton("Occupied")
        btn_occ.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; padding: 6px 12px; border-radius: 2px;")
        btn_occ.clicked.connect(lambda: self.set_grid_filter("Occupied"))
        
        btn_all = QPushButton("All")
        btn_all.setStyleSheet("background-color: #7f8c8d; color: white; font-weight: bold; padding: 6px 18px; border-radius: 2px;")
        btn_all.clicked.connect(lambda: self.set_grid_filter("All"))
        
        controls_layout.addWidget(btn_avail, alignment=Qt.AlignmentFlag.AlignBottom)
        controls_layout.addWidget(btn_occ, alignment=Qt.AlignmentFlag.AlignBottom)
        controls_layout.addWidget(btn_all, alignment=Qt.AlignmentFlag.AlignBottom)
        
        left_panel.addLayout(controls_layout)
        left_panel.addSpacing(10)
        
        # 3. VEHICLE CONTAINER RENDER ENVIRONMENT GRID
        grid_frame = QFrame()
        grid_frame.setStyleSheet("background-color: #3e3e42; border: 1px solid #555; border-radius: 4px;")
        grid_layout = QGridLayout(grid_frame)
        grid_layout.setContentsMargins(15, 15, 15, 15)
        grid_layout.setHorizontalSpacing(12)
        grid_layout.setVerticalSpacing(0)
        
        idx = 1
        for row in [0, 2]: # Row index 1 is reserved explicitly for drawing road markings layout line
            for col in range(6):
                spot_label = f"Spot {idx}"
                
                # Dynamic wrapper clickable frame asset block
                slot_card = QFrame()
                slot_card.setStyleSheet("background-color: #2d2d30; border: 1px solid #444; border-radius: 4px;")
                card_vbox = QVBoxLayout(slot_card)
                card_vbox.setContentsMargins(4, 4, 4, 4)
                
                # Generate custom vector car widget entity
                car_widget = ParkingSlotWidget(False, spot_label)
                card_vbox.addWidget(car_widget)
                
                # Interactive shortcut overlay button
                action_btn = QPushButton("Select Slot")
                action_btn.setStyleSheet("background-color: #555; color: white; font-size: 10px; border-radius: 2px; padding: 2px;")
                action_btn.clicked.connect(lambda checked, s=spot_label: self.handle_grid_button_click(s))
                card_vbox.addWidget(action_btn)
                
                grid_layout.addWidget(slot_card, row, col)
                
                # Save composite structured object references for fast runtime dynamic lookup queries
                self.slot_ui_elements[spot_label] = {"frame": slot_card, "car": car_widget}
                idx += 1
                
        # Draw central road dividers lines between split bays
        for col in range(6):
            lane_marking = QFrame()
            lane_marking.setFixedHeight(4)
            lane_marking.setStyleSheet("background-color: #f1c40f; border: none;")
            grid_layout.addWidget(lane_marking, 1, col)
            
        left_panel.addWidget(grid_frame)
        lower_layout.addLayout(left_panel, stretch=4)
        
        # 4. RUNTIME SYSTEM LIVE STREAM ACTIVITY LOGGER COLUMN
        right_panel = QFrame()
        right_panel.setFixedWidth(200)
        right_panel.setStyleSheet("background-color: #3e3e42; border: 1px solid #555; border-radius: 4px;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        log_title = QLabel("Activity Log")
        log_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        log_title.setStyleSheet("color: white; font-size: 13px; font-weight: bold; border: none;")
        right_layout.addWidget(log_title)
        
        self.activity_log_box = QTextEdit()
        self.activity_log_box.setReadOnly(True)
        self.activity_log_box.setStyleSheet("background-color: #1e1e1e; color: #2ecc71; border: none; font-family: Courier; font-size: 11px;")
        right_layout.addWidget(self.activity_log_box)
        
        lower_layout.addWidget(right_panel, stretch=1)
        layout.addLayout(lower_layout)
        
        self.tabs.addTab(tab, "Spot Dashboard")
        self.log_message("System initiated. Ready to manage tracking data.")

    # --- TAB 2: AUTOMATED TIME TRACKING & BILLING ---
    def init_time_tracking_tab(self):
        tab = QWidget()
        tab.setStyleSheet("color: white;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        checkout_layout = QHBoxLayout()
        self.active_spot_selector = QComboBox()
        self.active_spot_selector.setFixedWidth(150)
        self.active_spot_selector.setStyleSheet("background-color: #555; color: white; padding: 4px;")
        
        checkout_btn = QPushButton("Process Time-Out & Bill")
        checkout_btn.setStyleSheet("background-color: #e74c3c; font-weight: bold; padding: 6px 15px;")
        checkout_btn.clicked.connect(self.process_timeout)

        checkout_layout.addWidget(QLabel("Select Occupied Spot Area:"))
        checkout_layout.addWidget(self.active_spot_selector)
        checkout_layout.addWidget(checkout_btn)
        checkout_layout.addStretch()
        layout.addLayout(checkout_layout)

        # Rate configuration inputs
        rate_layout = QHBoxLayout()
        self.base_rate_spin = QSpinBox()
        self.base_rate_spin.setRange(0, 1000)
        self.base_rate_spin.setValue(50)
        self.base_rate_spin.setStyleSheet("background-color: #555; color: white; padding: 4px;")
        
        self.hourly_rate_spin = QSpinBox()
        self.hourly_rate_spin.setRange(0, 1000)
        self.hourly_rate_spin.setValue(20)
        self.hourly_rate_spin.setStyleSheet("background-color: #555; color: white; padding: 4px;")

        rate_layout.addWidget(QLabel("Base Rate (₱):"))
        rate_layout.addWidget(self.base_rate_spin)
        rate_layout.addSpacing(20)
        rate_layout.addWidget(QLabel("Additional Per Hour Rate Fee (₱):"))
        rate_layout.addWidget(self.hourly_rate_spin)
        rate_layout.addStretch()
        layout.addLayout(rate_layout)
        
        layout.addStretch()
        self.tabs.addTab(tab, "Time Tracking & Billing")

    # --- TAB 3: DIGITAL LOG & TEXT FILE TICKET PRINTING ---
    def init_ticket_management_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)

        self.ticket_log = QTableWidget(0, 5)
        self.ticket_log.setHorizontalHeaderLabels(["Customer", "Spot Code Location", "Checked In Timestamp", "Checked Out Timestamp", "Total Paid (PHP)"])
        self.ticket_log.setStyleSheet("""
            QTableWidget { background-color: #1e1e1e; color: white; gridline-color: #555; }
            QHeaderView::section { background-color: #3e3e42; color: white; padding: 5px; border: 1px solid #555; }
        """)
        self.ticket_log.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(QLabel("Digital Session Ledger Logs Archives:", styleSheet="color: white; font-weight: bold;"))
        layout.addWidget(self.ticket_log)

        self.tabs.addTab(tab, "Printing & Tickets Logs")

    # --- CORE ACTION LOGIC ENGINE ---

    def log_message(self, message):
        """Appends timestamped operations trace directly to continuous dashboard system streams"""
        timestamp = datetime.now().strftime("%I:%M:%S %p")
        self.activity_log_box.append(f"[{timestamp}] {message}")

    def set_grid_filter(self, filter_mode):
        """Filters the dashboard grid based on slot availability status."""
        self.current_filter = filter_mode
        self.log_message(f"Filtering display view to: {filter_mode}")
        self.update_ui_state()

    def handle_grid_button_click(self, spot_label):
        """Handles shortcuts when interacting with vector data nodes."""
        data = self.parking_slots[spot_label]
        
        if data is None:
            index = self.spot_selector.findText(spot_label)
            if index >= 0:
                self.spot_selector.setCurrentIndex(index)
            self.customer_name_input.setFocus()
            self.log_message(f"Selected vacant {spot_label}. Ready for allocation inputs.")
        else:
            self.tabs.setCurrentIndex(1) # Redirect focus instantly to Billing management tab
            index = self.active_spot_selector.findText(spot_label)
            if index >= 0:
                self.active_spot_selector.setCurrentIndex(index)
            self.log_message(f"Selected occupied {spot_label}. Switched view context to checkout billing process panel.")

    def update_ui_state(self):
        """Syncs backend state variables with layout controls and active matrix filter modes."""
        self.spot_selector.clear()
        self.active_spot_selector.clear()

        vacant_count = 0
        occupied_count = 0

        for spot_label, data in self.parking_slots.items():
            ui = self.slot_ui_elements[spot_label]
            
            if data is None:
                vacant_count += 1
                self.spot_selector.addItem(spot_label)
                ui["car"].set_occupied(False)
                
                # Apply visibility filtering rules
                if self.current_filter == "Occupied":
                    ui["frame"].setVisible(False)
                else:
                    ui["frame"].setVisible(True)
            else:
                occupied_count += 1
                self.active_spot_selector.addItem(spot_label)
                ui["car"].set_occupied(True)
                
                if self.current_filter == "Available":
                    ui["frame"].setVisible(False)
                else:
                    ui["frame"].setVisible(True)

        # Update counter values dynamically
        self.lbl_vacant_stat.setText(str(vacant_count))
        self.lbl_occupied_stat.setText(str(occupied_count))

    def assign_spot(self):
        customer = self.customer_name_input.text().strip()
        selected_spot = self.spot_selector.currentText()

        if not customer:
            QMessageBox.warning(self, "Input Error", "Please enter a valid customer identifier / vehicle plate code tracking reference.")
            return
        if not selected_spot:
            QMessageBox.warning(self, "Capacity Full", "No available parking spaces remaining across standard configurations.")
            return

        # Commit tracking session details
        self.parking_slots[selected_spot] = {
            "customer": customer,
            "time_in": datetime.now()
        }

        self.log_message(f"Check-In Commited: {selected_spot} assigned to {customer}")
        self.customer_name_input.clear()
        self.update_ui_state()
        QMessageBox.information(self, "Checked In", f"{selected_spot} successfully transitioned to Occupied state data structures.")

    def process_timeout(self):
        selected_spot = self.active_spot_selector.currentText()
        if not selected_spot:
            QMessageBox.warning(self, "Input Error", "No occupied spots selected for process tracking.")
            return

        spot_data = self.parking_slots[selected_spot]
        checkout_time = datetime.now()
        
        # Calculate dynamic timesheet spans metrics
        duration = checkout_time - spot_data["time_in"]
        total_seconds = duration.total_seconds()
        
        # Dev testing scale translation mapping (Calculates scale tracking metrics mapped via minute increments for speed)
        hours_parked = max(1.0, total_seconds / 60.0)  

        # Cost accounting computation values logic equations
        base_fee = self.base_rate_spin.value()
        hourly_fee = self.hourly_rate_spin.value()
        additional_hours = max(0.0, hours_parked - 1.0)
        total_bill = base_fee + (additional_hours * hourly_fee)

        # Append structured metrics directly into data log tracking grids
        row_count = self.ticket_log.rowCount()
        self.ticket_log.insertRow(row_count)
        self.ticket_log.setItem(row_count, 0, QTableWidgetItem(spot_data["customer"]))
        self.ticket_log.setItem(row_count, 1, QTableWidgetItem(selected_spot))
        self.ticket_log.setItem(row_count, 2, QTableWidgetItem(spot_data["time_in"].strftime("%I:%M:%S %p")))
        self.ticket_log.setItem(row_count, 3, QTableWidgetItem(checkout_time.strftime("%I:%M:%S %p")))
        self.ticket_log.setItem(row_count, 4, QTableWidgetItem(f"P{total_bill:.2f}"))

        # Save record output to disk
        self.export_ticket_to_txt(selected_spot, spot_data, checkout_time, hours_parked, total_bill)

        self.log_message(f"Processed checkout out for {selected_spot}. Collected: P{total_bill:.2f}")

        # CLEAR SLOT STATE MEMORY BLOCK -> Releases space back to Vacant
        self.parking_slots[selected_spot] = None

        self.update_ui_state()
        QMessageBox.information(self, "Receipt Saved", "Spot state transitioned cleanly back to Vacant.\nTicket plain file generated on localized directory paths root!")

    def export_ticket_to_txt(self, spot, data, checkout_dt, hours, bill):
        filename = f"ticket_{spot}_{data['customer'].replace(' ', '_')}.txt"
        with open(filename, "w", encoding="utf-8") as file:
            file.write("=========================================\n")
            file.write("        PARKING RECEIPT INVOICE         \n")
            file.write("=========================================\n")
            file.write(f"Customer/Plate: {data['customer']}\n")
            file.write(f"Assigned Space: {spot}\n")
            file.write(f"Arrival Time:   {data['time_in'].strftime('%Y-%m-%d %I:%M:%S %p')}\n")
            file.write(f"Departure Time: {checkout_dt.strftime('%Y-%m-%d %I:%M:%S %p')}\n")
            file.write(f"Duration Track: {hours:.2f} calculated hour billing units\n")
            file.write("-----------------------------------------\n")
            file.write(f"TOTAL CHARGED:  P{bill:.2f}\n")
            file.write("=========================================\n")


# --- SYSTEM CONSOLE ENTRY BOOT INITIALIZATION ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ParkingSystemApp()
    window.show()
    sys.exit(app.exec())
