import re

BLOCK_RE = re.compile(r"\{(\d):([^}]*)\}", re.S)
TAG_RE = re.compile(r"(?m)^:(\d{2}[A-Z]?):")

class MTParser:
    def parse(self, mt_type: str, raw: str) -> dict:
        blocks = dict(BLOCK_RE.findall(raw))
        b4 = blocks.get("4") or raw
        fields, order = {}, []
        for m in TAG_RE.finditer(b4):
            tag = m.group(1)
            start = m.end()
            nxt = TAG_RE.search(b4, start)
            val = b4[start:(nxt.start() if nxt else len(b4))].strip()
            if val.endswith("-}"):
                val = val[:-2].rstrip()
            # if the last line is a lone hyphen, drop it too
            if "\n" in val:
                last_line = val.splitlines()[-1].strip()
                if last_line == "-":
                    val = "\n".join(val.splitlines()[:-1]).rstrip()
            if val.endswith("-}"):
                val = val[:-2].rstrip()
            fields.setdefault(tag, []).append(val)
            order.append(tag)
        return {"mt_type": mt_type, "blocks": blocks, "fields": fields, "order": order}