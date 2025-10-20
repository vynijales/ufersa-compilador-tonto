from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class ChartWidget(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(6, 4), dpi=80)
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)

