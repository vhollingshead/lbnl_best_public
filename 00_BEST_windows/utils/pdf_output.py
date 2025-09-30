import pandas as pd
import json
import os
import datetime
from PyQt6.QtGui import QTextDocument, QPageLayout
from PyQt6.QtCore import QMarginsF
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QApplication

SAVE_FILE = "recent_session.json"
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

import reportlab
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image
import json
import pandas as pd
from PyQt6.QtWidgets import QMessageBox
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import plotly.graph_objects as go
import plotly.io as pio

from utils.save_progress import get_user_data_dir

import os, sys, subprocess

from pathlib import Path
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

def open_pdf(filepath):
    if sys.platform.startswith("darwin"):  # macOS
        subprocess.run(["open", filepath])
    elif os.name == "nt":  # Windows
        os.startfile(filepath)


def get_auto_text(df: pd.DataFrame):

    data_dir = get_user_data_dir()
    json_folder = data_dir / "Saved Progress"

    excel_file_path_1 = json_folder / "key_values_in_excel.xlsx"
    key_values_in_excel = pd.read_excel(excel_file_path_1, sheet_name=None)

    final_energy_before = key_values_in_excel["values"].iloc[0, 1]
    final_energy_after = key_values_in_excel["values"].iloc[0, 2]
    final_energy_ibp = key_values_in_excel["values"].iloc[0, 3]
    final_energy_reduction = final_energy_before - final_energy_after
    final_energy_difference_ibp = final_energy_ibp - final_energy_after

    cement_intensity_before = key_values_in_excel["values"].iloc[1, 1]
    cement_intensity_after = key_values_in_excel["values"].iloc[1, 2]
    cement_intensity_ibp = key_values_in_excel["values"].iloc[1, 3]
    cement_intensity_reduction = cement_intensity_before - cement_intensity_after
    cement_intensity_difference_ibp = cement_intensity_ibp - cement_intensity_after

    total_emissions_before = key_values_in_excel["values"].iloc[2, 1]
    total_emissions_after = key_values_in_excel["values"].iloc[2, 2]
    total_emissions_ibp = key_values_in_excel["values"].iloc[2, 3]
    total_emissions_reduction = total_emissions_before - total_emissions_after
    total_emissions_difference_ibp = total_emissions_ibp - total_emissions_after

    cement_emissions_intensity_before = key_values_in_excel["values"].iloc[3, 1]
    cement_emissions_intensity_after = key_values_in_excel["values"].iloc[3, 2]
    cement_emissions_intensity_ibp = key_values_in_excel["values"].iloc[3, 3]
    cement_emissions_intensity_reduction = cement_emissions_intensity_before - cement_emissions_intensity_after
    cement_emissions_intensity_difference_ibp = cement_emissions_intensity_ibp - cement_emissions_intensity_after

    # Helper functions
    def fmt_num(x, decimals=2):
        try:
            return f"{float(x):,.{decimals}f}"
        except Exception:
            return "0"

    def rel_phrase(diff, unit):
        """Return colored higher/lower/equal phrase."""
        try:
            d = float(diff)
        except Exception:
            d = 0.0
        if d < 0:
            return f"<b><font color='red'>{fmt_num(abs(d))} {unit} higher</font></b>"
        elif d > 0:
            return f"<b><font color='green'>{fmt_num(abs(d))} {unit} lower</font></b>"
        else:
            return "<b><font color='black'>equal to</font></b>"

    # Sentences
    text = (f"After applying your selected measures, your facility's final energy is reduced by "
        f"<b><font color='red'>{fmt_num(final_energy_reduction,1)} TJ</font></b> and is now "
        f"{rel_phrase(final_energy_difference_ibp, 'TJ')} than the International Best Practice value; "
        f"meanwhile, carbon dioxide emissions is reduced by "
        f"<b><font color='red'>{fmt_num(total_emissions_reduction,0)} tCO<sub>2</sub></font></b> and is now "
        f"{rel_phrase(total_emissions_difference_ibp, 'tCO<sub>2</sub>')} than the International Best Practice value.")

    return text

