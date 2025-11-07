from PyQt6 import QtWidgets, uic  
import sys

class HospitalApp(QtWidgets.QStackedWidget):
    def __init__(self):
        super(HospitalApp, self).__init__()
        uic.loadUi("dbproj.ui", self) 

        self.setCurrentIndex(0)  # Ensure it starts on first_page

        # Connect the button to the page switch
        self.GCH_login_button.clicked.connect(self.go_to_login_page)

    def go_to_login_page(self):
        self.setCurrentIndex(1)  # Switch to page_2

app = QtWidgets.QApplication(sys.argv)
window = HospitalApp()
window.show()
sys.exit(app.exec())