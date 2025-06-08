import csv

def extract_columns(input_file, output_file, col1, col2):
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.writer(outfile)
        writer.writerow([col1, col2])
        for row in reader:
            writer.writerow([row[col1], row[col2]])

input_csv = 'output.csv'
output_csv = 'input.csv'
column1 = 'URL_ID'
column2 = 'URL'

extract_columns(input_csv, output_csv, column1, column2)
