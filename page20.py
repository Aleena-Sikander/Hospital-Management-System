from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox  # <-- Import QMessageBox for error popups
from PyQt6.QtGui import QStandardItemModel, QStandardItem
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
        self.selected_specialisation_id = None
        self._doctor_list_cache = []
        self._availability_cache = []

        # Start at first page
        self.setCurrentIndex(0)

        # --- Connect buttons to their pages ---
        # First page (page index 0 - first_page) buttons
        self.GCH_login_button.clicked.connect(self.go_to_login_page)
        self.GCH_our_services_button.clicked.connect(self.go_to_service_page)
        self.specialization_tableview.clicked.connect(self.on_specialization_row_selected)


        # Login page (page index 1 - page_2) buttons
        self.appointments_details_button.clicked.connect(self.load_bills_from_appointments)
        self.login_patient_button.clicked.connect(self.go_to_login)
        self.login_patient_button.clicked.connect(self.prepare_login_as_patient)
        self.login_register_button.clicked.connect(self.go_to_patient_registration)
        self.patient_registration_submit_button.clicked.connect(self.go_to_login) #condition
        self.patient_registration_submit_button.clicked.connect(self.patient_registration_submit)
        self.login_submit_button.clicked.connect(self.handle_login_submit) # route based on chosen role

        # Patient portal page (page index 3 - page_3) buttons
        self.patient_portal_profile_button.clicked.connect(self.go_to_patient_portal_profile_page)
        self.patient_portal_appointment_button.clicked.connect(self.load_patient_appointments)
        self.patient_portal_bills_button.clicked.connect(self.go_to_bills_page)
        self.patient_portal_admission_details_button.clicked.connect(self.go_to_admission_details)
        self.our_services_specializations_button.clicked.connect(self.go_to_specialization_page)
        self.specialization_book_button.clicked.connect(self.go_to_appointment_booking)

        # Appointment page controls
        try:
            # When the user selects a different doctor in combo, update times
            self.appointment_booking_available_doctors.currentIndexChanged.connect(self.on_doctor_combo_changed)
            # When user clicks Book on appointment page: perform insertion
           # self.appointment_booking_book_button.clicked.connect(self.book_appointment)
        except Exception:
            # If the appointment widgets don't exist yet (UI differs), we'll fail gracefully.
            pass
        self.appointment_booking_generate_bill_button.clicked.connect(self.go_to_bill_gen_page)
        self.appointment_booking_back_button.clicked.connect(self.go_to_service_page)
        self.appointment_booking_book_button.clicked.connect(self.book_appointment) #change
        self.bills_generate_bill_button.clicked.connect(self.go_to_bill_gen_page)
        self.bill_generation_add_more_button.clicked.connect(self.go_to_service_page)
        self.our_services_lab_test_button.clicked.connect(self.go_to_lab_test_page)
        self.lab_tests_book_button.clicked.connect(self.go_to_patient_lab_page)
        self.our_services_pharmacy_button.clicked.connect(self.go_to_pharmacy_page)
        self.our_services_back_button.clicked.connect(self.go_to_patient_portal_profile_page)
        self.patient_labs_check_result_button.clicked.connect(self.go_to_check_result_page)
        self.lab_test_result_back_button.clicked.connect(self.go_to_patient_lab_page)
        self.patient_labs_generate_bill_button.clicked.connect(self.go_to_bill_gen_page)
        self.medical_history_back_button.clicked.connect(self.go_to_patient_portal_profile_page)
        self.patient_profile_back_button.clicked.connect(self.go_to_patient_portal_page)
        self.bills_back_button.clicked.connect(self.go_to_patient_portal_page)
        self.appointments_back_button.clicked.connect(self.go_to_patient_portal_page)
        self.admission_details_back_button.clicked.connect(self.go_to_patient_portal_page)
        self.specialization_back_button.clicked.connect(self.go_to_service_page)
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
        print("Navigated to patient portal")

    def go_to_patient_portal_profile_page(self):
        """Navigate to patient profile page"""
        self.setCurrentIndex(23)  # page_4 (Patient profile page)
        print("Navigated to patient profile page")
    
    def go_to_appointment_booking(self):
        """Navigate to appointment booking page"""
        """Called when user clicks 'Book' on specialization page.
           Requires that a specialization row has already been selected.
        """
        if not self.selected_specialisation_id:
            QMessageBox.warning(self, "No specialization selected", "Please select a specialization from the list first.")
            return

        # show appointment booking page
        self.setCurrentIndex(16)
        print("Navigated to appointment booking")

        # load doctors for selected specialization and load availability for the first doctor (if any)
        self.load_available_doctors_for_specialisation(self.selected_specialisation_id)
    
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
        """Load specialization table using PYODBC instead of QSqlDatabase."""
        self.setCurrentIndex(10)
        print("Navigated to specialization page")
        connection = get_db_connection()
        if connection is None:
            QMessageBox.critical(self, "Database Error", "Could not connect to the database.")
            return

        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM Specialisation")
            rows = cursor.fetchall()
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["ID", "Field Name", "Doctor ID"])
            for row in rows:
                items = [
                    QStandardItem(str(row[0])),
                    QStandardItem(str(row[1])),
                    QStandardItem(str(row[2])),
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
            row = index.row()
            model = self.specialization_tableview.model()

            # Try to access using QStandardItemModel indexing; adjust if your model differs
            spec_id_item = model.item(row, 0)
            if spec_id_item is None:
                self.selected_specialisation_id = None
            else:
                self.selected_specialisation_id = spec_id_item.text()

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

    # --- Load availability times for a specific doctor ---
    def load_availability_for_doctor(self, doctor_id):
        """Populate appointment_booking_available_times with times for the given doctor."""
        connection = get_db_connection()
        if connection is None:
            QMessageBox.critical(self, "Database Error", "Could not connect to the database.")
            return

        cursor = connection.cursor()
        try:
            query = """
                SELECT AvailabilityID, Available
                FROM Doctor_Availability
                WHERE DoctorID = ? AND Available IS NOT NULL
                ORDER BY Available
            """
            cursor.execute(query, (doctor_id,))
            rows = cursor.fetchall()

            # clear the combo box
            self.appointment_booking_available_times.clear()

            # cache mapping combo index -> availability_id
            self._availability_cache = []

            for availability_id, available_value in rows:
                # Format datetime for display
                if hasattr(available_value, 'strftime'):
                    display_text = available_value.strftime("%Y-%m-%d   %I:%M %p")
                else:
                    display_text = str(available_value)

                self._availability_cache.append((availability_id, available_value))
                self.appointment_booking_available_times.addItem(display_text, availability_id)

        except Exception as e:
            QMessageBox.critical(self, "Query Error", f"Failed to load availability: {e}")
        finally:
            connection.close()

    def book_appointment(self):
        """Insert a new appointment for the patient."""
        if not self.current_user_id:
            QMessageBox.warning(self, "Error", "No patient logged in.")
            return
        doctor_index = self.appointment_booking_available_doctors.currentIndex()
        doctor_id = self.appointment_booking_available_doctors.itemData(doctor_index)
        time_index = self.appointment_booking_available_times.currentIndex()
        availability_id = self.appointment_booking_available_times.itemData(time_index)
        if not doctor_id or not availability_id:
            QMessageBox.warning(self, "Error", "Please select doctor and time.")
            return

        connection = get_db_connection()
        if connection is None: return
        cursor = connection.cursor()
        try:
            # Insert into Doctor_Appointment
            cursor.execute("""
                INSERT INTO Doctor_Appointment (PatientID, DoctorID, AppointmentDateTime, AppointmentStatus, AppointmentPrice)
                VALUES (?, ?, (SELECT Available FROM Doctor_Availability WHERE AvailabilityID=?), 'Booked', 0)
            """, (self.current_user_id, doctor_id, availability_id))
            connection.commit()
            QMessageBox.information(self, "Success", "Appointment booked successfully!")
            # Reload availability to remove booked slot if needed
            self.load_availability_for_doctor(doctor_id)
        except Exception as e:
            QMessageBox.critical(self, "Booking Error", str(e))
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

    def go_to_bill_gen_page(self):
        self.setCurrentIndex(17)
        print("Navigated to bill generation page")
    
    def load_bills_from_appointments(self):
        """Load all bills of the current patient when clicking Details in appointments page."""
        
        if not self.current_user_id:
            QMessageBox.warning(self, "Error", "No patient logged in.")
            return

        # Navigate to bills page
        self.setCurrentIndex(24)

        connection = get_db_connection()
        if connection is None:
            QMessageBox.critical(self, "Database Error", "Could not connect to the database.")
            return

        cursor = connection.cursor()

        try:
            query = """
                SELECT 
                    B.BillID,
                    B.OrderID,
                    B.TotalPrice,
                    B.BillStatus,
                    DA.AppointmentDateTime
                FROM Bill B
                LEFT JOIN Doctor_Appointment DA ON B.OrderID = DA.AppointmentID
                WHERE B.PatientID = ?
                ORDER BY B.BillID DESC
            """

            cursor.execute(query, (self.current_user_id,))
            rows = cursor.fetchall()

            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(
                ["Bill ID", "Appointment ID", "Amount", "Status", "Appointment Date"]
            )
            
            for row in rows:
                items = [QStandardItem(str(col)) for col in row]
                model.appendRow(items)

            self.bills_detail_dataview.setModel(model)
            self.bills_detail_dataview.resizeColumnsToContents()

            # Connect row selection
            self.bills_detail_dataview.clicked.connect(self.on_bill_row_selected)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load bills: {e}")
        finally:
            connection.close()

    
    def on_bill_row_selected(self, index):
        """Enable or disable Generate Bill button depending on bill status."""
        model = self.bills_detail_dataview.model()
        row = index.row()

        status_item = model.item(row, 3)  # Status column
        status = status_item.text().strip().lower()

        if status == "paid" or status == "completed":
            self.bills_generate_bill_button.setEnabled(False)
        else:
            self.bills_generate_bill_button.setEnabled(True)



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
        self.setCurrentIndex(13)
    
    def go_to_patient_appointment_page(self):
        self.setCurrentIndex(25)

app = QtWidgets.QApplication(sys.argv)
window = HospitalApp()
window.show()
sys.exit(app.exec())
