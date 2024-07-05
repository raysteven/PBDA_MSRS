from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import BaseDocTemplate, SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle, PageTemplate, Frame, Flowable
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import utils, colors
from reportlab.lib.units import inch
from reportlab.lib.colors import Color, HexColor

from reportlab.lib import colors
from reportlab.platypus.flowables import KeepTogether
from reportlab.pdfbase.pdfmetrics import stringWidth

import json
import os

# Custom page size and margins
PAGE_WIDTH, PAGE_HEIGHT = A4
TOP_MARGIN = 1.7 * inch
BOTTOM_MARGIN = 0.29 * inch
LEFT_MARGIN = 0.5 * inch
RIGHT_MARGIN = 0.5 * inch

TITLE_TEXT = "Amino Acid Profile"
TITLE_FONT = "Helvetica-Bold"
TITLE_FONT_SIZE = 16

TITLE_WIDTH = stringWidth(TITLE_TEXT, TITLE_FONT, TITLE_FONT_SIZE)
TITLE_HEIGHT = TITLE_FONT_SIZE

AVAILABLE_PAGE_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN

TITLE_PADDING = 10
PATIENT_INFO_PADDING = 5

styles = getSampleStyleSheet()
#justified_paragraph = styles["Normal"]
#justified_paragraph.alignment = 4  # 4 corresponds to 'JUSTIFY'

#center_paragraph = styles["Normal"]
#center_paragraph.alignment = 1  # 1 corresponds to 'CENTER'

# Create a new style object for justified paragraph based on the existing Normal style
justified_paragraph = ParagraphStyle("Justified", parent=styles["Normal"])
justified_paragraph.alignment = 4  # 4 corresponds to 'JUSTIFY'

center_paragraph = ParagraphStyle("Centered", parent=styles["Normal"])
center_paragraph.alignment = 1  # 4 corresponds to 'JUSTIFY'


# Create a new style object for center-aligned paragraph based on the existing Normal style
imageTitle_style = ParagraphStyle("Centered", parent=styles["Normal"])
imageTitle_style.alignment = 1  # 1 corresponds to 'CENTER'
imageTitle_style.fontSize = 9

# Create a new style object for center-aligned paragraph based on the existing Normal style
imageCaption_style = ParagraphStyle("Centered", parent=styles["Normal"])
imageCaption_style.alignment = 1  # 1 corresponds to 'CENTER'
imageCaption_style.fontSize = 7
imageCaption_style.fontWeight = 'Normal'  # Set font weight to normal

# Create a new style object for center-aligned paragraph based on the existing Normal style
title_style = ParagraphStyle("Centered", parent=styles["Heading2"])
title_style.alignment = 1  # 1 corresponds to 'CENTER'
title_style.fontSize = 15

# Create a new style object for center-aligned paragraph based on the existing Normal style
left_paragraph = ParagraphStyle("Left", parent=styles["Normal"])
left_paragraph.alignment = 0  # 1 corresponds to 'CENTER'

class RepeatedTable(Flowable):
    """A custom Flowable that repeats a table at the start of each new page."""
    def __init__(self, table):
        Flowable.__init__(self)
        self.table = table

    def wrap(self, availWidth, availHeight):
        """Determines the space required by the table."""
        return self.table.wrap(availWidth, availHeight)

    def draw(self):
        """Draws the table on the canvas."""
        self.table.drawOn(self.canv, 0, 0)


