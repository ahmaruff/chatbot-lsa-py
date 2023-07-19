import sqlite3
import csv

connection = sqlite3.connect('database_lsa.db')

# CREATE TABLE
with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# CREATE DATASET from provided CSV
csv_data = []
with open('dataset/dataset.csv') as data:
    reader = csv.reader(data)
    next(reader, None) #skip header
    csv_data = list(tuple(line) for line in reader)

# print(csv_data)

# INSERT DATASET
cur.executemany('INSERT INTO datasets(message, response) VALUES(?,?);',csv_data)

connection.commit()
connection.close()