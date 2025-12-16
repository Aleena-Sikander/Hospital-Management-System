from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox 
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
import sys
import pyodbc 
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
        self.selected_specialisation_id = None
        self._doctor_list_cache = []
        self._availability_cache = []

        # Start at first page
        self.setCurrentIndex(0)
        print("1")

        # --- Connect buttons to their pages ---
        # First page (page index 0 - first_page) buttons
        self.GCH_login_button.clicked.connect(self.go_to_login_page)
        self.GCH_our_services_button.clicked.connect(self.go_to_service_page)
        self.specialization_tableview.clicked.connect(self.on_specialization_row_selected)
        self.appointments_admit_dataview.clicked.connect(self.on_doc_app_row_selected)

        # Login page (page index 1 - page_2) buttons
        # self.appointments_details_button.clicked.connect(self.load_bills_from_appointments)
        self.login_patient_button.clicked.connect(self.go_to_login)
        self.login_patient_button.clicked.connect(self.prepare_login_as_patient)
        self.login_register_button.clicked.connect(self.go_to_check_who_here)
        self.patient_registration_submit_button.clicked.connect(self.go_to_login) #condition
        self.patient_registration_submit_button.clicked.connect(self.patient_registration_submit)
        self.login_submit_button.clicked.connect(self.handle_login_submit) # route based on chosen role

        # Patient portal page (page index 3 - page_3) buttons
        self.patient_portal_profile_button.clicked.connect(self.go_to_patient_portal_profile_page)
        self.patient_labs_generate_back_button.clicked.connect(self.go_to_patient_portal_profile_page)
        self.patient_portal_appointment_button.clicked.connect(self.load_patient_appointments)
        self.patient_portal_admission_details_button.clicked.connect(self.go_to_admission_details)
        self.our_services_specializations_button.clicked.connect(self.go_to_specialization_page)
        self.specialization_book_button.clicked.connect(self.go_to_appointment_booking)
        
        try:
            self.appointment_booking_available_doctors.currentIndexChanged.connect(self.on_doctor_combo_changed)
        except Exception:
            pass
        # self.appointment_booking_generate_bill_button.clicked.connect(
        #         lambda: self.go_to_bill_gen_page(self.get_selected_appointment_bill_id()))
        self.appointment_booking_generate_bill_button.clicked.connect(self.load_bills_page)
        self.appointment_booking_back_button.clicked.connect(self.go_to_service_page)
        self.appointment_booking_book_button.clicked.connect(self.book_appointment) #change
        self.appointments_details_button.clicked.connect(self.show_appointment_details_popup)
        self.appointments_cancel_appointment_button.clicked.connect(self.cancel_appointment_button)
        # self.appointments_detail_dataview.selectionModel().selectionChanged.connect(self.on_appointment_selected)
        self.bill_generation_add_more_button.clicked.connect(self.go_to_service_page)
        self.our_services_lab_test_button.clicked.connect(self.go_to_lab_test_page)
        self.lab_tests_book_button.clicked.connect(self.book_lab_test)
        self.our_services_pharmacy_button.clicked.connect(self.go_to_pharmacy_page)
        self.our_services_back_button.clicked.connect(self.main_page)
        self.patient_labs_check_result_button.clicked.connect(self.on_check_result_clicked)
        self.lab_test_result_back_button.clicked.connect(self.go_to_patient_lab_page)
        self.lab_tests_mylabs.clicked.connect(self.go_to_patient_lab_page)
        self.lab_test_result_download_button.clicked.connect(self.show_lab_test_details)

        # self.patient_labs_generate_bill_button.clicked.connect(self.go_to_bill_gen_page)
        self.patient_labs_generate_bill_button.clicked.connect(
            lambda: self.go_to_bill_gen_page(self.get_selected_lab_bill_id()))
        self.medical_history_back_button.clicked.connect(self.go_to_patient_portal_profile_page)
        self.patient_profile_back_button.clicked.connect(self.go_to_patient_portal_page)
        self.appointments_back_button.clicked.connect(self.go_to_patient_portal_page)
        self.admission_details_back_button.clicked.connect(self.go_to_patient_portal_page)
        self.specialization_back_button.clicked.connect(self.go_to_service_page)
        self.admin_doctor_back_button.clicked.connect(self.go_to_admin_portal_page)
        # Patient profile page (page index 4 - page_4) buttons
        self.patient_profile_medical_history.clicked.connect(self.go_to_medical_history)
        self.patient_profile_our_services.clicked.connect(self.go_to_service_page)
        self.lab_tests_back_button.clicked.connect(self.go_to_service_page)
        self.lab_tests_items_view.clicked.connect(self.on_lab_test_row_selected)
        self.patient_labs_tableview.clicked.connect(self.on_patient_lab_test_row_selected)

        self.pharmacy_back_button.clicked.connect(self.go_to_service_page)

        # Connect the Details button to show details
        self.medical_history_details_button.clicked.connect(self.show_selected_medical_history_details)
        self.medical_history_details_button_top.clicked.connect(self.show_selected_medical_history_details)

        self.medical_history_list.itemDoubleClicked.connect(self.show_selected_medical_history_details)

        # Doctor Pages:
        self.login_doctor_button.clicked.connect(self.go_to_login)
        self.login_doctor_button.clicked.connect(self.prepare_login_as_doctor)
        self.doctor_registration_submit_button.clicked.connect(self.go_to_submit_doctor_registration)
        self.doctor_portal_profile_button.clicked.connect(self.go_to_doctor_profile_page)
        self.doctor_portal_appointment_button.clicked.connect(self.go_to_doctor_appointment_page)
        self.doctor_profile_back_button.clicked.connect(self.go_to_doctor_portal_page)
        self.appointments_medical_history_button.clicked.connect(self.go_to_editable_medical_history)
        self.doctor_medical_history_back_button.clicked.connect(self.go_to_doctor_appointment_page)
        self.doc_medical_history_list.itemDoubleClicked.connect(self.show_selected_doc_medical_history_details)
        self.doctor_medical_history_details_button.clicked.connect(self.show_selected_doc_medical_history_details)
        self.appointments_back_button_2.clicked.connect(self.go_to_doctor_portal_page)
        self.appointments_admit_button.clicked.connect(self.admit_patient_from_appointment)
        self.appointments_cancel_appointment_button_2.clicked.connect(self.cancel_selected_appointment)


        #admin pages:
        self.login_admin_button.clicked.connect(self.go_to_login)
        self.login_admin_button.clicked.connect(self.prepare_login_as_admin)
        self.admin_portal_patient_button.clicked.connect(self.go_to_admin_patient_page)
        self.admin_patient_admission_back_button.clicked.connect(self.go_to_admin_portal_page)
        self.admin_patient_admission_edit_button.clicked.connect(self.go_to_admin_patient_admission_edit_page)
        self.admin_admission_entry_save_button.clicked.connect(self.save_admission_changes)
        self.admin_admission_entry_back_button.clicked.connect(self.go_to_admin_patient_page)
        self.admin_portal_doctor_button.clicked.connect(self.go_to_admin_doctor_approval_page)
        self.admin_doctor_approval_approve_button.clicked.connect(self.approve_selected_doctor)
        self.admin_doctor_approval_reject_button.clicked.connect(self.reject_selected_doctor)
        self.admin_portal_pharmacy_button.clicked.connect(self.go_to_admin_pharmacy_edit_page)
        self.Admin_pharmacy_entry_back_button.clicked.connect(self.go_to_admin_portal_page)
        self.Admin_pharmacy_entry_add_button.clicked.connect(self.add_pharmacy_item)
        self.Admin_pharmacy_entry_remove_button.clicked.connect(self.remove_pharmacy_item)
        self.Admin_pharmacy_entry_labtest_entry.clicked.connect(self.go_to_admin_lab_entry_page)
        self.Admin_lab_tests_entry_back_button.clicked.connect(self.go_to_admin_pharmacy_edit_page)
        self.Admin_lab_tests_entry_add_button.clicked.connect(self.add_lab_entry)
        self.Admin_lab_tests_entry_remove_button.clicked.connect(self.remove_lab_entry)

        # #bills:
        self.patient_portal_bills_button.clicked.connect(self.load_bills_page)
        self.bills_back_button.clicked.connect(self.go_to_patient_portal_page)
        self.bill_generation_back_button.clicked.connect(self.go_to_patient_portal_page)
        self.order_generate_bill_button.clicked.connect(self.go_to_bill_gen_page)
        

        self.bills_generate_bill_button.clicked.connect(
            lambda: self.go_to_bill_gen_page(self.get_selected_bill_id_from_bills()))        
        self.bills_details_button.clicked.connect(self.show_bill_details)
        self.patient_labs_generate_bill_button.clicked.connect(
            lambda: self.go_to_bill_gen_page(self.get_selected_lab_bill_id()))   

        self.bills_generate_bill_button.setEnabled(False)  # disabled by default
        self.bills_detail_dataview.clicked.connect(self.on_bill_row_selected)
        self.bill_generation_proceed_to_payment.clicked.connect(self.show_payment_message)

        # logout 
        self.patient_profile_logout.clicked.connect(self.logout)
        self.doctor_profile_logout.clicked.connect(self.logout)
        self.admin_portal_logout.clicked.connect(self.logout)


    def logout(self):
        
        self.current_user_id = None
        self.current_login_type = None
        self.selected_specialisation_id = None
        
        self.setCurrentIndex(0) 
        print("Logged out successfully. Session cleared.")
        
    def go_to_check_who_here(self):
        if self.current_login_type == "doctor":
            self.go_to_doctor_registration_page()
        elif self.current_login_type == "patient":
            self.go_to_patient_registration()
    
    def go_to_login_page(self):
        """Navigate to login selection page"""
        self.setCurrentIndex(1)  # page_2
        print("Navigated to login page (2)")

    def prepare_login_as_patient(self):
        """Show login form and remember Patient role"""
        self.current_login_type = "patient"
        self.login_register_button.setEnabled(True)
        self.setCurrentIndex(4)  # login form page
        print("Preparing login as patient (5)")

    def prepare_login_as_doctor(self):
        """Show login form and remember Doctor role"""
        self.current_login_type = "doctor"
        self.login_register_button.setEnabled(True)
        self.setCurrentIndex(4)
        print("Preparing login as doctor (5)")

    def prepare_login_as_admin(self):
        """Show login form and remember Admin role"""
        self.current_login_type = "admin"
        self.login_register_button.setEnabled(False)
        self.setCurrentIndex(4)
        print("Preparing login as admin (5)")

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
            print("2")

    def main_page(self):
        """Navigate to main first page"""
        self.setCurrentIndex(0)  # first_page
        print("Navigated to main page (1)")

    def go_to_service_page(self):
        """Navigate to our services page"""
        self.setCurrentIndex(9)  # page_5 (Our Services page)
        print("Navigated to services page (10)")

    def go_to_patient_registration(self):
        """Navigate to patient registration form"""
        self.setCurrentIndex(2)  # page (Patient registration form)
        print("Navigated to patient registration (3)")

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
        user_id = 20
        user_id+=1

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
            INSERT INTO UserAccount (Name, ContactNumber, Gender, Role, DateOfBirth, Email, Password)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (name_text, contact_text, gender, 'Patient', dob, email_text, password))
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
            print("1")
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

    def go_to_submit_doctor_registration(self):
        """Validates input and sends data to PendingDoctor table"""
        
        # 1. Get data from UI
        name = self.doctor_registration__name.text() # Check your UI variable name
        email = self.doctor_registration_email.text()
        password = self.doctor_registration_password.text()
        confirm_pass = self.doctor_registration_confirm_passowrd.text()
        contact = self.doctor_registration_contact_no.text()
        specialization = self.doctor_registration_comboBox.currentText()

        # 2. Validation
        if not name or not email or not password or not contact:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return

        if password != confirm_pass:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return

        if len(contact) != 10 or not contact.isdigit():
            QMessageBox.warning(self, "Error", "Contact must be 10 digits.")
            return

        # 3. Insert into PendingDoctor Table
        connection = None
        try:
            connection = get_db_connection()
            if connection:
                cursor = connection.cursor()
                
                query = """
                INSERT INTO PendingDoctor (Name, Email, Password, Contact, Specialization)
                VALUES (?, ?, ?, ?, ?)
                """
                cursor.execute(query, (name, email, password, contact, specialization))
                connection.commit()

                QMessageBox.information(self, "Request Sent", "Registration submitted! Please wait for Admin approval.")
                
                # Clear fields
                self.doctor_registration__name.clear()
                self.doctor_registration_email.clear()
                self.doctor_registration_password.clear()
                self.doctor_registration_contact_no.clear()
                
                # Go back to login
                self.setCurrentIndex(0)
                print("1")

        except pyodbc.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error submitting request: {e}")
        finally:
            if connection:
                connection.close()
    
    def go_to_admin_doctor_approval_page(self):
        self.setCurrentIndex(6) # Or whatever your index is
        self.load_pending_doctor_requests() # <--- ADD THIS LINE
        print("Navigated to doctor approval page and loaded data (7)")

    def load_pending_doctor_requests(self):
        """Fetches pending doctors and displays them in the table"""
        
        table = self.admin_doctor_approval_approve_requests
        
        # --- FIX START: Setup the columns first! ---
        table.setColumnCount(5)  # Tell the table we need 5 columns
        table.setHorizontalHeaderLabels(["Request ID", "Name", "Email", "Contact", "Specialization"])
        # --- FIX END ---

        # Clear previous data rows (but keep the headers)
        table.setRowCount(0)
        
        connection = None
        try:
            connection = get_db_connection()
            if connection:
                cursor = connection.cursor()
                
                query = "SELECT RequestID, Name, Email, Contact, Specialization FROM PendingDoctor"
                cursor.execute(query)
                rows = cursor.fetchall()

                for row_number, row_data in enumerate(rows):
                    table.insertRow(row_number)
                    
                    # Now that columns exist, these lines will work:
                    table.setItem(row_number, 0, QtWidgets.QTableWidgetItem(str(row_data[0]))) 
                    table.setItem(row_number, 1, QtWidgets.QTableWidgetItem(str(row_data[1])))
                    table.setItem(row_number, 2, QtWidgets.QTableWidgetItem(str(row_data[2])))
                    table.setItem(row_number, 3, QtWidgets.QTableWidgetItem(str(row_data[3])))
                    table.setItem(row_number, 4, QtWidgets.QTableWidgetItem(str(row_data[4])))
                
                # Optional: Make columns stretch to fill the space
                header = table.horizontalHeader()
                header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

        except Exception as e:
            print(f"Error loading pending requests: {e}")
        finally:
            if connection:
                connection.close()

    def get_next_id(self, cursor, table_name, column_name):
        """Calculates the next available ID (MAX + 1)"""
        try:
            cursor.execute(f"SELECT MAX({column_name}) FROM {table_name}")
            val = cursor.fetchone()[0]
            if val is None:
                return 1
            return val + 1
        except Exception:
            return 1
    
    def approve_selected_doctor(self):
        """
        Approves the selected doctor request.
        Handles the logic to prevent duplicate doctor entries.
        """
        # 1. Get selected row
        current_row = self.admin_doctor_approval_approve_requests.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selection Error", "Please select a request to approve.")
            return

        # 2. Extract data from the table row
        # Column 0 is RequestID (Hidden or visible), Column 1 Name, 2 Email, 3 Contact, 4 Spec
        request_id = self.admin_doctor_approval_approve_requests.item(current_row, 0).text()
        
        # We need to fetch the PASSWORD from the database because it's not in the table view
        connection = get_db_connection()
        if not connection: return
        
        cursor = connection.cursor()
        
        try:
            # Fetch full details from PendingDoctor
            cursor.execute("SELECT Name, Email, Password, Contact, Specialization FROM PendingDoctor WHERE RequestID = ?", (request_id,))
            pending_data = cursor.fetchone()
            
            if not pending_data:
                QMessageBox.warning(self, "Error", "Request not found in database.")
                return

            name, email, password, contact, specialization = pending_data

            # --- LOGIC: CHECK IF DOCTOR EXISTS ---
            cursor.execute("SELECT DoctorID FROM Doctor WHERE DoctorEmail = ?", (email,))
            existing_doctor = cursor.fetchone()
            
            doctor_id = None

            if existing_doctor:
                # SCENARIO A: Doctor already exists (e.g., Thomas is adding a 2nd specialization)
                doctor_id = existing_doctor[0]
                print(f"Doctor exists (ID: {doctor_id}). Adding new specialization only.")
            else:
                # SCENARIO B: New Doctor
                doctor_id = self.get_next_id(cursor, "Doctor", "DoctorID")
                
                # Insert into Doctor Table
                insert_doc = """
                INSERT INTO Doctor (DoctorID, DoctorName, DoctorEmail, DoctorPassword, DoctorStatus, Contact, approved)
                VALUES (?, ?, ?, ?, 'Active', ?, 1)
                """
                cursor.execute(insert_doc, (doctor_id, name, email, password, contact))
                print(f"Created new Doctor (ID: {doctor_id}).")

            # --- ALWAYS: ADD SPECIALIZATION ---
            spec_id = self.get_next_id(cursor, "Specialisation", "SpecialisationID")
            insert_spec = "INSERT INTO Specialisation (SpecialisationID, FieldName, DoctorID) VALUES (?, ?, ?)"
            cursor.execute(insert_spec, (spec_id, specialization, doctor_id))

            # --- CLEANUP: REMOVE FROM PENDING ---
            cursor.execute("DELETE FROM PendingDoctor WHERE RequestID = ?", (request_id,))
            
            connection.commit()
            
            QMessageBox.information(self, "Success", f"Doctor {name} approved for {specialization}.")
            
            # Refresh the table
            self.load_pending_doctor_requests()

        except pyodbc.Error as e:
            connection.rollback()
            QMessageBox.critical(self, "Database Error", f"Approval failed: {e}")
        finally:
            connection.close()

    def reject_selected_doctor(self):
        current_row = self.admin_doctor_approval_approve_requests.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selection Error", "Please select a request to reject.")
            return

        request_id = self.admin_doctor_approval_approve_requests.item(current_row, 0).text()
        
        confirm = QMessageBox.question(self, "Confirm", "Are you sure you want to reject this request?", 
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.No:
            return

        connection = get_db_connection()
        if not connection: return
        cursor = connection.cursor()
        
        try:
            cursor.execute("DELETE FROM PendingDoctor WHERE RequestID = ?", (request_id,))
            connection.commit()
            QMessageBox.information(self, "Rejected", "Request has been removed.")
            self.load_pending_doctor_requests()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reject: {e}")
        finally:
            connection.close()

    def go_to_patient_portal_page(self):
        """
        Validates user credentials based on the ID length.
        - 3 digits = Doctor
        - Not 3 digits = Patient or Admin
        """
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
            if connection:
                connection.close()
        print("Navigated to patient portal (23)")

    def go_to_patient_portal_profile_page(self):
        """Navigate to patient profile page"""
        self.setCurrentIndex(23)  # page_4 (Patient profile page)
        print("Navigated to patient profile page (24)")
    
    def go_to_appointment_booking(self):
        if not self.selected_specialisation_id:
            QMessageBox.warning(self, "No specialization selected", "Please select a specialization from the list first.")
            return

        # show appointment booking page
        self.setCurrentIndex(16)
        print("Navigated to appointment booking (17)")

        # load doctors for selected specialization and load availability for the first doctor (if any)
        self.load_available_doctors_for_specialisation(self.selected_specialisation_id)

    def show_appointment_details_popup(self):
        # Get the current index (works for any column click)
        current_index = self.appointments_detail_dataview.currentIndex()
        
        if not current_index.isValid():
            QMessageBox.warning(self, "No Selection", "Please select an appointment first.")
            return
        
        selected_row = current_index.row()
        
        # Get the appointment ID from the first column (column 0 should have the ID)
        model = self.appointments_detail_dataview.model()
        appointment_id = model.data(model.index(selected_row, 0))
        
        if not appointment_id:
            QMessageBox.warning(self, "Error", "Could not retrieve appointment ID.")
            return
        
        # Fetch appointment details from database
        connection = get_db_connection()
        if connection is None:
            QMessageBox.critical(self, "Database Error", "Could not connect to the database.")
            return
        
        try:
            cursor = connection.cursor()
            
            query = """
                SELECT 
                    D.DoctorName,
                    U.Name AS PatientName,
                    DA.AppointmentDateTime,
                    DA.AppointmentStatus,
                    COALESCE(B.BillStatus, 'Unpaid') AS BillStatus
                FROM Doctor_Appointment DA
                INNER JOIN Doctor D ON DA.DoctorID = D.DoctorID
                INNER JOIN UserAccount U ON DA.PatientID = U.UserID
                LEFT JOIN Bill B ON B.OrderID = DA.AppointmentID AND B.PatientID = DA.PatientID
                WHERE DA.AppointmentID = ?
            """
            
            cursor.execute(query, (appointment_id,))
            result = cursor.fetchone()
            
            if not result:
                QMessageBox.warning(self, "Error", "Appointment details not found.")
                return
            
            # Extract data
            doctor_name = result[0] if result[0] else "N/A"
            patient_name = result[1] if result[1] else "N/A"
            appointment_datetime = result[2]
            appointment_status = result[3] if result[3] else "N/A"
            bill_status = result[4] if result[4] else "Unpaid"
            
            # Parse date and time
            if isinstance(appointment_datetime, str):
                parts = appointment_datetime.split(' ')
                appointment_date = parts[0]
                appointment_time = parts[1] if len(parts) > 1 else "N/A"
            else:
                appointment_date = appointment_datetime.strftime("%Y-%m-%d")
                appointment_time = appointment_datetime.strftime("%H:%M:%S")
            
            # Create popup dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Appointment Details")
            dialog.setFixedSize(500, 500)
            dialog.setStyleSheet("QDialog { background-color: #f5f5f5; }")
            
            # Create layout
            layout = QVBoxLayout()
            layout.setSpacing(15)
            layout.setContentsMargins(30, 30, 30, 30)
            
            # Title
            title_label = QLabel("Appointment Details")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet("""
                font-size: 20px;
                font-weight: bold;
                color: white;
                padding: 15px;
                background-color: #3498db;
                border-radius: 8px;
            """)
            layout.addWidget(title_label)
            
            layout.addSpacing(15)
            
            # Doctor Name
            doctor_label = QLabel("Doctor Name:")
            doctor_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
            layout.addWidget(doctor_label)
            
            doctor_value = QLabel(str(doctor_name))
            doctor_value.setWordWrap(True)
            doctor_value.setStyleSheet("""
                font-size: 14px;
                background-color: white;
                color: #2c3e50;
                padding: 12px;
                border-radius: 6px;
                border: 1px solid #bdc3c7;
            """)
            layout.addWidget(doctor_value)
            layout.addSpacing(5)
            
            # Patient Name
            patient_label = QLabel("Patient Name:")
            patient_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
            layout.addWidget(patient_label)
            
            patient_value = QLabel(str(patient_name))
            patient_value.setWordWrap(True)
            patient_value.setStyleSheet("""
                font-size: 14px;
                background-color: white;
                color: #2c3e50;
                padding: 12px;
                border-radius: 6px;
                border: 1px solid #bdc3c7;
            """)
            layout.addWidget(patient_value)
            layout.addSpacing(5)
            
            # Appointment Date
            date_label = QLabel("Appointment Date:")
            date_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
            layout.addWidget(date_label)
            
            date_value = QLabel(str(appointment_date))
            date_value.setWordWrap(True)
            date_value.setStyleSheet("""
                font-size: 14px;
                background-color: white;
                color: #2c3e50;
                padding: 12px;
                border-radius: 6px;
                border: 1px solid #bdc3c7;
            """)
            layout.addWidget(date_value)
            layout.addSpacing(5)
            
            # Appointment Time
            time_label = QLabel("Appointment Time:")
            time_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
            layout.addWidget(time_label)
            
            time_value = QLabel(str(appointment_time))
            time_value.setWordWrap(True)
            time_value.setStyleSheet("""
                font-size: 14px;
                background-color: white;
                color: #2c3e50;
                padding: 12px;
                border-radius: 6px;
                border: 1px solid #bdc3c7;
            """)
            layout.addWidget(time_value)
            layout.addSpacing(5)
            
            # Appointment Status
            status_label = QLabel("Appointment Status:")
            status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
            layout.addWidget(status_label)
            
            status_value = QLabel(str(appointment_status))
            status_value.setWordWrap(True)
            status_value.setStyleSheet("""
                font-size: 14px;
                background-color: white;
                color: #2c3e50;
                padding: 12px;
                border-radius: 6px;
                border: 1px solid #bdc3c7;
            """)
            layout.addWidget(status_value)
            layout.addSpacing(5)
            
            # Bill Status
            bill_label = QLabel("Bill Status:")
            bill_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
            layout.addWidget(bill_label)
            
            bill_value = QLabel(str(bill_status))
            bill_value.setWordWrap(True)
            if str(bill_status).lower() == 'paid':
                bill_value.setStyleSheet("""
                    font-size: 14px;
                    background-color: #d4edda;
                    color: #155724;
                    border: 2px solid #28a745;
                    padding: 12px;
                    border-radius: 6px;
                    font-weight: bold;
                """)
            else:
                bill_value.setStyleSheet("""
                    font-size: 14px;
                    background-color: #f8d7da;
                    color: #721c24;
                    border: 2px solid #dc3545;
                    padding: 12px;
                    border-radius: 6px;
                    font-weight: bold;
                """)
            layout.addWidget(bill_value)
            
            # Add stretch to push button down
            layout.addStretch()
            
            # OK Button
            ok_button = QPushButton("OK")
            ok_button.setFixedHeight(45)
            ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
            ok_button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #21618c;
                }
            """)
            ok_button.clicked.connect(dialog.accept)
            layout.addWidget(ok_button)
            
            dialog.setLayout(layout)
            # Position dialog to move it down
            parent_geometry = self.geometry()
            dialog_x = parent_geometry.x() + (parent_geometry.width() - dialog.width()) // 2  # Center horizontally
            dialog_y = parent_geometry.y() + 200  # Move down - increase this value for more down
            dialog.move(dialog_x, dialog_y)
            dialog.update()  # Force repaint
            dialog.repaint()
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load appointment details: {e}")
            print(f"Error details: {e}")
            import traceback
            traceback.print_exc()
        finally:
            connection.close()
    
    def cancel_appointment_button(self):
        try:
            selection_model = self.appointments_detail_dataview.selectionModel()
            if not selection_model:
                QMessageBox.warning(self, "Error", "No appointment selected.")
                return

            selected_indexes = selection_model.selectedIndexes()
            if not selected_indexes:
                QMessageBox.warning(self, "Error", "Please click any row in the table first.")
                return

            # Get the row of the clicked cell (no matter which column)
            row = selected_indexes[0].row()

            # Get AppointmentID from column 0
            model = self.appointments_detail_dataview.model()
            appointment_id = model.data(model.index(row, 0))

            if not appointment_id:
                QMessageBox.warning(self, "Error", "Invalid appointment selected.")
                return

            # Confirm cancellation - FIXED FOR PyQt6
            reply = QMessageBox.question(
                self,
                "Confirm Cancellation",
                f"Are you sure you want to cancel appointment ID {appointment_id}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Cancel the appointment in the database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Doctor_Appointment SET AppointmentStatus = 'Cancelled' WHERE AppointmentID = ?",
                (appointment_id,)
            )
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", "Appointment cancelled successfully!")

            # Refresh the table
            self.load_patient_appointments()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to cancel appointment: {e}")
    
    def go_to_patient_portal_appointment_page(self):
        """Navigate to appointment booking page"""
        self.setCurrentIndex(26)  # page_6
        print("Navigated to appointment booking (27)")
    
    def go_to_bills_page(self):
        """Navigate to bills page"""
        self.setCurrentIndex(24)  # page_10
        print("Navigated to bills page (25)")

    def load_bills_page(self):
        """Load bills using the mechanism from load_bills_from_appointments"""
        if not self.current_user_id:
            QMessageBox.warning(self, "Error", "No patient logged in.")
            return

        self.setCurrentIndex(24)  # bills page
        print("25")

        connection = get_db_connection()
        if connection is None:
            QMessageBox.critical(self, "Database Error", "Could not connect to the database.")
            return

        cursor = connection.cursor()

        try:
            # Create table model with the specific columns you asked for
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["ID", "Type", "Total Price", "Date"])

            # 1. Fetch ALL bills for this patient
            cursor.execute("""
                SELECT B.BillID, B.OrderID, B.TotalPrice, B.BillStatus, B.BillDate
                FROM Bill B
                WHERE B.PatientID = ?
                ORDER BY B.BillDate DESC
            """, (self.current_user_id,))
            bills = cursor.fetchall()

            for bill in bills:
                bill_id, order_id, total_price, bill_status, bill_date = bill
                
                # Default values
                type_str = "Unknown"
                date_time_str = str(bill_date) if bill_date else ""
                
                # We use the price as a 'tie-breaker' to distinguish Appointment 22 from Lab 22
                safe_price = float(total_price) if total_price else 0.0

                # ========== 1. CHECK IF IT'S A DOCTOR APPOINTMENT ==========
                # We check ID matches AND Price matches AND it's not Cancelled
                cursor.execute("""
                    SELECT DA.AppointmentDateTime
                    FROM Doctor_Appointment DA
                    WHERE DA.AppointmentID = ? 
                    AND ABS(DA.AppointmentPrice - ?) < 0.1
                    AND DA.AppointmentStatus != 'Cancelled'
                """, (order_id, safe_price))
                appointment = cursor.fetchone()
                
                if appointment:
                    type_str = "Appointment"
                    date_time_str = str(appointment[0])
                
                else:
                    # ========== 2. CHECK IF IT'S A LAB TEST ==========
                    cursor.execute("""
                        SELECT LT.TestDate
                        FROM LabTest LT
                        WHERE LT.TestID = ?
                        AND ABS(LT.TestPrice - ?) < 0.1
                    """, (order_id, safe_price))
                    lab_test = cursor.fetchone()
                    
                    if lab_test:
                        type_str = "Lab Test"
                        date_time_str = str(lab_test[0]) if lab_test[0] else ""
                    else:
                        # ========== 3. CHECK IF IT'S A PHARMACY ORDER ==========
                        # Pharmacy usually sums up multiple items, so price matching is harder, 
                        # but usually Pharmacy IDs don't conflict as much if generated sequentially.
                        cursor.execute("""
                            SELECT PO.OrderID
                            FROM Pharmacy_Order PO
                            WHERE PO.OrderID = ?
                        """, (order_id,))
                        pharmacy = cursor.fetchone()
                        
                        if pharmacy:
                            type_str = "Pharmacy"
                
                # Skip if we found nothing (likely a Cancelled appointment)
                if type_str == "Unknown":
                    continue

                # Add row to table
                id_item = QStandardItem(str(order_id))
                # Store Hidden Data for logic (Bill Status and Bill ID)
                id_item.setData(bill_status, role=Qt.ItemDataRole.UserRole)
                id_item.setData(bill_id, role=Qt.ItemDataRole.UserRole + 1) # Optional: Store BillID if needed

                row_items = [
                    id_item,
                    QStandardItem(type_str),                 # The new "Type" column
                    QStandardItem(f"{safe_price:.2f}"),      # Price
                    QStandardItem(date_time_str)             # Date
                ]
                model.appendRow(row_items)

            # Set model to dataview
            self.bills_detail_dataview.setModel(model)
            self.bills_detail_dataview.resizeColumnsToContents()
            
            # Button logic
            self.bills_generate_bill_button.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load bills: {e}")
            print(f"Error details: {e}")
        finally:
            connection.close()

    
    def go_to_admission_details(self):
        """Navigate to admission details page"""
        self.setCurrentIndex(26)  # page_11
        print("Navigated to admission details (27)")
        connection = None
        try:
            # --- 3. Connect to DB ---
            connection = get_db_connection()
            if connection is None:
                QMessageBox.critical(self, "Connection Error", "Could not connect to the database.")
                return
            
            cursor = connection.cursor()

            doc_query = "select doctorName from doctor where DoctorID in (select top 1 doctorId from Doctor_Appointment where PatientID = ? and AppointmentStatus = 'Completed' order by AppointmentDateTime desc)"
            cursor.execute(doc_query, (self.current_user_id,))
            doc_result = cursor.fetchone()

            if doc_result:
                self.admission_details_doctor.setText(str(doc_result[0]))
            else:
                self.admission_details_doctor.setText("N/A")

            # --- Patient / Admin Logic (Not 3 digits) ---
            query = "SELECT top 1 * FROM Admission_Details WHERE PatientID = ? ORDER BY ADMISSIONDATE DESC"
            cursor.execute(query, (self.current_user_id,))
            result = cursor.fetchone()
            if result:
                self.admission_details_room_no.setText(result[2])
                self.admission_details_date.setText(result[3].strftime("%Y-%m-%d"))
                self.admission_details_discharge_date.setText(str(result[4]))
                self.admission_details_total_chargers.setText(str(result[5]))
                
            else:
                self.admission_details_room_no.setText("N/A")
                self.admission_details_date.setText("N/A")
                self.admission_details_discharge_date.setText("N/A")
                self.admission_details_total_chargers.setText("N/A")

        except pyodbc.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred during login: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
        finally:
            if connection:
                connection.close()
    
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
            
            # Store medical history data for later use
            self.medical_history_data = results
            
            # Clear and populate the left list
            self.medical_history_list.clear()
            
            # Add only disease/allergy names to the left list
            for row in results:
                disease_name = row[3]  # Disease column
                allergy = row[2] if row[2] and row[2] != 'None' else ""
                
                if allergy:
                    display_text = f"{disease_name} (Allergy: {allergy})"
                else:
                    display_text = disease_name
                    
                self.medical_history_list.addItem(display_text)
            
            # Clear the right details box initially
            self.medical_history_details_text.clear()
            
            print(f"Fetched {len(results)} medical history records")
            
        except pyodbc.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error fetching medical history: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
        finally:
            if connection:
                connection.close()

        print("Navigated to medical history (29)")

    def show_selected_medical_history_details(self):
        """Display details of selected medical history in the right box"""
        selected_index = self.medical_history_list.currentRow()
        
        if selected_index < 0:
            QMessageBox.warning(self, "Selection Error", "Please select a medical record first.")
            return
        
        # Get the corresponding data
        if hasattr(self, 'medical_history_data') and selected_index < len(self.medical_history_data):
            row = self.medical_history_data[selected_index]
            
            # Format the details text
            details_text = f"Medical History Details:\n\n"
            details_text += f"Record ID: {row[0]}\n\n"
            details_text += f"Allergies: {row[2] or 'None'}\n\n"
            details_text += f"Disease: {row[3]}\n\n"
            details_text += f"Diagnosis Date: {row[4]}\n\n"
            details_text += f"Additional Details: {row[5]}\n"
            
            # Display in the right text box
            self.medical_history_details_text.setText(details_text)
        else:
            QMessageBox.warning(self, "Error", "Could not retrieve medical history details.")
            
    def go_to_specialization_page(self):
        """Load specialization table using PYODBC instead of QSqlDatabase."""
        self.setCurrentIndex(10)
        print("Navigated to specialization page 11)")
        connection = get_db_connection()
        if connection is None:
            QMessageBox.critical(self, "Database Error", "Could not connect to the database.")
            return

        cursor = connection.cursor()
        try:
            cursor.execute("SELECT SpecialisationID, FieldName, DoctorID FROM Specialisation")
            rows = cursor.fetchall()
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["Field Name"])
            for row in rows:
                name_item = QStandardItem(str(row[1]))
                name_item.setData(row[0], role=Qt.ItemDataRole.UserRole)  # Store SpecialisationID
                items = [
                    name_item
                ]
                model.appendRow(items)
            self.specialization_tableview.setModel(model)
            self.specialization_tableview.resizeColumnsToContents()
            print("Specialization table loaded successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Query Error", f"Failed to load specialization data: {e}")
        finally:
            connection.close()

    def on_specialization_row_selected(self, index):
        try:
            model = self.specialization_tableview.model()
            item = model.itemFromIndex(index)

            if item:
                self.selected_specialisation_id = item.data(Qt.ItemDataRole.UserRole)
                print("Selected SpecialisationID:", self.selected_specialisation_id)
            else:
                self.selected_specialisation_id = None

            print("Selected SpecialisationID:", self.selected_specialisation_id)
        except Exception as e:
            print("Error selecting specialization row:", e)
            self.selected_specialisation_id = None

    # --- Load doctors for a given specialisationID (populates combo box) ---
    def load_available_doctors_for_specialisation(self, specialisation_id):
        """Populate appointment_booking_available_doctors combo with doctors for the selected specialization."""
        connection = get_db_connection()
        if connection is None:
            QMessageBox.critical(self, "Database Error", "Could not connect to the database.")
            return

        cursor = connection.cursor()
        try:
            query = """
                SELECT D.DoctorID, ISNULL(D.DoctorName, 'Doctor') as DoctorName
                FROM Doctor D
                INNER JOIN Specialisation S ON D.DoctorID = S.DoctorID
                WHERE S.SpecialisationID = ?
            """
            cursor.execute(query, (specialisation_id,))
            rows = cursor.fetchall()

            # Clear combo
            try:
                self.appointment_booking_available_doctors.clear()
            except Exception:
                pass

            self._doctor_list_cache = []  # list of (doctor_id, doctor_name)

            for doc in rows:
                doc_id = str(doc[0])
                doc_name = str(doc[1])
                self._doctor_list_cache.append((doc_id, doc_name))
                # store doctor_id as userData
                try:
                    self.appointment_booking_available_doctors.addItem(f"{doc_name} (ID: {doc_id})", doc_id)
                except Exception:
                    # fallback if combo doesn't exist / name mismatched
                    pass

            # If at least one doctor, load availability for the first doctor
            if self._doctor_list_cache:
                first_doc_id = self._doctor_list_cache[0][0]
                # set combo index to 0 to trigger times load (if signal connected)
                try:
                    self.appointment_booking_available_doctors.setCurrentIndex(0)
                    print("1")
                except Exception:
                    pass
                # load availability explicitly
                self.load_availability_for_doctor(first_doc_id)
            else:
                # clear times if no doctors
                try:
                    self.appointment_booking_date_time.clear()
                except Exception:
                    pass

        except Exception as e:
            QMessageBox.critical(self, "Query Error", f"Failed to load doctors: {e}")
        finally:
            connection.close()

    # --- Doctor combo changed handler ---
    def on_doctor_combo_changed(self, index):
        # get doctor_id from userData if available, otherwise from our cache
        try:
            doctor_id = None
            try:
                doctor_id = self.appointment_booking_available_doctors.itemData(index)
            except Exception:
                doctor_id = None

            if doctor_id is None:
                # fallback to cache
                if hasattr(self, "_doctor_list_cache") and index < len(self._doctor_list_cache):
                    doctor_id = self._doctor_list_cache[index][0]
            if doctor_id:
                self.load_availability_for_doctor(str(doctor_id))
            else:
                self.appointment_booking_available_times.clear()
        except Exception as e:
            print("Error in on_doctor_combo_changed:", e)


    def load_availability_for_doctor(self, doctor_id):
        connection = get_db_connection()
        if connection is None:
            return

        cursor = connection.cursor()
        try:
            query = """
                SELECT A.AvailabilityID, A.Available
                FROM Doctor_Availability A
                WHERE A.DoctorID = ?
                AND NOT EXISTS (
                    SELECT 1 
                    FROM Doctor_Appointment DA
                    WHERE DA.DoctorID = A.DoctorID
                    AND CONVERT(VARCHAR(16), DA.AppointmentDateTime, 120) =
                        CONVERT(VARCHAR(16), A.Available, 120)
                    AND DA.AppointmentStatus IN ('Completed', 'Scheduled')
                )
                ORDER BY A.Available;
            """

            cursor.execute(query, (doctor_id,))
            rows = cursor.fetchall()

            self.appointment_booking_available_times.clear()
            for row in rows:
                self.appointment_booking_available_times.addItem(str(row[1]), row[0])

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load availability: {e}")
        finally:
            connection.close()


    def book_appointment(self):
        """Book an appointment with auto-incrementing BillID (requires IDENTITY on Bill table)."""
        if not self.current_user_id:
            QMessageBox.warning(self, "Error", "No patient logged in.")
            self.go_to_login_page()
            return

        doctor_index = self.appointment_booking_available_doctors.currentIndex()
        doctor_id = self.appointment_booking_available_doctors.itemData(doctor_index)

        time_index = self.appointment_booking_available_times.currentIndex()
        availability_id = self.appointment_booking_available_times.itemData(time_index)

        if doctor_id is None or availability_id is None:
            QMessageBox.warning(self, "Error", "Please select doctor and time.")
            return

        connection = get_db_connection()
        if connection is None:
            QMessageBox.critical(self, "Error", "Database connection failed.")
            return

        cursor = connection.cursor()

        try:
            # Generate next AppointmentID
            cursor.execute("SELECT COALESCE(MAX(AppointmentID), 0) + 1 FROM Doctor_Appointment")
            AppointmentID = cursor.fetchone()[0]

            AppointmentStatus = "Scheduled"
            appointment_price = 78

            # Step 1: Insert the appointment
            cursor.execute("""
                INSERT INTO Doctor_Appointment
                (AppointmentID, PatientID, DoctorID, AppointmentDateTime, AppointmentStatus, AppointmentPrice)
                VALUES (
                    ?, ?, ?, 
                    (SELECT Available FROM Doctor_Availability WHERE AvailabilityID=?),
                    ?, ?
                )
            """, (AppointmentID, self.current_user_id, doctor_id, availability_id, AppointmentStatus, appointment_price))

            # Step 2: Automatically create a bill (BillID auto-increments with IDENTITY)
            cursor.execute("""
                INSERT INTO Bill (OrderID, PatientID, BillDate, TotalPrice, BillStatus)
                VALUES (?, ?, GETDATE(), ?, 'Unpaid')
            """, (AppointmentID, self.current_user_id, appointment_price))

            connection.commit()
            QMessageBox.information(self, "Success", "Appointment booked and bill created successfully!")

            self.load_availability_for_doctor(doctor_id)

        except Exception as e:
            connection.rollback()
            QMessageBox.critical(self, "Booking Error", f"Failed to book appointment: {e}")

        finally:
            connection.close()


    def load_patient_appointments(self):
        """Load appointments for the logged-in patient and show in appointments page"""
        if not self.current_user_id:
            QMessageBox.warning(self, "Error", "No patient logged in.")
            return

        # Navigate to the appointments page
        self.go_to_patient_appointment_page()

        connection = get_db_connection()
        if connection is None: return
        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT A.AppointmentID, D.DoctorName, A.AppointmentDateTime, A.AppointmentStatus
                FROM Doctor_Appointment A
                JOIN Doctor D ON A.DoctorID = D.DoctorID
                WHERE A.PatientID = ?
                ORDER BY A.AppointmentDateTime
            """, (self.current_user_id,))
            rows = cursor.fetchall()

            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["ID", "Doctor", "Date & Time", "Status"])
            for row in rows:
                model.appendRow([
                    QStandardItem(str(row[0])),
                    QStandardItem(row[1]),
                    QStandardItem(str(row[2])),
                    QStandardItem(row[3])
                ])

            # Use correct QTableView from page_25
            self.appointments_detail_dataview.setModel(model)
            self.appointments_detail_dataview.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load appointments: {e}")
        finally:
            connection.close()

    def go_to_bill_gen_page(self, bill_id=None):
        self.setCurrentIndex(17)  # Bill generation page
        print("Navigated to bill generation page (18)")
        
        if bill_id:
            self.load_bill_for_generation(bill_id)
        else:
            # Clear the table if no bill is selected
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["Service Type", "Name", "Quantity/Price", "Total"])
            self.bill_generation_dataview.setModel(model)

    def load_bills_from_appointments(self):
        """Load all bills of the current patient."""
        if not self.current_user_id:
            QMessageBox.warning(self, "Error", "No patient logged in.")
            return

        # Navigate to bills page
        self.setCurrentIndex(24)
        print("25")

        connection = get_db_connection()
        if connection is None:
            QMessageBox.critical(self, "Database Error", "Could not connect to the database.")
            return

        cursor = connection.cursor()

        try:
            # Create table model
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["Bill ID", "Order ID", "Type", "Total Price", "Date / Time", "Status"])

            # ========== GET ALL BILLS FOR THIS PATIENT ==========
            # Since bills are auto-created, we just need to fetch all bills
            # and determine their type based on what the OrderID references
            
            cursor.execute("""
                SELECT B.BillID, B.OrderID, B.TotalPrice, B.BillStatus, B.BillDate
                FROM Bill B
                WHERE B.PatientID = ?
                ORDER BY B.BillID DESC
            """, (self.current_user_id,))
            bills = cursor.fetchall()

            for bill in bills:
                bill_id, order_id, total_price, bill_status, bill_date = bill
                
                type_str = "Unknown"
                date_time_str = str(bill_date) if bill_date else ""
                
                # ========== 1. CHECK IF IT'S A DOCTOR APPOINTMENT ==========
                cursor.execute("""
                    SELECT DA.AppointmentDateTime, DA.AppointmentPrice
                    FROM Doctor_Appointment DA
                    WHERE DA.AppointmentID = ?
                """, (order_id,))
                appointment = cursor.fetchone()
                
                if appointment:
                    type_str = "Doctor Appointment"
                    date_time_str = str(appointment[0])
                else:
                    # ========== 2. CHECK IF IT'S A LAB TEST ==========
                    cursor.execute("""
                        SELECT LT.TestDate, LT.TestName
                        FROM LabTest LT
                        WHERE LT.TestID = ?
                    """, (order_id,))
                    lab_test = cursor.fetchone()
                    
                    if lab_test:
                        type_str = "Lab Test"
                        date_time_str = str(lab_test[0]) if lab_test[0] else ""
                    else:
                        # ========== 3. CHECK IF IT'S A PHARMACY ORDER ==========
                        cursor.execute("""
                            SELECT PO.OrderID
                            FROM Pharmacy_Order PO
                            WHERE PO.OrderID = ?
                        """, (order_id,))
                        pharmacy = cursor.fetchone()
                        
                        if pharmacy:
                            type_str = "Pharmacy Order"
                            date_time_str = str(bill_date) if bill_date else ""
                
                # Add row to table
                bill_id_item = QStandardItem(str(bill_id))
                bill_id_item.setData(bill_status, Qt.ItemDataRole.UserRole)
                
                row_items = [
                    bill_id_item,
                    QStandardItem(str(order_id)),
                    QStandardItem(type_str),
                    QStandardItem(f"{total_price:.2f}"),
                    QStandardItem(date_time_str),
                    QStandardItem(bill_status if bill_status else "Unpaid")
                ]
                model.appendRow(row_items)

            # Set model to dataview
            self.bills_detail_dataview.setModel(model)
            self.bills_detail_dataview.resizeColumnsToContents()
            
            # Disconnect any existing connections to avoid duplicates
            try:
                self.bills_detail_dataview.clicked.disconnect()
            except:
                pass
            
            self.bills_detail_dataview.clicked.connect(self.on_bill_row_selected)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load bills: {e}")
            print(f"Error details: {e}")  # For debugging
        finally:
            connection.close()


    def on_bill_row_selected(self, index):
        """Enable/disable generate bill button based on bill status."""
        if not index.isValid():
            self.bills_generate_bill_button.setEnabled(False)
            return

        model = self.bills_detail_dataview.model()
        row = index.row()
        bill_id_item = model.item(row, 0)
        bill_status = bill_id_item.data(Qt.ItemDataRole.UserRole)

        # Disable button if already paid
        if bill_status and bill_status.lower() == "paid":
            self.bills_generate_bill_button.setEnabled(False)
        else:
            self.bills_generate_bill_button.setEnabled(True)

    def show_bill_details(self):
        index = self.bills_detail_dataview.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "Please select a bill first.")
            return

        bill_id = index.sibling(index.row(), 0).data()  # BillID
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # First, get the bill info
            cursor.execute("""
                SELECT OrderID, TotalPrice, BillStatus, PatientID
                FROM Bill
                WHERE BillID = ?
            """, (bill_id,))
            bill = cursor.fetchone()
            if not bill:
                QMessageBox.warning(self, "Error", "No details found for this bill.")
                return

            order_id, total_price, bill_status, patient_id = bill

            details_text = f"Bill ID: {bill_id}\nBill Status: {bill_status}\nTotal Amount: {total_price}\n\n"

            # Check if it's a Doctor Appointment
            cursor.execute("""
                SELECT DA.AppointmentDateTime, DA.AppointmentPrice, D.DoctorName, S.FieldName
                FROM Doctor_Appointment DA
                JOIN Doctor D ON DA.DoctorID = D.DoctorID
                LEFT JOIN Specialisation S ON D.DoctorID = S.DoctorID
                WHERE DA.AppointmentID = ?
            """, (order_id,))
            doctor_appt = cursor.fetchone()

            if doctor_appt:
                appointment_time, appointment_price, doctor_name, specialization = doctor_appt
                details_text += (
                    f"Type: Doctor Appointment\n"
                    f"Doctor Name: {doctor_name}\n"
                    f"Specialization: {specialization}\n"
                    f"Appointment Time: {appointment_time}\n"
                    f"Appointment Price: {appointment_price}\n"
                )
            else:
                # Check if it's a Lab Test
                cursor.execute("""
                    SELECT TestName, TestDate, TestPrice, TestStatus
                    FROM LabTest
                    WHERE TestID = ?
                """, (order_id,))
                lab_test = cursor.fetchone()
                if lab_test:
                    test_name, test_date, test_price, test_status = lab_test
                    details_text += (
                        f"Type: Lab Test\n"
                        f"Test Name: {test_name}\n"
                        f"Test Date: {test_date}\n"
                        f"Test Price: {test_price}\n"
                        f"Test Status: {test_status}\n"
                    )
                else:
                    # Check if it's a Pharmacy Order
                    cursor.execute("""
                        SELECT P.ItemName, O.ItemQuantity, O.PricePerItem, O.TotalPrice
                        FROM Pharmacy_Order O
                        JOIN Pharmacy_Item P ON O.ItemID = P.ItemID
                        WHERE O.OrderID = ?
                    """, (order_id,))
                    pharmacy_order = cursor.fetchone()
                    if pharmacy_order:
                        item_name, quantity, price_per_item, total = pharmacy_order
                        details_text += (
                            f"Type: Pharmacy Order\n"
                            f"Item Name: {item_name}\n"
                            f"Quantity: {quantity}\n"
                            f"Price Per Item: {price_per_item}\n"
                            f"Total: {total}\n"
                        )
                    else:
                        details_text += "Unknown order type."

            QMessageBox.information(self, "Bill Details", details_text)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            connection.close()

    def load_bill_for_generation(self, bill_id):
        """Load the selected bill's details into the bill generation table."""
        connection = get_db_connection()
        if connection is None:
            QMessageBox.critical(self, "Database Error", "Could not connect to database.")
            return

        cursor = connection.cursor()
        try:
            # Get bill info
            cursor.execute("""
                SELECT BillID, OrderID, TotalPrice, BillStatus, PatientID
                FROM Bill
                WHERE BillID = ?
            """, (bill_id,))
            bill = cursor.fetchone()

            if not bill:
                QMessageBox.warning(self, "Error", "Bill not found.")
                return

            bill_id_val, order_id, total_price, bill_status, patient_id = bill
            self.current_bill_id_for_payment = bill_id_val
            
            # Use price for tie-breaking
            safe_price = float(total_price) if total_price else 0.0

            # Prepare table model
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["Service Type", "Name", "Quantity/Price", "Total"])

            # --- 1. Check if it's a Doctor Appointment ---
            # Added Price check to avoid confusing Appointment #22 with Lab #22
            cursor.execute("""
                SELECT DA.AppointmentID, DA.AppointmentDateTime, DA.AppointmentPrice,
                    D.DoctorName, S.FieldName AS Specialisation
                FROM Doctor_Appointment DA
                LEFT JOIN Doctor D ON DA.DoctorID = D.DoctorID
                LEFT JOIN Specialisation S ON D.DoctorID = S.DoctorID
                WHERE DA.AppointmentID = ? 
                AND ABS(DA.AppointmentPrice - ?) < 0.1
            """, (order_id, safe_price))
            appointment = cursor.fetchone()
            
            if appointment:
                specialisation = appointment[4] if appointment[4] else "General"
                model.appendRow([
                    QStandardItem("Doctor"),
                    QStandardItem(f"{appointment[3]} ({specialisation})"),
                    QStandardItem(str(appointment[2])),
                    QStandardItem(str(appointment[2]))
                ])

            # --- 2. Check if it's a Lab Test ---
            else:
                cursor.execute("""
                    SELECT LT.TestName, LT.TestPrice
                    FROM LabTest LT
                    WHERE LT.TestID = ?
                    AND ABS(LT.TestPrice - ?) < 0.1
                """, (order_id, safe_price))
                lab = cursor.fetchone()
                
                if lab:
                    model.appendRow([
                        QStandardItem("Lab Test"),
                        QStandardItem(lab[0]),
                        QStandardItem(str(lab[1])),
                        QStandardItem(str(lab[1]))
                    ])

                # --- 3. Check if it's a Pharmacy Order ---
                else:
                    cursor.execute("""
                        SELECT PI.ItemName, PO.ItemQuantity, PO.PricePerItem, PO.TotalPrice
                        FROM Pharmacy_Order PO
                        LEFT JOIN Pharmacy_Item PI ON PO.ItemID = PI.ItemID
                        WHERE PO.OrderID = ?
                    """, (order_id,))
                    order = cursor.fetchone()
                    
                    if order:
                        model.appendRow([
                            QStandardItem("Pharmacy"),
                            QStandardItem(order[0]),
                            QStandardItem(f"{order[1]} x {order[2]}"),
                            QStandardItem(str(order[3]))
                        ])

            # Set model
            self.bill_generation_dataview.setModel(model)
            self.bill_generation_dataview.resizeColumnsToContents()
            self.calculate_bill_total()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load bill: {e}")
        finally:
            connection.close()
    
    def calculate_bill_total(self):
        """Calculate the total from all items in the bill generation table."""
        model = self.bill_generation_dataview.model()
        
        if not model:
            self.bill_generation_total_label.setText("0.00")
            return
        
        total = 0.0
        
        # Loop through all rows in the table
        for row in range(model.rowCount()):
            # Get the "Total" column (column index 3)
            total_item = model.item(row, 3)
            if total_item:
                try:
                    # Extract numeric value from the cell
                    value = float(total_item.text())
                    total += value
                except ValueError:
                    continue
        
        # Display the total with 2 decimal places
        self.bill_generation_total_label.setText(f"{total:.2f}")

    # --- Helper Functions to Get Selected Bill IDs ---
    def get_selected_bill_id_from_bills(self):
        from PyQt6.QtCore import Qt

        index = self.bills_detail_dataview.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "Please select a bill first.")
            return None
            
        # CHANGED: Retrieve the hidden BillID from UserRole + 1 
        # (We stored it there in the load_bills_page function)
        return index.sibling(index.row(), 0).data(Qt.ItemDataRole.UserRole + 1)

    def get_selected_lab_bill_id(self):
        index = self.patient_labs_tableview.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "Please select a lab bill first.")
            return None
        return index.sibling(index.row(), 0).data()

    def get_selected_appointment_bill_id(self):
        index = self.appointments_detail_dataview.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "Please select an appointment first.")
            return None
        return index.sibling(index.row(), 0).data()
    
    def show_payment_message(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Payment Status")
        msg.setText("Transaction Successful!\nYour payment has been received.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)

        result = msg.exec()

        if result == QMessageBox.StandardButton.Ok:

            if not hasattr(self, "current_bill_id_for_payment"):
                QMessageBox.warning(self, "Error", "No bill loaded.")
                return

            bill_id = self.current_bill_id_for_payment

            connection = get_db_connection()
            if connection is None:
                QMessageBox.critical(self, "Error", "Database connection failed.")
                return

            try:
                cursor = connection.cursor()
                cursor.execute("""
                    UPDATE Bill
                    SET BillStatus = 'Paid'
                    WHERE BillID = ?
                """, (bill_id,))
                connection.commit()

                QMessageBox.information(self, "Success", "Bill has been marked as Paid.")

                # Refresh bills page
                self.load_bills_page()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update bill: {e}")
            finally:
                connection.close()



    def go_to_lab_test_page(self):
        self.setCurrentIndex(12)
        print("Navigated to lab_test page (13)")
        self.load_available_lab_tests()


    def go_to_patient_lab_page(self):
        self.setCurrentIndex(27)
        print("Navigated to patient_lab (28)")
        self.load_patient_lab_tests()
    
    def load_available_lab_tests(self):
        if not self.current_user_id:
            QMessageBox.warning(self, "Error", "No patient logged in.")
            return

        connection = get_db_connection()
        if connection is None:
            QMessageBox.critical(self, "Database Error", "Could not connect to the database.")
            return

        cursor = connection.cursor()

        try:
            cursor.execute("""
                SELECT TestID, TestName, TestPrice 
                FROM LabTest
            """)

            rows = cursor.fetchall()

            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["Test ID", "Test Name", "Price"])

            for row in rows:
                model.appendRow([
                    QStandardItem(str(row[0])),
                    QStandardItem(str(row[1])),
                    QStandardItem(str(row[2]))
                ])

            self.lab_tests_items_view.setModel(model)
            self.lab_tests_items_view.resizeColumnsToContents()

            print("Lab test list loaded.")

        except Exception as e:
            QMessageBox.critical(self, "Query Error", f"Failed to load lab tests: {e}")

        finally:
            connection.close()


    def on_lab_test_row_selected(self, index):
        try:
            row = index.row()
            model = self.lab_tests_items_view.model()

            test_id_item = model.item(row, 0)

            if test_id_item:
                self.selected_test_id = test_id_item.text()
            else:
                self.selected_test_id = None

            print("Selected TestID:", self.selected_test_id)

        except Exception as e:
            print("Error selecting lab test row:", e)
            self.selected_test_id = None

    def on_patient_lab_test_row_selected(self, index):
        try:
            row = index.row()
            model = self.patient_labs_tableview.model()

            test_id_item = model.item(row, 0)

            if test_id_item:
                self.selected_test_id = test_id_item.text()
            else:
                self.selected_test_id = None

            print("Selected TestID:", self.selected_test_id)

        except Exception as e:
            print("Error selecting lab test row:", e)
            self.selected_test_id = None

    
    def book_lab_test(self):
        if not self.current_user_id:
            QMessageBox.warning(self, "Error", "No patient logged in.")
            self.go_to_login_page()
            return

        if not hasattr(self, "selected_test_id") or not self.selected_test_id:
            QMessageBox.warning(self, "Error", "Please select a lab test.")
            return

        connection = get_db_connection()
        if connection is None:
            QMessageBox.critical(self, "Error", "Database connection failed.")
            return

        cursor = connection.cursor()
        try:
            # Manually generate TestID
            cursor.execute("SELECT COALESCE(MAX(TestID), 0) + 1 FROM LabTest")
            new_test_id = cursor.fetchone()[0]

            # Fetch price
            cursor.execute("SELECT TestPrice FROM LabTest WHERE TestID = ?", (self.selected_test_id,))
            price = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO LabTest 
                (TestID, TestName, PatientID, TestDate, TestDesc, TestStatus, TestPrice)
                SELECT ?, TestName, ?, GETDATE(), 'Pending Test', 'Scheduled', TestPrice
                FROM LabTest WHERE TestID = ?
            """, (new_test_id, self.current_user_id, self.selected_test_id))

            # Create Bill
            cursor.execute("""
                INSERT INTO Bill (OrderID, PatientID, BillDate, TotalPrice, BillStatus)
                VALUES (?, ?, GETDATE(), ?, 'Unpaid')
            """, (new_test_id, self.current_user_id, price))

            connection.commit()

            QMessageBox.information(self, "Success", "Lab test booked and bill created!")
            self.go_to_patient_lab_page()


        except Exception as e:
            connection.rollback()
            QMessageBox.critical(self, "Booking Error", f"Failed to book lab test: {e}")
        finally:
            connection.close()
    
    def load_patient_lab_tests(self):
        if not self.current_user_id:
            QMessageBox.warning(self, "Error", "No patient logged in.")
            return

        connection = get_db_connection()
        if connection is None:
            return

        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT TestID, TestName, TestDate, TestStatus
                FROM LabTest
                WHERE PatientID = ?
                ORDER BY TestDate DESC
            """, (self.current_user_id,))

            rows = cursor.fetchall()

            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["ID", "Test Name", "Date", "Status"])

            for row in rows:
                model.appendRow([
                    QStandardItem(str(row[0])),
                    QStandardItem(str(row[1])),
                    QStandardItem(str(row[2])),
                    QStandardItem(str(row[3]))
                ])

            self.patient_labs_tableview.setModel(model)
            self.patient_labs_tableview.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load lab tests: {e}")
        finally:
            connection.close()


    def go_to_check_result_page(self):
        self.setCurrentIndex(18)
        print("Navigated to lab result page (19)")

    
    def on_check_result_clicked(self):
        # Guards
        if not getattr(self, "current_user_id", None):
            QMessageBox.warning(self, "Error", "No patient logged in.")
            self.go_to_login_page()
            return

        if not hasattr(self, "selected_test_id") or not self.selected_test_id:
            QMessageBox.warning(self, "Error", "Please select a lab test first.")
            return

        connection = get_db_connection()
        if connection is None:
            QMessageBox.critical(self, "Error", "Database connection failed.")
            return

        cursor = connection.cursor()
        try:
            # Fetch exactly your columns
            cursor.execute("""
                SELECT TestID, TestName, PatientID, TestDate, TestDesc, ResultDate, TestStatus, TestPrice
                FROM LabTest
                WHERE TestID = ?
                """, (self.selected_test_id,))

            row = cursor.fetchone()

            if not row:
                QMessageBox.warning(self, "Not Found",
                                    "The selected lab test was not found for this patient.")
                return

            (test_id, test_name, patient_id, test_date,
            test_desc, result_date, test_status, test_price) = row

            # Only allow if Completed
            if str(test_status).strip().lower() != "completed":
                QMessageBox.information(self, "Result not ready",
                                        "This test has not been completed yet.")
                return

            # Populate labels on result page
            self.result_test_id_value.setText(str(test_id))
            self.result_patient_id_value.setText(str(patient_id))
            self.result_doctor_id_value.setText("-")  # per your requirement
            # self.result_test_name_value.setText(str(test_name))
            self.result_date_taken_value.setText(str(test_date) if test_date else "—")
            # self.result_result_date_value.setText(str(result_date) if result_date else "—")
            # self.result_status_value.setText(str(test_status))
            # Price formatting
            # try:
                # self.result_price_value.setText(f"{float(test_price):.2f}")
            # except Exception:
            #     self.result_price_value.setText(str(test_price) if test_price is not None else "—")
            # self.result_test_id_value.setText(str(test_id))
            # self.result_desc_value.setText(str(test_desc) if test_desc else 
            # Navigate to Results page
            self.setCurrentIndex(18)
            print("19")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load lab test result: {e}")
        finally:
            connection.close()
    
    def show_lab_test_details(self):
        """Show all lab test details inside result_desc_value label"""

        if not hasattr(self, "selected_test_id") or not self.selected_test_id:
            QMessageBox.warning(self, "Error", "No test selected.")
            return

        connection = get_db_connection()
        if connection is None:
            QMessageBox.critical(self, "Error", "Database connection failed.")
            return

        cursor = connection.cursor()

        try:
            cursor.execute("""
                SELECT TestID, TestName, PatientID, TestDate, TestDesc,
                    ResultDate, TestStatus, TestPrice
                FROM LabTest
                WHERE TestID = ?
            """, (self.selected_test_id,))

            row = cursor.fetchone()

            if not row:
                QMessageBox.warning(self, "Error", "No details found for this test.")
                return

            (test_id, test_name, patient_id, test_date,
            test_desc, result_date, test_status, test_price) = row

            from datetime import datetime, timedelta

            # Parse test_date
            try:
                test_dt = datetime.strptime(str(test_date), "%Y-%m-%d")
            except:
                try:
                    test_dt = datetime.strptime(str(test_date), "%Y-%m-%d %H:%M:%S")
                except:
                    test_dt = None

            if result_date:
                result_date_text = str(result_date)
            else:
                if test_dt:
                    expected = (test_dt + timedelta(days=5)).strftime("%Y-%m-%d")
                    result_date_text = f"{expected} (Expected)"
                else:
                    result_date_text = "Pending"

            # ---------------------------
            # Build Details Text
            # ---------------------------
            details_text = "Lab Test Details:\n\n"
            details_text += f"Test ID: {test_id}\n\n"
            details_text += f"Test Name: {test_name}\n\n"
            details_text += f"Patient ID: {patient_id}\n\n"
            details_text += f"Test Date: {test_date}\n\n"
            details_text += f"Result Date: {result_date_text}\n\n"
            details_text += f"Status: {test_status}\n\n"
            details_text += f"Price: {test_price}\n\n"
            details_text += f"Description:\n{test_desc or 'No Description'}\n"

            self.result_desc_value.setText(details_text)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load details: {e}")

        finally:
            connection.close()


    def go_to_doctor_registration_page(self):
        self.setCurrentIndex(3)
        print("Navigated to doctor page (4)")

    def go_to_login(self):
        self.setCurrentIndex(4)
        print("5")

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

            special_query = "select FieldName from Specialisation where DoctorID=?"
            cursor.execute(special_query, (user_id,))
            spec_result = cursor.fetchall()

            if spec_result:
                specialization_list = [row[0] for row in spec_result]
                display_text = "\n".join(specialization_list)
                self.doctor_profile_specialization.setText(display_text)

            avail_query = "select Available from Doctor_Availability where DoctorID=?"
            cursor.execute(avail_query, (user_id,))
            avail_result = cursor.fetchall()

            if avail_result:
                availability_list = [row[0].strftime("%Y-%m-%d %H:%M") for row in avail_result]
                display_text = "\n".join(availability_list)
                self.doctor_profile_availability.setText(display_text)

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
                    self.setCurrentIndex(19)
                    self.doctor_profile_name.setText(result[1])
                    self.doctor_profile_email.setText(result[2])
                    self.doctor_profile_contact.setText(result[5])
                    self.doctor_profile_docid.setText(str(result[0]))
                    
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
            print("Navigated to doc portal (20)")

    def go_to_doctor_profile_page(self):
        self.setCurrentIndex(20)
        print("21")
    
    def go_to_doctor_appointment_page(self):
        """Load specialization table using PYODBC instead of QSqlDatabase."""
        self.setCurrentIndex(21)
        print("22")
        connection = get_db_connection()
        if connection is None:
            QMessageBox.critical(self, "Database Error", "Could not connect to the database.")
            return

        cursor = connection.cursor()
        try:
            cursor.execute("select AppointmentID, PatientID, AppointmentDateTime, AppointmentPrice, AppointmentStatus from Doctor_Appointment where DoctorID=?", (self.current_user_id,))
            rows = cursor.fetchall()
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["AppointmentID", "PatientID", "DateTime", "Price", "Status"])
            for row in rows:
                appointment_item = QStandardItem(str(row[0]))
                patient_item     = QStandardItem(str(row[1]))
                datetime_item    = QStandardItem(str(row[2]))
                price_item       = QStandardItem(str(row[3]))
                status_item      = QStandardItem(str(row[4]))

                patient_item.setData(row[1], Qt.ItemDataRole.UserRole)

                items = [
                    appointment_item,
                    patient_item,
                    datetime_item,
                    price_item,
                    status_item     
                ]
                model.appendRow(items)

            self.appointments_admit_dataview.setModel(model)
            self.appointments_admit_dataview.resizeColumnsToContents()
            print("Appointment table loaded successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Query Error", f"Failed to load appointment data: {e}")
        finally:
            connection.close()
    
    def on_doc_app_row_selected(self, index):
        model = self.appointments_admit_dataview.model()
        patient_item = model.item(index.row(), 1)

        if patient_item:
            self.selected_patient_id = patient_item.data(Qt.ItemDataRole.UserRole)
            self.appointments_medical_history_searchbutton.setText(str(self.selected_patient_id))
            print("Selected PatientID:", self.selected_patient_id)
    
    def go_to_editable_medical_history(self):
        if not hasattr(self, 'selected_patient_id') or self.selected_patient_id is None:
            QMessageBox.warning(self, "No Patient Selected", "Please select a patient first.")
            return
        
        self.setCurrentIndex(29)
        self.doc_medical_history_patient_id_lineedit.setText(str(self.selected_patient_id))
        print("30")

        connection = get_db_connection()
        if connection is None:
            QMessageBox.critical(self, "Database Error", "Could not connect to the database.")
            return
        cursor = connection.cursor()

        query = """SELECT *
            FROM Medical_History
            WHERE PatientID = ?
            ORDER BY DiagnosisDate DESC"""
        
        cursor.execute(query, (self.selected_patient_id,))
        results = cursor.fetchall()

        if not results:
            QMessageBox.information(self, "No Records", "No medical history records found for this patient.")
            return
        
        self.medical_history = results
        self.doc_medical_history_list.clear()

        for row in results:
            disease_name = row[3]
            allergy = row[2] if row[2] and row[2] != 'None' else ""
                
            if allergy:
                display_text = f"{disease_name} (Allergy: {allergy})"
            else:
                display_text = disease_name
                
            self.doc_medical_history_list.addItem(display_text)

        self.medical_history_details_text.clear()
        print(f"Fetched {len(results)} medical history records")
        connection.close()

    def show_selected_doc_medical_history_details(self):
        """Display details of selected medical history in the right box"""
        selected_index = self.doc_medical_history_list.currentRow()
        
        if selected_index < 0:
            QMessageBox.warning(self, "Selection Error", "Please select a medical record first.")
            return
        
        # Get the corresponding data
        if hasattr(self, 'medical_history') and selected_index < len(self.medical_history):
            row = self.medical_history[selected_index]
            
            # Format the details text
            details_text = f"Medical History Details:\n\n"
            details_text += f"Record ID: {row[0]}\n\n"
            details_text += f"Allergies: {row[2] or 'None'}\n\n"
            details_text += f"Disease: {row[3]}\n\n"
            details_text += f"Diagnosis Date: {row[4]}\n\n"
            details_text += f"Additional Details: {row[5]}\n"
            
            # Display in the right text box
            self.doc_medical_history_details_text.setText(details_text)
        else:
            QMessageBox.warning(self, "Error", "Could not retrieve medical history details.")

    def admit_patient_from_appointment(self):
        if not hasattr(self, 'selected_patient_id') or self.selected_patient_id is None:
            QMessageBox.warning(self, "No Patient Selected", "Please select a patient first.")
            return

        connection = get_db_connection()
        if connection is None:
            QMessageBox.critical(self, "Database Error", "Could not connect to the database.")
            return

        cursor = connection.cursor()
        try:
            # Manually generate AdmissionID
            cursor.execute("SELECT COALESCE(MAX(AdmissionID), 0) + 1 FROM Admission_Details")
            new_admission_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO Admission_Details (AdmissionID, PatientID, Ref_DoctorID, AdmissionDate)
                VALUES (?, ?, ?, GETDATE())
            """, (new_admission_id, self.selected_patient_id, self.current_user_id))

            connection.commit()

            QMessageBox.information(self, "Success", f"Patient {self.selected_patient_id} admitted with Admission ID {new_admission_id}.")

        except Exception as e:
            connection.rollback()
            QMessageBox.critical(self, "Admission Error", f"Failed to admit patient: {e}")
        finally:
            connection.close()
    
    def cancel_selected_appointment(self):
        view = self.appointments_admit_dataview
        index = view.currentIndex()

        if not index.isValid():
            QMessageBox.warning(self, "No Selection", "Please select an appointment first.")
            return

        model = view.model()

        # AppointmentID is in column 0
        appointment_id = model.item(index.row(), 0).text()

        confirm = QMessageBox.question(
            self,
            "Confirm Cancellation",
            f"Cancel appointment ID {appointment_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        connection = get_db_connection()
        if connection is None:
            QMessageBox.critical(self, "Database Error", "Could not connect to database.")
            return

        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE Doctor_Appointment
                SET AppointmentStatus = ?
                WHERE AppointmentID = ?
            """, ('Cancelled', appointment_id))

            connection.commit()

            status_item = model.item(index.row(), 4)  
            status_item.setText("Cancelled")

            QMessageBox.information(self, "Success", "Appointment cancelled successfully.")

        except Exception as e:
            connection.rollback()
            QMessageBox.critical(self, "Error", f"Failed to cancel appointment:\n{e}")
        finally:
            connection.close()


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
            print("Navigated to admin portal (6)")

    def go_to_admin_patient_page(self):
        self.setCurrentIndex(7)
        print("8")
        self.load_admission_details()

    def load_admission_details(self):
        from PyQt6.QtCore import Qt  
        
        connection = get_db_connection()
        if connection is None:
            return

        cursor = connection.cursor()
        try:
            # UPDATED QUERY: Added ORDER BY to show 'Admitted' (NULL DischargeDate) first
            query = """
                SELECT 
                    AD.AdmissionID, 
                    UA.Name AS PatientName, 
                    D.DoctorName, 
                    AD.RoomNo, 
                    AD.AdmissionDate,
                    AD.DischargeDate
                FROM Admission_Details AD
                INNER JOIN UserAccount UA ON AD.PatientID = UA.UserID
                INNER JOIN Doctor D ON AD.Ref_DoctorID = D.DoctorID
                ORDER BY 
                    CASE WHEN AD.DischargeDate IS NULL THEN 0 ELSE 1 END ASC, 
                    AD.AdmissionDate DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["Patient Name", "Doctor Name", "Room No", "Admission Date", "Status"])

            for row in rows:
                patient_item = QStandardItem(str(row[1]))
                patient_item.setData(row[0], Qt.ItemDataRole.UserRole)

                discharge_date = row[5]
                if discharge_date is None:
                    status_text = "Admitted"
                else:
                    status_text = "Discharged"

                items = [
                    patient_item,                 
                    QStandardItem(str(row[2])),   
                    QStandardItem(str(row[3])),   
                    QStandardItem(str(row[4])),   
                    QStandardItem(status_text)    
                ]
                model.appendRow(items)
            
            self.admin_patient_admission_dataview.setModel(model)
            self.admin_patient_admission_dataview.resizeColumnsToContents()

        except Exception as e:
            print(f"Error loading admission details: {e}")
        finally:
            connection.close()
        

    def go_to_admin_patient_admission_edit_page(self):
        from PyQt6.QtCore import Qt
        
        index = self.admin_patient_admission_dataview.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Selection Error", "Please select an admission record to edit.")
            return

        model = self.admin_patient_admission_dataview.model()
        patient_item = model.item(index.row(), 0)
        admission_id = patient_item.data(Qt.ItemDataRole.UserRole)
        
        if not admission_id:
            QMessageBox.warning(self, "Error", "Could not retrieve Admission ID.")
            return

        self.current_editing_admission_id = admission_id

        connection = get_db_connection()
        if not connection: return
        
        cursor = connection.cursor()
        try:
            query = """
                SELECT RoomNo, AdmissionDate, DischargeDate, Ref_DoctorID 
                FROM Admission_Details 
                WHERE AdmissionID = ?
            """
            cursor.execute(query, (admission_id,))
            result = cursor.fetchone()

            if result:
                self.setCurrentIndex(8)
                print(f"Editing Admission ID: {admission_id}")

                self.admin_admission_entry_room.setText(str(result[0]))
                
                self.admin_admission_entry_AdDate.setText(str(result[1]))
                self.admin_admission_entry_AdDate.setReadOnly(True)  # <-- Added this line
                
                if result[2]:
                    self.admin_admission_entry_DisDate.setText(str(result[2]))
                else:
                    self.admin_admission_entry_DisDate.clear()
                
                self.admin_admission_entry_AsDoc.setText(str(result[3]))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {e}")
        finally:
            connection.close()
    
    def save_admission_changes(self):
        room_no = self.admin_admission_entry_room.text()
        ad_date = self.admin_admission_entry_AdDate.text()
        dis_date = self.admin_admission_entry_DisDate.text()
        doc_id = self.admin_admission_entry_AsDoc.text()

        if not room_no or not ad_date or not doc_id:
            QMessageBox.warning(self, "Input Error", "Room, Admission Date, and Doctor ID are required.")
            return
        
        if dis_date.strip() == "":
            dis_date = None

        connection = get_db_connection()
        if not connection: return
        
        cursor = connection.cursor()
        try:
            query = """
                UPDATE Admission_Details 
                SET RoomNo = ?, AdmissionDate = ?, DischargeDate = ?, Ref_DoctorID = ?
                WHERE AdmissionID = ?
            """
            cursor.execute(query, (room_no, ad_date, dis_date, doc_id, self.current_editing_admission_id))
            connection.commit()

            QMessageBox.information(self, "Success", "Admission details updated successfully!")

            self.go_to_admin_patient_page()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Update failed: {e}")
        finally:
            connection.close()

    def go_to_admin_apecialization_edit_page(self):
        self.setCurrentIndex(11)
        print("12")
    
    def go_to_admin_pharmacy_edit_page(self):
        self.setCurrentIndex(15)
        print("16")
        self.load_pharmacy_items()
    
    def load_pharmacy_items(self):
        from PyQt6.QtCore import Qt  # Ensure this import exists
        
        connection = get_db_connection()
        if connection is None:
            return

        cursor = connection.cursor()
        try:
            query = "SELECT ItemID, ItemName, Category, QuantityInStock, PricePerItem FROM Pharmacy_Item"
            cursor.execute(query)
            rows = cursor.fetchall()

            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["Name", "Category", "Stock", "Price"])

            for row in rows:
                # Create the Name item separately so we can attach the ID to it
                name_item = QStandardItem(str(row[1]))
                name_item.setData(row[0], Qt.ItemDataRole.UserRole)  # Store ID hidden inside the name item

                items = [
                    name_item,
                    QStandardItem(str(row[2])),
                    QStandardItem(str(row[3])),
                    QStandardItem(str(row[4]))
                ]
                model.appendRow(items)
            
            self.Admin_pharmacy_entry_dataview.setModel(model)
            self.Admin_pharmacy_entry_dataview.resizeColumnsToContents()

        except Exception as e:
            print(f"Error loading pharmacy items: {e}")
        finally:
            connection.close()
    
    def add_pharmacy_item(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
        from PyQt6.QtCore import Qt

        dialog = QDialog(self)
        dialog.setWindowTitle("Add Pharmacy Item")
        dialog.setFixedSize(500, 600)
        dialog.setStyleSheet("QDialog { background-color: #f5f5f5; }")

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        title_label = QLabel("Add New Item")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: white;
            padding: 15px;
            background-color: #f46677;
            border-radius: 8px;
        """)
        layout.addWidget(title_label)
        layout.addSpacing(15)

        name_label = QLabel("Item Name:")
        name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(name_label)

        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter item name")
        name_input.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                background-color: white;
                color: #2c3e50;
                padding: 12px;
                border-radius: 6px;
                border: 1px solid #bdc3c7;
            }
        """)
        layout.addWidget(name_input)

        category_label = QLabel("Category:")
        category_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(category_label)

        category_input = QLineEdit()
        category_input.setPlaceholderText("Enter category")
        category_input.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                background-color: white;
                color: #2c3e50;
                padding: 12px;
                border-radius: 6px;
                border: 1px solid #bdc3c7;
            }
        """)
        layout.addWidget(category_input)

        stock_label = QLabel("Quantity in Stock:")
        stock_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(stock_label)

        stock_input = QLineEdit()
        stock_input.setPlaceholderText("Enter numeric quantity")
        stock_input.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                background-color: white;
                color: #2c3e50;
                padding: 12px;
                border-radius: 6px;
                border: 1px solid #bdc3c7;
            }
        """)
        layout.addWidget(stock_input)

        price_label = QLabel("Price Per Item:")
        price_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(price_label)

        price_input = QLineEdit()
        price_input.setPlaceholderText("Enter price")
        price_input.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                background-color: white;
                color: #2c3e50;
                padding: 12px;
                border-radius: 6px;
                border: 1px solid #bdc3c7;
            }
        """)
        layout.addWidget(price_input)

        layout.addStretch()

        submit_button = QPushButton("Add Item")
        submit_button.setFixedHeight(45)
        submit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        submit_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)

        def submit_data():
            name = name_input.text()
            category = category_input.text()
            stock = stock_input.text()
            price = price_input.text()

            if not name or not category or not stock or not price:
                QMessageBox.warning(dialog, "Input Error", "Please fill in all fields.")
                return

            if not stock.isdigit():
                QMessageBox.warning(dialog, "Input Error", "Stock must be a valid integer.")
                return

            try:
                float(price)
            except ValueError:
                QMessageBox.warning(dialog, "Input Error", "Price must be a valid number.")
                return

            connection = get_db_connection()
            if connection is None:
                return
            
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT MAX(ItemID) FROM Pharmacy_Item")
                max_id = cursor.fetchone()[0]
                next_id = 1 if max_id is None else max_id + 1

                query = "INSERT INTO Pharmacy_Item (ItemID, ItemName, Category, QuantityInStock, PricePerItem) VALUES (?, ?, ?, ?, ?)"
                cursor.execute(query, (next_id, name, category, stock, price))
                connection.commit()
                
                QMessageBox.information(dialog, "Success", "Item added successfully.")
                self.load_pharmacy_items() 
                dialog.accept()

            except Exception as e:
                QMessageBox.critical(dialog, "Database Error", f"Failed to add item: {e}")
            finally:
                connection.close()

        submit_button.clicked.connect(submit_data)
        layout.addWidget(submit_button)

        dialog.setLayout(layout)
        
        parent_geometry = self.geometry()
        dialog_x = parent_geometry.x() + (parent_geometry.width() - dialog.width()) // 2
        dialog_y = parent_geometry.y() + 100 
        dialog.move(dialog_x, dialog_y)
        
        dialog.exec()

    def remove_pharmacy_item(self):
        from PyQt6.QtCore import Qt 

        index = self.Admin_pharmacy_entry_dataview.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Selection Error", "Please select an item to remove.")
            return

        model = self.Admin_pharmacy_entry_dataview.model()
        
        # Get the item from the first column (Name column) which holds our hidden ID
        name_item = model.item(index.row(), 0)
        item_id = name_item.data(Qt.ItemDataRole.UserRole)

        confirm = QMessageBox.question(self, "Confirm", "Are you sure you want to delete this item?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.No:
            return

        connection = get_db_connection()
        if connection is None:
            return
        
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM Pharmacy_Item WHERE ItemID = ?", (item_id,))
            connection.commit()
            QMessageBox.information(self, "Success", "Item removed successfully.")
            self.load_pharmacy_items()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to remove item: {e}")
        finally:
            connection.close()

    def go_to_admin_lab_entry_page(self):
        self.setCurrentIndex(14)
        self.load_lab_entries()
    
    def load_lab_entries(self):
        from PyQt6.QtCore import Qt
        
        connection = get_db_connection()
        if connection is None:
            return

        cursor = connection.cursor()
        try:
            query = "SELECT LabID, TestName, TestPrice FROM LabEntries"
            cursor.execute(query)
            rows = cursor.fetchall()

            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["Test Name", "Price"])

            for row in rows:
                name_item = QStandardItem(str(row[1]))
                name_item.setData(row[0], Qt.ItemDataRole.UserRole)

                items = [
                    name_item,
                    QStandardItem(str(row[2]))
                ]
                model.appendRow(items)
            
            self.Admin_lab_tests_entry_dataview.setModel(model)
            self.Admin_lab_tests_entry_dataview.resizeColumnsToContents()

        except Exception as e:
            print(f"Error loading lab entries: {e}")
        finally:
            connection.close()
    
    def add_lab_entry(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
        from PyQt6.QtCore import Qt

        dialog = QDialog(self)
        dialog.setWindowTitle("Add Lab Test")
        dialog.setFixedSize(500, 450)
        dialog.setStyleSheet("QDialog { background-color: #f5f5f5; }")

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        title_label = QLabel("Add New Lab Test")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: white;
            padding: 15px;
            background-color: #3498db;
            border-radius: 8px;
        """)
        layout.addWidget(title_label)
        layout.addSpacing(15)

        name_label = QLabel("Test Name:")
        name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(name_label)

        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter test name")
        name_input.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                background-color: white;
                color: #2c3e50;
                padding: 12px;
                border-radius: 6px;
                border: 1px solid #bdc3c7;
            }
        """)
        layout.addWidget(name_input)

        price_label = QLabel("Price:")
        price_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(price_label)

        price_input = QLineEdit()
        price_input.setPlaceholderText("Enter price")
        price_input.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                background-color: white;
                color: #2c3e50;
                padding: 12px;
                border-radius: 6px;
                border: 1px solid #bdc3c7;
            }
        """)
        layout.addWidget(price_input)

        layout.addStretch()

        submit_button = QPushButton("Add Test")
        submit_button.setFixedHeight(45)
        submit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        submit_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)

        def submit_data():
            name = name_input.text()
            price = price_input.text()

            if not name or not price:
                QMessageBox.warning(dialog, "Input Error", "Please fill in all fields.")
                return

            try:
                float(price)
            except ValueError:
                QMessageBox.warning(dialog, "Input Error", "Price must be a valid number.")
                return

            connection = get_db_connection()
            if connection is None:
                return
            
            cursor = connection.cursor()
            try:
                # --- CHANGED: No manual ID calculation needed! ---
                
                # We simply insert Name and Price. The DB creates the ID automatically.
                query = "INSERT INTO LabEntries (TestName, TestPrice) VALUES (?, ?)"
                cursor.execute(query, (name, price))
                connection.commit()
                
                QMessageBox.information(dialog, "Success", "Lab test added successfully.")
                self.load_lab_entries()
                dialog.accept()

            except Exception as e:
                QMessageBox.critical(dialog, "Database Error", f"Failed to add test: {e}")
            finally:
                connection.close()

        submit_button.clicked.connect(submit_data)
        layout.addWidget(submit_button)

        dialog.setLayout(layout)
        
        parent_geometry = self.geometry()
        dialog_x = parent_geometry.x() + (parent_geometry.width() - dialog.width()) // 2
        dialog_y = parent_geometry.y() + 100
        dialog.move(dialog_x, dialog_y)
        
        dialog.exec()

    def remove_lab_entry(self):
        from PyQt6.QtCore import Qt

        index = self.Admin_lab_tests_entry_dataview.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Selection Error", "Please select a test to remove.")
            return

        model = self.Admin_lab_tests_entry_dataview.model()
        name_item = model.item(index.row(), 0)
        lab_id = name_item.data(Qt.ItemDataRole.UserRole)

        confirm = QMessageBox.question(self, "Confirm", "Are you sure you want to delete this test?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.No:
            return

        connection = get_db_connection()
        if connection is None:
            return
        
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM LabEntries WHERE LabID = ?", (lab_id,))
            connection.commit()
            QMessageBox.information(self, "Success", "Lab test removed successfully.")
            self.load_lab_entries()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to remove test: {e}")
        finally:
            connection.close()


    def go_to_pharmacy_page(self):
        self.setCurrentIndex(13)
        print("14")
    
    def go_to_patient_appointment_page(self):
        self.setCurrentIndex(25)
        print("26")

app = QtWidgets.QApplication(sys.argv)
window = HospitalApp()
window.show()
sys.exit(app.exec())
