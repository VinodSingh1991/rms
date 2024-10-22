BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Campaign" (
	"CampId"	INTEGER,
	"CampaignID"	INTEGER,
	"CampaignName"	TEXT NOT NULL,
	"StartDate"	DATE,
	"EndDate"	DATE,
	"Budget"	REAL,
	"CreatedOn"	DATETIME DEFAULT CURRENT_TIMESTAMP,
	"CreatedBy"	TEXT,
	PRIMARY KEY("CampId" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Leads" (
	"LeadID"	INTEGER,
	"CampaignID"	INTEGER,
	"FirstName"	TEXT,
	"LastName"	TEXT,
	"MiddleName"	TEXT,
	"Phone"	TEXT,
	"Email"	TEXT,
	"Address"	TEXT,
	"City"	TEXT,
	"State"	TEXT,
	"PinCode"	TEXT,
	"Country"	TEXT,
	"ProductId"	INTEGER,
	"AccountId"	INTEGER,
	"RatingId"	INTEGER,
	"CreatedOn"	DATETIME DEFAULT CURRENT_TIMESTAMP,
	"CreatedBy"	TEXT,
	"ActivityId"	INTEGER,
	"Amount"	REAL,
	PRIMARY KEY("LeadID")
);
CREATE TABLE IF NOT EXISTS "Rating" (
	"RatingId"	INTEGER,
	"RatingValue"	INTEGER NOT NULL CHECK("RatingValue" BETWEEN 1 AND 5),
	"Description"	TEXT,
	PRIMARY KEY("RatingId" AUTOINCREMENT)
);
INSERT INTO "Campaign" VALUES (1,101,'Summer Sale','2023-06-01','2023-08-31',5000.0,'2023-05-15 09:00:00','marketing');
INSERT INTO "Campaign" VALUES (2,102,'Winter Fest','2023-11-01','2023-12-31',10000.0,'2023-10-15 10:00:00','marketing');
INSERT INTO "Campaign" VALUES (3,103,'Black Friday Special','2023-11-24','2023-11-25',15000.0,'2023-11-01 09:30:00','sales');
INSERT INTO "Campaign" VALUES (4,104,'New Year Bonanza','2024-01-01','2024-01-07',7000.0,'2023-12-10 08:45:00','admin');
INSERT INTO "Campaign" VALUES (5,105,'Spring Clearance','2024-03-01','2024-03-31',6000.0,'2024-02-01 11:00:00','sales');
INSERT INTO "Campaign" VALUES (6,106,'Holiday Discount','2023-12-20','2023-12-30',8000.0,'2023-11-25 12:00:00','marketing');
INSERT INTO "Campaign" VALUES (7,107,'Flash Sale','2023-10-20','2023-10-21',2000.0,'2023-10-15 14:30:00','admin');
INSERT INTO "Campaign" VALUES (8,108,'Cyber Monday Deals','2023-11-27','2023-11-27',18000.0,'2023-11-10 09:15:00','sales');
INSERT INTO "Campaign" VALUES (9,109,'Valentine''s Special','2024-02-14','2024-02-14',3000.0,'2024-01-15 16:00:00','admin');
INSERT INTO "Campaign" VALUES (10,110,'Back to School','2023-09-01','2023-09-15',4000.0,'2023-08-01 10:30:00','sales');
INSERT INTO "Leads" VALUES (1,101,'John','Doe','A','1234567890','john.doe@example.com','123 Main St','New York','NY','10001','USA',201,301,5,'2023-10-01 10:30:00','admin',1001,150.75);
INSERT INTO "Leads" VALUES (2,102,'Jane','Smith','B','2345678901','jane.smith@example.com','456 Elm St','Los Angeles','CA','90001','USA',202,302,4,'2023-10-02 11:15:00','admin',1002,200.5);
INSERT INTO "Leads" VALUES (3,103,'Michael','Johnson','C','3456789012','michael.j@example.com','789 Oak St','Chicago','IL','60601','USA',203,303,3,'2023-10-03 09:45:00','admin',1003,300.25);
INSERT INTO "Leads" VALUES (4,104,'Emily','Davis','D','4567890123','emily.davis@example.com','101 Pine St','Houston','TX','77001','USA',204,304,2,'2023-10-04 12:00:00','admin',1004,250.1);
INSERT INTO "Leads" VALUES (5,105,'David','Miller','E','5678901234','david.miller@example.com','202 Maple St','Phoenix','AZ','85001','USA',205,305,5,'2023-10-05 14:30:00','admin',1005,175.0);
INSERT INTO "Leads" VALUES (6,106,'Sarah','Wilson','F','6789012345','sarah.wilson@example.com','303 Cedar St','Philadelphia','PA','19101','USA',206,306,4,'2023-10-06 08:15:00','admin',1006,225.6);
INSERT INTO "Leads" VALUES (7,107,'Chris','Brown','G','7890123456','chris.brown@example.com','404 Birch St','San Antonio','TX','78201','USA',207,307,3,'2023-10-07 13:45:00','admin',1007,190.3);
INSERT INTO "Leads" VALUES (8,108,'Jessica','Garcia','H','8901234567','jessica.garcia@example.com','505 Spruce St','San Diego','CA','92101','USA',208,308,2,'2023-10-08 10:20:00','admin',1008,275.4);
INSERT INTO "Leads" VALUES (9,109,'Daniel','Martinez','I','9012345678','daniel.martinez@example.com','606 Willow St','Dallas','TX','75201','USA',209,309,5,'2023-10-09 16:00:00','admin',1009,310.5);
INSERT INTO "Leads" VALUES (10,110,'Ashley','Anderson','J','0123456789','ashley.anderson@example.com','707 Ash St','San Jose','CA','95101','USA',210,310,4,'2023-10-10 09:30:00','admin',1010,230.75);
INSERT INTO "Rating" VALUES (1,1,'Poor - Very dissatisfied with the service.');
INSERT INTO "Rating" VALUES (2,2,'Fair - Somewhat dissatisfied, but some aspects were acceptable.');
INSERT INTO "Rating" VALUES (3,3,'Good - Satisfied with the service, met my expectations.');
INSERT INTO "Rating" VALUES (4,4,'Very Good - Exceeded my expectations, minor issues only.');
INSERT INTO "Rating" VALUES (5,5,'Excellent - Completely satisfied, service was outstanding.');
COMMIT;
