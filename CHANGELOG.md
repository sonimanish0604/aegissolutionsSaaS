# 1.0.0-rc.1 (2025-11-07)


### Bug Fixes

* align test client dependencies and clarify xsd skip message ([d425b60](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/d425b60a6ee6916f207437fc9f7de5a0907a0317))
* correct commit message format ([678f293](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/678f2934052eb5871f1485d53069ce69490a942e))
* pin xmlschema to 2.3.1 for Python compatibility ([00c7458](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/00c7458f6bd32907d1946569d98be68731c5e96b))
* relax xmlschema pin and add python-multipart ([2ba4f8a](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/2ba4f8afd49912730de22b1fa93cf98ab501aa2f))
* run SOC2 workflow on Python 3.11 ([b97c016](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/b97c0163cee4a048f7820fa678cd3adfd236fc78))
* update xmlschema dependency ([3315814](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/3315814fdad4841f7982f87b0fbdf546b8cb9e06))


### Features

* add audit event model and hashing utilities ([092377b](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/092377b04c381983eff900e563f2cb210a189d6f))
* add audit middleware and logging emitter scaffolding ([8a2599e](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/8a2599e8411c8eee61f2155ce9284b67afd24ebb))
* add batch translate endpoint with XML validator options ([eeb7971](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/eeb797120aa9a3d64fb40c78c99d8761bc2c0f06))
* add event idempotency metadata and Kafka headers ([6f211fe](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/6f211fe99c4b1fdb0ea5064c1cb39869b7e9fba9))
* add Kafka audit emitter scaffolding ([7909f57](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/7909f57624514ebb1e119f589f430e1030cee8f1))
* add manifest builder for audit archive integrity ([a6a53b0](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/a6a53b0a6699747ca9eb0684b91fff421cfe5075))
* add signer abstraction with KMS integration ([7881825](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/7881825b4336e409e22097df213da3eb21f3bffb))
* **audit:** add durable audit middleware + schema reconcile ([ec206be](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/ec206be5ec5d287f7ca4e138b29e012142cca0bf))
* capture created_by in audit manifest and document layout ([04009a1](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/04009a16f25c9c79dddf25d6b466780b20f042ee))
* **idempotency:** add table, alembic setup, and TTL cleanup script ([ebd0d76](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/ebd0d764a175d3c1b8e2e9c58316c29a221a10c7))
* **idempotency:** add table, alembic setup, and TTL cleanup script+onboarding-ci.yml ([e6f2f70](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/e6f2f7096df4873bf8002570ec8d214c7de73fd6))
* include tenant_uuid on audit events ([77b9671](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/77b9671bbe6f1f9a6be84a092149b6e87ca98606))
* **onboarding:** initial FastAPI service scaffold with DB integration ([8fc9fc5](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/8fc9fc5bc6f39dea59389656ec4ebc38f43b7550))

# 1.0.0-rc.1 (2025-11-07)


### Bug Fixes

* align test client dependencies and clarify xsd skip message ([d425b60](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/d425b60a6ee6916f207437fc9f7de5a0907a0317))
* correct commit message format ([678f293](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/678f2934052eb5871f1485d53069ce69490a942e))
* pin xmlschema to 2.3.1 for Python compatibility ([00c7458](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/00c7458f6bd32907d1946569d98be68731c5e96b))
* relax xmlschema pin and add python-multipart ([2ba4f8a](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/2ba4f8afd49912730de22b1fa93cf98ab501aa2f))
* run SOC2 workflow on Python 3.11 ([b97c016](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/b97c0163cee4a048f7820fa678cd3adfd236fc78))
* update xmlschema dependency ([3315814](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/3315814fdad4841f7982f87b0fbdf546b8cb9e06))


### Features

