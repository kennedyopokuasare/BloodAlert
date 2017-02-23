PRAGMA foreign_keys=OFF;

BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS Blood_Banks(
  bloodBankId INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE ,
  address TEXT,
  city TEXT NOT NULL,
  telephone TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  latitude REAL,
  longitude REAL,
  threshold INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS Blood_Donors (
  donorId  INTEGER PRIMARY KEY AUTOINCREMENT,
  firstname TEXT NOT NULL,
  familyName TEXT NOT NULL,
  birthDate TEXT,
  gender  TEXT,
  bloodTypeId INTEGER ,
  telephone TEXT NOT NULL,
  city TEXT,
  address TEXT,
  email TEXT NOT NULL UNIQUE,
  FOREIGN KEY(bloodTypeId) REFERENCES Blood_Types(bloodTypeId) ON DELETE SET NULL
  );

CREATE TABLE IF NOT EXISTS History(
    historyId INTEGER PRIMARY KEY AUTOINCREMENT,
    donorId  INTEGER NOT NULL,
    bloodTypeId INTEGER ,
    bloodBankId INTEGER ,
    amount INTEGER NOT NULL,
    timeStamp REAL NOT NULL, 
    FOREIGN KEY(donorId) REFERENCES Blood_Donors(donorId) ON DELETE CASCADE,
    FOREIGN KEY(bloodTypeId) REFERENCES Blood_Types(bloodTypeId) ON DELETE SET NULL,
    FOREIGN KEY(bloodBankId) REFERENCES Blood_Banks(bloodBankId) ON DELETE SET NULL
);
    
CREATE TABLE IF NOT EXISTS Blood_Types(
  bloodTypeId INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Current_Blood_State(
  bloodStateId INTEGER PRIMARY KEY AUTOINCREMENT,
  bloodBankId INTEGER,
  bloodTypeId INTEGER,
  amount INTEGER ,
  timeStamp REAL,
  FOREIGN KEY(bloodBankId) REFERENCES Blood_Banks(bloodBankId) ON DELETE SET NULL,
  FOREIGN KEY(bloodTypeId) REFERENCES Blood_Types(bloodTypeId) ON DELETE SET NULL
);

COMMIT;

PRAGMA foreign_keys=ON;