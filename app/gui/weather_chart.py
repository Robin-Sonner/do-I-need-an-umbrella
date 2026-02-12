"""Weather chart factory supporting both daily and hourly data with PyQtGraph and Matplotlib backends."""

import numpy as np
import pandas as pd
import pyqtgraph as pg
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt
from pyqtgraph import PlotWidget


class WeatherChart:
    """
    Weather chart factory for creating various weather visualizations. Supports both PyQtGraph and Matplotlib backends.
    Handles both daily (forecast) and hourly (today) data.
    """

    def __init__(self, use_pyqtgraph: bool = True):
        """
        Initialize the ChartFactory with the desired backend.

        Args:
            use_pyqtgraph: If True, use pyqtgraph backend; otherwise matplotlib
        """
        self.use_pyqtgraph = use_pyqtgraph
        if self.use_pyqtgraph:
            pg.setConfigOptions(antialias=True)

    def create_temperature_precipitation_chart(
        self,
        data: pd.DataFrame,
        temp1_col: str = "temperature",
        temp2_col: str = "apparent_temperature",
        precip_col: str = "precipitation",
        x_labels: list[tuple[int, str]] = None,
        title: str = "Temperature & Precipitation",
        label1: str = "Temperature",
        label2: str = "Feels Like",
        color1: str = "#e74c3c",
        color2: str = "#ff9800",
    ) -> PlotWidget | FigureCanvasQTAgg:
        """
        Create a dual-axis temperature and precipitation chart.

        Args:
            data: DataFrame with weather data
            temp1_col: Column name for first temperature dataset
            temp2_col: Column name for second temperature dataset
            precip_col: Column name for precipitation data
            x_labels: Optional list of (index, label) tuples for x-axis
            title: Chart title
            label1: Label for first temperature line
            label2: Label for second temperature line
            color1: Color for first temperature line
            color2: Color for second temperature line

        Returns:
            PlotWidget or FigureCanvasQTAgg depending on backend
        """
        if self.use_pyqtgraph:
            return self._create_temp_precip_pyqtgraph(
                data,
                temp1_col,
                temp2_col,
                precip_col,
                x_labels,
                title,
                label1,
                label2,
                color1,
                color2,
            )
        else:
            return self._create_temp_precip_matplotlib(
                data,
                temp1_col,
                temp2_col,
                precip_col,
                x_labels,
                title,
                label1,
                label2,
                color1,
                color2,
            )

    def create_wind_speed_chart(
        self, data: pd.DataFrame
    ) -> PlotWidget | FigureCanvasQTAgg:
        """
        Create a wind speed bar chart.

        Args:
            data: DataFrame with weather data containing a 'wind_speed' column

        Returns:
            PlotWidget if using pyqtgraph backend, FigureCanvasQTAgg if using matplotlib backend
        """
        x_data = list(range(len(data)))
        wind_data = data["wind_speed"].values
        if self.use_pyqtgraph:
            return self._create_wind_pyqtgraph(wind_data, x_data)
        else:
            return self._create_wind_matplotlib(wind_data, x_data)

    def set_backend(self, use_pyqtgraph: bool):
        """
        Switch between charting backends.

        Args:
            use_pyqtgraph: If True, use pyqtgraph; otherwise matplotlib
        """
        self.use_pyqtgraph = use_pyqtgraph
        if self.use_pyqtgraph:
            pg.setConfigOptions(antialias=True)

    @staticmethod
    def get_nice_axis_range(data_min: float, data_max: float):
        """
        Calculate a nice range with round tick intervals.

        Args:
            data_min: Minimum value in the data
            data_max: Maximum value in the data

        Returns:
            tuple: A tuple containing (nice_min, nice_max, interval) where:
                - nice_min: Rounded minimum value for axis
                - nice_max: Rounded maximum value for axis
                - interval: Tick interval for the axis
        """
        data_range = data_max - data_min
        # Determine a nice interval based on range
        if data_range <= 2:
            interval = 0.5
        elif data_range <= 5:
            interval = 1
        elif data_range <= 10:
            interval = 2
        elif data_range <= 25:
            interval = 5
        else:
            interval = 10
        # Calculate nice min and max
        nice_min = np.floor(data_min / interval) * interval
        nice_max = np.ceil(data_max / interval) * interval
        # Ensure a minimum range of 1
        if nice_max - nice_min < 1:
            nice_max = nice_min + interval
        return nice_min, nice_max, interval

    # ============================================================================
    # PyQtGraph Implementations
    # ============================================================================

    @staticmethod
    def _create_temp_precip_pyqtgraph(
        data: pd.DataFrame,
        temp1_col: str,
        temp2_col: str,
        precip_col: str,
        x_labels: list[tuple[int, str]],
        title: str,
        label1: str,
        label2: str,
        color1: str,
        color2: str,
    ) -> PlotWidget:
        """
        Create temperature/precipitation chart using PyQtGraph.

        Args:
            data: DataFrame with weather data
            temp1_col: Column name for first temperature dataset
            temp2_col: Column name for second temperature dataset
            precip_col: Column name for precipitation data
            x_labels: List of (index, label) tuples for x-axis tick labels
            title: Chart title
            label1: Label for first temperature line
            label2: Label for second temperature line
            color1: Hex color code for first temperature line
            color2: Hex color code for second temperature line

        Returns:
            PlotWidget: Configured PyQtGraph PlotWidget with dual-axis chart
        """
        # Prepare data
        x_data = list(range(len(data)))
        temp_data1 = data[temp1_col].values
        temp_data2 = data[temp2_col].values
        precip_data = data[precip_col].values

        # Create and configure the widget
        widget = PlotWidget()
        WeatherChart._configure_basic_plot_widget(widget)
        widget.setTitle(title)
        widget.setLabel("left", "Temperature", units="°C", color=color1)
        widget.setLabel("bottom", "Time Period" if x_labels else "Hour")

        # Set x-axis labels if provided
        if x_labels:
            ax = widget.getAxis("bottom")
            ax.setTicks([x_labels])

        # Calculate aligned axis ranges
        temp_min = min(temp_data1.min(), temp_data2.min())
        temp_max = max(temp_data1.max(), temp_data2.max())
        precip_min = 0
        precip_max = precip_data.max() if len(precip_data) > 0 else 10
        # Get nice ranges for both axes
        temp_nice_min, temp_nice_max, temp_interval = WeatherChart.get_nice_axis_range(
            temp_min, temp_max
        )
        precip_nice_min, precip_nice_max, precip_interval = (
            WeatherChart.get_nice_axis_range(precip_min, precip_max)
        )
        # Calculate the number of ticks for each axis
        temp_num_ticks = int((temp_nice_max - temp_nice_min) / temp_interval) + 1
        precip_num_ticks = (
            int((precip_nice_max - precip_nice_min) / precip_interval) + 1
        )
        # Extend the axis with fewer ticks to match the one with more ticks
        target_num_ticks = max(temp_num_ticks, precip_num_ticks)
        temp_nice_max = temp_nice_min + temp_interval * (target_num_ticks - 1)
        precip_nice_max = precip_nice_min + precip_interval * (target_num_ticks - 1)

        # Plot temperature lines
        pen1 = pg.mkPen(color=color1, width=3)
        widget.plot(x_data, temp_data1, pen=pen1, name=label1)
        pen2 = pg.mkPen(color=color2, width=2, style=Qt.PenStyle.DashLine)
        widget.plot(x_data, temp_data2, pen=pen2, name=label2)
        widget.setYRange(temp_nice_min, temp_nice_max)

        # Create a secondary viewbox for precipitation
        precip_viewbox = WeatherChart._create_secondary_viewbox(
            widget, "Precipitation", "mm", "#3498db"
        )

        # Add precipitation bars
        width = 0.6 if not x_labels else 0.4  # Narrower bars for daily data
        bar_graph = pg.BarGraphItem(
            x=x_data,
            height=precip_data,
            width=width,
            brush="#3498db80",
            pen=pg.mkPen("#3498db", width=1),
        )
        precip_viewbox.addItem(bar_graph)
        precip_viewbox.setYRange(precip_nice_min, precip_nice_max)

        return widget

    @staticmethod
    def _create_wind_pyqtgraph(wind_data: np.ndarray, x_data: list[int]) -> PlotWidget:
        """
        Create wind speed chart using PyQtGraph.

        Args:
            wind_data: Array of wind speed values in km/h
            x_data: List of x-axis positions (indices)

        Returns:
            PlotWidget: Configured PyQtGraph PlotWidget with wind speed bar chart
        """
        # Create and configure the widget
        widget = PlotWidget()
        WeatherChart._configure_basic_plot_widget(widget)
        widget.setTitle("Wind Speed")
        widget.setLabel("left", "Wind Speed", units="km/h", color="#2ecc71")
        widget.setLabel("bottom", "Hour")
        # Create wind speed bars
        bar_graph = pg.BarGraphItem(
            x=x_data,
            height=wind_data,
            width=0.8,
            brush="#2ecc7180",
            pen=pg.mkPen("#2ecc71", width=1),
        )
        widget.addItem(bar_graph)
        # Set x-axis range for hourly data
        widget.setXRange(0, 23)
        return widget

    @staticmethod
    def _create_secondary_viewbox(
        primary_widget: PlotWidget,
        label: str,
        units: str,
        color: str,
    ) -> pg.ViewBox:
        """
        Create and configure a secondary ViewBox for dual-axis charts.

        Args:
            primary_widget: The primary PlotWidget
            label: Label for right Y-axis
            units: Units for right Y-axis
            color: Color for right Y-axis label

        Returns:
            pg.ViewBox: Configured ViewBox linked to the primary widget
        """
        view_box = pg.ViewBox()
        primary_widget.scene().addItem(view_box)
        primary_widget.getAxis("right").linkToView(view_box)
        view_box.setXLink(primary_widget)
        view_box.setMouseEnabled(x=False, y=False)
        view_box.setMenuEnabled(False)
        primary_widget.setLabel("right", label, units=units, color=color)
        primary_widget.showAxis("right")

        # Sync the views
        def update_views():
            view_box.setGeometry(primary_widget.getViewBox().sceneBoundingRect())
            view_box.linkedViewChanged(primary_widget.getViewBox(), view_box.XAxis)

        update_views()
        primary_widget.getViewBox().sigResized.connect(update_views)

        return view_box

    @staticmethod
    def _configure_basic_plot_widget(widget: PlotWidget) -> PlotWidget:
        """
        Apply basic configuration to a PyQtGraph PlotWidget.

        Args:
            widget: The PlotWidget to configure

        Returns:
            PlotWidget: The configured PlotWidget with white background, grid, and disabled interactions
        """
        widget.setBackground("w")
        widget.setMinimumHeight(300)
        widget.showGrid(x=True, y=True, alpha=0.3)
        widget.setMouseEnabled(x=False, y=False)
        widget.setMenuEnabled(False)
        widget.hideButtons()
        return widget

    # ============================================================================
    # Matplotlib Implementations
    # ============================================================================

    @staticmethod
    def _create_temp_precip_matplotlib(
        data: pd.DataFrame,
        temp1_col: str,
        temp2_col: str,
        precip_col: str,
        x_labels: list[tuple[int, str]],
        title: str,
        label1: str,
        label2: str,
        color1: str,
        color2: str,
    ) -> FigureCanvasQTAgg:
        """
        Create temperature/precipitation chart using Matplotlib.

        Args:
            data: DataFrame with weather data
            temp1_col: Column name for first temperature dataset
            temp2_col: Column name for second temperature dataset
            precip_col: Column name for precipitation data
            x_labels: List of (index, label) tuples for x-axis tick labels
            title: Chart title
            label1: Label for first temperature line
            label2: Label for second temperature line
            color1: Hex color code for first temperature line
            color2: Hex color code for second temperature line

        Returns:
            FigureCanvasQTAgg: Matplotlib canvas with dual-axis temperature and precipitation chart
        """
        # Prepare data
        x_data = list(range(len(data)))
        temp_data1 = data[temp1_col].values
        temp_data2 = data[temp2_col].values
        precip_data = data[precip_col].values

        # Calculate aligned axis ranges
        temp_min = min(temp_data1.min(), temp_data2.min())
        temp_max = max(temp_data1.max(), temp_data2.max())
        precip_min = 0
        precip_max = precip_data.max() if len(precip_data) > 0 else 10
        # Get nice ranges for both axes
        temp_nice_min, temp_nice_max, temp_interval = WeatherChart.get_nice_axis_range(
            temp_min, temp_max
        )
        precip_nice_min, precip_nice_max, precip_interval = (
            WeatherChart.get_nice_axis_range(precip_min, precip_max)
        )
        # Calculate the number of ticks for each axis
        temp_num_ticks = int((temp_nice_max - temp_nice_min) / temp_interval) + 1
        precip_num_ticks = (
            int((precip_nice_max - precip_nice_min) / precip_interval) + 1
        )
        # Extend the axis with fewer ticks to match the one with more ticks
        target_num_ticks = max(temp_num_ticks, precip_num_ticks)
        temp_nice_max = temp_nice_min + temp_interval * (target_num_ticks - 1)
        precip_nice_max = precip_nice_min + precip_interval * (target_num_ticks - 1)

        # Create the figure
        fig = Figure(figsize=(8, 4) if not x_labels else (10, 5), dpi=100)
        canvas = FigureCanvasQTAgg(fig)
        canvas.setMinimumHeight(300)
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx()

        # Plot temperature lines on ax1
        ax1.plot(x_data, temp_data1, color=color1, linewidth=2.5, label=label1)
        ax1.plot(x_data, temp_data2, color2, linewidth=2, linestyle="--", label=label2)

        # Configure ax1 (temperature)
        if x_labels:
            ax1.set_xlabel("Time Period")
            ax1.set_ylabel("Temperature (°C)", color=color1)
            ax1.tick_params(axis="y", labelcolor=color1)
            ax1.set_ylim((temp_nice_min, temp_nice_max))
            ax1.set_yticks(
                np.arange(
                    temp_nice_min, temp_nice_max + temp_interval / 2, temp_interval
                )
            )
            positions = [pos for pos, _ in x_labels]
            labels = [label for _, label in x_labels]
            ax1.set_xticks(positions, labels)
        else:
            ax1.set_xlabel("Hour")
            ax1.set_ylabel("Temperature (°C)", color=color1)
            ax1.set_ylim((temp_nice_min, temp_nice_max))
            ax1.set_yticks(
                np.arange(
                    temp_nice_min, temp_nice_max + temp_interval / 2, temp_interval
                )
            )
            ax1.set_xlim((-0.5, 23.5))
            ax1.set_xticks(np.arange(0, 24, 3))
        ax1.set_title(title)
        ax1.grid(True, alpha=0.3)

        # Add precipitation bars to ax2
        bar_width = 1.0 if not x_labels else 0.4
        ax2.bar(
            x_data,
            precip_data,
            width=bar_width,
            color="#3498db",
            alpha=0.5,
            label="Precipitation",
        )

        # Configure ax2 (precipitation)
        ax2.set_ylabel("Precipitation (mm)", color="#3498db")
        ax2.tick_params(axis="y", labelcolor="#3498db")
        ax2.set_ylim((precip_nice_min, precip_nice_max))
        ax2.set_yticks(
            np.arange(
                precip_nice_min, precip_nice_max + precip_interval / 2, precip_interval
            )
        )

        ax1.set_title(title)
        fig.tight_layout()
        return canvas

    @staticmethod
    def _create_wind_matplotlib(
        wind_data: np.ndarray, x_data: list[int]
    ) -> FigureCanvasQTAgg:
        """
        Create a wind speed chart using Matplotlib.

        Args:
            wind_data: Array of wind speed values in km/h
            x_data: List of x-axis positions (indices)

        Returns:
            FigureCanvasQTAgg: Matplotlib canvas with wind speed bar chart
        """
        # Create the figure
        fig = Figure(figsize=(8, 3), dpi=100)
        canvas = FigureCanvasQTAgg(fig)
        canvas.setMinimumHeight(250)
        ax = fig.add_subplot(111)
        # Plot wind bars
        ax.bar(x_data, wind_data, color="#2ecc71", alpha=0.6)
        # Configure axis
        ax.set_xlabel("Hour")
        ax.set_ylabel("Wind Speed (km/h)")
        ax.set_xlim((-0.5, 23.5))
        ax.set_xticks(np.arange(0, 24, 1))
        ax.set_title("Wind Speed")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        return canvas
