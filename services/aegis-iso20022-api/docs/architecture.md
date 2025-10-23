# ISO 20022 Translator – Architecture Overview

```mermaid
flowchart TD
    subgraph API Layer
        ROUTES[translator_api/routes.py]
    end

    subgraph Core Engine
        DET[Detector]\ntranslator_core/detector.py
        PARSE[MTParser]\ntranslator_core/mt_parser.py
        MAPSTORE[MappingStore]\ntranslator_core/mapping_store.py
        TRANS[Transformer]\ntranslator_core/transformer.py
        MBUILD[MXBuilder]\ntranslator_core/mx_builder.py
        XSD[XSDValidator]\ntranslator_core/xsd_validator.py
        AUD[Audit]\ntranslator_core/audit.py
        METRICS[Metrics]\ntranslator_core/metrics.py
    end

    ROUTES --> DET
    DET --> ROUTES
    ROUTES --> PARSE
    ROUTES --> MAPSTORE
    MAPSTORE --> ROUTES
    ROUTES --> TRANS
    TRANS --> ROUTES
    ROUTES --> MBUILD
    MBUILD --> ROUTES
    ROUTES --> XSD
    XSD --> ROUTES

    ROUTES -.-> AUD
    ROUTES -.-> METRICS

    subgraph Artefacts
        MAPPINGS[mappings/*.json]
        PAIRS[iso-bootstrap/pairs.yaml]
        XSDDIR[iso-bootstrap/out/**.xsd]
    end

    MAPSTORE --> MAPPINGS
    MAPSTORE --> PAIRS
    XSD --> XSDDIR
```

## Request Flow
1. `translator_api/routes.py` receives the `/translate` request and instantiates shared services.
2. `Detector` inspects block headers to auto-detect the MT message type.
3. `MTParser` tokenises the MT message into a structured dictionary (`fields`, `blocks`, `order`).
4. `MappingStore` resolves the mapping profile and XSD directory for the detected type (and optional variant) using `pairs.yaml`.
5. `Transformer` executes the JSON mapping rules against the parsed fields, producing a flat XPath → value map and audit details.
6. `MXBuilder` renders the flat map into a fully-formed ISO 20022 document.
7. `XSDValidator` validates the document against the target XSD.
8. `Audit` and `Metrics` modules assemble execution details before the response is returned to the client.

## Key Modules
- **translator_api/routes.py** – FastAPI entry point orchestrating the flow.
- **translator_core/detector.py** – Detects MT type and variants.
- **translator_core/mt_parser.py** – Parses MT block 4 tags into structured data.
- **translator_core/mapping_store.py** – Loads mapping JSON and XSD metadata.
- **translator_core/transformer.py** – Applies mapping, transforms, and validations.
- **translator_core/mx_builder.py** – Builds ISO 20022 XML from flat paths.
- **translator_core/xsd_validator.py** – Validates XML against the appropriate schema.
- **translator_core/audit.py & metrics.py** – Produce telemetry and audit entries.
- **mappings/** – JSON mapping templates for each MT→MX conversion.
- **iso-bootstrap/** – XSD catalogues and mapping-index metadata (`pairs.yaml`).
