import json
import xml.etree.ElementTree as ET
import sqlite3

def load_txt(filename):
    with open(filename, 'r') as file:
        data = [line.strip().split('\t') for line in file.readlines()]
    return data

def save_txt(filename, data):
    with open(filename, 'w') as file:
        for row in data:
            file.write('\t'.join(row) + '\n')

def load_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

def save_json(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def load_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    data = [[cell.text for cell in row] for row in root.findall('row')]
    return data

def save_xml(filename, data):
    root = ET.Element('data')
    for row in data:
        row_elem = ET.SubElement(root, 'row')
        for cell in row:
            cell_elem = ET.SubElement(row_elem, 'cell')
            cell_elem.text = cell
    tree = ET.ElementTree(root)
    tree.write(filename)

def load_sql(filename):
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fmea")
    data = cursor.fetchall()
    conn.close()
    return data

def save_sql(filename, data):
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS fmea
        (operation_sequence TEXT, part_or_product TEXT, characteristics TEXT, failure_mode TEXT,
        effect_of_failure TEXT, severity INTEGER, classification TEXT, cause_of_failure TEXT, 
        controls_prevention TEXT, occurrence INTEGER, controls_detection TEXT, detection INTEGER, 
        rpn INTEGER, recommended_action TEXT, responsibility TEXT, completion_date TEXT, 
        actions_taken TEXT, severity_a INTEGER, occurrence_a INTEGER, detection_a INTEGER, rpn_a INTEGER)''')
    cursor.executemany('INSERT INTO fmea VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', data)
    conn.commit()
    conn.close()


