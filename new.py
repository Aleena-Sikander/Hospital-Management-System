# from PyQt6 import QtWidgets, uic
# import sys

# class HospitalApp(QtWidgets.QStackedWidget):
#     def __init__(self):
#         super(HospitalApp, self).__init__()
#         uic.loadUi("dbproj.ui", self)

#         # To store whether doctor/admin selected login
#         self.current_login_role = None  

#         print("Profile button index of registration = ", self.indexOf(self.patient_registration_submit_button))
#         print("Profile button index = ", self.indexOf(self.patient_portal_profile_button))
#         print("Does button exist?", hasattr(self, "patient_portal_profile_button"))
#         print(self.count())  # number of pages in stacked widget

#         # Start at first page
#         self.setCurrentIndex(0)

#         # --- Connect buttons to their pages ---

#         # First landing page buttons
#         self.GCH_login_button.clicked.connect(self.go_to_login_page)
#         self.GCH_our_services_button.clicked.connect(self.go_to_service_page)

#         # Login page buttons
#         self.login_patient_button.clicked.connect(self.go_to_patient_registration)

#         # Patient registration page
#         self.patient_registration_submit_button.clicked.connect(self.go_to_patient_portal_page)

#         # Patient portal page
#         self.patient_portal_profile_button.clicked.connect(self.go_to_patient_portal_profile_page)
#         self.patient_portal_appointment_button.clicked.connect(self.go_to_appointment_booking)
#         self.patient_portal_bills_button.clicked.connect(self.go_to_bills_page)
#         self.patient_portal_admission_details_button.clicked.connect(self.go_to_admission_details)

#         # Services & specialization pages
#         self.our_services_specializations_button.clicked.connect(self.go_to_specialization_page)
#         self.specialization_book_button.clicked.connect(self.go_to_appointment_booking)

#         # Appointment booking
#         self.appointment_booking_generate_bill_button.clicked.connect(self.go_to_bill_gen_page)
#         self.appointment_booking_back_button.clicked.connect(self.go_to_service_page)

#         # Bills page
#         self.bills_generate_bill_button.clicked.connect(self.go_to_bill_gen_page)

#         # Bill generation
#         self.bill_generation_add_more_button.clicked.connect(self.go_to_service_page)

#         # Lab test
#         self.our_services_lab_test_button.clicked.connect(self.go_to_lab_test_page)
#         self.lab_tests_book_button.clicked.connect(self.go_to_patient_lab_page)
#         self.patient_labs_check_result_button.clicked.connect(self.go_to_check_result_page)
#         self.lab_test_result_back_button.clicked.connect(self.go_to_patient_lab_page)
#         self.patient_labs_generate_bill_button.clicked.connect(self.go_to_bill_gen_page)

#         # Patient profile page
#         self.patient_profile_medical_history.clicked.connect(self.go_to_medical_history)
#         self.patient_profile_our_services.clicked.connect(self.go_to_service_page)

#         # --- DOCTOR pages ---
#         self.login_doctor_button.clicked.connect(lambda: self.open_login_page("doctor"))
#         self.doctor_registration_submit_button.clicked.connect(self.go_to_doctor_registration_page)
#         self.login_register_button.clicked.connect(self.go_to_doctor_registration_page)

#         # Submit button now depends on role (doctor/admin)
#         self.login_submit_button.clicked.connect(self.process_login_submit)

#         self.doctor_portal_profile_button.clicked.connect(self.go_to_doctor_profile_page)
#         self.doctor_portal_appointment_button.clicked.connect(self.go_to_doctor_appointment_page)
#         self.appointments_medical_history_button.clicked.connect(self.go_to_editable_medical_history)

#         # --- ADMIN pages ---
#         self.login_admina_button.clicked.connect(lambda: self.open_login_page("admin"))

#     # ======================================================================
#     # --- ROLE-BASED LOGIN HANDLING ----------------------------------------
#     # ======================================================================

#     def open_login_page(self, role):
#         """Opens login page with register button ON/OFF depending on role."""
#         self.current_login_role = role

#         if role == "admin":
#             self.login_register_button.setEnabled(False)   # disable register
#         else:
#             self.login_register_button.setEnabled(True)    # enable register

#         self.setCurrentIndex(4)  # login page
#         print(f"Login page opened for: {role}")

#     def process_login_submit(self):
#         """Handles Submit button behaviour depending on whether doctor/admin."""
#         if self.current_login_role == "admin":
#             self.go_to_admin_portal_page()
#         elif self.current_login_role == "doctor":
#             self.go_to_doctor_portal_page()
#         else:
#             print("ERROR: No login role selected!")

#     def go_to_login_page(self):
#         self.setCurrentIndex(1)

#     def go_to_service_page(self):
#         self.setCurrentIndex(9)

#     def go_to_patient_registration(self):
#         self.setCurrentIndex(2)

#     def go_to_patient_portal_page(self):
#         self.setCurrentIndex(22)

#     def go_to_patient_portal_profile_page(self):
#         self.setCurrentIndex(23)

#     def go_to_appointment_booking(self):
#         self.setCurrentIndex(16)

#     def go_to_bills_page(self):
#         self.setCurrentIndex(24)

#     def go_to_admission_details(self):
#         self.setCurrentIndex(26)

#     def go_to_medical_history(self):
#         self.setCurrentIndex(28)

#     def go_to_specialization_page(self):
#         self.setCurrentIndex(10)

#     def go_to_bill_gen_page(self):
#         self.setCurrentIndex(17)

#     def go_to_lab_test_page(self):
#         self.setCurrentIndex(12)

#     def go_to_patient_lab_page(self):
#         self.setCurrentIndex(27)

#     def go_to_check_result_page(self):
#         self.setCurrentIndex(18)

#     def go_to_doctor_registration_page(self):
#         self.setCurrentIndex(3)

#     def go_to_doctor_portal_page(self):
#         self.setCurrentIndex(19)

#     def go_to_doctor_profile_page(self):
#         self.setCurrentIndex(20)

#     def go_to_doctor_appointment_page(self):
#         self.setCurrentIndex(21)

#     def go_to_editable_medical_history(self):
#         self.setCurrentIndex(29)

#     def go_to_admin_portal_page(self):
#         self.setCurrentIndex(5)


# # --- Run App ---
# app = QtWidgets.QApplication(sys.argv)
# window = HospitalApp()
# window.show()
# sys.exit(app.exec())
