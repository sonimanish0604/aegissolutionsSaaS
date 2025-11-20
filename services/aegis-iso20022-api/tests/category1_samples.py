from __future__ import annotations

import textwrap


def _mt(message: str) -> str:
    """Normalize multiline MT fixtures."""
    return textwrap.dedent(message).strip()


CATEGORY1_SAMPLES: dict[str, dict[str, str | None]] = {
    "MT101": {
        "mt_raw": _mt(
            """\
            {1:F01BANKDEFFXXXX0000000000}{2:I101BANKUS33XXXXN}{4:
            :20:REF20251022A
            :28D:1/1
            :50H:/DE44500105175407324931
            MAX MUSTERMANN
            :30:20251022
            :21:INV-5568
            :32B:USD12345,67
            :57A:BANKUS33XXX
            :59:/US12300099900011122
            JOHN DOE
            :70:/INV/5568 NET30
            :71A:SHA
            -}
            """
        ),
        "force_type": "MT101",
    },
    "MT102": {
        "mt_raw": _mt(
            """\
            {1:F01CITIGB2LAXXX0000000000}{2:I102DEUTDEFFXXXXN}{3:{108:MT102SAMPLE003}}
            {4:
            :20:REF102-251028-01
            :21R:BATCHREF001
            :23:CRED
            :50K:/FR7630001007941234567890185
            ACME IMPORTS
            75 RUE DE LA PAIX
            75002 PARIS
            FR
            :30:251028
            :32A:251028EUR12345,67
            :52A:CITIGB2LXXX
            :71A:SHA

            :21:TRXREF001
            :32B:EUR7000,00
            :33B:EUR7000,00
            :59:/US12300099900055566
            GLOBAL IMPORTS LLC
            100 BROADWAY
            NEW YORK NY
            US
            :70:/INV/54321 Goods Payment

            :21:TRXREF002
            :32B:EUR5345,67
            :59:/DE89370400440532013000
            MUSTER GMBH
            MUSTERSTRASSE 12
            10115 BERLIN
            DE
            :70:/INV/98765 Services

            :19:EUR12345,67
            -}
            {5:{CHK:ABC123XYZ}}
            """
        ),
        "force_type": None,
    },
    "MT102-STP": {
        "mt_raw": _mt(
            """\
            {1:F01BNPAFRPPAXXX0000000000}{2:I102CITIUS33XXXXN}{3:{119:STP}}{4:
            :20:BATCH20251022
            :23:CRED
            :32A:251022USD56789,00
            :50A:BNPAFRPPXXX
            :59A:CITIUS33XXX
            :71A:SHA

            :21:TRXSTP0001
            :32B:USD56789,00
            :59A:CITIUS33XXX
            :70:/INV/5568 NET30
            -}
            """
        ),
        "force_type": "MT102-STP",
    },
    "MT103": {
        "mt_raw": _mt(
            """\
            {1:F01AAAAUS33XXXX0000000000}{2:I103BBBBNZ2XXXXN}{4:
            :20:REF123456
            :23B:CRED
            :32A:250921USD12345,67
            :50K:/123456789
            JOHN DOE
            1 MAIN STREET
            NEW YORK US
            :59:/GB29NWBK60161331926819
            JANE SMITH
            :70:Invoice 9981
            :71A:SHA
            -}
            """
        ),
        "force_type": None,
    },
    "MT103-REMIT": {
        "mt_raw": _mt(
            """\
            {1:F01AAAAUS33XXXX0000000000}{2:I103BBBBNZ2XXXXN}{4:
            :20:REFREMIT01
            :23B:CRED
            :32A:251022EUR9876,54
            :50K:/DE44500105175407324931
            MAX MUSTERMANN
            1 MAIN STREET
            DE-60311 FRANKFURT
            :59:/FR1420041010050500013M02606
            SOCIETE EXAMPLE
            99 AVENUE DES CHAMPS
            FR-75008 PARIS
            :70:Invoice 123456
            :71A:SHA
            :77T:Remittance information for invoice 123456 covering consulting services.
            -}
            """
        ),
        "force_type": "MT103-REMIT",
    },
    "MT103-STP": {
        "mt_raw": _mt(
            """\
            {1:F01AAAAUS33XXXX0000000000}{2:I103BBBBDEFFXXXXN}{3:{119:STP}}{4:
            :20:STPREF0001
            :23B:CRED
            :32A:251022EUR5432,10
            :50A:AAAAUS33XXX
            :57A:BBBBDEFFXXX
            :59A:CCCCGB2LXXX
            :71A:SHA
            -}
            """
        ),
        "force_type": "MT103-STP",
    },
    "MT104": {
        "mt_raw": _mt(
            """\
            {1:F01AAAADEFFXXXX0000000000}{2:I104BBBBUS33XXXXN}{4:
            :20:DDREF20250101
            :30:250101
            :50K:/DE09876543210987654321
            UTILITY AG
            1 ENERGIESTRASSE
            DE-10115 BERLIN
            :52A:AAAADEFFXXX

            :21:DDTRX0001
            :32B:EUR150,00
            :50C:DEUTDEFFXXX
            :59:/US12300099900011122
            JANE DOE
            45 BROADWAY AVE
            US-10004 NEW YORK
            :70:Electricity invoice 445566
            -}
            """
        ),
        "force_type": "MT104",
    },
    "MT105": {
        "mt_raw": _mt(
            """\
            {1:F01AAAADEFFXXXX0000000000}{2:I105BBBBUS33XXXXN}{4:
            :27:1/1
            :20:EDIFACTREF0001
            :21:INVMSG0001
            :12:381
            :77F:UNH+1+REMADV:D:96A:UN'
            BGM+381+INVMSG0001+9'
            UNT+3+1'
            -}
            """
        ),
        "force_type": "MT105",
    },
    "MT107": {
        "mt_raw": _mt(
            """\
            {1:F01AAAADEFFXXXX0000000000}{2:I107BBBBUS33XXXXN}{4:
            :20:COLLBATCH2025
            :30:250201
            :50K:/DE09876543210987654321
            UTILITY AG
            1 ENERGIESTRASSE
            DE-10115 BERLIN
            :52A:AAAADEFFXXX

            :21:COLLREF0001
            :32B:EUR250,00
            :59:/US12300099900022233
            JOHN CONSUMER
            789 MARKET ST
            US-94105 SAN FRANCISCO
            :70:January subscription
            -}
            """
        ),
        "force_type": "MT107",
    },
    "MT110": {
        "mt_raw": _mt(
            """\
            {1:F01AAAAUS33XXXX0000000000}{2:I110BBBBDEFFXXXXN}{4:
            :20:CHKCOLL202501
            :53A:AAAAUS33XXX

            :21:CHK000123456789
            :30:250201
            :32A:250203USD1250,00
            :50F:/1234567890
            1/JOHN PAYER
            2/10 MARKET STREET
            3/US/NEW YORK
            :59:PAYEE LIMITED
            10 PAYMENT LANE
            GB-LONDON
            :70:Cheque settlement invoice 555
            -}
            """
        ),
        "force_type": "MT110",
    },
    "MT111": {
        "mt_raw": _mt(
            """\
            {1:F01AAAAUS33XXXX0000000000}{2:I111BBBBDEFFXXXXN}{4:
            :20:STOPCHK202501
            :21:CHK99887766
            :30:241231
            :32B:USD1500,00
            :52A:AAAAUS33XXX
            :59:PAYEE LIMITED
            :75:Lost cheque reported by customer
            -}
            """
        ),
        "force_type": "MT111",
    },
    "MT112": {
        "mt_raw": _mt(
            """\
            {1:F01AAAAUS33XXXX0000000000}{2:I112BBBBDEFFXXXXN}{4:
            :20:ANSWERCHK202501
            :21:CHK99887766
            :30:241231
            :32B:USD1500,00
            :52A:AAAAUS33XXX
            :59:PAYEE LIMITED
            :76:1/Stop payment confirmed
            2/Replacement cheque may be issued
            -}
            """
        ),
        "force_type": "MT112",
    },
    "MT192": {
        "mt_raw": _mt(
            """\
            {1:F01NDEAFIHHXXXX0000000000}{2:O1920000991231 RBOSGB2LXXXX00000000009912310000N}{3:{121: 8a562c67-ca16-48ba-b074-65581be6f001}}{4:
            :20:CSE-001
            :21:pacs8bizmsgidr01
            :11S:103
            201217
            :79:/AM09/
            /UETR/8a562c67-ca16-48ba-b074-65581be6f001
            :32A:210217EUR1500000,
            -}
            {5:{CHK:A8D90896761B}}
            """
        ),
        "force_type": "MT192",
    },
    "MT195-CONFIRM": {
        "mt_raw": _mt(
            """\
            {1:F01BANKUS33AXXX0000000000}{2:I195BANKDEFFXXXXN}{4:
            :20:QRY20251022
            :21:TRX10320251020
            :11S:251022
            :32B:USD10000,
            :50K:/123456789
            JOHN DOE
            123 MAIN ST
            NEW YORK NY
            :59:/987654321
            ACME CORP
            456 INDUSTRY RD
            BERLIN
            :72:/QUERY/PLEASE CONFIRM RECEIPT OF MT103 TRX10320251020
            -}
            """
        ),
        "force_type": "MT195",
        "variant": None,
    },
    "MT195-UNABLE": {
        "mt_raw": _mt(
            """\
            {1:F01BANKUS33AXXX0000000000}{2:I195BANKDEFFXXXXN}{4:
            :20:QRY20251022
            :21:TRX10320251020
            :11S:251022
            :32B:USD10000,
            :50K:/123456789
            JOHN DOE
            123 MAIN ST
            NEW YORK NY
            :59:/987654321
            ACME CORP
            456 INDUSTRY RD
            BERLIN
            :72:/QUERY/UNABLE TO APPLY MT103 TRX10320251020
            -}
            """
        ),
        "force_type": "MT195",
        "variant": "unable_to_apply",
    },
    "MT195-CLAIM": {
        "mt_raw": _mt(
            """\
            {1:F01BANKUS33AXXX0000000000}{2:I195BANKDEFFXXXXN}{4:
            :20:QRY20251022
            :21:TRX10320251020
            :11S:251022
            :32B:USD10000,
            :50K:/123456789
            JOHN DOE
            123 MAIN ST
            NEW YORK NY
            :59:/987654321
            ACME CORP
            456 INDUSTRY RD
            BERLIN
            :72:/QUERY/CLAIM NON RECEIPT OF MT103 TRX10320251020
            -}
            """
        ),
        "force_type": "MT195",
        "variant": "claim_non_receipt",
    },
    "MT195-DUPLICATE": {
        "mt_raw": _mt(
            """\
            {1:F01BANKUS33AXXX0000000000}{2:I195BANKDEFFXXXXN}{4:
            :20:QRY20251022
            :21:TRX10320251020
            :11S:251022
            :32B:USD10000,
            :50K:/123456789
            JOHN DOE
            123 MAIN ST
            NEW YORK NY
            :59:/987654321
            ACME CORP
            456 INDUSTRY RD
            BERLIN
            :72:/QUERY/REQUEST FOR DUPLICATE OF MT103 TRX10320251020
            -}
            """
        ),
        "force_type": "MT195",
        "variant": "request_duplicate",
    },
    "MT195-INFO": {
        "mt_raw": _mt(
            """\
            {1:F01BANKUS33AXXX0000000000}{2:I195BANKDEFFXXXXN}{4:
            :20:QRY20251022
            :21:TRX10320251020
            :11S:251022
            :32B:USD10000,
            :50K:/123456789
            JOHN DOE
            123 MAIN ST
            NEW YORK NY
            :59:/987654321
            ACME CORP
            456 INDUSTRY RD
            BERLIN
            :72:/QUERY/REQUEST FOR INFORMATION MT103 TRX10320251020
            -}
            """
        ),
        "force_type": "MT195",
        "variant": None,
    },
    "MT196-CANCEL": {
        "mt_raw": _mt(
            """\
            {1:F01ABNANL2AXXXX0000000000}{2:I196UBSWCHZH80AN}{4:
            :20:6457AZ
            :21:23191
            :76:CANCELLED
            :11R:103 090527
            -}
            """
        ),
        "force_type": "MT196",
    },
    "MT196-QUERY": {
        "mt_raw": _mt(
            """\
            {1:F01ABNANL2AXXXX0000000000}{2:I196UBSWCHZH80AN}{4:
            :20:AW191
            :21:316ARB
            :76:VALUE DATE SHOULD BE 090601 WE HAVE CHANGED ACCORDINGLY
            :11S:950 090527
            -}
            """
        ),
        "force_type": "MT196",
    },
}
