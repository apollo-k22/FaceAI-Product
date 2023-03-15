QSS = """
QLabel {
    background: transparent; 
    color: rgb(255,255,255);
    font: bold;
    font-size: 14pt;
    font-family: Arial;
}
QLineEdit {
    color: rgb(255, 255, 255);
    font-size: 14pt;
    font-family: Arial;
    background:transparent;
    border: 1px solid rgb(53, 132, 228);
}
QRadioButton{
    color: rgb(255, 255, 255);
    font-size: 12pt;
    font-family: Arial;
    background:transparent;
    border: 1px solid rgb(53, 132, 228);
}
QTextEdit{
    color: rgb(255, 255, 255);
    font-size: 14pt;
    font-family: Arial;
    background:transparent;
    border: 1px solid rgb(53, 132, 228);
}
QPushButton {
    color: rgb(255, 255, 255);
    font-size: 12pt;
    font: bold;
    font-family: Arial;
}
QStatusBar{
    color: rgb(255, 255, 255);
    font-size: 10pt;
    font-family: Arial;
}
* {
    # background-color: transparent; 
    font-family: "Arial";
}

QScrollArea  QWidget  QTextEdit
{
    background-color: rgb(98, 136, 178);
    border-radius: 10px;
    border: 1px solid rgb(53, 132, 228);
    font: 12pt "Arial";
}
QMessageBox{
    background:transparent;
}
QTableWidget::item{
    max-height:50px;
}
"""