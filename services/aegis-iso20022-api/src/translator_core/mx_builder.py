from lxml import etree
from pathlib import Path

NS_BY_MSG = {
    "pacs.008.001.13": "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.13",
    "pacs.009.001.12": "urn:iso:std:iso:20022:tech:xsd:pacs.009.001.12",
    "pacs.008.001.10": "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.10",
    "pacs.009.001.09": "urn:iso:std:iso:20022:tech:xsd:pacs.009.001.09",
    "pacs.003.001.11": "urn:iso:std:iso:20022:tech:xsd:pacs.003.001.11",
    "camt.053.001.08": "urn:iso:std:iso:20022:tech:xsd:camt.053.001.08",
    "camt.054.001.08": "urn:iso:std:iso:20022:tech:xsd:camt.054.001.08",
    "camt.057.001.08": "urn:iso:std:iso:20022:tech:xsd:camt.057.001.08",
    "camt.056.001.11": "urn:iso:std:iso:20022:tech:xsd:camt.056.001.11",
    "camt.026.001.10": "urn:iso:std:iso:20022:tech:xsd:camt.026.001.10",
    "camt.027.001.10": "urn:iso:std:iso:20022:tech:xsd:camt.027.001.10",
    "camt.028.001.12": "urn:iso:std:iso:20022:tech:xsd:camt.028.001.12",
    "camt.033.001.07": "urn:iso:std:iso:20022:tech:xsd:camt.033.001.07",
    "pain.001.001.12": "urn:iso:std:iso:20022:tech:xsd:pain.001.001.12",
    "pain.008.001.11": "urn:iso:std:iso:20022:tech:xsd:pain.008.001.11",
    "camt.107.001.02": "urn:iso:std:iso:20022:tech:xsd:camt.107.001.02",
    "camt.029.001.09": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.09",
    "camt.108.001.02": "urn:iso:std:iso:20022:tech:xsd:camt.108.001.02",
    "camt.109.001.02": "urn:iso:std:iso:20022:tech:xsd:camt.109.001.02",
    "camt.029.001.13": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.13",
    "camt.111.001.02": "urn:iso:std:iso:20022:tech:xsd:camt.111.001.02",
}

class MXBuilder:
    def build(self, mx_type: str, flat: dict) -> str:
        ns = NS_BY_MSG.get(mx_type)
        if not ns:
            raise ValueError(f"Unknown namespace for {mx_type}")
        root = etree.Element("Document", nsmap={None: ns})
        # create nodes for each xpath, supporting attributes
        for xp, values in flat.items():
            self._ensure_path(root, xp, values)
        return etree.tostring(root, pretty_print=True, encoding="UTF-8", xml_declaration=True).decode()

    def _ensure_path(self, root, xpath: str, values):
        # xpath like /Document/FIToFICstmrCdtTrf/CdtTrfTxInf[1]/PmtId/TxId
        parts = [p for p in xpath.split("/") if p and p != "Document"]
        node = root
        for i, part in enumerate(parts):
            if part.startswith("@"):  # attribute
                for v in values:
                    node.set(part[1:], v)
                return
            # strip [1] index for path creation
            tag = part.split("[",1)[0]
            child = node.find(f"{{*}}{tag}")
            if child is None:
                child = etree.SubElement(node, tag)
            node = child
        # assign values (repeat creates multiple entries)
        for v in values:
            node.text = v  # last value wins; for multi-occ, map to separate paths/rules
