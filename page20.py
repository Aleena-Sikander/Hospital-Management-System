from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox  # <-- Import QMessageBox for error popups
from PyQt6.QtGui import QStandardItemModel, QStandardItem
import sys
import pyodbc  # <-- Import pyodbc to handle exceptions
from sql_connection import get_db_connection

class HospitalApp(QtWidgets.QStackedWidget):
    def __init__(self):
        super(HospitalApp, self).__init__()
        uic.loadUi("Hospital-Management-System\dbproj.ui", self)
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
        self.login_register_button.clicked.connect(self.go_to_patient_registration)
        self.patient_registration_submit_button.clicked.connect(self.go_to_login) #condition
        self.login_submit_button.clicked.connect(self.go_to_patient_portal_page) #condition

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
        """
        Validates user credentials based on the ID length.
        - 3 digits = Doctor
        - Not 3 digits = Patient or Admin
        """
        id_text = self.login_register_id.text()
        password = self.login_register_password.text()

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

            # --- 4. Check logic based on ID length ---
            is_doctor_check = (len(id_text) == 3)

            if is_doctor_check:
                # --- Doctor Logic (3 digits) ---
                query = "SELECT DoctorPassword, DoctorStatus FROM Doctor WHERE DoctorID = ?"
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()

                if result:
                    db_password, db_status = result
                    if db_password == password:
                        if db_status == 'Active':
                            print(f"Login successful for Doctor: {user_id}")
                            self.current_user_id = user_id # Save the doctor's ID
                            self.go_to_doctor_portal_page()
                        else:
                            QMessageBox.warning(self, "Login Failed", f"Account is not active. Status: {db_status}")
                    else:
                        QMessageBox.warning(self, "Login Failed", "Invalid ID or password.")
                else:
                    QMessageBox.warning(self, "Login Failed", "Invalid ID or password.")

            else:
                # --- Patient / Admin Logic (Not 3 digits) ---
                query = "SELECT Password, Role FROM UserAccount WHERE UserID = ?"
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()

                if result:
                    db_password, db_role = result
                    if db_password == password:
                        if db_role == 'Patient':
                            print(f"Login successful for Patient: {user_id}")
                            self.current_user_id = user_id # Save the patient's ID
                            self.setCurrentIndex(22)
                        elif db_role == 'Admin':
                            print(f"Login successful for Admin: {user_id}")
                            self.current_user_id = user_id # Save the admin's ID
                            self.go_to_admin_portal_page()
                        else:
                            QMessageBox.warning(self, "Login Failed", f"User role '{db_role}' is not valid for login.")
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
        self.setCurrentIndex(28)  # page_15
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

app = QtWidgets.QApplication(sys.argv)
window = HospitalApp()
window.show()
sys.exit(app.exec())
