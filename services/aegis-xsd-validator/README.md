# Aegis XSD validation service

This sidecar service exposes a simple REST API that validates MX documents against ISO 20022 schemas. It supports multiple engines so tenants can choose between the bundled Python validator (XSD 1.1 via `xmlschema`) or a simulated Saxon-EE backend. The translator service can call this endpoint by setting `XSD_VALIDATOR_BACKEND=remote`.

## Usage

```bash
uvicorn src.app:app --reload --port 8080
```

```
POST /validate
  form-data:
    engine=xmlschema|xmlschema11|saxon-sim
    mx_type=<optional descriptor>
    xsd=<schema file>    # required for xmlschema engine
    xml=<payload file>
```

Example:

```bash
curl -s http://localhost:8080/validate \
  -F engine=xmlschema \
  -F mx_type=pacs.008.001.13 \
  -F xsd=@schemas/pacs.008.001.13.xsd \
  -F xml=@samples/pacs008_ok.xml | jq
```

To simulate Saxon behaviour:

```bash
curl -s http://localhost:8080/validate \
  -F engine=saxon-sim \
  -F xml=@samples/pacs008_ok.xml | jq
```

## Integrating with the translator

Configure the main service to delegate validation to this sidecar:

```bash
export XSD_VALIDATOR_BACKEND=remote
export XSD_VALIDATOR_ENDPOINT=http://xsd-validator:8080/validate
export XSD_VALIDATOR_ENGINE=xmlschema    # or saxon-sim / saxon-ee
```

Per-tenant overrides can be implemented by setting these variables at deployment time (for example, different Kubernetes namespaces or Compose profiles).
