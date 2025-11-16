from PyQt6 import QtWidgets, uic
import sys

class HospitalApp(QtWidgets.QStackedWidget):
    def __init__(self):
        super(HospitalApp, self).__init__()
        uic.loadUi("dbproj.ui", self)
        print("Profile button index of registration = ", self.indexOf(self.patient_registration_submit_button))
        print("Profile button index = ", self.indexOf(self.patient_portal_profile_button))
        print("Does button exist?", hasattr(self, "patient_portal_profile_button"))
        print(self.count())  # number of pages in stacked widget

        # Start at first page
        self.setCurrentIndex(0)

        # --- Connect buttons to their pages ---
        # First page (page index 0 - first_page) buttons
        self.GCH_login_button.clicked.connect(self.go_to_login_page)
        self.GCH_our_services_button.clicked.connect(self.go_to_service_page)

        # Login page (page index 1 - page_2) buttons
        self.login_patient_button.clicked.connect(self.go_to_login)
        self.login_register_button.clicked.connect(self.go_to_patient_registration)
        self.patient_registration_submit_button.clicked.connect(self.go_to_login) #condition
        self.login_submit_button.clicked.connect(self.go_to_patient_portal_page) #condition

        # Patient portal page (page index 3 - page_3) buttons
        self.patient_portal_profile_button.clicked.connect(self.go_to_patient_portal_profile_page)
        self.patient_portal_appointment_button.clicked.connect(self.go_to_patient_portal_appointment_page)
        self.patient_portal_bills_button.clicked.connect(self.go_to_bills_page)
        self.patient_portal_admission_details_button.clicked.connect(self.go_to_admission_details)
        self.our_services_specializations_button.clicked.connect(self.go_to_specialization_page)
        self.specialization_book_button.clicked.connect(self.go_to_appointment_booking)
        self.appointment_booking_generate_bill_button.clicked.connect(self.go_to_bill_gen_page)
        self.appointment_booking_back_button.clicked.connect(self.go_to_service_page)
        self.appointment_booking_book_button.clicked.connect(self.go_to_patient_appointment_page)
        self.bills_generate_bill_button.clicked.connect(self.go_to_bill_gen_page)
        self.bill_generation_add_more_button.clicked.connect(self.go_to_service_page)
        self.our_services_lab_test_button.clicked.connect(self.go_to_lab_test_page)
        self.lab_tests_book_button.clicked.connect(self.go_to_patient_lab_page)
        self.our_services_pharmacy_button.clicked.connect(self.go_to_pharmacy_page)
        self.patient_labs_check_result_button.clicked.connect(self.go_to_check_result_page)
        self.lab_test_result_back_button.clicked.connect(self.go_to_patient_lab_page)
        self.patient_labs_generate_bill_button.clicked.connect(self.go_to_bill_gen_page)
        self.medical_history_back_button.clicked.connect(self.go_to_patient_portal_profile_page)
        # Patient profile page (page index 4 - page_4) buttons
        self.patient_profile_medical_history.clicked.connect(self.go_to_medical_history)
        self.patient_profile_our_services.clicked.connect(self.go_to_service_page)
        self.lab_tests_back_button.clicked.connect(self.go_to_service_page)
        self.pharmacy_back_button.clicked.connect(self.go_to_service_page)

        
        # Doctor Pages:
        self.login_doctor_button.clicked.connect(self.go_to_login)
        self.doctor_registration_submit_button.clicked.connect(self.go_to_login)
        # self.login_register_button.clicked.connect(self.go_to_doctor_registration_page)
        # self.login_submit_button.clicked.connect(self.go_to_doctor_profile_page) # conditions
        self.doctor_portal_profile_button.clicked.connect(self.go_to_doctor_profile_page)
        self.doctor_portal_appointment_button.clicked.connect(self.go_to_doctor_appointment_page)
        self.appointments_medical_history_button.clicked.connect(self.go_to_editable_medical_history)
        self.doctor_medical_history_back_button.clicked.connect(self.go_to_doctor_appointment_page)

        #admin pages:
        self.login_admin_button.clicked.connect(self.go_to_login)
        # self.login_submit_button.clicked.connect(self.go_to_admin_portal_page) # conditions
        self.admin_portal_patient_button.clicked.connect(self.go_to_admin_patient_page)
        self.admin_patient_admission_edit_button.clicked.connect(self.go_to_admin_patient_admission_edit_page)
        self.admin_portal_doctor_button.clicked.connect(self.go_to_admin_doctor_approval_page)
        self.admin_doctor_approval_approve_button.clicked.connect(self.go_to_admin_apecialization_edit_page)
        self.admin_portal_pharmacy_button.clicked.connect(self.go_to_admin_pharmacy_edit_page)
        self.Admin_pharmacy_entry_back_button.clicked.connect(self.go_to_admin_portal_page)
        self.order_generate_bill_button.clicked.connect(self.go_to_bill_gen_page)
        


    
    # --- Navigation Methods ---
    def go_to_login_page(self):
        """Navigate to login selection page"""
        self.setCurrentIndex(1)  # page_2
        print("Navigated to login page")

    def go_to_service_page(self):
        """Navigate to our services page"""
        self.setCurrentIndex(9)  # page_5 (Our Services page)
        print("Navigated to services page")

    def go_to_patient_registration(self):
        """Navigate to patient registration form"""
        self.setCurrentIndex(2)  # page (Patient registration form)
        print("Navigated to patient registration")

    def go_to_patient_portal_page(self):
        """Navigate to patient portal main page (with 4 buttons)"""
        self.setCurrentIndex(22)  # page_3 (Patient portal with 4 options)
        print("Navigated to patient portal")

    def go_to_patient_portal_profile_page(self):
        """Navigate to patient profile page"""
        self.setCurrentIndex(23)  # page_4 (Patient profile page)
        print("Navigated to patient profile page")
    
    def go_to_appointment_booking(self):
        """Navigate to appointment booking page"""
        self.setCurrentIndex(16)  # page_6
        print("Navigated to appointment booking")
    
    def go_to_patient_portal_appointment_page(self):
        """Navigate to appointment booking page"""
        self.setCurrentIndex(26)  # page_6
        print("Navigated to appointment booking")
    
    def go_to_bills_page(self):
        """Navigate to bills page"""
        self.setCurrentIndex(24)  # page_10
        print("Navigated to bills page")
    
    def go_to_admission_details(self):
        """Navigate to admission details page"""
        self.setCurrentIndex(26)  # page_11
        print("Navigated to admission details")
    
    def go_to_medical_history(self):
        """Navigate to medical history page"""
        self.setCurrentIndex(28)  # page_15
        print("Navigated to medical history")
    
    def go_to_specialization_page(self):
        self.setCurrentIndex(10)
        print("Navigated to specialization page")

    def go_to_bill_gen_page(self):
        self.setCurrentIndex(17)
        print("Navigated to bill generation page")

    def go_to_lab_test_page(self):
        self.setCurrentIndex(12)
        print("Navigated to lab_test page")

    def go_to_patient_lab_page(self):
        self.setCurrentIndex(27)
        print("Navigated to patient_lab")

    def go_to_check_result_page(self):
        self.setCurrentIndex(18)
        print("Navigated to lab result page")

    def go_to_doctor_registration_page(self):
        self.setCurrentIndex(3)
        print("Navigated to doctor page")

    def go_to_login(self):
        self.setCurrentIndex(4)

    def go_to_doctor_portal_page(self):
        self.setCurrentIndex(19)

    def go_to_doctor_profile_page(self):
        self.setCurrentIndex(20)
    
    def go_to_doctor_appointment_page(self):
        self.setCurrentIndex(21)
    
    def go_to_editable_medical_history(self):
        self.setCurrentIndex(29)
    
    def go_to_admin_portal_page(self):
        self.setCurrentIndex(5)

    def go_to_admin_patient_page(self):
        self.setCurrentIndex(7)

    def go_to_admin_patient_admission_edit_page(self):
        self.setCurrentIndex(8)

    def go_to_admin_doctor_approval_page(self):
        self.setCurrentIndex(6)
    
    def go_to_admin_apecialization_edit_page(self):
        self.setCurrentIndex(11)
    
    def go_to_admin_pharmacy_edit_page(self):
        self.setCurrentIndex(15)
    
    def go_to_pharmacy_page(self):
        self.setCurrentIndex(14)
    
    def go_to_patient_appointment_page(self):
        self.setCurrentIndex(25)

    

    

    


# --- Run App ---
app = QtWidgets.QApplication(sys.argv)
window = HospitalApp()
window.show()
sys.exit(app.exec())
