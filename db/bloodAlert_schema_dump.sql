PRAGMA foreign_keys=OFF;

BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS Blood_Banks(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
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
  id  INTEGER PRIMARY KEY AUTOINCREMENT,
  firstname TEXT NOT NULL,
  familyName TEXT NOT NULL,
  birthDay TEXT,
  gender  TEXT,
  bloodType_Id INTEGER,
  telephone TEXT,
  city TEXT,
  address TEXT,
  email TEXT,
  FOREIGN KEY(bloodType_Id) REFERENCES BloodType(id) ON DELETE SET NULL
  );

CREATE TABLE IF NOT EXISTS History(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    donor_id  INTEGER,
    bloodType_Id INTEGER,
    bbank_Id INTEGER,
    amount INTEGER,
    timeStamp REAL, 
    FOREIGN KEY(donor_id) REFERENCES Blood_Donors(id) ON DELETE CASCADE,
    FOREIGN KEY(bloodType_Id) REFERENCES BloodType(id) ON DELETE SET NULL,
    FOREIGN KEY(bbank_Id) REFERENCES Blood_Banks(id) ON DELETE SET NULL
);
    
CREATE TABLE IF NOT EXISTS Blood_Type(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Current_Blood_State(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  bbank_Id INTEGER,
  bloodType_Id INTEGER,
  amount INTEGER ,
  timeStamp REAL,
  FOREIGN KEY(bbank_Id) REFERENCES Blood_Banks(id) ON DELETE SET NULL,
  FOREIGN KEY(bloodType_Id) REFERENCES BloodType(id) ON DELETE SET NULL
);

COMMIT;

PRAGMA foreign_keys=ON;