def json_to_pdf(report_df, runfolder, workdir):
    for i in report_df.index:
        patient_id = report_df.at[i, "patient_id"]

        ##### Create out_folder
        out_folder = os.path.join(runfolder, patient_id)
        
        def get_parent_directory(path):
            return os.path.abspath(os.path.join(path, os.pardir))

        workdir_parent = get_parent_directory(workdir)

        outdir_path = os.path.join(workdir_parent, out_folder)
        # Check if the folder already exists
        if not os.path.exists(outdir_path):
            # Create the folder
            os.makedirs(outdir_path)


        json_file = f"{patient_id}_AminoAcidPanel.json"
        pdf_file = f"{patient_id}_AminoAcidPanel.pdf"

        sample_report_dir = os.path.join(outdir_path)

        json_file_path = os.path.join(outdir_path, json_file)
        pdf_file_path = os.path.join(outdir_path, pdf_file)

        # Open the JSON file
        with open(json_file_path, 'r') as f:
            # Load the JSON data
            data = json.load(f)

        metadata = data['metadata']
        test_result = data['test_result']

        # New file path for the corrected PDF using ReportLab
        pdf_file_path_rl_corrected = pdf_file_path

        # Patient Information
        patient_id_data = [
            [Paragraph("Name:", left_paragraph), Paragraph(":  "+metadata["Nama"],left_paragraph), Paragraph("Ref. Number",left_paragraph)],
            [Paragraph("Lab Number", left_paragraph), Paragraph(":  "+metadata["Lab Number"],left_paragraph), Paragraph(metadata["Ref. Number"],left_paragraph)],
            [Paragraph("Age", left_paragraph), Paragraph(":  "+str(metadata["Age"]),left_paragraph), None],
        ]
        patient_id_table_colWidths = [100, 300, 100]
        patient_id_table = Table(patient_id_data, colWidths=patient_id_table_colWidths)
        patient_id_table.setStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align images at the top of the cells
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Align images to the left
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),  # Padding at the bottom of the cells
            ('TOPPADDING', (0, 0), (-1, -1), 2),  # Padding at the top of the cells
            ('LEFTPADDING', (0, 0), (-1, -1), 2),  # Padding on the left of the cells
            ('RIGHTPADDING', (0, 0), (-1, -1), 2), 
        ])
        
        required_width, required_height = patient_id_table.wrap(PAGE_WIDTH, PAGE_HEIGHT)
        
        def myFirstPage(canvas, doc, table_data=patient_id_table):
            canvas.saveState()
            # Add the title for the first page
            canvas.setFont(TITLE_FONT, TITLE_FONT_SIZE)
            canvas.drawString((PAGE_WIDTH/2)-(TITLE_WIDTH/2), PAGE_HEIGHT-TOP_MARGIN-TITLE_HEIGHT, TITLE_TEXT)
            canvas.restoreState()

            table = table_data
            
            # Before positioning and drawing the table, calculate its required size
            required_width, required_height = table.wrap(PAGE_WIDTH, PAGE_HEIGHT)

            # Now that you have the dimensions, you can adjust the positioning as needed
            # For example, to position the table with the left margin and a specific top margin
            table_x_position = LEFT_MARGIN
            table_y_position = PAGE_HEIGHT - TOP_MARGIN - required_height - TITLE_HEIGHT - TITLE_PADDING # Adjust based on the table's height

            table.wrapOn(canvas, *doc.pagesize)
            table.drawOn(canvas, table_x_position, table_y_position)  # Adjust the coordinates as needed

            # Optionally, move the table down a bit if you need space for the title
            # This is handled by adjusting the frame in the document template or manually drawing the table lower

        def myLaterPages(canvas, doc, table_data=patient_id_table):
            canvas.saveState()
            # Here, you can add any header or footer that repeats on every pag

            table = table_data

            # Before positioning and drawing the table, calculate its required size
            required_width, required_height = table.wrap(PAGE_WIDTH, PAGE_HEIGHT)
            globals()['required_height'] = required_height

            # Now that you have the dimensions, you can adjust the positioning as needed
            # For example, to position the table with the left margin and a specific top margin
            table_x_position = LEFT_MARGIN
            table_y_position = PAGE_HEIGHT - TOP_MARGIN - required_height  # Adjust based on the table's height


            table.wrapOn(canvas, *doc.pagesize)
            table.drawOn(canvas, table_x_position, table_y_position)  # Adjust the coordinates as needed

            canvas.restoreState()
            # No need to move the table down since it starts at the top of these pages

        # Create a PDF document with ReportLab
        doc = SimpleDocTemplate(pdf_file_path_rl_corrected, pagesize=A4, leftMargin=LEFT_MARGIN, rightMargin=RIGHT_MARGIN, topMargin=TOP_MARGIN+required_height+PATIENT_INFO_PADDING, bottomMargin=BOTTOM_MARGIN)
        story = []


        styles = getSampleStyleSheet()


        story.append(Spacer(1, TITLE_HEIGHT))
        story.append(Spacer(1, TITLE_PADDING))
        story.append(Spacer(1, PATIENT_INFO_PADDING))

        # 
        #
        #
        #('BACKGROUND', (0,0), (2,0), HexColor("#90acdc")),
        #result_data = [

            #[Paragraph("<b>Essential</b>", center_paragraph), Paragraph("<b>Result (\u00B5mol/L)</b>",center_paragraph), Paragraph("<b>Reference Range</b>",center_paragraph)]

        #]
        result_data_table_colWidths = [(AVAILABLE_PAGE_WIDTH/5), (AVAILABLE_PAGE_WIDTH*3/5), (AVAILABLE_PAGE_WIDTH/5)]
        result_data_table_style = [
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Align images at the top of the cells
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Align images to the left
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),  # Padding at the bottom of the cells
            ('TOPPADDING', (0, 0), (-1, -1), 2),  # Padding at the top of the cells
            ('LEFTPADDING', (0, 0), (-1, -1), 2),  # Padding on the left of the cells
            ('RIGHTPADDING', (0, 0), (-1, -1), 2), 
        ]

        result_data_pg1 = [
            [Paragraph("<b>Essential</b>", center_paragraph), Paragraph("<b>Result (\u00B5mol/L)</b>",center_paragraph), Paragraph("<b>Reference Range</b>",center_paragraph)],
            [Paragraph(f"<b>Threonine (THR) </b>", center_paragraph), Image(os.path.join(sample_report_dir,"THR_graph.png"), width=277.32375, height=67.5), Paragraph(f"<b>{test_result['THR']['ref_value']}</b>",center_paragraph)],
            [Paragraph(test_result['THR']['result_interpretation'], justified_paragraph), None, None],
            [Paragraph(f"<b>Histidine (HIS) </b>", center_paragraph), Image(os.path.join(sample_report_dir,"HIS_graph.png"), width=277.32375, height=67.5), Paragraph(f"<b>{test_result['HIS']['ref_value']}</b>",center_paragraph)],
            [Paragraph(test_result['HIS']['result_interpretation'], justified_paragraph), None, None],
            [Paragraph(f"<b>Lysine (LYS) </b>", center_paragraph), Image(os.path.join(sample_report_dir,"LYS_graph.png"), width=277.32375, height=67.5), Paragraph(f"<b>{test_result['LYS']['ref_value']}</b>",center_paragraph)],
            [Paragraph(test_result['LYS']['result_interpretation'], justified_paragraph), None, None],
            [Paragraph(f"<b>Arginine (ARG) </b>", center_paragraph), Image(os.path.join(sample_report_dir,"ARG_graph.png"), width=277.32375, height=67.5), Paragraph(f"<b>{test_result['ARG']['ref_value']}</b>",center_paragraph)],
            [Paragraph(test_result['ARG']['result_interpretation'], justified_paragraph), None, None],
        ]


        result_data_table_colWidths = [(AVAILABLE_PAGE_WIDTH/5), (AVAILABLE_PAGE_WIDTH*3/5), (AVAILABLE_PAGE_WIDTH/5)]
        result_data_table_style_pg1 = [
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Align images at the top of the cells
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Align images to the left
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),  # Padding at the bottom of the cells
            ('TOPPADDING', (0, 0), (-1, -1), 2),  # Padding at the top of the cells
            ('LEFTPADDING', (0, 0), (-1, -1), 2),  # Padding on the left of the cells
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('BACKGROUND', (0,0), (2,0), HexColor("#90acdc")),
        ]
        

        for interpretation_cell_row_number in (2,4,6,8):
            result_data_interpretation_cell_merge = ('BACKGROUND', (0,interpretation_cell_row_number), (2,interpretation_cell_row_number), HexColor("#90acdc"))
            result_data_interpretation_cell_merge = ('SPAN', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number))
            result_data_interpretation_cell_bottom_padding  = ('BOTTOMPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 5)
            result_data_interpretation_cell_top_padding = ('TOPPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 10)
            result_data_interpretation_cell_left_padding = ('LEFTPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 20)
            result_data_interpretation_cell_right_padding = ('RIGHTPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 20)

            result_data_table_style_pg1.append(result_data_interpretation_cell_merge) 
            result_data_table_style_pg1.append(result_data_interpretation_cell_bottom_padding) 
            result_data_table_style_pg1.append(result_data_interpretation_cell_top_padding)
            result_data_table_style_pg1.append(result_data_interpretation_cell_left_padding)
            result_data_table_style_pg1.append(result_data_interpretation_cell_right_padding)


        result_data_table = Table(result_data_pg1, colWidths=result_data_table_colWidths)
        result_data_table.setStyle(result_data_table_style_pg1)
        story.append(result_data_table)
        story.append(PageBreak())

        result_data_pg2 = [
            [Paragraph("<b>Essential</b>", center_paragraph), Paragraph("<b>Result (\u00B5mol/L)</b>",center_paragraph), Paragraph("<b>Reference Range</b>",center_paragraph)],
            [Paragraph(f"<b>Methionine (MET) </b>", center_paragraph), Image(os.path.join(sample_report_dir,"MET_graph.png"), width=277.32375, height=67.5), Paragraph(f"<b>{test_result['MET']['ref_value']}</b>",center_paragraph)],
            [Paragraph(test_result['MET']['result_interpretation'], justified_paragraph), None, None],
            [Paragraph(f"<b>Valine (VAL) </b>", center_paragraph), Image(os.path.join(sample_report_dir,"VAL_graph.png"), width=277.32375, height=67.5), Paragraph(f"<b>{test_result['VAL']['ref_value']}</b>",center_paragraph)],
            [Paragraph(test_result['VAL']['result_interpretation'], justified_paragraph), None, None],
            [Paragraph(f"<b>Isoleucine (ILE) </b>", center_paragraph), Image(os.path.join(sample_report_dir,"ILE_graph.png"), width=277.32375, height=67.5), Paragraph(f"<b>{test_result['ILE']['ref_value']}</b>",center_paragraph)],
            [Paragraph(test_result['ILE']['result_interpretation'], justified_paragraph), None, None],
            [Paragraph(f"<b>Leucine (LEU) </b>", center_paragraph), Image(os.path.join(sample_report_dir,"LEU_graph.png"), width=277.32375, height=67.5), Paragraph(f"<b>{test_result['LEU']['ref_value']}</b>",center_paragraph)],
            [Paragraph(test_result['LEU']['result_interpretation'], justified_paragraph), None, None],
        ]

        result_data_table_style_pg2 = [
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Align images at the top of the cells
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Align images to the left
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),  # Padding at the bottom of the cells
            ('TOPPADDING', (0, 0), (-1, -1), 2),  # Padding at the top of the cells
            ('LEFTPADDING', (0, 0), (-1, -1), 2),  # Padding on the left of the cells
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('BACKGROUND', (0,0), (2,0), HexColor("#90acdc")),
        ]
        

        for interpretation_cell_row_number in (2,4,6,8):
            result_data_interpretation_cell_merge = ('BACKGROUND', (0,interpretation_cell_row_number), (2,interpretation_cell_row_number), HexColor("#90acdc"))
            result_data_interpretation_cell_merge = ('SPAN', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number))
            result_data_interpretation_cell_bottom_padding  = ('BOTTOMPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 5)
            result_data_interpretation_cell_top_padding = ('TOPPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 10)
            result_data_interpretation_cell_left_padding = ('LEFTPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 20)
            result_data_interpretation_cell_right_padding = ('RIGHTPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 20)

            result_data_table_style_pg2.append(result_data_interpretation_cell_merge) 
            result_data_table_style_pg2.append(result_data_interpretation_cell_bottom_padding) 
            result_data_table_style_pg2.append(result_data_interpretation_cell_top_padding)
            result_data_table_style_pg2.append(result_data_interpretation_cell_left_padding)
            result_data_table_style_pg2.append(result_data_interpretation_cell_right_padding)

        result_data_table2 = Table(result_data_pg2, colWidths=result_data_table_colWidths)
        result_data_table2.setStyle(result_data_table_style_pg2)
        story.append(result_data_table2)
        story.append(PageBreak())

        result_data_pg2a = [
            [Paragraph("<b>Essential</b>", center_paragraph), Paragraph("<b>Result (\u00B5mol/L)</b>",center_paragraph), Paragraph("<b>Reference Range</b>",center_paragraph)],
            [Paragraph(f"<b>Phenylalanine (PHE) </b>", center_paragraph), Image(os.path.join(sample_report_dir,"PHE_graph.png"), width=277.32375, height=67.5), Paragraph(f"<b>{test_result['PHE']['ref_value']}</b>",center_paragraph)],
            [Paragraph(test_result['PHE']['result_interpretation'], justified_paragraph), None, None],
            [Paragraph(f"<b>Tryptophan (TRP) </b>", center_paragraph), Image(os.path.join(sample_report_dir,"TRP_graph.png"), width=277.32375, height=67.5), Paragraph(f"<b>{test_result['TRP']['ref_value']}</b>",center_paragraph)],
            [Paragraph(test_result['TRP']['result_interpretation'], justified_paragraph), None, None],
        ]



        result_data_table_style_pg2a = [
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Align images at the top of the cells
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Align images to the left
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),  # Padding at the bottom of the cells
            ('TOPPADDING', (0, 0), (-1, -1), 2),  # Padding at the top of the cells
            ('LEFTPADDING', (0, 0), (-1, -1), 2),  # Padding on the left of the cells
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('BACKGROUND', (0,0), (2,0), HexColor("#90acdc")),
        ]
        

        for interpretation_cell_row_number in (2,4):
            result_data_interpretation_cell_merge = ('BACKGROUND', (0,interpretation_cell_row_number), (2,interpretation_cell_row_number), HexColor("#90acdc"))
            result_data_interpretation_cell_merge = ('SPAN', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number))
            result_data_interpretation_cell_bottom_padding  = ('BOTTOMPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 5)
            result_data_interpretation_cell_top_padding = ('TOPPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 10)
            result_data_interpretation_cell_left_padding = ('LEFTPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 20)
            result_data_interpretation_cell_right_padding = ('RIGHTPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 20)

            result_data_table_style_pg2a.append(result_data_interpretation_cell_merge) 
            result_data_table_style_pg2a.append(result_data_interpretation_cell_bottom_padding) 
            result_data_table_style_pg2a.append(result_data_interpretation_cell_top_padding)
            result_data_table_style_pg2a.append(result_data_interpretation_cell_left_padding)
            result_data_table_style_pg2a.append(result_data_interpretation_cell_right_padding)

        result_data_table2a = Table(result_data_pg2a, colWidths=result_data_table_colWidths)
        result_data_table2a.setStyle(result_data_table_style_pg2a)
        story.append(result_data_table2a)

        story.append(Spacer(1, 24))

        result_data_pg2b = [
            [Paragraph("<b>Non-Essential</b>", center_paragraph), Paragraph("<b>Result (\u00B5mol/L)</b>",center_paragraph), Paragraph("<b>Reference Range</b>",center_paragraph)],
            [Paragraph(f"<b>Glutamic Acid (GLU) </b>", center_paragraph), Image(os.path.join(sample_report_dir,"GLU_graph.png"), width=277.32375, height=67.5), Paragraph(f"<b>{test_result['GLU']['ref_value']}</b>",center_paragraph)],
            [Paragraph(test_result['GLU']['result_interpretation'], justified_paragraph), None, None],
            [Paragraph(f"<b>Proline (PRO) </b>", center_paragraph), Image(os.path.join(sample_report_dir,"PRO_graph.png"), width=277.32375, height=67.5), Paragraph(f"<b>{test_result['PRO']['ref_value']}</b>",center_paragraph)],
            [Paragraph(test_result['PRO']['result_interpretation'], justified_paragraph), None, None],
        ]

        result_data_table_style_pg2b = [
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Align images at the top of the cells
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Align images to the left
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),  # Padding at the bottom of the cells
            ('TOPPADDING', (0, 0), (-1, -1), 2),  # Padding at the top of the cells
            ('LEFTPADDING', (0, 0), (-1, -1), 2),  # Padding on the left of the cells
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('BACKGROUND', (0,0), (2,0), HexColor("#90acdc")),
        ]


        for interpretation_cell_row_number in (2,4):
            result_data_interpretation_cell_merge = ('BACKGROUND', (0,interpretation_cell_row_number), (2,interpretation_cell_row_number), HexColor("#90acdc"))
            result_data_interpretation_cell_merge = ('SPAN', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number))
            result_data_interpretation_cell_bottom_padding  = ('BOTTOMPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 5)
            result_data_interpretation_cell_top_padding = ('TOPPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 10)
            result_data_interpretation_cell_left_padding = ('LEFTPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 20)
            result_data_interpretation_cell_right_padding = ('RIGHTPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 20)

            result_data_table_style_pg2b.append(result_data_interpretation_cell_merge) 
            result_data_table_style_pg2b.append(result_data_interpretation_cell_bottom_padding) 
            result_data_table_style_pg2b.append(result_data_interpretation_cell_top_padding)
            result_data_table_style_pg2b.append(result_data_interpretation_cell_left_padding)
            result_data_table_style_pg2b.append(result_data_interpretation_cell_right_padding)

        result_data_table2a = Table(result_data_pg2b, colWidths=result_data_table_colWidths)
        result_data_table2a.setStyle(result_data_table_style_pg2b)
        story.append(result_data_table2a)


        story.append(PageBreak())


        result_data_pg3 = [
            [Paragraph("<b>Non-Essential</b>", center_paragraph), Paragraph("<b>Result (\u00B5mol/L)</b>",center_paragraph), Paragraph("<b>Reference Range</b>",center_paragraph)],
            [Paragraph(f"<b>Aspartic Acid (ASP) </b>", center_paragraph), Image(os.path.join(sample_report_dir,"ASP_graph.png"), width=277.32375, height=67.5), Paragraph(f"<b>{test_result['ASP']['ref_value']}</b>",center_paragraph)],
            [Paragraph(test_result['ASP']['result_interpretation'], justified_paragraph), None, None],
            [Paragraph(f"<b>Serine (SER) </b>", center_paragraph), Image(os.path.join(sample_report_dir,"SER_graph.png"), width=277.32375, height=67.5), Paragraph(f"<b>{test_result['SER']['ref_value']}</b>",center_paragraph)],
            [Paragraph(test_result['SER']['result_interpretation'], justified_paragraph), None, None],
            [Paragraph(f"<b>Glycine (GLY) </b>", center_paragraph), Image(os.path.join(sample_report_dir,"GLY_graph.png"), width=277.32375, height=67.5), Paragraph(f"<b>{test_result['GLY']['ref_value']}</b>",center_paragraph)],
            [Paragraph(test_result['GLY']['result_interpretation'], justified_paragraph), None, None],
            [Paragraph(f"<b>Cystine (CYS) </b>", center_paragraph), Image(os.path.join(sample_report_dir,"CYS_graph.png"), width=277.32375, height=67.5), Paragraph(f"<b>{test_result['CYS']['ref_value']}</b>",center_paragraph)],
            [Paragraph(test_result['CYS']['result_interpretation'], justified_paragraph), None, None],
        ]

        result_data_table_style_pg3 = [
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Align images at the top of the cells
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Align images to the left
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),  # Padding at the bottom of the cells
            ('TOPPADDING', (0, 0), (-1, -1), 2),  # Padding at the top of the cells
            ('LEFTPADDING', (0, 0), (-1, -1), 2),  # Padding on the left of the cells
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('BACKGROUND', (0,0), (2,0), HexColor("#90acdc")),
        ]
        
        for interpretation_cell_row_number in (2,4,6,8,10):
            result_data_interpretation_cell_merge = ('BACKGROUND', (0,interpretation_cell_row_number), (2,interpretation_cell_row_number), HexColor("#90acdc"))
            result_data_interpretation_cell_merge = ('SPAN', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number))
            result_data_interpretation_cell_bottom_padding  = ('BOTTOMPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 5)
            result_data_interpretation_cell_top_padding = ('TOPPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 10)
            result_data_interpretation_cell_left_padding = ('LEFTPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 20)
            result_data_interpretation_cell_right_padding = ('RIGHTPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 20)

            result_data_table_style_pg3.append(result_data_interpretation_cell_merge) 
            result_data_table_style_pg3.append(result_data_interpretation_cell_bottom_padding) 
            result_data_table_style_pg3.append(result_data_interpretation_cell_top_padding)
            result_data_table_style_pg3.append(result_data_interpretation_cell_left_padding)
            result_data_table_style_pg3.append(result_data_interpretation_cell_right_padding)

        result_data_table3 = Table(result_data_pg3, colWidths=result_data_table_colWidths)
        result_data_table3.setStyle(result_data_table_style_pg3)
        story.append(result_data_table3)
        story.append(PageBreak())

        result_data_pg4 = [
            [Paragraph("<b>Non-Essential</b>", center_paragraph), Paragraph("<b>Result (\u00B5mol/L)</b>",center_paragraph), Paragraph("<b>Reference Range</b>",center_paragraph)],
            [Paragraph(f"<b>Tyrosine (TYR) </b>", center_paragraph), Image(os.path.join(sample_report_dir,"TYR_graph.png"), width=277.32375, height=67.5), Paragraph(f"<b>{test_result['TYR']['ref_value']}</b>",center_paragraph)],
            [Paragraph(test_result['TYR']['result_interpretation'], justified_paragraph), None, None],
            [Paragraph(f"<b>Glutamine (GLN) </b>", center_paragraph), Image(os.path.join(sample_report_dir,"GLN_graph.png"), width=277.32375, height=67.5), Paragraph(f"<b>{test_result['GLN']['ref_value']}</b>",center_paragraph)],
            [Paragraph(test_result['GLN']['result_interpretation'], justified_paragraph), None, None],
            [Paragraph(f"<b>Alanine (ALA) </b>", center_paragraph), Image(os.path.join(sample_report_dir,"ALA_graph.png"), width=277.32375, height=67.5), Paragraph(f"<b>{test_result['ALA']['ref_value']}</b>",center_paragraph)],
            [Paragraph(test_result['ALA']['result_interpretation'], justified_paragraph), None, None],
        ]

        result_data_table_style_pg4 = [
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Align images at the top of the cells
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Align images to the left
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),  # Padding at the bottom of the cells
            ('TOPPADDING', (0, 0), (-1, -1), 2),  # Padding at the top of the cells
            ('LEFTPADDING', (0, 0), (-1, -1), 2),  # Padding on the left of the cells
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('BACKGROUND', (0,0), (2,0), HexColor("#90acdc")),
        ]
        
        for interpretation_cell_row_number in (2,4,6,8):
            result_data_interpretation_cell_merge = ('BACKGROUND', (0,interpretation_cell_row_number), (2,interpretation_cell_row_number), HexColor("#90acdc"))
            result_data_interpretation_cell_merge = ('SPAN', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number))
            result_data_interpretation_cell_bottom_padding  = ('BOTTOMPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 5)
            result_data_interpretation_cell_top_padding = ('TOPPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 10)
            result_data_interpretation_cell_left_padding = ('LEFTPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 20)
            result_data_interpretation_cell_right_padding = ('RIGHTPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 20)

            result_data_table_style_pg4.append(result_data_interpretation_cell_merge) 
            result_data_table_style_pg4.append(result_data_interpretation_cell_bottom_padding) 
            result_data_table_style_pg4.append(result_data_interpretation_cell_top_padding)
            result_data_table_style_pg4.append(result_data_interpretation_cell_left_padding)
            result_data_table_style_pg4.append(result_data_interpretation_cell_right_padding)

        result_data_table4 = Table(result_data_pg4, colWidths=result_data_table_colWidths)
        result_data_table4.setStyle(result_data_table_style_pg4)
        story.append(result_data_table4)

        story.append(PageBreak())

        result_data_pg5 = [
            [Paragraph("<b>Derivatives</b>", center_paragraph), Paragraph("<b>Result (\u00B5mol/L)</b>",center_paragraph), Paragraph("<b>Reference Range</b>",center_paragraph)],
            [Paragraph(f"<b>Citruline (CIT) </b>", center_paragraph), Image(os.path.join(sample_report_dir,"CIT_graph.png"), width=277.32375, height=67.5), Paragraph(f"<b>{test_result['CIT']['ref_value']}</b>",center_paragraph)],
            [Paragraph(test_result['CIT']['result_interpretation'], justified_paragraph), None, None],
            [Paragraph(f"<b>Ornithine (ORN) </b>", center_paragraph), Image(os.path.join(sample_report_dir,"ORN_graph.png"), width=277.32375, height=67.5), Paragraph(f"<b>{test_result['ORN']['ref_value']}</b>",center_paragraph)],
            [Paragraph(test_result['ORN']['result_interpretation'], justified_paragraph), None, None],
        ]

        result_data_table_style_pg5 = [
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Align images at the top of the cells
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Align images to the left
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),  # Padding at the bottom of the cells
            ('TOPPADDING', (0, 0), (-1, -1), 2),  # Padding at the top of the cells
            ('LEFTPADDING', (0, 0), (-1, -1), 2),  # Padding on the left of the cells
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('BACKGROUND', (0,0), (2,0), HexColor("#90acdc")),
        ]
        
        for interpretation_cell_row_number in (2,4):
            result_data_interpretation_cell_merge = ('BACKGROUND', (0,interpretation_cell_row_number), (2,interpretation_cell_row_number), HexColor("#90acdc"))
            result_data_interpretation_cell_merge = ('SPAN', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number))
            result_data_interpretation_cell_bottom_padding  = ('BOTTOMPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 5)
            result_data_interpretation_cell_top_padding = ('TOPPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 10)
            result_data_interpretation_cell_left_padding = ('LEFTPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 20)
            result_data_interpretation_cell_right_padding = ('RIGHTPADDING', (0, interpretation_cell_row_number), (2, interpretation_cell_row_number), 20)

            result_data_table_style_pg5.append(result_data_interpretation_cell_merge) 
            result_data_table_style_pg5.append(result_data_interpretation_cell_bottom_padding) 
            result_data_table_style_pg5.append(result_data_interpretation_cell_top_padding)
            result_data_table_style_pg5.append(result_data_interpretation_cell_left_padding)
            result_data_table_style_pg5.append(result_data_interpretation_cell_right_padding)

        result_data_table5 = Table(result_data_pg5, colWidths=result_data_table_colWidths)
        result_data_table5.setStyle(result_data_table_style_pg5)
        story.append(result_data_table5)

        story.append(Spacer(1, 100))
        story.append(Paragraph("<b>Authorized By</b>", center_paragraph))
        story.append(Spacer(1, 12))
        auth_sign_image = os.path.join(workdir, 'ttd_lab_head_ms.png')
        story.append(Spacer(1, 12))
        story.append(Image(auth_sign_image, width=94.8, height=29.4))
        story.append(Spacer(1, 20))
        story.append(Paragraph("Mass Spectrometry & Separation Sciences Laboratory Head", center_paragraph))
        story.append(PageBreak())

        # Title
        interpretation_title = [
            [Paragraph("<b>Interpretation at-A-Glance/Implied Conditions</b >", title_style)]
        ]

        interpretation_title_table_style = [
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Align images at the top of the cells
            ('ALIGN', (0, 0), (-1, -1), 'CENTRE'),  # Align images to the left
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),  # Padding at the bottom of the cells
            ('TOPPADDING', (0, 0), (-1, -1), 2),  # Padding at the top of the cells
            ('LEFTPADDING', (0, 0), (-1, -1), 2),  # Padding on the left of the cells
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('BACKGROUND', (0,0), (0,0), HexColor("#90acdc")),
        ]

        interpretation_title_table = Table(interpretation_title)
        interpretation_title_table.setStyle(interpretation_title_table_style)
        story.append(interpretation_title_table)

        story.append(Paragraph("Nutrition Intake", styles['Heading3']))
        story.append(Paragraph("""
                                When three or more essential amino acids level in your plasma are tend to be low, you should check your protein intake to help ensuring amino acid adequacy. Pay attention for lysine, it can be lowered by excessive intake of arginine. For particular amino acid, such as histidine and arginine, low level also found in malabsorption condition, take care your gut healthy for better nutrition absorption.
                                When you found that your particular amino acids are tend to high, please refer to another condition. The excess of protein intake mostly give direct impact to increase amino acid level in your blood.
                                """, justified_paragraph))

        story.append(Spacer(1, 12))
        
        story.append(Paragraph("<b>Here are some of the top food sources of essential amino acids:</b>",
                               justified_paragraph))
        story.append(Spacer(1, 12))
        story.append(Paragraph("<b>Meat</b>: beef, lamb, and many other red meats",
                               justified_paragraph))
        story.append(Paragraph("<b>Poultry</b>: chicken, turkey, duck, goose",
                               justified_paragraph))
        story.append(Paragraph("<b>Seafood</b>: salmon, trout, tuna, mackerel, shrimp, lobster",
                               justified_paragraph))
        story.append(Paragraph("<b>Eggs</b>: whole eggs, egg whites",
                               justified_paragraph))
        story.append(Paragraph("<b>Dairy</b>: milk, cheese, yogurt",
                               justified_paragraph))
        story.append(Paragraph("<b>Nuts</b>: almonds, pistachios, macadamia nuts, cashews, walnuts",
                               justified_paragraph))
        story.append(Paragraph("<b>Seeds</b>: pumpkin seeds, squash seeds, hemp seeds, sunflower seeds",
                               justified_paragraph))   
        story.append(Paragraph("<b>Nut butters</b>: peanut butter, almond butter, cashew butter",
                               justified_paragraph))           
        story.append(Paragraph("<b>Legumes</b>: lentils, chickpeas, black beans, kidney beans",
                               justified_paragraph))    
        story.append(Paragraph("<b>Whole grains</b>: quinoa, oats, rye, barley, wheat",
                               justified_paragraph))    
        story.append(Paragraph("<b>Soy products</b>: soybeans, tofu, tempeh, edamame, protein supplements",
                               justified_paragraph))
        story.append(Spacer(1, 12))
        story.append(Paragraph("In general, you don’t need to select foods based on their particular amino acid content. Instead, eating a variety of protein-rich foods throughout the day will provide you with all the essential amino acids and nutrients you need",
                               justified_paragraph))


        story.append(Paragraph("Detoxification Capacity", styles['Heading3']))
        story.append(Paragraph("""
                                The amino acids glutamic acid, cystine, and glycine combine to form glutathione. It is generated by the liver and has a role in numerous bodily functions. Functions of the immune system, synthesis of chemicals and proteins required by the body, and tissue growth and repair are all aided by glutathione. Always monitor your levels of these three amino acids. If they tend to be low, you can take a supplement of glutathione and increase your protein intake.
                                """, justified_paragraph))
        story.append(Spacer(1, 12))


        
        story.append(Paragraph("Vitamin & Mineral Suplementation Presumptive Needs", styles['Heading3']))
        story.append(Paragraph("""
                                Some vitamins and minerals are required in amino acid metabolism, when you found that following amino acids level are tend to high in your blood, consider to take your vitamin and mineral supplementation. When you found that your threonine, lysine, phenylalanine, methionine, cystine, and tyrosine are tend to high, you can take the benefit of zinc, iron, copper, and magnesium in combination with vitamin B1, B6, and vitamin C supplementation. But when you found that your arginine, valine, leucine, tryptophan, glycine, proline, glutamic acid, and glutamine are tend to high, you should consider to take multivitamin B supplementation. Multivitamin and mineral supplements are readily available. Excessive nutririon intake also causing the elevation of your amino acid levels, balanced nutrition intake should be very beneficial for your health. When you found that your severals amino acids are tend to low, please refer to the nutrition intake section.
                                """, justified_paragraph))
        story.append(Spacer(1, 12))        

        story.append(PageBreak())
        story.append(interpretation_title_table)

        story.append(Paragraph("Neurological Effect", styles['Heading3']))
        story.append(Paragraph("""
                                Insufficiencies in catecholamines and thyroid function brought on by low phenylalanine levels can cause symptoms of sadness, exhaustion, autonomic dysfunction, and cognitive decline. You should take phenylalanine supplements and try to live a less stressed lifestyle. Mental health issues including depression, insomnia, and schizophrenia are commonly linked to low tryptophan levels. Taking supplements containing 5-hydroxytryptophan (5-HTP) may be advantageous. Pay more attention to phenylalanine and tryptophan when their levels are tend to low.
                                """, justified_paragraph))

        story.append(Paragraph("Obesity and Diabetes Mellitus", styles['Heading3']))
        story.append(Paragraph("""
                                Excessive intake of nutrition should not be beneficial for our health, one of the main disorder is obesity and lead to higher risk for Diabetes Mellitus. Before Diabetes Mellitus occur, several amino acids disturbance are detected as a risk pattern. Pay more attention for the elevation one of these following amino acids; leucine, isoleucine, valine, phenylalanine, tyrosine and tryptophan and also lower level of glycine in your blood, it is better to also check your blood glucose level. If you can detect your risk earlier, the better outcome will you get.
                                """, justified_paragraph))


        
        # Build the PDF
        doc.build(story, onFirstPage=myFirstPage, onLaterPages=myLaterPages) #

        #pdf_file_path_rl_corrected
