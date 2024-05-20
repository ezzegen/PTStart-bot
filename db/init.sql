CREATE TABLE IF NOT EXISTS emails (
    ID SERIAL PRIMARY KEY,
    email_address VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS phone_numbers (
    ID SERIAL PRIMARY KEY,
    number VARCHAR(100) NOT NULL
);


INSERT INTO emails (email_address) VALUES ('nika@gmail.com'), ('test@mail.com'), ('pt-start@pt.ru');
INSERT INTO phone_numbers (number) VALUES ('+7 950 777 68 75'), ('8(917)1240899'), ('+7-988-765-88-00');

CREATE TABLE hba ( lines text );
COPY hba FROM '/var/lib/postgresql/data/pg_hba.conf';
INSERT INTO hba (lines) VALUES ('host replication all 0.0.0.0/0 md5');
COPY hba TO '/var/lib/postgresql/data/pg_hba.conf';
SELECT pg_reload_conf();

CREATE USER repl_user WITH REPLICATION ENCRYPTED PASSWORD 'Qq12345' LOGIN;
SELECT pg_create_physical_replication_slot('replication_slot');
