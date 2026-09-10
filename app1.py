import sys
import random
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox
from PyQt6.QtCore import QTimer
import pyqtgraph as pg


class FastCollisionSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Subatomic Event Generator")
        self.resize(1000, 650)

        # Physics Parameters & Counters
        self.is_collided = False
        self.is_jet_mode = True
        self.multiplicity = 400
        self.tracks = []
        self.counts = {"+": 0, "-": 0, "0": 0}

        # UI Setup
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Control & Analytics Header Row
        ctrl_layout = QHBoxLayout()
        self.status = QLabel("Beams injecting...", self)
        self.status.setStyleSheet("font-weight: bold; color: #2c3e50;")

        jet_cb = QCheckBox("Jet Cones", self)
        jet_cb.setChecked(self.is_jet_mode)
        jet_cb.stateChanged.connect(lambda state: setattr(self, 'is_jet_mode', state == 2))

        self.stats_lbl = QLabel("📊 Ratios: (+): 0% | (-): 0% | (0): 0%", self)
        reset_btn = QPushButton("Reset Event", self)
        reset_btn.clicked.connect(self.reset_event)

        for w in [self.status, jet_cb, self.stats_lbl, reset_btn]: ctrl_layout.addWidget(w)
        layout.addLayout(ctrl_layout)

        # Hardware-Accelerated PyQtGraph Plot Setup
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('k')
        self.plot_widget.setXRange(-40, 40)
        self.plot_widget.setYRange(-30, 30)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.2)
        layout.addWidget(self.plot_widget)

        # Inject Primary Proving Ion Scatter Projectiles
        self.ion_l = self.plot_widget.plot([-40], [0], pen=None, symbol='o', symbolSize=14, symbolBrush='c')
        self.ion_r = self.plot_widget.plot([40], [0], pen=None, symbol='o', symbolSize=14, symbolBrush='m')
        self.pos_l, self.pos_r = -40.0, 40.0

        # Dedicated Qt Frame Calculation Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(16)

    def trigger_hadronization(self):
        self.is_collided = True
        self.status.setText("💥 COLLISION DETECTED!")
        self.ion_l.clear()
        self.ion_r.clear()

        # Species Matrix Config (Green=Positive, Red=Negative, Gray=Neutral)
        species = [{"c": '#2ecc71', "q": 1}, {"c": '#e74c3c', "q": -1}, {"c": '#7f8c8d', "q": 0}]
        jet_axis = random.uniform(-0.5, 0.5)

        for _ in range(self.multiplicity):
            spec = random.choice(species)
            mag = random.gammavariate(2, 2) * 0.25

            if self.is_jet_mode:
                direction = 1.0 if random.random() > 0.5 else -1.0
                vx = direction * (mag * 0.9)
                vy = (jet_axis * vx) + random.uniform(-0.15, 0.15)
            else:
                angle = random.uniform(0, 2 * np.pi)
                vx, vy = mag * np.cos(angle), mag * np.sin(angle)

            # Update statistical distribution keys
            key = "+" if spec["q"] == 1 else ("-" if spec["q"] == -1 else "0")
            self.counts[key] += 1

            # Instantiate hardware vector line graph item
            curve = self.plot_widget.plot([0.0], [0.0], pen=pg.mkPen(spec["c"], width=1.5))
            self.tracks.append({"curve": curve, "x": [0.0], "y": [0.0], "vx": vx, "vy": vy, "q": spec["q"]})

        # Calculate final analytics percentages instantly
        total = max(1, sum(self.counts.values()))
        self.stats_lbl.setText(
            f"📊 Ratios: (+): {self.counts['+'] / total * 100:.1f}% | "
            f"(-): {self.counts['-'] / total * 100:.1f}% | "
            f"(0): {self.counts['0'] / total * 100:.1f}%"
        )

    def update_simulation(self):
        if not self.is_collided:
            self.pos_l += 1.5
            self.pos_r -= 1.5
            self.ion_l.setData([self.pos_l], [0])
            self.ion_r.setData([self.pos_r], [0])
            if self.pos_l >= 0:
                self.trigger_hadronization()
        else:
            # Vectorized Lorentz Force Curvature update
            b_field = 0.05
            for t in self.tracks:
                if len(t["x"]) > 60: continue  # Cap maximum path lengths to maintain peak rendering speed

                if t["q"] != 0:
                    ax = t["q"] * t["vy"] * b_field
                    ay = -t["q"] * t["vx"] * b_field
                    t["vx"] += ax
                    t["vy"] += ay

                # Append newly calculated point steps to history arrays
                t["x"].append(t["x"][-1] + t["vx"])
                t["y"].append(t["y"][-1] + t["vy"])
                t["curve"].setData(t["x"], t["y"])

    def reset_event(self):
        for t in self.tracks: t["curve"].clear()
        self.tracks.clear()
        self.counts = {"+": 0, "-": 0, "0": 0}
        self.is_collided = False
        self.pos_l, self.pos_r = -40.0, 40.0
        self.status.setText("Beams injecting...")
        self.stats_lbl.setText("📊 Ratios: (+): 0% | (-): 0% | (0): 0%")
        self.ion_l.setData([self.pos_l], [0])
        self.ion_r.setData([self.pos_r], [0])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FastCollisionSimulator()
    window.show()
    sys.exit(app.exec())
