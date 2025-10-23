from pathlib import Path
from lxml import etree

class XSDValidator:
    def __init__(self, xsd_dir: str, mx_type: str):
        """
        xsd_dir can be either a directory containing multiple .xsd files
        (e.g., .../downloads/pacs) or a per-version folder.
        mx_type is like 'pacs.008.001.13'.
        """
        p = Path(xsd_dir)
        if p.is_dir():
            # prefer exact filename match: pacs.008.001.13.xsd
            target = p / f"{mx_type}.xsd"
            if target.exists():
                self.schema_doc = etree.parse(str(target))
            else:
                # fallback: search by targetNamespace match
                ns_wanted = f"urn:iso:std:iso:20022:tech:xsd:{mx_type}"
                self.schema_doc = None
                for f in p.glob("*.xsd"):
                    doc = etree.parse(str(f))
                    root = doc.getroot()
                    if root.get("targetNamespace") == ns_wanted:
                        self.schema_doc = doc
                        break
                if self.schema_doc is None:
                    raise FileNotFoundError(
                        f"Cannot find XSD for {mx_type} in {xsd_dir} "
                        f"(expected {mx_type}.xsd or matching targetNamespace).")
        else:
            # xsd_dir points to a file
            self.schema_doc = etree.parse(str(p))

        self.schema = etree.XMLSchema(self.schema_doc)

    def validate(self, xml_str: str):
        doc = etree.fromstring(xml_str.encode("utf-8"))
        ok = self.schema.validate(doc)
        return ok, [str(e) for e in self.schema.error_log]