def df_to_table_part2(df: pd.DataFrame, title: str):
        styles = getSampleStyleSheet()

        df_display = df.copy().fillna("")

        # Paragraph style for table cells
        cell_style = ParagraphStyle(
            name="TableCell",
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            wordWrap="CJK",   # enables wrapping
            alignment=1
        )
        header_style = ParagraphStyle(
            name="TableHeader",
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11,
            alignment=1
        )

        page_width, page_height = LETTER
        usable_width = page_width - 2 * 72  # 1-inch margins

        # Build table data with header row as Paragraphs
        data = [
            [Paragraph(str(col), header_style) for col in df_display.columns]
        ]
        for row in df_display.to_numpy():
            data.append([Paragraph(str(x), cell_style) for x in row])

        # Compute column widths (simple even split)
        ncols = max(1, len(df_display.columns))
        col_width = usable_width / ncols
        col_widths = [col_width] * ncols

        # Table with repeating header
        tbl = Table(data, colWidths=col_widths, repeatRows=1)

        # Style
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F0F0F0")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LINEABOVE", (0, 0), (-1, 0), 0.75, colors.black),
            ("LINEBELOW", (0, 0), (-1, 0), 0.75, colors.black),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CCCCCC")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FBFBFB")]),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),

            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))

        # Title + table
        return [
            Paragraph(title, styles["Heading3"]),
            Spacer(1, 6),
            tbl,
            Spacer(1, 12),
        ]

def df_to_table_input_summary(df: pd.DataFrame, title: str):
        styles = getSampleStyleSheet()

        df_display = df.copy().fillna("")

        # Paragraph style for table cells
        cell_style = ParagraphStyle(
            name="TableCell",
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            wordWrap="CJK",   # enables wrapping
            # center vertically
            spaceBefore=12,
            spaceAfter=12
        )
        header_style = ParagraphStyle(
            name="TableHeader",
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11,
            alignment=1, # center
            spaceBefore=12,
            spaceAfter=12
        )

        page_width, page_height = LETTER
        usable_width = page_width - 2 * 72  # 1-inch margins

        # Build table data with header row as Paragraphs
        data = [
            [Paragraph(str(col), header_style) for col in df_display.columns]
        ]
        for row in df_display.to_numpy():
            data.append([Paragraph(str(x), cell_style) for x in row])

        # Compute column widths (simple even split)
        ncols = max(1, len(df_display.columns))
        col_width = usable_width / ncols
        col_widths = [col_width] * ncols

        # Table with repeating header
        tbl = Table(data, colWidths=col_widths, repeatRows=1)

        # Style
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F0F0F0")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LINEABOVE", (0, 0), (-1, 0), 0.75, colors.black),
            ("LINEBELOW", (0, 0), (-1, 0), 0.75, colors.black),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CCCCCC")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FBFBFB")]),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))

        # Title + table
        return [
            Paragraph(title, styles["Heading3"]),
            Spacer(1, 6),
            tbl,
            Spacer(1, 12),
        ]

def generate_part1_report(self):
    data_dir = get_user_data_dir()
    graphs_dir = data_dir / "Graphs"

    OUTPUT_FILE_PATH = data_dir / f"Part1_BEST_Report_Output_{timestamp}.pdf"
    OUTPUT_FILE = str(OUTPUT_FILE_PATH)

    # Load Graphs
    graph_1 = graphs_dir / "Energy Benchmark.png"
    graph_2 = graphs_dir / "Direct Energy CO2 Emissions Benchmark.png"
    graph_3 = graphs_dir / "Indirect Energy CO2 Emissions Benchmark.png"
    graph_4 = graphs_dir / "Total CO2 Emissions Benchmark.png"
    graph_5 = graphs_dir / "energy benchmark by process.png"
    graph_6 = graphs_dir / "energy benchmark by process normalized.png"
    graph_7 = graphs_dir / "final energy consumption.png"
    graph_8 = graphs_dir / "primary energy consumption.png"
    graph_9 = graphs_dir / "energy cost.png"
    graph_10 = graphs_dir / "final energy by process.png"
    graph_11 = graphs_dir / "primary energy by process.png"
    graph_12 = graphs_dir / "energy cost by process.png"

    # Create PDF with ReportLab
    doc = SimpleDocTemplate(OUTPUT_FILE, pagesize=LETTER)
    styles = getSampleStyleSheet()

    page_width, page_height = LETTER
    usable_width = page_width - 2 * 72  # 1-inch margins

    elements = []

    elements.append(Paragraph("Part 1 BEST Report ", styles['Title']))
    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Energy Benchmark", styles['Heading2']))
    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))
    elements.append(Image(graph_1, width=usable_width, height=usable_width*0.56))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Direct Energy CO2 Emissions Benchmark", styles['Heading2']))
    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))
    elements.append(Image(graph_2, width=usable_width, height=usable_width*0.56))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Indirect Energy CO2 Emissions Benchmark", styles['Heading2']))
    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))
    elements.append(Image(graph_3, width=usable_width, height=usable_width*0.56))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Total CO2 Emissions Benchmark", styles['Heading2']))
    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))
    elements.append(Image(graph_4, width=usable_width, height=usable_width*0.56))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Energy Benchmark by Process", styles['Heading2']))
    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))
    elements.append(Image(graph_5, width=usable_width, height=usable_width*0.56))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Energy Benchmark by Process Normalized", styles['Heading2']))
    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))
    elements.append(Image(graph_6, width=usable_width, height=usable_width*0.56))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Final Energy Consumption", styles['Heading2']))
    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))
    elements.append(Image(graph_7, width=usable_width, height=usable_width*0.56))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Primary Energy Consumption", styles['Heading2']))
    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))
    elements.append(Image(graph_8, width=usable_width, height=usable_width*0.56))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Energy Cost", styles['Heading2']))
    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))
    elements.append(Image(graph_9, width=usable_width, height=usable_width*0.56))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Final Energy by Process", styles['Heading2']))
    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))
    elements.append(Image(graph_10, width=usable_width, height=usable_width*0.56))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Primary Energy by Process", styles['Heading2']))
    elements.append(Image(graph_11, width=usable_width, height=usable_width*0.56))
    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Share of Energy Cost by Process Step", styles['Heading2']))
    elements.append(Image(graph_12, width=usable_width, height=usable_width*0.56))
    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))

    try:
        doc.build(elements)
    except Exception as e:
        print("PDF generation failed:", e)
        return

    QMessageBox.information(self, "Report Saved", f"Part 1 Report saved successfully.\n After review, please continue with Part 2.")
    open_pdf(OUTPUT_FILE)