* add audit event model and hashing utilities ([092377b](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/092377b04c381983eff900e563f2cb210a189d6f))
* add audit middleware and logging emitter scaffolding ([8a2599e](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/8a2599e8411c8eee61f2155ce9284b67afd24ebb))
* add batch translate endpoint with XML validator options ([eeb7971](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/eeb797120aa9a3d64fb40c78c99d8761bc2c0f06))
* add event idempotency metadata and Kafka headers ([6f211fe](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/6f211fe99c4b1fdb0ea5064c1cb39869b7e9fba9))
* add Kafka audit emitter scaffolding ([7909f57](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/7909f57624514ebb1e119f589f430e1030cee8f1))
* add manifest builder for audit archive integrity ([a6a53b0](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/a6a53b0a6699747ca9eb0684b91fff421cfe5075))
* add signer abstraction with KMS integration ([7881825](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/7881825b4336e409e22097df213da3eb21f3bffb))
* **audit:** add durable audit middleware + schema reconcile ([ec206be](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/ec206be5ec5d287f7ca4e138b29e012142cca0bf))
* capture created_by in audit manifest and document layout ([04009a1](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/04009a16f25c9c79dddf25d6b466780b20f042ee))
* **idempotency:** add table, alembic setup, and TTL cleanup script ([ebd0d76](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/ebd0d764a175d3c1b8e2e9c58316c29a221a10c7))
* **idempotency:** add table, alembic setup, and TTL cleanup script+onboarding-ci.yml ([e6f2f70](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/e6f2f7096df4873bf8002570ec8d214c7de73fd6))
* include tenant_uuid on audit events ([77b9671](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/77b9671bbe6f1f9a6be84a092149b6e87ca98606))
* **onboarding:** initial FastAPI service scaffold with DB integration ([8fc9fc5](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/8fc9fc5bc6f39dea59389656ec4ebc38f43b7550))

# 1.0.0-rc.1 (2025-11-07)


### Bug Fixes

* align test client dependencies and clarify xsd skip message ([d425b60](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/d425b60a6ee6916f207437fc9f7de5a0907a0317))
* correct commit message format ([678f293](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/678f2934052eb5871f1485d53069ce69490a942e))
* pin xmlschema to 2.3.1 for Python compatibility ([00c7458](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/00c7458f6bd32907d1946569d98be68731c5e96b))
* relax xmlschema pin and add python-multipart ([2ba4f8a](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/2ba4f8afd49912730de22b1fa93cf98ab501aa2f))
* run SOC2 workflow on Python 3.11 ([b97c016](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/b97c0163cee4a048f7820fa678cd3adfd236fc78))
* update xmlschema dependency ([3315814](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/3315814fdad4841f7982f87b0fbdf546b8cb9e06))


### Features

* add audit event model and hashing utilities ([092377b](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/092377b04c381983eff900e563f2cb210a189d6f))
* add audit middleware and logging emitter scaffolding ([8a2599e](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/8a2599e8411c8eee61f2155ce9284b67afd24ebb))
* add batch translate endpoint with XML validator options ([eeb7971](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/eeb797120aa9a3d64fb40c78c99d8761bc2c0f06))
* add event idempotency metadata and Kafka headers ([6f211fe](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/6f211fe99c4b1fdb0ea5064c1cb39869b7e9fba9))
* add Kafka audit emitter scaffolding ([7909f57](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/7909f57624514ebb1e119f589f430e1030cee8f1))
* add manifest builder for audit archive integrity ([a6a53b0](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/a6a53b0a6699747ca9eb0684b91fff421cfe5075))
* add signer abstraction with KMS integration ([7881825](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/7881825b4336e409e22097df213da3eb21f3bffb))
* **audit:** add durable audit middleware + schema reconcile ([ec206be](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/ec206be5ec5d287f7ca4e138b29e012142cca0bf))
* capture created_by in audit manifest and document layout ([04009a1](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/04009a16f25c9c79dddf25d6b466780b20f042ee))
* **idempotency:** add table, alembic setup, and TTL cleanup script ([ebd0d76](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/ebd0d764a175d3c1b8e2e9c58316c29a221a10c7))
* **idempotency:** add table, alembic setup, and TTL cleanup script+onboarding-ci.yml ([e6f2f70](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/e6f2f7096df4873bf8002570ec8d214c7de73fd6))
* include tenant_uuid on audit events ([77b9671](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/77b9671bbe6f1f9a6be84a092149b6e87ca98606))
* **onboarding:** initial FastAPI service scaffold with DB integration ([8fc9fc5](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/8fc9fc5bc6f39dea59389656ec4ebc38f43b7550))

# 1.0.0-rc.1 (2025-11-05)


### Bug Fixes

* align test client dependencies and clarify xsd skip message ([d425b60](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/d425b60a6ee6916f207437fc9f7de5a0907a0317))
* correct commit message format ([678f293](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/678f2934052eb5871f1485d53069ce69490a942e))
* pin xmlschema to 2.3.1 for Python compatibility ([00c7458](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/00c7458f6bd32907d1946569d98be68731c5e96b))
* relax xmlschema pin and add python-multipart ([2ba4f8a](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/2ba4f8afd49912730de22b1fa93cf98ab501aa2f))
* run SOC2 workflow on Python 3.11 ([b97c016](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/b97c0163cee4a048f7820fa678cd3adfd236fc78))
* update xmlschema dependency ([3315814](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/3315814fdad4841f7982f87b0fbdf546b8cb9e06))


