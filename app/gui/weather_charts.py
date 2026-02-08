"""Weather chart creation utilities supporting both pyqtgraph and matplotlib."""

import numpy as np
import pandas as pd
import pyqtgraph as pg
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from pyqtgraph import PlotWidget


def get_nice_axis_range(data_min: float, data_max: float):
    """Calculate a nice range with round tick intervals."""
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


class WeatherCharts:
    """Factory class for creating weather visualization charts."""

    def __init__(self, use_pyqtgraph: bool = True):
        """
        Initialize the chart factory.

        Args:
            use_pyqtgraph: If True, use pyqtgraph backend; otherwise matplotlib
        """
        self.use_pyqtgraph = use_pyqtgraph
        if self.use_pyqtgraph:
            pg.setConfigOptions(antialias=True)

    def create_temperature_precipitation_chart(
        self, hourly_data: pd.DataFrame
    ) -> PlotWidget | FigureCanvasQTAgg:
        """
        Create a temperature and precipitation dual-axis chart.

        Args:
            hourly_data: DataFrame with hourly weather data containing 'temperature' and 'precipitation' columns

        Returns:
            PlotWidget (if using pyqtgraph) or FigureCanvasQTAgg (if using matplotlib)
        """
        if self.use_pyqtgraph:
            return self._create_temp_precip_chart_pyqtgraph(hourly_data)
        else:
            hours = list(range(len(hourly_data)))
            return self._create_temp_precip_chart_matplotlib(hourly_data, hours)

    def create_wind_speed_chart(
        self, hourly_data: pd.DataFrame
    ) -> PlotWidget | FigureCanvasQTAgg:
        """
        Create a wind speed bar chart.

        Args:
            hourly_data: DataFrame with hourly weather data containing 'wind_speed' column

        Returns:
            PlotWidget (if using pyqtgraph) or FigureCanvasQTAgg (if using matplotlib)
        """
        if self.use_pyqtgraph:
            return self._create_wind_chart_pyqtgraph(hourly_data)
        else:
            hours = list(range(len(hourly_data)))
            return self._create_wind_chart_matplotlib(hourly_data, hours)

    @staticmethod
    def _create_temp_precip_chart_pyqtgraph(df: pd.DataFrame) -> PlotWidget:
        """
        Create a temperature and precipitation chart using pyqtgraph.
        Args:
            df: DataFrame with hourly weather data
        Returns:
            PlotWidget with dual-axis chart
        """
        widget = PlotWidget()
        widget.setBackground("w")
        widget.setMinimumHeight(300)
        widget.showGrid(x=True, y=True, alpha=0.3)
        widget.setLabel("left", "Temperature", units="°C", color="#e74c3c")
        widget.setLabel("right", "Precipitation", units="mm", color="#3498db")
        widget.setLabel("bottom", "Hour")
        widget.setTitle("Temperature & Precipitation")
        widget.setMouseEnabled(x=False, y=False)
        widget.setMenuEnabled(False)
        widget.hideButtons()

        # Create hours for x-axis
        hours = [i for i in range(len(df))]

        # Calculate data ranges
        temp_min = min(df["temperature"].min(), df["apparent_temperature"].min())
        temp_max = max(df["temperature"].max(), df["apparent_temperature"].max())
        precip_min, precip_max = 0, df["precipitation"].max()
        temp_nice_min, temp_nice_max, temp_interval = get_nice_axis_range(
            temp_min, temp_max
        )
        precip_nice_min, precip_nice_max, precip_interval = get_nice_axis_range(
            precip_min, precip_max
        )
        # Calculate the number of ticks for each axis
        temp_num_ticks = int((temp_nice_max - temp_nice_min) / temp_interval) + 1
        precip_num_ticks = (
            int((precip_nice_max - precip_nice_min) / precip_interval) + 1
        )
        target_num_ticks = max(temp_num_ticks, precip_num_ticks)
        # Extend the axis with fewer ticks
        temp_nice_max = temp_nice_min + temp_interval * (target_num_ticks - 1)
        precip_nice_max = precip_nice_min + precip_interval * (target_num_ticks - 1)
        # Temperature line (left axis)
        temp_pen = pg.mkPen(color="#e74c3c", width=3)
        widget.plot(hours, df["temperature"].values, pen=temp_pen, name="Temperature")

        # Feel temperature line (left axis)
        feel_temp_pen = pg.mkPen(
            color="#ff9800", width=2, style=pg.QtCore.Qt.PenStyle.DashLine
        )
        widget.plot(
            hours,
            df["apparent_temperature"].values,
            pen=feel_temp_pen,
            name="Feels Like temperature",
        )

        widget.setYRange(temp_nice_min, temp_nice_max)
        # Precipitation bars (right axis)
        precip_viewbox = pg.ViewBox()
        widget.scene().addItem(precip_viewbox)
        widget.getAxis("right").linkToView(precip_viewbox)
        precip_viewbox.setXLink(widget)
        precip_viewbox.setMouseEnabled(x=False, y=False)

        def update_views():
            precip_viewbox.setGeometry(widget.getViewBox().sceneBoundingRect())
            precip_viewbox.linkedViewChanged(widget.getViewBox(), precip_viewbox.XAxis)

        update_views()
        widget.getViewBox().sigResized.connect(update_views)
        # Create the bar graph for precipitation
        width = 0.6
        bar_graph = pg.BarGraphItem(
            x=hours,
            height=df["precipitation"].values,
            width=width,
            brush="#3498db80",
            pen=pg.mkPen("#3498db", width=1),
        )
        precip_viewbox.addItem(bar_graph)
        # Set the precipitation axis range to align with the temperature axis
        precip_viewbox.setYRange(precip_nice_min, precip_nice_max)

        return widget

    @staticmethod
    def _create_wind_chart_pyqtgraph(df: pd.DataFrame) -> PlotWidget:
        """
        Create a wind speed chart using pyqtgraph.

        Args:
            df: DataFrame with hourly weather data

        Returns:
            PlotWidget with wind speed bars
        """
        widget = PlotWidget()
        widget.setBackground("w")
        widget.setMinimumHeight(250)
        widget.showGrid(x=True, y=True, alpha=0.3)
        widget.setLabel("left", "Wind Speed", units="km/h", color="#2ecc71")
        widget.setLabel("bottom", "Hour")
        widget.setTitle("Wind Speed")
        widget.setMouseEnabled(x=False, y=False)
        widget.setMenuEnabled(False)
        widget.hideButtons()
        # Create hours for x-axis
        hours = [i for i in range(len(df))]
        # Create a bar graph for wind speed
        bar_graph = pg.BarGraphItem(
            x=hours,
            height=df["wind_speed"].values,
            width=0.8,
            brush="#2ecc7180",
            pen=pg.mkPen("#2ecc71", width=1),
        )
        widget.addItem(bar_graph)
        # Rather weird. Arguments are shown in the IDE as r, padding but interpreted as min, max, optionally padding. Overload?
        widget.setXRange(0, 23)
        return widget

    @staticmethod
    def _create_temp_precip_chart_matplotlib(
        df: pd.DataFrame, hours: list
    ) -> FigureCanvasQTAgg:
        """
        Create a temperature and precipitation chart using matplotlib.

        Args:
            df: DataFrame with hourly weather data
            hours: List of hour indices

        Returns:
            FigureCanvasQTAgg with dual-axis chart
        """
        # Calculate data ranges
        temp_min = min(df["temperature"].min(), df["apparent_temperature"].min())
        temp_max = max(df["temperature"].max(), df["apparent_temperature"].max())
        precip_min, precip_max = 0, df["precipitation"].max()
        temp_nice_min, temp_nice_max, temp_interval = get_nice_axis_range(
            temp_min, temp_max
        )
        precip_nice_min, precip_nice_max, precip_interval = get_nice_axis_range(
            precip_min, precip_max
        )

        # Calculate the number of ticks for each axis
        temp_num_ticks = int((temp_nice_max - temp_nice_min) / temp_interval) + 1
        precip_num_ticks = (
            int((precip_nice_max - precip_nice_min) / precip_interval) + 1
        )
        target_num_ticks = max(temp_num_ticks, precip_num_ticks)

        # Extend the axis with fewer ticks
        temp_nice_max = temp_nice_min + temp_interval * (target_num_ticks - 1)
        precip_nice_max = precip_nice_min + precip_interval * (target_num_ticks - 1)

        fig = Figure(figsize=(8, 4), dpi=100)
        canvas = FigureCanvasQTAgg(fig)
        canvas.setMinimumHeight(300)
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx()
        # Temperature line
        ax1.plot(
            hours,
            df["temperature"].values,
            color="#e74c3c",
            linewidth=2.5,
            label="Temperature",
        )
        # apparent temperature line
        ax1.plot(
            hours,
            df["apparent_temperature"].values,
            color="#ff9800",
            linewidth=2,
            linestyle="--",
            label="Feels Like temperature",
        )
        ax1.set_xlabel("Hour")
        ax1.set_xlim(-0.5, 23.5)
        ax1.set_xticks(np.arange(0, 24, 1))
        ax1.set_ylabel("Temperature (°C)", color="#e74c3c")
        ax1.tick_params(axis="y", labelcolor="#e74c3c")
        ax1.grid(True, alpha=0.3)
        # Set the temperature axis range to match pyqtgraph
        ax1.set_ylim(temp_nice_min, temp_nice_max)
        ax1.set_yticks(
            np.arange(temp_nice_min, temp_nice_max + temp_interval / 2, temp_interval)
        )
        # Precipitation bars
        ax2.bar(
            hours,
            df["precipitation"].values,
            alpha=0.5,
            color="#3498db",
            label="Precipitation",
        )
        ax2.set_ylabel("Precipitation (mm)", color="#3498db")
        ax2.tick_params(axis="y", labelcolor="#3498db")
        ax2.set_ylim(precip_nice_min, precip_nice_max)
        ax2.set_yticks(
            np.arange(
                precip_nice_min, precip_nice_max + precip_interval / 2, precip_interval
            )
        )
        ax1.set_title("Temperature & Precipitation")
        fig.tight_layout()
        return canvas

    @staticmethod
    def _create_wind_chart_matplotlib(
        df: pd.DataFrame, hours: list
    ) -> FigureCanvasQTAgg:
        """
        Create a wind speed chart using matplotlib.

        Args:
            df: DataFrame with hourly weather data
            hours: List of hour indices

        Returns:
            FigureCanvasQTAgg with wind speed bars
        """
        fig = Figure(figsize=(8, 3), dpi=100)
        canvas = FigureCanvasQTAgg(fig)
        canvas.setMinimumHeight(250)
        ax = fig.add_subplot(111)
        ax.bar(hours, df["wind_speed"].values, color="#2ecc71", alpha=0.6)
        ax.set_xlabel("Hour")
        ax.set_ylabel("Wind Speed (km/h)")
        ax.set_title("Wind Speed")
        ax.set_xlim(-0.5, 23.5)
        ax.set_xticks(np.arange(0, 24, 1))
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        return canvas

    def set_backend(self, use_pyqtgraph: bool):
        """
        Switch between charting backends.

        Args:
            use_pyqtgraph: If True, use pyqtgraph; otherwise matplotlib
        """
        self.use_pyqtgraph = use_pyqtgraph
        if self.use_pyqtgraph:
            pg.setConfigOptions(antialias=True)
