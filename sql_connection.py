import pyodbc

# --- Connection Details ---
SERVER = r'DESKTOP-GDT94QR\ALEENASQLSERVER'
DATABASE = 'Hospital_Managment_System'
USE_WINDOWS_AUTH = True

def get_db_connection():
    """
    Establishes and returns a new database connection.
    """
    if USE_WINDOWS_AUTH:
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'
    else:
        # You would need to get username/password from a secure source
        username = 'your_username' 
        password = 'your_password'
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={username};PWD={password}'
    
    try:
        connection = pyodbc.connect(connection_string)
        return connection
    except Exception as e: #ok this should change it
        print(f"Error establishing database connection: {e}")
        return None

def setup_database():
    """
    Drops existing tables (if they exist) and creates/populates all tables.
    USE WITH CAUTION - THIS WILL DELETE ALL EXISTING DATA.
    """
    print("Setting up new database...")
    connection = get_db_connection()
    if connection is None:
        print("Failed to get DB connection. Aborting setup.")
        return

    cursor = connection.cursor()

    # --- Drop tables in reverse order of creation to avoid FK constraints ---
    drop_statements = [
        "IF OBJECT_ID('Bill', 'U') IS NOT NULL DROP TABLE Bill",
        "IF OBJECT_ID('Pharmacy_Order', 'U') IS NOT NULL DROP TABLE Pharmacy_Order",
        "IF OBJECT_ID('Pharmacy_Item', 'U') IS NOT NULL DROP TABLE Pharmacy_Item",
        "IF OBJECT_ID('Doctor_Appointment', 'U') IS NOT NULL DROP TABLE Doctor_Appointment",
        "IF OBJECT_ID('Admission_Details', 'U') IS NOT NULL DROP TABLE Admission_Details",
        "IF OBJECT_ID('Doctor_Availability', 'U') IS NOT NULL DROP TABLE Doctor_Availability",
        "IF OBJECT_ID('Specialisation', 'U') IS NOT NULL DROP TABLE Specialisation",
        "IF OBJECT_ID('Doctor', 'U') IS NOT NULL DROP TABLE Doctor",
        "IF OBJECT_ID('LabTest', 'U') IS NOT NULL DROP TABLE LabTest",
        "IF OBJECT_ID('Medical_History', 'U') IS NOT NULL DROP TABLE Medical_History",
        "IF OBJECT_ID('UserAccount', 'U') IS NOT NULL DROP TABLE UserAccount",
    ]
    
    print("Dropping existing tables...")
    for statement in drop_statements:
        try:
            cursor.execute(statement)
        except Exception as e:
            print(f"Error dropping table: {e}")
            
    connection.commit()

    # SQL queries to create tables
    create_statements = [
        """
        CREATE TABLE UserAccount (
            UserID INTEGER IDENTITY(1,1) NOT NULL,  -- CHANGED THIS LINE
            Name VARCHAR(100) NOT NULL,
            ContactNumber VARCHAR(15),
            Gender CHAR(1),
            Role VARCHAR(20),
            DateOfBirth DATE,
            Email VARCHAR(100) UNIQUE NOT NULL,
            Password VARCHAR(100) NOT NULL,
            CONSTRAINT pk_user PRIMARY KEY (UserID)
        )
        """,
        """
        CREATE TABLE Medical_History (
            MedicalHistoryID INTEGER PRIMARY KEY,
            PatientID INTEGER NOT NULL,
            Allergies TEXT,
            Disease TEXT,
            DiagnosisDate DATE,
            Details TEXT,
            CONSTRAINT fk_medhist_user FOREIGN KEY (PatientID) REFERENCES UserAccount(UserID)
        )
        """,
        """
        CREATE TABLE LabTest (
            TestID INTEGER PRIMARY KEY,
            TestName VARCHAR(50) NOT NULL,
            PatientID INTEGER NOT NULL,
            TestDate DATE NOT NULL,
            TestDesc TEXT,
            ResultDate DATE,
            TestStatus VARCHAR(20),
            TestPrice FLOAT NOT NULL,
            CONSTRAINT fk_labtest_user FOREIGN KEY (PatientID) REFERENCES UserAccount(UserID)
        )
        """,
        """
        CREATE TABLE Doctor (
            DoctorID INTEGER PRIMARY KEY,
            DoctorName VARCHAR(100) NOT NULL,
            DoctorEmail VARCHAR(100) UNIQUE NOT NULL,
            DoctorPassword VARCHAR(100) NOT NULL,
            DoctorStatus VARCHAR(20),
            Contact VARCHAR(20),   -- New Column
            approved INTEGER       -- New Column (1 or 0)
        )
        """,
        """
        CREATE TABLE Specialisation (
            SpecialisationID INTEGER PRIMARY KEY,
            FieldName VARCHAR(50) NOT NULL,
            DoctorID INTEGER NOT NULL,
            CONSTRAINT fk_specialisation_doctor FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID)
        )
        """,
        """
        CREATE TABLE Doctor_Availability (
            AvailabilityID INTEGER PRIMARY KEY,
            DoctorID INTEGER NOT NULL,
            Available DATETIME NOT NULL,
            CONSTRAINT fk_availability_doctor FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID)
        )
        """,
        """
        CREATE TABLE Admission_Details (
            AdmissionID INTEGER PRIMARY KEY,
            PatientID INTEGER NOT NULL,
            RoomNo VARCHAR(5) NOT NULL,
            AdmissionDate DATE NOT NULL,
            DischargeDate DATE,
            RoomPrice FLOAT NOT NULL,
            CONSTRAINT fk_admission_user FOREIGN KEY (PatientID) REFERENCES UserAccount(UserID)
        )
        """,
        """
        CREATE TABLE Doctor_Appointment (
            AppointmentID INTEGER PRIMARY KEY,
            PatientID INTEGER NOT NULL,
            DoctorID INTEGER NOT NULL,
            AppointmentDateTime DATETIME NOT NULL,
            AppointmentStatus VARCHAR(20),
            AppointmentPrice FLOAT NOT NULL,
            CONSTRAINT fk_appointment_user FOREIGN KEY (PatientID) REFERENCES UserAccount(UserID),
            CONSTRAINT fk_appointment_doctor FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID)
        )
        """,
        """
        CREATE TABLE Pharmacy_Item (
            ItemID INTEGER PRIMARY KEY,
            ItemName VARCHAR(50) NOT NULL,
            Category VARCHAR(30),
            QuantityInStock INTEGER DEFAULT 0,
            PricePerItem FLOAT NOT NULL
        )
        """,
        """
        CREATE TABLE Pharmacy_Order (
            OrderID INTEGER NOT NULL PRIMARY KEY,
            ItemID INTEGER NOT NULL,
            ItemQuantity INTEGER NOT NULL,
            PricePerItem FLOAT NOT NULL,
            TotalPrice AS (PricePerItem * ItemQuantity),
            CONSTRAINT fk_order_item FOREIGN KEY (ItemID) REFERENCES Pharmacy_Item(ItemID)
        )
        """,
        """
        CREATE TABLE PendingDoctor (
            RequestID INTEGER IDENTITY(1,1) PRIMARY KEY,
            Name VARCHAR(100) NOT NULL,
            Email VARCHAR(100) NOT NULL,
            Password VARCHAR(100) NOT NULL,
            Contact VARCHAR(20) NOT NULL,
            Specialization VARCHAR(50) NOT NULL,
            RequestDate DATE DEFAULT GETDATE()
        )
        """,
        """
        CREATE TABLE Bill (
            BillID INTEGER PRIMARY KEY,
            OrderID INTEGER NOT NULL,
            PatientID INTEGER NOT NULL,
            BillDate DATE NOT NULL,
            TotalPrice FLOAT NOT NULL,
            BillStatus VARCHAR(20),
            CONSTRAINT fk_bill_user FOREIGN KEY (PatientID) REFERENCES UserAccount(UserID),
            CONSTRAINT fk_bill_order FOREIGN KEY (OrderID) REFERENCES Pharmacy_Order(OrderID)
        )
    """]

    print("Creating new tables...")
    for statement in create_statements:
        try:
            cursor.execute(statement)
            print("Table created successfully.")
        except Exception as e:
            print(f"Error creating table: {e}")
    print("All tables created.")
    connection.commit() # Commit after all tables are created
    print("Inserting data...")
    # sql queries to populate tables with sample data

    user_data = [
        (1, 'Aleena Sikander', '03001234567', 'F', 'Admin', '1980-05-12', 'aleena.sik@hospital.com', 'as123'),
        (2, 'Asad Ali Lodhi', '03011234567', 'M', 'Admin', '1975-08-22', 'asad.ali@hospital.com', 'aal123'),
        (3, 'Saira Talha', '03021234567', 'F', 'Admin', '1982-03-15', 'saira.tal@hospital.com', 'st123'),
        (4, 'Bilal Amir', '03031234567', 'M', 'Patient', '1978-11-30', 'bilal.amir@hospital.com', 'ba123'),
        (5, 'Dania Nadeem', '03041234567', 'F', 'Patient', '1985-07-09', 'dania.nad@hospital.com', 'dn123'),
        (6, 'Alina Rehman', '03051234567', 'F', 'Patient', '1990-01-01', 'alina.rehman@gmail.com', 'ar123'),
        (7, 'Alishba Inshal Qasim', '03061234567', 'F', 'Patient', '1992-02-02', 'alishba.insh@gmail.com', 'aiq123'),
        (8, 'Zainab Tariq', '03071234567', 'F', 'Patient', '1988-03-03', 'zainab.tariq@gmail.com', 'zt123'),
        (9, 'Usman Javed', '03081234567', 'M', 'Patient', '1985-04-04', 'usman.javed@gmail.com', 'uj123'),
        (10, 'Sameea Ahmer', '03091234567', 'F', 'Patient', '1993-05-05', 'sam.ahm@gmail.com', 'sa123'),
        (11, 'Ahmed Raza', '03101234567', 'M', 'Patient', '1987-06-06', 'ahmed.raza@gmail.com', 'ar123'),
        (12, 'Mehwish Ali', '03111234567', 'F', 'Patient', '1991-07-07', 'mehwish.ali@gmail.com', 'ma23'),
        (13, 'Tariq Mehmood', '03121234567', 'M', 'Patient', '1989-08-08', 'tariq.mehmood@gmail.com', 'tm123'),
        (14, 'Sana Iqbal', '03131234567', 'F', 'Patient', '1994-09-09', 'sana.iqbal@gmail.com', 'si123'),
        (15, 'Rizwan Khan', '03141234567', 'M', 'Patient', '1986-10-10', 'rizwan.khan@gmail.com', 'rk123'),
        (16, 'Lubna Sheikh', '03151234567', 'F', 'Patient', '1995-11-11', 'lubna.sheikh@gmail.com', 'ls123'),
        (17, 'Noman Qureshi', '03161234567', 'M', 'Patient', '1990-12-12', 'noman.qureshi@gmail.com', 'nq123'),
        (18, 'Areeba Siddiqui', '03171234567', 'F', 'Patient', '1996-01-13', 'areeba.siddiqui@gmail.com', 'arsi123'),
        (19, 'Fahad Saleem', '03181234567', 'M', 'Patient', '1984-02-14', 'fahad.saleem@gmail.com', 'fs123'),
        (20, 'Mariam Zafar', '03191234567', 'F', 'Patient', '1997-03-15', 'mariam.zafar@gmail.com', 'mz123')
    ]

    cursor.execute("SET IDENTITY_INSERT UserAccount ON")
    
    user_insert_query = """
        INSERT INTO UserAccount (UserID, Name, ContactNumber, Gender, Role, DateOfBirth, Email, Password)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.executemany(user_insert_query, user_data)
    
    # Turn it back OFF so the App can auto-generate IDs later
    cursor.execute("SET IDENTITY_INSERT UserAccount OFF")
    connection.commit()
    print("Inserted UserAccount records.")

    medical_data = [
        (1, 6, 'Peanuts', 'Asthma', '2020-01-01', 'Uses inhaler daily'),
        (2, 7, 'None', 'Diabetes', '2019-05-10', 'Type 2, on medication'),
        (3, 8, 'Penicillin', 'Hypertension', '2021-03-15', 'Monitored monthly'),
        (4, 9, 'Dust', 'Allergy', '2022-06-20', 'Seasonal symptoms'),
        (5, 10, 'None', 'Migraine', '2020-09-12', 'Occasional headaches'),
        (6, 11, 'Shellfish', 'Thyroid', '2018-11-05', 'Hypothyroidism'),
        (7, 12, 'None', 'Arthritis', '2021-07-07', 'Knee pain'),
        (8, 13, 'None', 'Gastritis', '2022-01-01', 'Diet controlled'),
        (9, 14, 'Pollen', 'Sinusitis', '2020-04-04', 'Recurring congestion'),
        (10, 15, 'None', 'Back Pain', '2019-08-08', 'Physiotherapy ongoing'),
        (11, 16, 'None', 'PCOS', '2021-10-10', 'Hormonal treatment'),
        (12, 17, 'None', 'High Cholesterol', '2022-12-12', 'Statins prescribed'),
        (13, 18, 'None', 'Anxiety', '2020-02-02', 'Counseling sessions'),
        (14, 19, 'None', 'Ulcer', '2021-03-03', 'Medication taken'),
        (15, 20, 'None', 'Vitamin D Deficiency', '2022-05-05', 'Supplements advised'),
        (16, 6, 'None', 'Flu', '2023-01-01', 'Recovered'),
        (17, 7, 'None', 'COVID-19', '2021-06-06', 'Vaccinated'),
        (18, 8, 'None', 'Anemia', '2022-07-07', 'Iron supplements'),
        (19, 9, 'None', 'Depression', '2020-08-08', 'Therapy ongoing'),
        (20, 10, 'None', 'Kidney Stone', '2023-09-09', 'Surgery done')
    ]

    medical_insert_query = """
        INSERT INTO Medical_History (MedicalHistoryID, PatientID, Allergies, Disease, DiagnosisDate, Details)
        VALUES (?, ?, ?, ?, ?, ?)
    """

    cursor.executemany(medical_insert_query, medical_data)
    connection.commit()
    print("Inserted Medical_History records.")

    LabTest_data = [
        (1, 'CBC', 6, '2025-10-01', 'Complete blood count for fatigue', '2025-10-02', 'Completed', 500),
        (2, 'Lipid Profile', 7, '2025-10-03', 'Cholesterol screening', '2025-10-04', 'Completed', 700),
        (3, 'Blood Sugar', 8, '2025-10-05', 'Routine diabetes check', '2025-10-06', 'Completed', 400),
        (4, 'Thyroid Panel', 9, '2025-10-07', 'Thyroid hormone levels', '2025-10-08', 'Completed', 600),
        (5, 'Urine Test', 10, '2025-10-09', 'Kidney function screening', '2025-10-10', 'Completed', 300),
        (6, 'ECG', 11, '2025-10-11', 'Heart rhythm analysis', '2025-10-12', 'Completed', 900),
        (7, 'MRI Brain', 12, '2025-10-13', 'Headache investigation', None, 'Pending', 5000),
        (8, 'X-Ray Chest', 13, '2025-10-14', 'Cough and chest pain', '2025-10-15', 'Completed', 800),
        (9, 'CT Abdomen', 14, '2025-10-16', 'Abdominal pain', None, 'Pending', 4500),
        (10, 'Vitamin D', 15, '2025-10-17', 'Deficiency check', '2025-10-18', 'Completed', 550),
        (11, 'CBC', 16, '2025-10-19', 'Routine check', '2025-10-20', 'Completed', 500),
        (12, 'Blood Sugar', 17, '2025-10-21', 'Routine check', '2025-10-22', 'Completed', 400),
        (13, 'Thyroid Panel', 18, '2025-10-23', 'Routine check', '2025-10-24', 'Completed', 600),
        (14, 'Liver Function', 19, '2025-10-25', 'Routine check', None, 'Pending', 750),
        (15, 'Kidney Function', 20, '2025-10-26', 'Routine check', None, 'Pending', 800),
        (16, 'ECG', 6, '2025-10-27', 'Follow-up for arrhythmia', '2025-10-28', 'Completed', 900),
        (17, 'HbA1c', 7, '2025-10-29', 'Diabetes control check', '2025-10-30', 'Completed', 650),
        (18, 'Stool Test', 8, '2025-10-31', 'Digestive issues', None, 'Pending', 350),
        (19, 'Allergy Panel', 9, '2025-11-01', 'Seasonal allergies', '2025-11-02', 'Completed', 1200),
        (20, 'Pap Smear', 10, '2025-11-03', 'Routine gynecological exam', None, 'Pending', 950)
    ]
    LabTest_insert_query = """
        INSERT INTO LabTest (TestID, TestName, PatientID, TestDate, TestDesc, ResultDate, TestStatus, TestPrice)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

    cursor.executemany(LabTest_insert_query, LabTest_data)
    connection.commit()
    print("Inserted LabTest records.")

    doctor_data = [
        (100, 'Dr. Bilal Amir', 'bilal.amir@hospital.com', 'ba123', 'Active', '03001234501', 1),
        (200, 'Dr. Imran Malik', 'imran.malik@hospital.com', 'passImran2', 'Active', '03001234502', 1),
        (300, 'Dr. Sara Ahmed', 'sara.ahmed@hospital.com', 'passSara3', 'Active', '03001234503', 1),
        (400, 'Dr. Bilal Raza', 'bilal.raza@hospital.com', 'passBilal4', 'Active', '03001234504', 1),
        (500, 'Dr. Nadia Farooq', 'nadia.farooq@hospital.com', 'passNadia5', 'Active', '03001234505', 1),
        (600, 'Dr. Kamran Shah', 'kamran.shah@hospital.com', 'passKamran6', 'Active', '03001234506', 1),
        (700, 'Dr. Hina Qureshi', 'hina.qureshi@hospital.com', 'passHina7', 'Active', '03001234507', 1),
        (800, 'Dr. Faisal Mehmood', 'faisal.mehmood@hospital.com', 'passFaisal8', 'Active', '03001234508', 1),
        (900, 'Dr. Rabia Aslam', 'rabia.aslam@hospital.com', 'passRabia9', 'Active', '03001234509', 1),
        (110, 'Dr. Shazia Tariq', 'shazia.tariq@hospital.com', 'passShazia11', 'Active', '03001234510', 1),
        (120, 'Dr. Adnan Javed', 'adnan.javed@hospital.com', 'passAdnan12', 'Active', '03001234511', 1),
        (130, 'Dr. Mehmood Ali', 'mehmood.ali@hospital.com', 'passMehmood13', 'Active', '03001234512', 1),
        (140, 'Dr. Farah Siddiqui', 'farah.siddiqui@hospital.com', 'passFarah14', 'Active', '03001234513', 1),
        (150, 'Dr. Salman Rafiq', 'salman.rafiq@hospital.com', 'passSalman15', 'Active', '03001234514', 1),
        (160, 'Dr. Naila Hussain', 'naila.hussain@hospital.com', 'passNaila16', 'Active', '03001234515', 1),
        (170, 'Dr. Usman Tariq', 'usman.tariq@hospital.com', 'passUsman17', 'Active', '03001234516', 1),
        (180, 'Dr. Mahnoor Zia', 'mahnoor.zia@hospital.com', 'passMahnoor18', 'Active', '03001234517', 1),
        (190, 'Dr. Danish Khan', 'danish.khan@hospital.com', 'passDanish19', 'Active', '03001234518', 1),
        (220, 'Dr. Saba Rehman', 'saba.rehman@hospital.com', 'passSaba20', 'Active', '03001234519', 1),
        (210, 'Dr. Zafar Iqbal', 'zafar.iqbal@hospital.com', 'passZafar10', 'Active', '03001234520', 1),
    ]

    # Updated INSERT query to include the 2 new columns
    doctor_insert_query = """
        INSERT INTO Doctor (DoctorID, DoctorName, DoctorEmail, DoctorPassword, DoctorStatus, Contact, approved)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    cursor.executemany(doctor_insert_query, doctor_data)
    connection.commit()
    print("Inserted Doctor records.")

    specialisation_data = [
    (1, 'Cardiology', 100),
    (2, 'Internal Medicine', 100),
    (3, 'Pulmonology', 200),
    (4, 'Critical Care', 200),
    (5, 'Neurology', 300),
    (6, 'Sleep Medicine', 300),
    (7, 'Orthopedics', 400),
    (8, 'Sports Medicine', 400),
    (9, 'Gynecology', 500),
    (10, 'Obstetrics', 500),
    (11, 'Dermatology', 600),
    (12, 'Cosmetic Dermatology', 600),
    (13, 'Gastroenterology', 700),
    (14, 'Hepatology', 700),
    (15, 'Endocrinology', 800),
    (16, 'Diabetology', 800),
    (17, 'Pediatrics', 900),
    (18, 'Neonatology', 900),
    (19, 'Psychiatry', 110),
    (20, 'Addiction Medicine', 110),
    (21, 'Urology', 120),
    (22, 'Andrology', 120),
    (23, 'Nephrology', 130),
    (24, 'Transplant Medicine', 130),
    (25, 'Oncology', 140),
    (26, 'Radiation Oncology', 140),
    (27, 'Rheumatology', 150),
    (28, 'Immunology', 150),
    (29, 'Hematology', 160),
    (30, 'Blood Disorders', 160),
    (31, 'Radiology', 170),
    (32, 'Interventional Radiology', 170),
    (33, 'ENT', 180),
    (34, 'Audiology', 180),
    (35, 'Infectious Diseases', 190),
    (36, 'Tropical Medicine', 190),
    (37, 'General Surgery', 220),
    (38, 'Laparoscopic Surgery', 220),
    (39, 'Family Medicine', 210),
    (40, 'Preventive Medicine', 210)
]

    specialisation_insert_query = """
        INSERT INTO Specialisation (SpecialisationID, FieldName, DoctorID)
        VALUES (?, ?, ?)
    """

    cursor.executemany(specialisation_insert_query, specialisation_data)
    connection.commit()
    print("Inserted Specialisation records.")

    availability_data = [
        (1, 100, '2025-10-28 09:00:00'),
        (2, 100, '2025-10-29 14:00:00'),
        (3, 200, '2025-10-28 10:00:00'),
        (4, 200, '2025-10-30 15:00:00'),
        (5, 300, '2025-10-28 11:00:00'),
        (6, 300, '2025-10-31 16:00:00'),
        (7, 400, '2025-10-28 12:00:00'),
        (8, 400, '2025-10-29 17:00:00'),
        (9, 500, '2025-10-28 13:00:00'),
        (10, 500, '2025-10-30 18:00:00'),
        (11, 600, '2025-10-29 09:30:00'),
        (12, 600, '2025-10-31 14:30:00'),
        (13, 700, '2025-10-29 10:30:00'),
        (14, 700, '2025-10-30 15:30:00'),
        (15, 800, '2025-10-29 11:30:00'),
        (16, 800, '2025-10-31 16:30:00'),
        (17, 900, '2025-10-29 12:30:00'),
        (18, 900, '2025-10-30 17:30:00'),
        (19, 110, '2025-10-29 13:30:00'),
        (20, 110, '2025-10-31 18:30:00'),
        (21, 120, '2025-10-30 09:00:00'),
        (22, 120, '2025-11-01 14:00:00'),
        (23, 130, '2025-10-30 10:00:00'),
        (24, 130, '2025-11-01 15:00:00'),
        (25, 140, '2025-10-30 11:00:00'),
        (26, 140, '2025-11-01 16:00:00'),
        (27, 150, '2025-10-30 12:00:00'),
        (28, 150, '2025-11-01 17:00:00'),
        (29, 160, '2025-10-30 13:00:00'),
        (30, 160, '2025-11-01 18:00:00'),
        (31, 170, '2025-10-31 09:00:00'),
        (32, 170, '2025-11-02 14:00:00'),
        (33, 180, '2025-10-31 10:00:00'),
        (34, 180, '2025-11-02 15:00:00'),
        (35, 190, '2025-10-31 11:00:00'),
        (36, 190, '2025-11-02 16:00:00'),
        (37, 220, '2025-10-31 12:00:00'),
        (38, 220, '2025-11-02 17:00:00'),
        (39, 210, '2025-10-31 13:00:00'),
        (40, 210, '2025-11-02 18:00:00')
    ]


    availability_insert_query = """
        INSERT INTO Doctor_Availability (AvailabilityID, DoctorID, Available)
        VALUES (?, ?, ?)
    """

    cursor.executemany(availability_insert_query, availability_data)
    connection.commit()
    print("Inserted Doctor_Availability records.")

    Admission_Details_data = [
        (1, 6, '101A', '2025-10-01', '2025-10-05', 5000),
        (2, 7, '102B', '2025-10-02', '2025-10-06', 5200),
        (3, 8, '103C', '2025-10-03', '2025-10-07', 4800),
        (4, 9, '104D', '2025-10-04', '2025-10-08', 5100),
        (5, 10, '105E', '2025-10-05', '2025-10-09', 5300),
        (6, 11, '106F', '2025-10-06', '2025-10-10', 4900),
        (7, 12, '107G', '2025-10-07', '2025-10-11', 5000),
        (8, 13, '108H', '2025-10-08', '2025-10-12', 5200),
        (9, 14, '109I', '2025-10-09', '2025-10-13', 4800),
        (10, 15, '110J', '2025-10-10', '2025-10-14', 5100),
        (11, 16, '111K', '2025-10-11', '2025-10-15', 5300),
        (12, 17, '112L', '2025-10-12', '2025-10-16', 4900),
        (13, 18, '113M', '2025-10-13', '2025-10-17', 5000),
        (14, 19, '114N', '2025-10-14', '2025-10-18', 5200),
        (15, 20, '115O', '2025-10-15', '2025-10-19', 4800),
        (16, 6, '116P', '2025-10-20', None, 5100),
        (17, 7, '117Q', '2025-10-21', None, 5300),
        (18, 8, '118R', '2025-10-22', None, 4900),
        (19, 9, '119S', '2025-10-23', None, 5000),
        (20, 10, '120T', '2025-10-24', None, 5200)
    ]

    Admission_Details_insert_query = """
        INSERT INTO Admission_Details (AdmissionID, PatientID, RoomNo, AdmissionDate, DischargeDate, RoomPrice)
        VALUES (?, ?, ?, ?, ?, ?)
    """

    cursor.executemany(Admission_Details_insert_query, Admission_Details_data)
    connection.commit()
    print("Inserted Admission_Details records.")

    apointment_data = [
    (1, 6, 100, '2025-10-28 09:00', 'Completed', 1500),
    (2, 7, 100, '2025-10-28 10:00', 'Completed', 1600),
    (3, 8, 200, '2025-10-28 11:00', 'Completed', 1700),
    (4, 9, 200, '2025-10-28 12:00', 'Completed', 1800),
    (5, 10, 300, '2025-10-28 13:00', 'Completed', 1900),
    (6, 11, 300, '2025-10-29 09:30', 'Completed', 1500),
    (7, 12, 400, '2025-10-29 10:30', 'Completed', 1600),
    (8, 13, 400, '2025-10-29 11:30', 'Completed', 1700),
    (9, 14, 500, '2025-10-29 12:30', 'Completed', 1800),
    (10, 15, 500, '2025-10-29 13:30', 'Completed', 1900),
    (11, 16, 600, '2025-10-30 09:00', 'Scheduled', 1500),
    (12, 17, 600, '2025-10-30 10:00', 'Scheduled', 1600),
    (13, 18, 700, '2025-10-30 11:00', 'Scheduled', 1700),
    (14, 19, 700, '2025-10-30 12:00', 'Scheduled', 1800),
    (15, 20, 800, '2025-10-30 13:00', 'Scheduled', 1900),
    (16, 6, 800, '2025-10-31 09:00', 'Scheduled', 1500),
    (17, 7, 900, '2025-10-31 10:00', 'Scheduled', 1600),
    (18, 8, 900, '2025-10-31 11:00', 'Scheduled', 1700),
    (19, 9, 110, '2025-10-31 12:00', 'Scheduled', 1800),
    (20, 10, 110, '2025-10-31 13:00', 'Scheduled', 1900)
]
    apointment_insert_query = """
        INSERT INTO Doctor_Appointment (AppointmentID, PatientID, DoctorID, AppointmentDateTime, AppointmentStatus, AppointmentPrice)
        VALUES (?, ?, ?, ?, ?, ?)
    """

    cursor.executemany(apointment_insert_query, apointment_data)
    connection.commit()
    print("Inserted Doctor_Availability records.")

    Pharmacy_Item_data = [
        (1, 'Paracetamol 500mg', 'Pain Relief', 200, 5.00),
        (2, 'Ibuprofen 200mg', 'Pain Relief', 150, 6.50),
        (3, 'Amoxicillin 250mg', 'Antibiotic', 100, 12.00),
        (4, 'Azithromycin 500mg', 'Antibiotic', 80, 18.00),
        (5, 'Omeprazole 20mg', 'Gastrointestinal', 120, 10.00),
        (6, 'Loratadine 10mg', 'Antihistamine', 90, 8.00),
        (7, 'Metformin 500mg', 'Diabetes', 110, 7.50),
        (8, 'Atorvastatin 10mg', 'Cholesterol', 130, 9.00),
        (9, 'Salbutamol Inhaler', 'Respiratory', 60, 25.00),
        (10, 'Insulin Pen', 'Diabetes', 40, 55.00),
        (11, 'Hydrocortisone Cream', 'Dermatology', 70, 15.00),
        (12, 'Vitamin D3 1000 IU', 'Supplements', 200, 4.50),
        (13, 'Iron Tablets', 'Supplements', 180, 6.00),
        (14, 'ORS Sachets', 'Hydration', 250, 3.00),
        (15, 'Bandages (Pack)', 'First Aid', 300, 2.50),
        (16, 'Digital Thermometer', 'Equipment', 50, 30.00),
        (17, 'Surgical Gloves (Box)', 'Supplies', 75, 20.00),
        (18, 'Face Masks (Pack)', 'Supplies', 100, 10.00),
        (19, 'Antiseptic Solution', 'First Aid', 90, 12.00),
        (20, 'Cough Syrup 100ml', 'Respiratory', 85, 14.00)
    ]

    Pharmacy_Item_insert_query = """
        INSERT INTO Pharmacy_Item (ItemID, ItemName, Category, QuantityInStock, PricePerItem)
        VALUES (?, ?, ?, ?, ?)
    """

    cursor.executemany(Pharmacy_Item_insert_query, Pharmacy_Item_data)
    connection.commit()
    print("Inserted Pharmacy_Item records.")

    Pharmacy_Order_data = [
        (1, 1, 10, 5.00),     
        (2, 2, 5, 6.50),      
        (3, 3, 3, 12.00),     
        (4, 4, 2, 18.00),     
        (5, 5, 4, 10.00),     
        (6, 6, 6, 8.00),      
        (7, 7, 5, 7.50),      
        (8, 8, 3, 9.00),      
        (9, 9, 2, 25.00),     
        (10, 10, 1, 55.00),   
        (11, 11, 2, 15.00),   
        (12, 12, 10, 4.50),   
        (13, 13, 8, 6.00),    
        (14, 14, 12, 3.00),   
        (15, 15, 20, 2.50),   
        (16, 16, 1, 30.00),   
        (17, 17, 2, 20.00),   
        (18, 18, 5, 10.00),   
        (19, 19, 3, 12.00),   
        (20, 20, 4, 14.00)
    ]

    Pharmacy_Order_insert_query = """
        INSERT INTO Pharmacy_Order (OrderID, ItemID, ItemQuantity, PricePerItem)
        VALUES (?, ?, ?, ?)
    """

    cursor.executemany(Pharmacy_Order_insert_query, Pharmacy_Order_data)
    connection.commit()
    print("Inserted Pharmacy_Order records.")

    Bill_data = [
        (1, 1, 6, '2025-10-28', 50.00, 'Paid'),
        (2, 2, 7, '2025-10-28', 32.50, 'Paid'),
        (3, 3, 8, '2025-10-28', 36.00, 'Paid'),
        (4, 4, 9, '2025-10-28', 36.00, 'Paid'),
        (5, 5, 10, '2025-10-28', 40.00, 'Paid'),
        (6, 6, 11, '2025-10-28', 48.00, 'Paid'),
        (7, 7, 12, '2025-10-28', 37.50, 'Paid'),
        (8, 8, 13, '2025-10-28', 27.00, 'Paid'),
        (9, 9, 14, '2025-10-28', 50.00, 'Paid'),
        (10, 10, 15, '2025-10-28', 55.00, 'Paid'),
        (11, 11, 16, '2025-10-29', 30.00, 'Unpaid'),
        (12, 12, 17, '2025-10-29', 45.00, 'Unpaid'),
        (13, 13, 18, '2025-10-29', 48.00, 'Unpaid'),
        (14, 14, 19, '2025-10-29', 36.00, 'Unpaid'),
        (15, 15, 20, '2025-10-29', 50.00, 'Unpaid'),
        (16, 16, 6, '2025-10-30', 30.00, 'Unpaid'),
        (17, 17, 7, '2025-10-30', 40.00, 'Unpaid'),
        (18, 18, 8, '2025-10-30', 50.00, 'Unpaid'),
        (19, 19, 9, '2025-10-30', 36.00, 'Unpaid'),
        (20, 20, 10, '2025-10-30', 56.00, 'Unpaid')

    ]

    Bill_insert_query = """
        INSERT INTO Bill (BillID, OrderID, PatientID, BillDate, TotalPrice, BillStatus)
        VALUES (?, ?, ?, ?, ?, ?)
    """

    cursor.executemany(Bill_insert_query, Bill_data)
    connection.commit()
    print("Inserted Bill records.")

    print("Committing all data...")
    connection.commit()
    cursor.close()
    connection.close()
    print("Database setup complete.")


if __name__ == "__main__":
    # This will wipe and rebuild your database.
    # Run this file once to set everything up.
    setup_database()