import re

class Detector:
    MT_HEADER_RE = re.compile(r"\{2:[IO](\d{3})")
    TAG_RE = re.compile(r":(\d{2}[A-Z]?):")

    def detect(self, raw: str) -> str | None:
        tags = set(self.TAG_RE.findall(raw))

        m = self.MT_HEADER_RE.search(raw)
        if m:
            mt = f"MT{m.group(1)}"
            if mt == "MT202":
                cov_present = ({"50A", "50F", "50K"} & tags) and ({tag for tag in tags if tag.startswith("59")})
                if cov_present:
                    return "MT202COV"
            return mt

        if {"20","23B","32A","50K","59","71A"} <= tags: return "MT103"
        if {"20","21","32A"} <= tags and ({"57A","57D"} & tags): return "MT202"
        if {"25","28C","61"} <= tags: return "MT940"
        if {"25","61"} <= tags: return "MT910"  # weak heuristic
        return None
