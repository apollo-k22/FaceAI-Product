# importing modules
from functools import partial

from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib.colors import blue, black
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors, styles

# initializing variables with values
from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph, PageTemplate, Frame

# registering a external font in python
pdfmetrics.registerFont(
    TTFont('Arial', 'arial.ttf')
)

fileName = 'sample.pdf'
documentTitle = 'sample'
title = 'FaceAI Probe Report'
subTitle = 'The largest thing now!!'
textLines = [
    'Technology makes us aware of',
    'the world around us.',
]
image = r'data/images/t1.jpg'


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        self.PAGE_HEIGHT = 14 * inch
        self.PAGE_WIDTH = 8.5 * inch
        self.logo = ImageReader(r'FaceAI-Logo.png')

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.drawImage(self.logo, 30, self.PAGE_HEIGHT - 100, width=70, height=50, mask='auto')
        self.setFont("Arial", 12)
        # self.drawString(0, 1 * inch, "CNI TECHNOLOGYPTE LTD")
        self.drawRightString(self.PAGE_WIDTH / 2.0 + 10, 0.35 * inch,
                             "Page %d of %d" % (self._pageNumber, page_count))


# # creating a pdf object
# pdf = canvas.Canvas(fileName)
#
# # setting the title of the document
# pdf.setTitle(documentTitle)
#
#
# pdf.setFont('Arial', 12)
#
#
# pdf.setPageSize((610, 1010))
#
# pdf.drawCentredString(300, 770, title)


def header(canvas, doc, header_content, probe_id):
    canvas.saveState()
    w, h = header_content.wrap(doc.width, doc.topMargin)
    header_content.drawOn(canvas, doc.leftMargin, doc.height + doc.bottomMargin - h)
    w, h = probe_id.wrap(doc.width, doc.topMargin)
    probe_id.drawOn(canvas, doc.leftMargin, doc.height + doc.bottomMargin - 5*h)
    canvas.restoreState()
# def footer(canvas, doc, content):
#     canvas.saveState()
#     w, h = content.wrap(doc.width, doc.bottomMargin)
#     content.drawOn(canvas, doc.leftMargin, h)
#     canvas.restoreState()
#
# def header_and_footer(canvas, doc, header_content, footer_content):
#     header(canvas, doc, header_content)
#     footer(canvas, doc, footer_content)


BottomMargin = 0.5 * inch
TopMargin = 0.5 * inch
LeftMargin = 0.5 * inch
RightMargin = 0.5 * inch
doc = SimpleDocTemplate(fileName,
                        pagesize=(8.5 * inch, 14 * inch),
                        rightMargin=RightMargin,
                        leftMargin=LeftMargin,
                        topMargin=TopMargin,
                        bottomMargin=BottomMargin)

# story = [Paragraph('''<para align=left><font size=12><b>S/N</b></font></para>'''),
#          Paragraph('''<para align=left><font size=12><b>Description</b></font></para>'''),
#          Paragraph('''<para align=left><font size=12><b>UOM</b></font></para>'''),
#          Paragraph('''<para align=left><font size=12><b>QTY</b></font></para>'''),
#          Paragraph('''<para align=left><font size=12><b>U/Price(S$)</b></font></para>'''),
#          Paragraph('''<para align=left><font size=12><b>Amount(S$)</b></font></para>''')]
#
# orden = ParagraphStyle('orden')
# orden.leading = 14
#
# story.append(Spacer(100, 30))
#
# title = Paragraph('''<para align=left><font size=12><b>Description</b></font></para>''')
# story.append(title)

header_style = ParagraphStyle(name="style", fontName="Arial", fontSize=24, alignment=TA_CENTER, textColor=blue)
header_content = Paragraph("FaceAI Probe Report", style=header_style)
probe_style = ParagraphStyle(name="style", fontName="Arial", fontSize=18, alignment=TA_CENTER, textColor=black)
probe_id = Paragraph("Probe ID: 523598675", style=probe_style)
header_frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='header_frame')
header_template = PageTemplate(id='header_temp', frames=header_frame,
                               onPage=partial(header, header_content=header_content, probe_id=probe_id))

line_frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='line_frame')
line_template = PageTemplate(id='line_temp', frames=line_frame)

doc.addPageTemplates([header_template])
draw_line = Drawing(doc.width, 30, hAlign='CENTER')
draw_line.add(Line(0, 0, doc.width - doc.leftMargin / 2, 0, strokeColor=blue))

# draw_line.add(Line(doc.leftMargin,doc.height + doc.bottomMargin-50 , doc.width-doc.leftMargin, doc.height + doc.bottomMargin-50, strokeColor=blue))
story = []
story.append(draw_line)

doc.build(story, canvasmaker=NumberedCanvas)
# creating the subtitle by setting it's font,
# colour and putting it on the canvas
# pdf.setFillColorRGB(0, 0, 255)
# pdf.setFont("Courier-Bold", 24)
# pdf.drawCentredString(290, 720, subTitle)
#
# # drawing a line
# pdf.line(30, 710, 550, 710)
#
# # creating a multiline text using
# # textline and for loop
# text = pdf.beginText(40, 680)
# text.setFont("Courier", 18)
# text.setFillColor(colors.red)
#
# for line in textLines:
#     text.textLine(line)
#
# pdf.drawText(text)
#
# # drawing a image at the
# # specified (x.y) position
# pdf.drawInlineImage(image, 130, 400)
#
# # saving the pdf
# pdf.save()