def generate_part_2_report(self):

    filename="Saved_BEST_Report_Progress.json"
    data_dir = get_user_data_dir()
    json_folder = data_dir / "Saved Progress"

    graphs_dir = data_dir / "Graphs"

    OUTPUT_FILE_PATH = data_dir / f"BEST_Report_Part2_{timestamp}.pdf"
    OUTPUT_FILE = str(OUTPUT_FILE_PATH)

    # graph_1 = graphs_dir / "Energy Benchmark.png"
    # graph_2 = graphs_dir / "Direct Energy CO2 Emissions Benchmark.png"
    # graph_3 = graphs_dir / "Indirect Energy CO2 Emissions Benchmark.png"
    # graph_4 = graphs_dir / "Total CO2 Emissions Benchmark.png"
    # graph_5 = graphs_dir / "emissions waterfall.png"
    # graph_6 = graphs_dir / "energy waterfall.png"
    # graph_7 = graphs_dir / "abatement cost.png"

    graph_1 = graphs_dir / "energy benchmark after measures.png"
    graph_2 = graphs_dir / "direct energy co2 emissions benchmark after measures.png"
    graph_3 = graphs_dir / "indirect energy co2 emissions benchmark after measures.png"
    graph_4 = graphs_dir / "total co2 emissions benchmark after measures.png"
    graph_5 = graphs_dir / "emissions waterfall.png"
    graph_6 = graphs_dir / "energy waterfall.png"
    graph_7 = graphs_dir / "abatement cost.png"


    # Load Excel (all sheets)
    excel_file_path_1 = json_folder / "key_values_in_excel.xlsx"
    key_values_in_excel = pd.read_excel(excel_file_path_1, sheet_name=None)

    # Create PDF with ReportLab
    doc = SimpleDocTemplate(OUTPUT_FILE, pagesize=LETTER)
    styles = getSampleStyleSheet()

    page_width, page_height = LETTER
    usable_width = page_width - 2 * 72  # 1-inch margins

    elements = []

    elements.append(Paragraph("BEST Report ", styles['Title']))
    elements.append(Spacer(1, 12))

    auto_text = get_auto_text(key_values_in_excel)
    # add paragraph below
    elements.append(Paragraph(auto_text, styles['Normal']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Key Performance Values", styles['Heading2']))

    for sheet_name, df in key_values_in_excel.items():
        df.columns = ["Performance Metric", "Your facility before applying measures", "Your facility after applying measures", "International Best Practice"]

        elements.extend(df_to_table_part2(df, ""))
        elements.append(Spacer(1, 12))

    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Energy Benchmark", styles['Heading2']))
    elements.append(Image(graph_1, width=usable_width*.75, height=usable_width*.75*0.56))

    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Direct Energy CO2 Emissions Benchmark", styles['Heading2']))
    elements.append(Image(graph_2, width=usable_width*.75, height=usable_width*.75*0.56))

    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Indirect Energy CO2 Emissions Benchmark", styles['Heading2']))

    elements.append(Image(graph_3, width=usable_width*.75, height=usable_width*.75*0.56))

    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Total CO2 Emissions Benchmark", styles['Heading2']))

    elements.append(Image(graph_4, width=usable_width*.75, height=usable_width*.75*0.56))

    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Final Energy Reduction by Measurement Category", styles['Heading2']))

    elements.append(Image(graph_5, width=usable_width*.75, height=usable_width*.75*0.56))

    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Total Carbon Dioxide Emissions Reduction by Measurement Category", styles['Heading2']))

    elements.append(Image(graph_6, width=usable_width*.75, height=usable_width*.75*0.56))

    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Marginal Abatement Cost Curve", styles['Heading2']))

    elements.append(Image(graph_7, width=usable_width*.75, height=usable_width*.75*0.56))

    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))

    try:
        doc.build(elements)
    except Exception as e:
        print("PDF generation failed:", e)
        return

    return OUTPUT_FILE
    

