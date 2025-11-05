#!/usr/bin/env python3
"""
Extract MT101 table data from mt101rules.docx and emit a provisional YAML file.
This automates the mechanical extraction of field lists; manual review is still
required to inject detailed constraints, options, and cross-field rules.
"""
from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import yaml

DOCX_PATH = Path('services/aegis-iso20022-api/pre-validateMT/mt101rules.docx').resolve()
OUTPUT_PATH = Path('services/aegis-iso20022-api/pre-validateMT/MT101_auto.yaml').resolve()

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


def extract_tables(docx_path: Path):
    with ZipFile(docx_path) as z:
        with z.open('word/document.xml') as f:
            xml = f.read()
    root = ET.fromstring(xml)
    tables = root.findall('.//w:tbl', NS)
    return tables


def cell_text(cell: ET.Element) -> str:
    texts = []
    for node in cell.iter():
        if node.tag == '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t':
            texts.append(node.text or '')
    return ''.join(texts).strip()


def parse_table(table: ET.Element):
    rows = []
    for row in table.findall('.//w:tr', NS):
        cells = [cell_text(cell) for cell in row.findall('.//w:tc', NS)]
        if cells:
            rows.append(cells)
    return rows


def interpret_field_table(rows):
    fields = []
    current_sequence = None
    for row in rows:
        if not row:
            continue
        header = row[0]
        if header.startswith('Mandatory Sequence') or header.startswith('Optional Sequence'):
            current_sequence = header
            continue
        if len(row) >= 5 and row[0] in {'M', 'O'}:
            status, tag, name, fmt, number = row[:5]
            fields.append({
                'status': status,
                'tag': tag,
                'name': name,
                'format': fmt,
                'number': number,
                'sequence_hint': current_sequence,
            })
    return fields


def build_yaml_structure(fields):
    sequences = {
        'A': {'mandatory': True},
        'B': {'mandatory': True, 'repetitive': True}
    }
    field_map = {}
    for field in fields:
        tag = field['tag']
        seq_hint = field['sequence_hint'] or ''
        if 'Sequence B' in seq_hint:
            sequence = 'B'
        else:
            sequence = 'A'
        entry = {
            'name': field['name'],
            'sequence': sequence,
            'presence': 'M' if field['status'] == 'M' else 'O',
            'format': field['format'] if field['format'] else None,
            'notes': [f"Extracted from table: column number {field['number']}"]
        }
        field_map[tag] = entry
    yaml_struct = {
        'mt': 'MT101',
        'sequences': sequences,
        'fields': field_map,
        'cross_field_rules': []
    }
    return yaml_struct


def main():
    if not DOCX_PATH.exists():
        raise SystemExit(f'DOCX not found: {DOCX_PATH}')
    tables = extract_tables(DOCX_PATH)
    if len(tables) < 2:
        raise SystemExit('Expected at least two tables for MT101 sequences')
    rows_a = parse_table(tables[0])
    rows_b = parse_table(tables[1])
    fields = interpret_field_table(rows_a) + interpret_field_table(rows_b)
    yaml_struct = build_yaml_structure(fields)
    with OUTPUT_PATH.open('w') as f:
        yaml.safe_dump(yaml_struct, f, sort_keys=False, allow_unicode=True)
    print(f"Generated provisional YAML at {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
