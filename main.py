import sys
from datetime import date
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateEdit,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import database
from calculations import BodyMetrics, calculate_bmi, calculate_bmr_mifflin_st_jeor, calculate_tdee


class MplCanvas(FigureCanvas):
    def __init__(self, width: float = 5, height: float = 3, dpi: int = 100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)


class FoodDiaryTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout()

        # Date selector
        date_layout = QHBoxLayout()
        date_label = QLabel("Date")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(date.today())
        self.date_edit.dateChanged.connect(self.refresh_logs)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit)
        date_layout.addStretch()

        # Search and food details
        search_group = QGroupBox("Search Food")
        s_layout = QGridLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search in food database (e.g., Chicken, Rice)...")
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.perform_search)
        self.search_results = QComboBox()
        self.search_results.setPlaceholderText("Results")

        s_layout.addWidget(QLabel("Query"), 0, 0)
        s_layout.addWidget(self.search_input, 0, 1)
        s_layout.addWidget(self.search_button, 0, 2)
        s_layout.addWidget(QLabel("Match"), 1, 0)
        s_layout.addWidget(self.search_results, 1, 1, 1, 2)
        search_group.setLayout(s_layout)

        # Log form
        log_group = QGroupBox("Log Food Entry")
        form = QFormLayout()

        self.meal_time_input = QComboBox()
        self.meal_time_input.addItems(["Breakfast", "Lunch", "Dinner", "Snack"])

        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setDecimals(2)
        self.quantity_input.setMinimum(0.1)
        self.quantity_input.setMaximum(1000)
        self.quantity_input.setValue(1.0)

        self.calories_input = QDoubleSpinBox()
        self.calories_input.setRange(0, 5000)
        self.carbs_input = QDoubleSpinBox()
        self.carbs_input.setRange(0, 1000)
        self.fat_input = QDoubleSpinBox()
        self.fat_input.setRange(0, 1000)
        self.protein_input = QDoubleSpinBox()
        self.protein_input.setRange(0, 1000)

        form.addRow("Meal", self.meal_time_input)
        form.addRow("Quantity (× selected food)", self.quantity_input)
        form.addRow("Calories", self.calories_input)
        form.addRow("Carbs (g)", self.carbs_input)
        form.addRow("Fat (g)", self.fat_input)
        form.addRow("Protein (g)", self.protein_input)

        self.log_button = QPushButton("Add to Diary")
        self.log_button.clicked.connect(self.add_entry)
        form.addRow(self.log_button)
        log_group.setLayout(form)

        # Table for today's logs
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Meal", "Food", "Qty", "Calories", "Carbs (g)", "Protein (g)"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)

        main_layout.addLayout(date_layout)
        main_layout.addWidget(search_group)
        main_layout.addWidget(log_group)
        main_layout.addWidget(QLabel("Today's Food Log"))
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)
        self.refresh_logs()

    def current_date_str(self) -> str:
        return self.date_edit.date().toString("yyyy-MM-dd")

    def perform_search(self):
        query = self.search_input.text().strip()
        if not query:
            return
        rows = database.search_foods(query)
        self.search_results.clear()
        for row in rows:
            label = f"{row['name']} ({row['calories']} kcal)"
            self.search_results.addItem(label, userData=row)
        if rows:
            self.search_results.setCurrentIndex(0)
            self.apply_selected_food_to_fields()
        self.search_results.currentIndexChanged.connect(self.apply_selected_food_to_fields)

    def apply_selected_food_to_fields(self):
        data = self.search_results.currentData()
        if not data:
            return
        qty = self.quantity_input.value()
        self.calories_input.setValue(data["calories"] * qty)
        self.carbs_input.setValue(data["carbs_g"] * qty)
        self.fat_input.setValue(data["fat_g"] * qty)
        self.protein_input.setValue(data["protein_g"] * qty)

    def add_entry(self):
        date_str = self.current_date_str()
        meal = self.meal_time_input.currentText()
        qty = self.quantity_input.value()
        calories = self.calories_input.value()
        carbs = self.carbs_input.value()
        fat = self.fat_input.value()
        protein = self.protein_input.value()
        base_food = self.search_results.currentData()

        if calories <= 0:
            QMessageBox.warning(self, "Invalid data", "Calories must be greater than 0.")
            return

        database.add_food_log(
            log_date=date_str,
            meal_time=meal,
            base_food=base_food,
            quantity=qty,
            calories=calories,
            carbs_g=carbs,
            fat_g=fat,
            protein_g=protein,
        )
        self.refresh_logs()

    def refresh_logs(self):
        date_str = self.current_date_str()
        rows = database.get_food_logs_by_date(date_str)
        self.table.setRowCount(0)
        for row in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(row["meal_time"] or ""))
            self.table.setItem(r, 1, QTableWidgetItem(row["food_name"] or "Custom"))
            self.table.setItem(r, 2, QTableWidgetItem(str(row["quantity"])))
            self.table.setItem(r, 3, QTableWidgetItem(f"{row['calories']:.0f}"))
            self.table.setItem(r, 4, QTableWidgetItem(f"{row['carbs_g']:.1f}"))
            self.table.setItem(r, 5, QTableWidgetItem(f"{row['protein_g']:.1f}"))


class ExerciseDiaryTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout()

        # Date selector
        date_layout = QHBoxLayout()
        date_label = QLabel("Date")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(date.today())
        self.date_edit.dateChanged.connect(self.refresh_logs)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit)
        date_layout.addStretch()

        # Card to log exercise
        group = QGroupBox("Log Exercise")
        form = QFormLayout()

        self.exercise_type_input = QLineEdit()
        self.exercise_type_input.setPlaceholderText("e.g., Running, Bench Press")

        self.category_input = QComboBox()
        self.category_input.addItems(["cardio", "strength"])
        self.category_input.currentTextChanged.connect(self._toggle_fields)

        self.duration_input = QDoubleSpinBox()
        self.duration_input.setSuffix(" min")
        self.duration_input.setRange(0, 1000)

        self.sets_input = QSpinBox()
        self.sets_input.setRange(0, 50)

        self.reps_input = QSpinBox()
        self.reps_input.setRange(0, 1000)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("How did it feel? Pace, weight used, etc.")
        self.notes_input.setFixedHeight(60)

        form.addRow("Exercise", self.exercise_type_input)
        form.addRow("Category", self.category_input)
        form.addRow("Duration", self.duration_input)
        form.addRow("Sets", self.sets_input)
        form.addRow("Reps per Set", self.reps_input)
        form.addRow("Notes", self.notes_input)

        self.log_button = QPushButton("Add Exercise")
        self.log_button.clicked.connect(self.add_entry)
        form.addRow(self.log_button)
        group.setLayout(form)

        # Table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Type", "Category", "Duration (min)", "Sets", "Reps", "Notes"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)

        main_layout.addLayout(date_layout)
        main_layout.addWidget(group)
        main_layout.addWidget(QLabel("Today's Exercise Log"))
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)
        self._toggle_fields(self.category_input.currentText())
        self.refresh_logs()

    def current_date_str(self) -> str:
        return self.date_edit.date().toString("yyyy-MM-dd")

    def _toggle_fields(self, category: str):
        is_cardio = category == "cardio"
        self.duration_input.setEnabled(is_cardio)
        self.sets_input.setEnabled(not is_cardio)
        self.reps_input.setEnabled(not is_cardio)

    def add_entry(self):
        exercise = self.exercise_type_input.text().strip()
        if not exercise:
            QMessageBox.warning(self, "Missing data", "Exercise name is required.")
            return
        category = self.category_input.currentText()
        duration = self.duration_input.value() if category == "cardio" else None
        sets = self.sets_input.value() if category == "strength" else None
        reps = self.reps_input.value() if category == "strength" else None
        notes = self.notes_input.toPlainText().strip()

        database.add_exercise_log(
            log_date=self.current_date_str(),
            exercise_type=exercise,
            category=category,
            duration_min=duration,
            sets=sets,
            reps_per_set=reps,
            notes=notes,
        )
        self.refresh_logs()

    def refresh_logs(self):
        rows = database.get_exercise_logs_by_date(self.current_date_str())
        self.table.setRowCount(0)
        for row in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(row["exercise_type"]))
            self.table.setItem(r, 1, QTableWidgetItem(row["category"]))
            self.table.setItem(r, 2, QTableWidgetItem(str(row["duration_min"] or "")))
            self.table.setItem(r, 3, QTableWidgetItem(str(row["sets"] or "")))
            self.table.setItem(r, 4, QTableWidgetItem(str(row["reps_per_set"] or "")))
            self.table.setItem(r, 5, QTableWidgetItem(row["notes"] or ""))


class ReportingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout()

        # Date filter for nutrient summary (single day)
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Nutrient date"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(date.today())
        self.date_edit.dateChanged.connect(self.refresh_charts)
        top_layout.addWidget(self.date_edit)
        top_layout.addStretch()

        # Weight chart
        weight_group = QGroupBox("Weight Progress")
        w_layout = QVBoxLayout()
        self.weight_canvas = MplCanvas()
        w_layout.addWidget(self.weight_canvas)
        weight_group.setLayout(w_layout)

        # Nutrient chart
        nutrient_group = QGroupBox("Daily Nutrients")
        n_layout = QVBoxLayout()
        self.nutrient_canvas = MplCanvas()
        n_layout.addWidget(self.nutrient_canvas)
        nutrient_group.setLayout(n_layout)

        main_layout.addLayout(top_layout)
        main_layout.addWidget(weight_group)
        main_layout.addWidget(nutrient_group)

        self.setLayout(main_layout)
        self.refresh_charts()

    def refresh_charts(self):
        # Weight chart
        weight_rows = database.get_weight_entries()
        ax = self.weight_canvas.ax
        ax.clear()
        if weight_rows:
            dates = [r["log_date"] for r in weight_rows]
            weights = [r["weight_kg"] for r in weight_rows]
            ax.plot(dates, weights, marker="o", color="#0070ba")
            ax.set_ylabel("Weight (kg)")
            ax.set_xticklabels(dates, rotation=45, ha="right")
        ax.set_title("Weight Over Time")
        self.weight_canvas.fig.tight_layout()
        self.weight_canvas.draw()

        # Nutrient chart
        n_ax = self.nutrient_canvas.ax
        n_ax.clear()
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        totals = database.get_daily_nutrient_totals(date_str)
        labels = ["Calories", "Carbs (g)", "Fat (g)", "Protein (g)"]
        values = [
            totals["calories"],
            totals["carbs_g"],
            totals["fat_g"],
            totals["protein_g"],
        ]
        n_ax.bar(labels, values, color=["#0070ba", "#2ecc71", "#f39c12", "#9b59b6"])
        n_ax.set_title(f"Nutrients for {date_str}")
        self.nutrient_canvas.fig.tight_layout()
        self.nutrient_canvas.draw()


class ProfileAndCalculatorTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.load_profile()

    def _build_ui(self):
        main_layout = QHBoxLayout()

        # Left: profile
        profile_group = QGroupBox("Profile")
        p_form = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Your name")
        self.age_input = QSpinBox()
        self.age_input.setRange(10, 120)

        self.gender_input = QComboBox()
        self.gender_input.addItems(["male", "female"])

        self.height_input = QDoubleSpinBox()
        self.height_input.setRange(100, 250)
        self.height_input.setSuffix(" cm")
        self.height_input.setValue(170)

        self.weight_input = QDoubleSpinBox()
        self.weight_input.setRange(30, 300)
        self.weight_input.setSuffix(" kg")
        self.weight_input.setValue(70)

        self.activity_input = QComboBox()
        self.activity_input.addItem("Sedentary (little or no exercise)", 1.2)
        self.activity_input.addItem("Lightly active (1–3 days/week)", 1.375)
        self.activity_input.addItem("Moderately active (3–5 days/week)", 1.55)
        self.activity_input.addItem("Very active (6–7 days/week)", 1.725)
        self.activity_input.addItem("Extra active (physical job + exercise)", 1.9)

        self.save_button = QPushButton("Save Profile & Log Weight")
        self.save_button.clicked.connect(self.save_profile)

        p_form.addRow("Name", self.name_input)
        p_form.addRow("Age", self.age_input)
        p_form.addRow("Gender", self.gender_input)
        p_form.addRow("Height", self.height_input)
        p_form.addRow("Current weight", self.weight_input)
        p_form.addRow("Activity", self.activity_input)
        p_form.addRow(self.save_button)
        profile_group.setLayout(p_form)

        # Right: calculator
        calc_group = QGroupBox("BMI / BMR / TDEE")
        c_layout = QVBoxLayout()
        self.bmi_label = QLabel("BMI: –")
        self.bmr_label = QLabel("BMR (Mifflin–St Jeor): – kcal")
        self.tdee_label = QLabel("TDEE (Maintenance): – kcal")

        for lbl in (self.bmi_label, self.bmr_label, self.tdee_label):
            font = QFont()
            font.setPointSize(11)
            font.setBold(True)
            lbl.setFont(font)

        self.calc_button = QPushButton("Recalculate")
        self.calc_button.clicked.connect(self.calculate_all)

        c_layout.addWidget(self.bmi_label)
        c_layout.addWidget(self.bmr_label)
        c_layout.addWidget(self.tdee_label)
        c_layout.addStretch()
        c_layout.addWidget(self.calc_button, alignment=Qt.AlignmentFlag.AlignRight)
        calc_group.setLayout(c_layout)

        main_layout.addWidget(profile_group, stretch=2)
        main_layout.addWidget(calc_group, stretch=1)
        self.setLayout(main_layout)

    def load_profile(self):
        profile = database.get_profile()
        if not profile:
            return
        self.name_input.setText(profile["name"] or "")
        if profile["age"]:
            self.age_input.setValue(profile["age"])
        if profile["gender"]:
            index = self.gender_input.findText(profile["gender"])
            if index >= 0:
                self.gender_input.setCurrentIndex(index)
        if profile["height_cm"]:
            self.height_input.setValue(profile["height_cm"])
        # activity_factor
        af = profile["activity_factor"] or 1.2
        for i in range(self.activity_input.count()):
            if abs(self.activity_input.itemData(i) - af) < 1e-6:
                self.activity_input.setCurrentIndex(i)
                break

    def save_profile(self):
        name = self.name_input.text().strip()
        age = int(self.age_input.value())
        gender = self.gender_input.currentText()
        height_cm = float(self.height_input.value())
        weight_kg = float(self.weight_input.value())
        activity_factor = float(self.activity_input.currentData())

        database.upsert_profile(
            name=name,
            age=age,
            gender=gender,
            height_cm=height_cm,
            activity_factor=activity_factor,
        )
        # also log weight for chart
        database.add_weight_entry(date.today().isoformat(), weight_kg)
        self.calculate_all()
        QMessageBox.information(self, "Saved", "Profile and weight updated.")

    def calculate_all(self):
        age = int(self.age_input.value())
        gender = self.gender_input.currentText()
        height_cm = float(self.height_input.value())
        weight_kg = float(self.weight_input.value())
        activity_factor = float(self.activity_input.currentData())

        metrics = BodyMetrics(
            weight_kg=weight_kg,
            height_cm=height_cm,
            age=age,
            gender=gender,  # type: ignore[arg-type]
            activity_factor=activity_factor,
        )
        try:
            bmi = calculate_bmi(weight_kg, height_cm)
            bmr = calculate_bmr_mifflin_st_jeor(metrics)
            tdee = calculate_tdee(bmr, activity_factor)
        except ValueError as e:
            QMessageBox.warning(self, "Invalid data", str(e))
            return

        self.bmi_label.setText(f"BMI: {bmi:.1f}")
        self.bmr_label.setText(f"BMR (Mifflin–St Jeor): {bmr:.0f} kcal/day")
        self.tdee_label.setText(f"TDEE (Maintenance): {tdee:.0f} kcal/day")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DynamicBUD")
        self.resize(1100, 700)
        self._build_ui()

    def _build_ui(self):
        # Top-level container
        central = QWidget()
        root_layout = QVBoxLayout()

        # Header
        header = QHBoxLayout()
        title = QLabel("DynamicBUD")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        title.setFont(font)
        title.setStyleSheet("color: #111;")
        header.addWidget(title)
        header.addStretch()
        header_label = QLabel("Track food, workouts, and goals in one place.")
        header_label.setStyleSheet("color: #3b4a5a;")
        header.addWidget(header_label)

        # Tabs
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.North)
        tabs.setStyleSheet(
            """
            QTabWidget::pane {
                border-top: 2px solid #e2e6ea;
                background: #f5f7fa;
            }
            QTabBar::tab {
                background: #f5f7fa;
                border: 1px solid #e2e6ea;
                border-bottom: none;
                padding: 8px 18px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                color: #0070ba;
                border-color: #c0d0e0;
            }
            """
        )

        self.profile_tab = ProfileAndCalculatorTab()
        self.food_tab = FoodDiaryTab()
        self.exercise_tab = ExerciseDiaryTab()
        self.reporting_tab = ReportingTab()

        tabs.addTab(self.profile_tab, "Profile & Calculator")
        tabs.addTab(self.food_tab, "Food Diary")
        tabs.addTab(self.exercise_tab, "Exercise Diary")
        tabs.addTab(self.reporting_tab, "Reports")

        root_layout.addLayout(header)
        root_layout.addWidget(tabs)
        central.setLayout(root_layout)
        self.setCentralWidget(central)

        # Global styling (light, PayPal-ish)
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f2f4f7;
            }
            QGroupBox {
                background-color: #ffffff;
                border: 1px solid #dde1e7;
                border-radius: 10px;
                margin-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
                color: #0070ba;
                font-weight: 600;
            }
            QLabel {
                color: #1f2933;
            }
            QPushButton {
                background-color: #0070ba;
                color: #ffffff;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #005ea6;
            }
            QPushButton:pressed {
                background-color: #004c8c;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTextEdit {
                border: 1px solid #c4c9d4;
                border-radius: 4px;
                padding: 6px 8px;
                background: #ffffff;
                color: #111827;
                selection-background-color: #0070ba;
                selection-color: #ffffff;
            }
            QLineEdit::placeholder, QTextEdit::placeholder {
                color: #9ca3af;
            }
            QTableWidget {
                background: #ffffff;
                gridline-color: #e2e6ea;
            }
            QHeaderView::section {
                background: #f3f4f6;
                padding: 4px;
                border: 1px solid #e2e6ea;
                font-weight: 600;
            }
            """
        )


def main():
    database.init_db()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