def generate_report_reportlab(self):

    filename="Saved_BEST_Report_Progress.json"
    data_dir = get_user_data_dir()
    json_folder = data_dir / "Saved Progress"
    OUTPUT_FILE_PATH = data_dir / f"User_Input_Summary_{timestamp}.pdf"
    OUTPUT_FILE = str(OUTPUT_FILE_PATH)

    excel_file_path_1 = json_folder / "report_in_excel.xlsx"
    report_in_excel_sheets = pd.read_excel(excel_file_path_1, sheet_name=None) 

    # Create PDF with ReportLab
    doc = SimpleDocTemplate(OUTPUT_FILE, pagesize=LETTER)
    styles = getSampleStyleSheet()

    page_width, page_height = LETTER
    usable_width = page_width - 2 * 72  # 1-inch margins

    elements = []

    elements.append(Paragraph("BEST Report ", styles['Title']))
    elements.append(Spacer(1, 12))
    # add paragraph below
    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("User Input Summary", styles['Heading2']))

    for sheet_name, df in report_in_excel_sheets.items():
        # remove first row
        df = df.iloc[1:]
        df.columns = ["Field", "Value"]
        # add first sheet in excel file
        elements.extend(df_to_table_input_summary(df, sheet_name))
        elements.append(Spacer(1, 12))

    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))

    # add table from excel
    # elements.extend(df_to_table(sheets_2, "Measures Output in Excel"))

    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))

    # add table from excel
    # elements.extend(df_to_table(sheets_3, "Measures DT Output in Excel"))

    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))
    #elements.append(Image(graph_path_process_co2_emissions_benchmark, width=600, height=300))

    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Calculations", styles['Heading2']))
    elements.append(Spacer(1, 12))
    # elements.append(Image(graph_path_process_co2_emissions_benchmark_normalized, width=600, height=300))
    elements.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod, nisl nec elementum lacinia, eros sem dictum est, in fringilla justo sapien non eros. Quisque ultrices turpis vel nibh fermentum, vel scelerisque nulla dictum. Morbi dapibus, lorem vel consequat volutpat, sapien sem facilisis velit, at pulvinar lorem mauris a metus. Fusce vel magna sit amet neque aliquam pulvinar sed non leo. Donec viverra, magna sed hendrerit bibendum, ligula erat posuere purus, vitae luctus velit ipsum in nisl. Sed eget ipsum justo. Pellentesque euismod, mauris id sodales bibendum, nisl nunc volutpat magna, a euismod magna orci vitae elit.", styles['Normal']))
    elements.append(Spacer(1, 12))

    try:
        doc.build(elements)
    except Exception as e:
        print("PDF generation failed:", e)
        return

    print(f"PDF report generated as '{OUTPUT_FILE}'")
    return OUTPUT_FILE



def final_report_pdf(self):
    data_dir = get_user_data_dir()
    part2_report = generate_part_2_report(self)
    user_summary_report = generate_report_reportlab(self)

    QMessageBox.information(self, "Report Saved", f"Reports saved successfully.\nPlease find your files here: {data_dir}")
    
    QApplication.quit()
    open_pdf(user_summary_report)
    open_pdf(part2_report)

    print(f"PDF report generation successful")