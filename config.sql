CREATE TABLE Info (
	Account VARCHAR(20) PRIMARY KEY NOT NULL,
	Password VARCHAR(30) NOT NULL,
	Cookies BINARY NULL,
	Longitude FLOAT NULL,
	Latitude FLOAT NULL,
	Address VARCHAR(100) NULL,
	Inschool BOOL NULL,
	Email BOOL NULL,
	Email_server VARCHAR(30) NULL,
	Server_key VARCHAR(30) NULL,
	Email_client VARCHAR(30) NULL
);

