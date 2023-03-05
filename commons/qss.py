QSS = """
QLabel {
    background-color: transparent; 
    color: rgb(255,255,255);
    font: bold;
    font-size: 14pt;
    font-family: Arial;
}
QLineEdit {
    color: rgb(255, 255, 255);
    font-size: 12pt;
    font-family: Arial;
}
QPlainTextEdit{
    color: rgb(255, 255, 255);
    font-size: 12pt;
    font-family: Arial;
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

.QWidget{
    background-image: ":/newPrefix/Background.png";
}
.main-widget{
    background-image: url(":/newPrefix/Background.png");
    background-color:red;
}
QScrollArea  QWidget  QTextEdit
{
    background-color: rgb(98, 136, 178);
    border-radius: 10px;
    border: 1px solid rgb(53, 132, 228);
    font: 12pt "Arial";
}
QMessageBox{
    background-color: rgb(98, 136, 178)
}
QTableWidget::item{
    max-height:50px;
}
"""