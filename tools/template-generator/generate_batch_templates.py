import os, re, json, argparse
from pdfminer.high_level import extract_text
from xmlschema import XMLSchema
from datetime import datetime
from tqdm import tqdm

def extract_mt_blocks(pdf_text):
    messages = re.findall(r"(MT\d{3}.*?)\n(?=MT\d{3}|$)", pdf_text, re.DOTALL)
    return {msg[:6]: msg for msg in messages}

def extract_mt_fields(mt_text):
    return dict(re.findall(r":(\d{2}[A-Z]?): (.*?)\n", mt_text))

def extract_mx_xpaths(xsd_path):
    schema = XMLSchema(xsd_path)
    return [e for e in schema.iter() if e.tag.endswith("element")]

def match_fields(mt_fields, mx_xpaths):
    template = {}
    for code, desc in mt_fields.items():
        match = next((xpath for xpath in mx_xpaths if desc.lower() in xpath.lower()), None)
        template[code] = {
            "description": desc,
            "xpath": match or "UNMAPPED"
        }
    return template

def process_pdf(pdf_path, xsd_dir, output_dir):
    pdf_text = extract_text(pdf_path)
    mt_blocks = extract_mt_blocks(pdf_text)
    xsd_files = [f for f in os.listdir(xsd_dir) if f.endswith(".xsd")]

    for mt_code, mt_text in mt_blocks.items():
        mt_fields = extract_mt_fields(mt_text)
        for xsd_file in xsd_files:
            mx_xpaths = extract_mx_xpaths(os.path.join(xsd_dir, xsd_file))
            template = match_fields(mt_fields, mx_xpaths)
            template["_meta"] = {
                "source": mt_code,
                "target": xsd_file.replace(".xsd", ""),
                "generated_by": "AI-assisted batch",
                "confidence": "strict-match",
                "timestamp": datetime.utcnow().isoformat()
            }
            out_path = os.path.join(output_dir, f"{mt_code.lower()}_to_{xsd_file.replace('.xsd','').lower()}.json")
            with open(out_path, "w") as f:
                json.dump(template, f, indent=2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mt-dir", required=True)
    parser.add_argument("--xsd-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    pdf_files = [f for f in os.listdir(args.mt_dir) if f.endswith(".pdf")]

    for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
        process_pdf(os.path.join(args.mt_dir, pdf_file), args.xsd_dir, args.output_dir)

if __name__ == "__main__":
    main()