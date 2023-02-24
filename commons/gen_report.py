from io import BytesIO
from reportlab.lib.pagesizes import letter, A4, LETTER
from reportlab.platypus import BaseDocTemplate, SimpleDocTemplate, Paragraph, PageTemplate, Frame, TableStyle, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import blue, black, red, white, HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
 
class MyPrint:
    _probid_ = "0"
    def __init__(self, buffer, probid):
        self.buffer = buffer
        self.pagesize = (8.5 * inch, 14 * inch)
        self.width, self.height = self.pagesize
        self.margin = 0.5 * inch
        _probid_ = probid
        pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))

    @staticmethod
    def _header_footer(canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        styles = getSampleStyleSheet()
 
        # Header
        header = Paragraph('FaceAI Probe Report', ParagraphStyle(name="style", fontName="Arial", fontSize=14, alignment=TA_CENTER, textColor=HexColor(0x0070C0)))
        w, h = header.wrap(doc.width, doc.topMargin)
        header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)
        header = Paragraph('Probe ID: ', ParagraphStyle(name="style", fontName="Arial", fontSize=12, alignment=TA_CENTER, textColor=black))
        w, h = header.wrap(doc.width, doc.topMargin)
        header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h * 2.9)
 
        # Footer
        footer = Paragraph('', ParagraphStyle(name="style", fontName="Arial", fontSize=12, alignment=TA_RIGHT, textColor=black))
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, h)
 
        # Release the canvas
        canvas.restoreState()


    def print_users(self, reportinfo):
        buffer = self.buffer
        doc = SimpleDocTemplate(buffer,
                                rightMargin=self.margin,
                                leftMargin=self.margin,
                                topMargin=self.margin * 2.4,
                                bottomMargin=self.margin,
                                pagesize=self.pagesize)

        # doc = BaseDocTemplate(buffer)

        # column_gap = 10 * mm
        # doc.addPageTemplates([
        #     PageTemplate(
        #         frames=[
        #             Frame(
        #                 doc.leftMargin,
        #                 doc.bottomMargin,
        #                 doc.width / 2,
        #                 doc.height,
        #                 id='left',
        #                 rightPadding=column_gap / 2,
        #                 showBoundary=0  # set to 1 for debugging
        #             ),
        #             Frame(
        #                 doc.leftMargin + doc.width / 2,
        #                 doc.bottomMargin,
        #                 doc.width / 2,
        #                 doc.height,
        #                 id='right',
        #                 leftPadding=column_gap / 2,
        #                 showBoundary=0
        #             ),
        #         ]
        #     ),
        # ])

 
        # Our container for 'Flowable' objects
        elements = []
 
        # A large collection of style sheets pre-made for us
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='centered', alignment=TA_CENTER))
 
        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        textsize = 12
        leading = 14
        # elements.append(Paragraph('''<para align=center leading=18 fontName='Arial'><font size=12 color=0xff0000><b>''' + 'Probe result: ' + reportinfo["result"] + '''</b></font></para>'''))
        elements.append(Paragraph('Probe result: ' + reportinfo["result"], ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_CENTER, textColor=red, leading=20)))

        ministy = TableStyle([('GRID', (0,0), (-1,-1), 1.0, white),])
        nested1 = [
            Paragraph('Time of report generation: ' + reportinfo["created"], ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading)),
            Paragraph('Case no.:' + reportinfo["casenum"], ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading)),
            Paragraph('PS: ' + reportinfo["ps"], ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading)),
            Paragraph('Examiner’s name: ' + reportinfo["examname"], ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading)),
            Paragraph('BP no.: ' + reportinfo["bpnum"], ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading)),
            Paragraph('Remarks: ' + reportinfo["remarks"] * 5, ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading))
        ]   
        nested2 = [Paragraph('Subject photo', ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_CENTER, textColor=black, leading=leading))]
        t = Table([[nested1, nested2]],
                  colWidths=('50%', '50%'),
                  rowHeights=None,
                  style=ministy)
        elements.append(t)

        elements.append(Paragraph('The subject photo has matched to the following old case photos. Respective similarity scores and case details are attached herewith.', ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading, spaceBefore=6)))
        

        doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer,
                  canvasmaker=NumberedCanvas)        
        
    '''
        Usage with django
    @staff_member_required
    def print_users(request):
        # Create the HttpResponse object with the appropriate PDF headers.
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="My Users.pdf"'
     
        buffer = BytesIO()
     
        report = MyPrint(buffer, 'Letter')
        pdf = report.print_users()
     
        response.write(pdf)
        return response
    '''


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.logo = r'FaceAI-Logo.png'
        self.photo = r'C:\Users\marko\Documents\Work\20230211\03_Work\test_images\ttt3.png'
        self.pagesize = (8.5 * inch, 14 * inch)
        self.width, self.height = self.pagesize
        self.margin = 0.5 * inch
        self._saved_page_states = []
 

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
        # self.drawImage(self.logo, 30, self.height - 100, width=70, height=50, mask='auto')
        page = "Page %s of %s" % (self._pageNumber, page_count)
        x = 128
        self.saveState()
        self.setStrokeColor(HexColor(0x0070C0))
        self.setLineWidth(0.5)
        # self.drawImage(self.logo, self.width-inch*8-5, self.height-50, width=100, height=20, preserveAspectRatio=True)
        self.line(30, self.height - self.margin * 1.6, LETTER[0] - 50, self.height - self.margin * 1.6)
        self.restoreState()
        self.setFont("Arial", 12)
        self.drawRightString(self.width / 2.0 + 10, 0.35 * inch,
                             "Page %d of %d" % (self._pageNumber, page_count))




if __name__ == '__main__':
    buffer = BytesIO()
    
    probid = "523598675"
    reportinfo = {
        "result": "Matched",
        "created": datetime.strftime(datetime.now(), "%d/%m/%Y %I:%M %p"),
        "casenum": "111",
        "ps": "wwwwwwwwwwwwww",
        "examname": "wwwwwwwwwwwwwwwwww",
        "bpnum": "wwwwwwwwwwwwwwwwwwwwww",
        "remarks": "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww"
    }

    report = MyPrint(buffer, probid)
    pdf = report.print_users(reportinfo)
    buffer.seek(0)
 
    with open('sample.pdf', 'wb') as f:
        f.write(buffer.read())