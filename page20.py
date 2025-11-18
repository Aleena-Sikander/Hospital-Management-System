from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox  # <-- Import QMessageBox for error popups
import sys
import pyodbc  # <-- Import pyodbc to handle exceptions
from sql_connection import get_db_connection

class HospitalApp(QtWidgets.QStackedWidget):
    def __init__(self):
        super(HospitalApp, self).__init__()
        uic.loadUi("dbproj.ui", self)
        print("Profile button index of registration = ", self.indexOf(self.patient_registration_submit_button))
        print("Profile button index = ", self.indexOf(self.patient_portal_profile_button))
        print("Does button exist?", hasattr(self, "patient_portal_profile_button"))
        print(self.count())  # number of pages in stacked widget

        self.current_login_type = None
        self.current_user_id = None

        # Start at first page
        self.setCurrentIndex(0)

        # --- Connect buttons to their pages ---
        # First page (page index 0 - first_page) buttons
        self.GCH_login_button.clicked.connect(self.go_to_login_page)
        self.GCH_our_services_button.clicked.connect(self.go_to_service_page)

        # Login page (page index 1 - page_2) buttons
        # self.login_patient_button.clicked.connect(self.go_to_login)
        # self.login_register_button.clicked.connect(self.go_to_patient_registration)
        # self.patient_registration_submit_button.clicked.connect(self.go_to_login) #condition
        # self.login_submit_button.clicked.connect(self.go_to_patient_portal_page) #condition
        self.login_patient_button.clicked.connect(self.go_to_login)
        self.login_patient_button.clicked.connect(self.prepare_login_as_patient)
        self.login_register_button.clicked.connect(self.go_to_patient_registration)
        self.patient_registration_submit_button.clicked.connect(self.go_to_login) #condition
        self.patient_registration_submit_button.clicked.connect(self.patient_registration_submit)
        self.login_submit_button.clicked.connect(self.handle_login_submit) # route based on chosen role

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
        self.login_doctor_button.clicked.connect(self.prepare_login_as_doctor)
        self.doctor_registration_submit_button.clicked.connect(self.go_to_login)
        # self.login_register_button.clicked.connect(self.go_to_doctor_registration_page)
        # self.login_submit_button.clicked.connect(self.go_to_doctor_profile_page) # conditions
        self.doctor_portal_profile_button.clicked.connect(self.go_to_doctor_profile_page)
        self.doctor_portal_appointment_button.clicked.connect(self.go_to_doctor_appointment_page)
        self.appointments_medical_history_button.clicked.connect(self.go_to_editable_medical_history)
        self.doctor_medical_history_back_button.clicked.connect(self.go_to_doctor_appointment_page)

        #admin pages:
        self.login_admin_button.clicked.connect(self.go_to_login)
        self.login_admin_button.clicked.connect(self.prepare_login_as_admin)
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

    def prepare_login_as_patient(self):
        """Show login form and remember Patient role"""
        self.current_login_type = "patient"
        self.login_register_button.setEnabled(True)
        self.setCurrentIndex(4)  # login form page
        print("Preparing login as patient")

    def prepare_login_as_doctor(self):
        """Show login form and remember Doctor role"""
        self.current_login_type = "doctor"
        self.login_register_button.setEnabled(False)
        self.setCurrentIndex(4)
        print("Preparing login as doctor")

    def prepare_login_as_admin(self):
        """Show login form and remember Admin role"""
        self.current_login_type = "admin"
        self.login_register_button.setEnabled(False)
        self.setCurrentIndex(4)
        print("Preparing login as admin")

    def handle_login_submit(self):
        """Dispatch login submit to the correct handler based on chosen role"""
        if self.current_login_type == "doctor":
            self.go_to_doctor_portal_page()
        elif self.current_login_type == "patient":
            self.go_to_patient_portal_page()
        elif self.current_login_type == "admin":
            self.go_to_admin_portal_page()
        else:
            QMessageBox.warning(self, "Login Error", "Please choose Patient, Doctor or Admin before submitting login.")
            self.setCurrentIndex(1)  # back to role selection

    def go_to_service_page(self):
        """Navigate to our services page"""
        self.setCurrentIndex(9)  # page_5 (Our Services page)
        print("Navigated to services page")

    def go_to_patient_registration(self):
        """Navigate to patient registration form"""
        self.setCurrentIndex(2)  # page (Patient registration form)
        print("Navigated to patient registration")

    def patient_registration_submit(self):
        """Validate and submit patient registration to database"""
        # --- 1. Get text from UI ---
        name_text = self.patient_registration_name.text()
        email_text = self.patient_registration_email.text()
        password = self.patient_registration_password.text()  
        confirm_password = self.patient_registration_confirm_password.text()

        if password != confirm_password:
            QMessageBox.warning(self, "Registration Error", "Passwords do not match.")
            return

        contact_text = self.patient_registration_contact.text()

        if (not contact_text.isdigit()) or (len(contact_text) != 10):
            QMessageBox.warning(self, "Registration Error", "Contact number must be exactly 10 digits.")
            return
        
        gender = self.patient_registration_gender.currentText()
        dob = self.patient_registration_dob.date().toString("yyyy-MM-dd")

        # Validate all fields are filled
        if not name_text or not email_text or not contact_text:
            QMessageBox.warning(self, "Registration Error", "Please fill in all fields.")
            return

        connection = None
        try:
            # --- 2. Connect to DB ---
            connection = get_db_connection()
            if connection is None:
                QMessageBox.critical(self, "Connection Error", "Could not connect to the database.")
                return
            
            cursor = connection.cursor()

            # --- 3. Insert patient data into UserAccount table ---
            insert_query = """
            INSERT INTO UserAccount (UserID, Name, ContactNumber, Gender, Role, DateOfBirth, Email, Password)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (name_text, contact_text, email_text, gender, dob, password))
            connection.commit()

            print(f"Patient registered successfully: {name_text}")
            QMessageBox.information(self, "Success", "Registration successful! Please login with your credentials.")
            
            # Clear form fields
            self.patient_registration_name.clear()
            self.patient_registration_email.clear()
            self.patient_registration_password.clear()
            self.patient_registration_confirm_password.clear()
            self.patient_registration_contact.clear()
            self.patient_registration_gender.setCurrentIndex(0)
            self.patient_registration_dob.setDate(self.patient_registration_dob.date())

            # Navigate to login
            self.go_to_login()

        except pyodbc.Error as e:
            QMessageBox.critical(self, "Database Error", f"Registration failed: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
        finally:
            if connection:
                connection.close()

    def go_to_patient_portal_page(self):
        # --- 1. Get text from UI ---
        # We assume 'login_register_id' is the QLineEdit for the ID
        id_text = self.login_register_id.text()
        password = self.login_register_password.text()
        print(id_text, password)

        if not id_text or not password:
            QMessageBox.warning(self, "Login Error", "Please enter both ID and password.")
            return

        # --- 2. Check if ID is a valid number (CRITICAL) ---
        try:
            user_id = int(id_text)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "ID must be a number.")
            return

        connection = None
        try:
            # --- 3. Connect to DB ---
            connection = get_db_connection()
            if connection is None:
                QMessageBox.critical(self, "Connection Error", "Could not connect to the database.")
                return
            
            cursor = connection.cursor()
            # --- Patient / Admin Logic (Not 3 digits) ---
            query = "SELECT * FROM UserAccount WHERE UserID = ? and UserAccount.Role='Patient' "
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            if result:
                db_password = result[7]
                print(db_password)
                if db_password == password:
                    print(f"Login successful for Patient: {user_id}")
                    self.current_user_id = user_id # Save the patient's ID
                    self.setCurrentIndex(22)
                    self.patient_profile_patient_id.setText(str(user_id))
                    self.patient_profile_name.setText(result[1])
                    self.patient_profile_email.setText(result[6])
                    self.patient_profile_contact.setText(result[2])
                    self.patient_profile_gender.setText(result[3])
                    self.patient_profile_dob.setText(str(result[5]))
                    
                else:
                    QMessageBox.warning(self, "Login Failed", "Invalid ID or password.")
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid ID or password.")

        except pyodbc.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred during login: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
        finally:
            # --- 5. Always close connection ---
            if connection:
                connection.close()
        
          # page_3 (Patient portal with 4 options)
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
        self.setCurrentIndex(28)  
        self.medical_history_patient_id_lineedit.setText(str(self.current_user_id))
        print(f"Displaying medical history for patient: {self.current_user_id}")

        if not self.current_user_id:
            QMessageBox.warning(self, "Error", "No patient ID available.")
            return
        
        connection = None
        try:
            connection = get_db_connection()
            if connection is None:
                QMessageBox.critical(self, "Connection Error", "Could not connect to the database.")
                return
            
            cursor = connection.cursor()
            
            # Query to fetch medical history for current patient
            query = """
            SELECT *
            FROM Medical_History
            WHERE PatientID = ?
            ORDER BY DiagnosisDate DESC
            """
            cursor.execute(query, (self.current_user_id,))
            results = cursor.fetchall()
            
            if not results:
                QMessageBox.information(self, "No Records", "No medical history found for this patient.")
                return
            
            # Display results (you can format this as needed)
            history_text = "Medical History:\n\n"
            for row in results:
                history_text += f"ID: {row[0]}\n"
                history_text += f"Allergies: {row[2] or 'None'}\n"
                history_text += f"Disease: {row[3]}\n"
                history_text += f"Diagnosis Date: {row[4]}\n"
                history_text += f"Details: {row[5]}\n"
                history_text += "-" * 50 + "\n"
            
            QMessageBox.information(self, "Medical History", history_text)
            print(f"Fetched medical history for patient: {self.current_user_id}")
            
        except pyodbc.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error fetching medical history: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
        finally:
            if connection:
                connection.close()

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
        # self.setCurrentIndex(19)
        # --- 1. Get text from UI ---
        # We assume 'login_register_id' is the QLineEdit for the ID
        id_text = self.login_register_id.text()
        password = self.login_register_password.text()
        print(id_text, password)

        if not id_text or not password:
            QMessageBox.warning(self, "Login Error", "Please enter both ID and password.")
            return

        # --- 2. Check if ID is a valid number (CRITICAL) ---
        try:
            user_id = int(id_text)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "ID must be a number.")
            return

        connection = None
        print("Connecting to DB...")
        try:
            # --- 3. Connect to DB ---
            connection = get_db_connection()
            if connection is None:
                QMessageBox.critical(self, "Connection Error", "Could not connect to the database.")
                return
            
            cursor = connection.cursor()
            # --- Doctor Logic (3 digits) ---
            query = "SELECT * FROM Doctor WHERE DoctorID = ?"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            print("Fetched result from DB:", result)

            if result:
                db_password = result[3]
                print(db_password)
                if db_password == password:
                    print(f"Login successful for Doctor: {user_id}")
                    self.current_user_id = user_id # Save the doctor's ID
                    # self.go_to_doctor_portal_page()
                    self.setCurrentIndex(19)
                else:
                    QMessageBox.warning(self, "Login Failed", "Invalid ID or password.")
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid ID or password.")

        except pyodbc.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred during login: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
        finally:
            # --- 5. Always close connection ---
            if connection:
                connection.close()
        
          # page_3 (Patient portal with 4 options)
            print("Navigated to doc portal")

    def go_to_doctor_profile_page(self):
        self.setCurrentIndex(20)
    
    def go_to_doctor_appointment_page(self):
        self.setCurrentIndex(21)
    
    def go_to_editable_medical_history(self):
        self.setCurrentIndex(29)
    
    def go_to_admin_portal_page(self):
        # self.setCurrentIndex(5)
        # --- 1. Get text from UI ---
        # We assume 'login_register_id' is the QLineEdit for the ID
        id_text = self.login_register_id.text()
        password = self.login_register_password.text()
        print(id_text, password)

        if not id_text or not password:
            QMessageBox.warning(self, "Login Error", "Please enter both ID and password.")
            return

        # --- 2. Check if ID is a valid number (CRITICAL) ---
        try:
            user_id = int(id_text)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "ID must be a number.")
            return

        connection = None
        try:
            # --- 3. Connect to DB ---
            connection = get_db_connection()
            if connection is None:
                QMessageBox.critical(self, "Connection Error", "Could not connect to the database.")
                return
            
            cursor = connection.cursor()
            query = "SELECT Password FROM UserAccount WHERE UserAccount.UserID = ? and UserAccount.Role='Admin' "
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            if result:
                db_password = result[0]
                print(f"Entered password: '{password}'")
                print(f"DB password: '{db_password}'")  
                if db_password == password:
                    print(f"Login successful for Admin: {user_id}")
                    self.current_user_id = user_id # Save the admin's ID
                    self.setCurrentIndex(5)
                else:
                    QMessageBox.warning(self, "Login Failed", "Invalid ID or password.")
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid ID or password.")

        except pyodbc.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred during login: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
        finally:
            # --- 5. Always close connection ---
            if connection:
                connection.close()
        
          # page_3 (Patient portal with 4 options)
            print("Navigated to admin portal")

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