### Features

* add audit event model and hashing utilities ([092377b](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/092377b04c381983eff900e563f2cb210a189d6f))
* add audit middleware and logging emitter scaffolding ([8a2599e](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/8a2599e8411c8eee61f2155ce9284b67afd24ebb))
* add batch translate endpoint with XML validator options ([eeb7971](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/eeb797120aa9a3d64fb40c78c99d8761bc2c0f06))
* add event idempotency metadata and Kafka headers ([6f211fe](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/6f211fe99c4b1fdb0ea5064c1cb39869b7e9fba9))
* add Kafka audit emitter scaffolding ([7909f57](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/7909f57624514ebb1e119f589f430e1030cee8f1))
* add manifest builder for audit archive integrity ([a6a53b0](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/a6a53b0a6699747ca9eb0684b91fff421cfe5075))
* add signer abstraction with KMS integration ([7881825](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/7881825b4336e409e22097df213da3eb21f3bffb))
* **audit:** add durable audit middleware + schema reconcile ([ec206be](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/ec206be5ec5d287f7ca4e138b29e012142cca0bf))
* capture created_by in audit manifest and document layout ([04009a1](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/04009a16f25c9c79dddf25d6b466780b20f042ee))
* **idempotency:** add table, alembic setup, and TTL cleanup script ([ebd0d76](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/ebd0d764a175d3c1b8e2e9c58316c29a221a10c7))
* **idempotency:** add table, alembic setup, and TTL cleanup script+onboarding-ci.yml ([e6f2f70](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/e6f2f7096df4873bf8002570ec8d214c7de73fd6))
* include tenant_uuid on audit events ([77b9671](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/77b9671bbe6f1f9a6be84a092149b6e87ca98606))
* **onboarding:** initial FastAPI service scaffold with DB integration ([8fc9fc5](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/8fc9fc5bc6f39dea59389656ec4ebc38f43b7550))

# 1.0.0-rc.1 (2025-11-05)


### Bug Fixes

* align test client dependencies and clarify xsd skip message ([d425b60](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/d425b60a6ee6916f207437fc9f7de5a0907a0317))
* correct commit message format ([678f293](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/678f2934052eb5871f1485d53069ce69490a942e))
* pin xmlschema to 2.3.1 for Python compatibility ([00c7458](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/00c7458f6bd32907d1946569d98be68731c5e96b))
* relax xmlschema pin and add python-multipart ([2ba4f8a](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/2ba4f8afd49912730de22b1fa93cf98ab501aa2f))
* run SOC2 workflow on Python 3.11 ([b97c016](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/b97c0163cee4a048f7820fa678cd3adfd236fc78))
* update xmlschema dependency ([3315814](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/3315814fdad4841f7982f87b0fbdf546b8cb9e06))


### Features

* add audit event model and hashing utilities ([092377b](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/092377b04c381983eff900e563f2cb210a189d6f))
* add audit middleware and logging emitter scaffolding ([8a2599e](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/8a2599e8411c8eee61f2155ce9284b67afd24ebb))
* add batch translate endpoint with XML validator options ([eeb7971](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/eeb797120aa9a3d64fb40c78c99d8761bc2c0f06))
* add event idempotency metadata and Kafka headers ([6f211fe](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/6f211fe99c4b1fdb0ea5064c1cb39869b7e9fba9))
* add Kafka audit emitter scaffolding ([7909f57](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/7909f57624514ebb1e119f589f430e1030cee8f1))
* add manifest builder for audit archive integrity ([a6a53b0](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/a6a53b0a6699747ca9eb0684b91fff421cfe5075))
* add signer abstraction with KMS integration ([7881825](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/7881825b4336e409e22097df213da3eb21f3bffb))
* **audit:** add durable audit middleware + schema reconcile ([ec206be](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/ec206be5ec5d287f7ca4e138b29e012142cca0bf))
* capture created_by in audit manifest and document layout ([04009a1](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/04009a16f25c9c79dddf25d6b466780b20f042ee))
* **idempotency:** add table, alembic setup, and TTL cleanup script ([ebd0d76](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/ebd0d764a175d3c1b8e2e9c58316c29a221a10c7))
* **idempotency:** add table, alembic setup, and TTL cleanup script+onboarding-ci.yml ([e6f2f70](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/e6f2f7096df4873bf8002570ec8d214c7de73fd6))
* include tenant_uuid on audit events ([77b9671](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/77b9671bbe6f1f9a6be84a092149b6e87ca98606))
* **onboarding:** initial FastAPI service scaffold with DB integration ([8fc9fc5](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/8fc9fc5bc6f39dea59389656ec4ebc38f43b7550))

