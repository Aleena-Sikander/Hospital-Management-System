-- UserAccount table
-- CREATE TABLE UserAccount (
--     UserID INTEGER NOT NULL,
--     Name VARCHAR(100) NOT NULL,
--     ContactNumber VARCHAR(15),
--     Gender CHAR(1),
--     Role VARCHAR(20),
--     DateOfBirth DATE,
--     Email VARCHAR(100) UNIQUE NOT NULL,
--     Password VARCHAR(100) NOT NULL,
--     CONSTRAINT pk_user PRIMARY KEY (UserID)
-- );

-- -- Medical_History table
-- CREATE TABLE Medical_History (
--     MedicalHistoryID INTEGER PRIMARY KEY,
--     PatientID INTEGER NOT NULL,
--     Allergies TEXT,
--     Disease TEXT,
--     DiagnosisDate DATE,
--     Details TEXT,
--     CONSTRAINT fk_medhist_user FOREIGN KEY (PatientID) REFERENCES UserAccount(UserID)
-- );

-- -- LabTest table
-- CREATE TABLE LabTest (
--     TestID INTEGER PRIMARY KEY,
--     TestName VARCHAR(50) NOT NULL,
--     PatientID INTEGER NOT NULL,
--     TestDate DATE NOT NULL,
--     TestDesc TEXT,
--     ResultDate DATE,
--     TestStatus VARCHAR(20),
--     TestPrice FLOAT NOT NULL,
--     CONSTRAINT fk_labtest_user FOREIGN KEY (PatientID) REFERENCES UserAccount(UserID)
-- );

-- Doctor table
-- CREATE TABLE Doctor (
--     DoctorID INTEGER PRIMARY KEY,
--     DoctorName VARCHAR(100) NOT NULL,
--     DoctorEmail VARCHAR(100) UNIQUE NOT NULL,
--     DoctorPassword VARCHAR(100) NOT NULL,
--     DoctorStatus VARCHAR(20)
-- );

-- -- Specialisation table
-- CREATE TABLE Specialisation (
--     SpecialisationID INTEGER PRIMARY KEY,
--     FieldName VARCHAR(50) NOT NULL,
--     DoctorID INTEGER NOT NULL,
--     CONSTRAINT fk_specialisation_doctor FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID)
-- );

-- Doctor_Availability table
-- CREATE TABLE Doctor_Availability (
--     AvailabilityID INTEGER PRIMARY KEY,
--     DoctorID INTEGER NOT NULL,
--     Available DATETIME NOT NULL,
--     CONSTRAINT fk_availability_doctor FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID)
-- );

-- Admission_Details table
-- CREATE TABLE Admission_Details (
--     AdmissionID INTEGER PRIMARY KEY,
--     PatientID INTEGER NOT NULL,
--     RoomNo VARCHAR(5) NOT NULL,
--     AdmissionDate DATE NOT NULL,
--     DischargeDate DATE,
--     RoomPrice FLOAT NOT NULL,
--     CONSTRAINT fk_admission_user FOREIGN KEY (PatientID) REFERENCES UserAccount(UserID)
-- );

-- Doctor_Appointment table
-- CREATE TABLE Doctor_Appointment (
--     AppointmentID INTEGER PRIMARY KEY,
--     PatientID INTEGER NOT NULL,
--     DoctorID INTEGER NOT NULL,
--     AppointmentDateTime DATETIME NOT NULL,
--     AppointmentStatus VARCHAR(20),
--     AppointmentPrice FLOAT NOT NULL,
--     CONSTRAINT fk_appointment_user FOREIGN KEY (PatientID) REFERENCES UserAccount(UserID),
--     CONSTRAINT fk_appointment_doctor FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID)
-- );

-- Pharmacy_Item table
-- CREATE TABLE Pharmacy_Item (
--     ItemID INTEGER PRIMARY KEY,
--     ItemName VARCHAR(50) NOT NULL,
--     Category VARCHAR(30),
--     QuantityInStock INTEGER DEFAULT 0,
--     PricePerItem FLOAT NOT NULL
-- );

-- Pharmacy_Order_Details table
-- CREATE TABLE Pharmacy_Order (
--     OrderID INTEGER NOT NULL PRIMARY KEY,
--     ItemID INTEGER NOT NULL,
--     ItemQuantity INTEGER NOT NULL,
--     PricePerItem FLOAT NOT NULL,
--     TotalPrice AS (PricePerItem * ItemQuantity),
--     CONSTRAINT fk_order_item FOREIGN KEY (ItemID) REFERENCES Pharmacy_Item(ItemID)
-- );

-- Bill table
CREATE TABLE Bill (
    BillID INTEGER PRIMARY KEY,
    OrderID INTEGER NOT NULL,
    PatientID INTEGER NOT NULL,
    BillDate DATE NOT NULL,
    TotalPrice FLOAT NOT NULL,
    BillStatus VARCHAR(20),
    CONSTRAINT fk_bill_user FOREIGN KEY (PatientID) REFERENCES UserAccount(UserID),
    CONSTRAINT fk_bill_order FOREIGN KEY (OrderID) REFERENCES Pharmacy_Order(OrderID)
);