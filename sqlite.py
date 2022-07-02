import sqlite3
drivers = [(1,'ADC','918078706253', 40.712776, -74.005974,""),
            (2,'ABC','918590939103', 41.712776, -74.005974,""),
            (3,'AFC','919847809874', 41.712776, -70.005974,""),
            (4,'AKC','917034487669', 31.712776, -70.005974,""),
            (5,'LMP','918111948462', 21.712776, -70.005974,""),
            (6,'PBP','918078205315', 31.712776, 70.005974,""),
            (7,'KMK','918589947708', 21.712776, 70.005974,"")]
conn  = sqlite3.connect('accident.db')
cur = conn.cursor()
try:
    
    cur.execute('''CREATE TABLE DRIVER
            (ID INTEGER PRIMARY KEY,
            NAME CHAR(30) NOT NULL,
            PHONE CHAR(12) NOT NULL ,
            MESSAGE_ID INTEGER,
            LATITUDE REAL ,
            LONGITUDE REAL,
            ACCIDENT CHAR(30))''')
    
    cur.execute('''CREATE TABLE LOG
            (MESSAGE CHAR(100) NOT NULL UNIQUE,
            PHONE_RELATIVE1 CHAR(12) NOT NULL,
            PHONE_RELATIVE2 CHAR(12) NOT NULL,
            PHONE_RELATIVE3 CHAR(12) NOT NULL,
            PHONE_DRIVER1 CHAR(12) NOT NULL,
            PHONE_DRIVER2 CHAR(12) NOT NULL,
            PHONE_DRIVER3 CHAR(12) NOT NULL,
            MSG_IDR1 CHAR(10) NOT NULL,
            MSG_IDR2 CHAR(10) NOT NULL,
            MSR_IDR3 CHAR(10) NOT NULL,
            MSG_IDD1 CHAR(10) NOT NULL,
            MSG_IDD2 CHAR(10) NOT NULL,
            MSR_IDD3 CHAR(10) NOT NULL,
            STATUS INTEGER NOT NULL,
            ACCEPTED_DRIVER CHAR(30) NOT NULL,
            ACCEPTED_DRIVER_PH INTEGER,
            TIME TIMESTAMP,
            NAME CHAR(30) NOT NULL)''')
        
except:
    #cur.rollback()
    print("table exist")
cur.executemany('''INSERT INTO DRIVER(ID,NAME, PHONE,LATITUDE, LONGITUDE, ACCIDENT) VALUES(?,?,?,?,?,?)''', drivers)
conn.commit()
conn.close()