# 1.0.0-rc.1 (2025-11-05)


### Bug Fixes

* align test client dependencies and clarify xsd skip message ([d425b60](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/d425b60a6ee6916f207437fc9f7de5a0907a0317))
* correct commit message format ([678f293](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/678f2934052eb5871f1485d53069ce69490a942e))
* pin xmlschema to 2.3.1 for Python compatibility ([00c7458](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/00c7458f6bd32907d1946569d98be68731c5e96b))
* relax xmlschema pin and add python-multipart ([2ba4f8a](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/2ba4f8afd49912730de22b1fa93cf98ab501aa2f))
* run SOC2 workflow on Python 3.11 ([b97c016](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/b97c0163cee4a048f7820fa678cd3adfd236fc78))
* update xmlschema dependency ([3315814](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/3315814fdad4841f7982f87b0fbdf546b8cb9e06))


### Features

* add audit event model and hashing utilities ([092377b](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/092377b04c381983eff900e563f2cb210a189d6f))
* add audit middleware and logging emitter scaffolding ([8a2599e](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/8a2599e8411c8eee61f2155ce9284b67afd24ebb))
* add batch translate endpoint with XML validator options ([eeb7971](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/eeb797120aa9a3d64fb40c78c99d8761bc2c0f06))
* add event idempotency metadata and Kafka headers ([6f211fe](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/6f211fe99c4b1fdb0ea5064c1cb39869b7e9fba9))
* add Kafka audit emitter scaffolding ([7909f57](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/7909f57624514ebb1e119f589f430e1030cee8f1))
* add manifest builder for audit archive integrity ([a6a53b0](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/a6a53b0a6699747ca9eb0684b91fff421cfe5075))
* add signer abstraction with KMS integration ([7881825](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/7881825b4336e409e22097df213da3eb21f3bffb))
* **audit:** add durable audit middleware + schema reconcile ([ec206be](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/ec206be5ec5d287f7ca4e138b29e012142cca0bf))
* capture created_by in audit manifest and document layout ([04009a1](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/04009a16f25c9c79dddf25d6b466780b20f042ee))
* **idempotency:** add table, alembic setup, and TTL cleanup script ([ebd0d76](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/ebd0d764a175d3c1b8e2e9c58316c29a221a10c7))
* **idempotency:** add table, alembic setup, and TTL cleanup script+onboarding-ci.yml ([e6f2f70](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/e6f2f7096df4873bf8002570ec8d214c7de73fd6))
* include tenant_uuid on audit events ([77b9671](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/77b9671bbe6f1f9a6be84a092149b6e87ca98606))
* **onboarding:** initial FastAPI service scaffold with DB integration ([8fc9fc5](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/8fc9fc5bc6f39dea59389656ec4ebc38f43b7550))

# 1.0.0-rc.1 (2025-11-05)


### Bug Fixes

* align test client dependencies and clarify xsd skip message ([d425b60](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/d425b60a6ee6916f207437fc9f7de5a0907a0317))
* correct commit message format ([678f293](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/678f2934052eb5871f1485d53069ce69490a942e))
* pin xmlschema to 2.3.1 for Python compatibility ([00c7458](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/00c7458f6bd32907d1946569d98be68731c5e96b))
* relax xmlschema pin and add python-multipart ([2ba4f8a](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/2ba4f8afd49912730de22b1fa93cf98ab501aa2f))
* run SOC2 workflow on Python 3.11 ([b97c016](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/b97c0163cee4a048f7820fa678cd3adfd236fc78))
* update xmlschema dependency ([3315814](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/3315814fdad4841f7982f87b0fbdf546b8cb9e06))


### Features

