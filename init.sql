DROP TABLE IF EXISTS DOCS;
DROP TABLE IF EXISTS QUERIES;
DROP TABLE IF EXISTS QRELS;
DROP VIEW IF EXISTS JOINED;

CREATE TABLE DOCS(
ID NUMBER PRIMARY KEY,
DOC_ID NUMBER,
DATA TEXT);

CREATE TABLE QUERIES(
ID NUMBER PRIMARY KEY,
QUERY_ID NUMBER,
DATA TEXT);

CREATE TABLE QRELS(
ID NUMBER PRIMARY KEY,
QUERY_ID NUMBER,
DOC_ID NUMBER);


CREATE UNIQUE INDEX DOCS_D_ID ON DOCS(DOC_ID);
CREATE UNIQUE INDEX QUERIES_Q_ID ON QUERIES(QUERY_ID);

CREATE INDEX QRELS_D_ID ON QRELS(DOC_ID);
CREATE INDEX QRELS_Q_ID ON QRELS(QUERY_ID);


CREATE VIEW JOINED AS
SELECT QRELS.ID ID, QUERIES.QUERY_ID, QUERIES.DATA QUERY_DATA, DOCS.DOC_ID, DOCS.DATA DOC_DATA FROM DOCS
LEFT JOIN QRELS ON DOCS.DOC_ID = QRELS.DOC_ID
LEFT JOIN QUERIES ON QRELS.QUERY_ID = QUERIES.QUERY_ID;