* add audit event model and hashing utilities ([092377b](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/092377b04c381983eff900e563f2cb210a189d6f))
* add audit middleware and logging emitter scaffolding ([8a2599e](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/8a2599e8411c8eee61f2155ce9284b67afd24ebb))
* add batch translate endpoint with XML validator options ([eeb7971](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/eeb797120aa9a3d64fb40c78c99d8761bc2c0f06))
* add event idempotency metadata and Kafka headers ([6f211fe](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/6f211fe99c4b1fdb0ea5064c1cb39869b7e9fba9))
* add Kafka audit emitter scaffolding ([7909f57](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/7909f57624514ebb1e119f589f430e1030cee8f1))
* add manifest builder for audit archive integrity ([a6a53b0](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/a6a53b0a6699747ca9eb0684b91fff421cfe5075))
* add signer abstraction with KMS integration ([7881825](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/7881825b4336e409e22097df213da3eb21f3bffb))
* **audit:** add durable audit middleware + schema reconcile ([ec206be](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/ec206be5ec5d287f7ca4e138b29e012142cca0bf))
* capture created_by in audit manifest and document layout ([04009a1](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/04009a16f25c9c79dddf25d6b466780b20f042ee))
* **idempotency:** add table, alembic setup, and TTL cleanup script ([ebd0d76](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/ebd0d764a175d3c1b8e2e9c58316c29a221a10c7))
* **idempotency:** add table, alembic setup, and TTL cleanup script+onboarding-ci.yml ([e6f2f70](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/e6f2f7096df4873bf8002570ec8d214c7de73fd6))
* include tenant_uuid on audit events ([77b9671](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/77b9671bbe6f1f9a6be84a092149b6e87ca98606))
* **onboarding:** initial FastAPI service scaffold with DB integration ([8fc9fc5](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/8fc9fc5bc6f39dea59389656ec4ebc38f43b7550))

# 1.0.0-beta.1 (2025-11-05)


### Bug Fixes

* align test client dependencies and clarify xsd skip message ([d425b60](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/d425b60a6ee6916f207437fc9f7de5a0907a0317))
* correct commit message format ([678f293](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/678f2934052eb5871f1485d53069ce69490a942e))
* pin xmlschema to 2.3.1 for Python compatibility ([00c7458](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/00c7458f6bd32907d1946569d98be68731c5e96b))
* relax xmlschema pin and add python-multipart ([2ba4f8a](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/2ba4f8afd49912730de22b1fa93cf98ab501aa2f))
* run SOC2 workflow on Python 3.11 ([b97c016](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/b97c0163cee4a048f7820fa678cd3adfd236fc78))
* update xmlschema dependency ([3315814](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/3315814fdad4841f7982f87b0fbdf546b8cb9e06))


### Features

* add audit event model and hashing utilities ([092377b](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/092377b04c381983eff900e563f2cb210a189d6f))
* add audit middleware and logging emitter scaffolding ([8a2599e](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/8a2599e8411c8eee61f2155ce9284b67afd24ebb))
* add batch translate endpoint with XML validator options ([eeb7971](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/eeb797120aa9a3d64fb40c78c99d8761bc2c0f06))
* add event idempotency metadata and Kafka headers ([6f211fe](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/6f211fe99c4b1fdb0ea5064c1cb39869b7e9fba9))
* add Kafka audit emitter scaffolding ([7909f57](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/7909f57624514ebb1e119f589f430e1030cee8f1))
* add manifest builder for audit archive integrity ([a6a53b0](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/a6a53b0a6699747ca9eb0684b91fff421cfe5075))
* add signer abstraction with KMS integration ([7881825](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/7881825b4336e409e22097df213da3eb21f3bffb))
* **audit:** add durable audit middleware + schema reconcile ([ec206be](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/ec206be5ec5d287f7ca4e138b29e012142cca0bf))
* capture created_by in audit manifest and document layout ([04009a1](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/04009a16f25c9c79dddf25d6b466780b20f042ee))
* **idempotency:** add table, alembic setup, and TTL cleanup script ([ebd0d76](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/ebd0d764a175d3c1b8e2e9c58316c29a221a10c7))
* **idempotency:** add table, alembic setup, and TTL cleanup script+onboarding-ci.yml ([e6f2f70](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/e6f2f7096df4873bf8002570ec8d214c7de73fd6))
* include tenant_uuid on audit events ([77b9671](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/77b9671bbe6f1f9a6be84a092149b6e87ca98606))
* **onboarding:** initial FastAPI service scaffold with DB integration ([8fc9fc5](https://github.com/sonimanish0604/aegissolutionsSaaS/commit/8fc9fc5bc6f39dea59389656ec4ebc38f43b7550))

# Changelog

All notable changes to this project will be documented in this file.

This document is managed by semantic-release; do not edit entries manually.
