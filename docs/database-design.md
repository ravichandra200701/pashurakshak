DATABASE DESIGN
1. Users

Purpose:

Stores application accounts.

users
------------------------------------------------
id                  UUID / primary key
name                VARCHAR
phone               VARCHAR / unique
email               VARCHAR / nullable
password_hash       VARCHAR
role                ENUM
created_at          TIMESTAMP
updated_at          TIMESTAMP

Roles:

FARMER
PASHU_SAKHI
VETERINARIAN
ADMIN

Relationship:

User
  │
  └── Owner
2. Owners

Purpose:

Represents livestock ownership information.

owners
------------------------------------------------
id                  UUID / primary key
user_id             UUID / FK → users.id
name                VARCHAR
phone               VARCHAR
address             TEXT
village_id          UUID / FK → villages.id
created_at          TIMESTAMP
updated_at          TIMESTAMP

Relationship:

User
  │
  └── Owner
        │
        └── Animals
3. Villages

Purpose:

Geographic administrative location for livestock and disease surveillance.

villages
------------------------------------------------
id                  UUID / primary key
name                VARCHAR
district             VARCHAR
state                VARCHAR
latitude             DECIMAL
longitude            DECIMAL
created_at          TIMESTAMP
updated_at          TIMESTAMP

This will later help the outbreak/GIS layer.

4. Animals

Purpose:

Stores livestock information.

animals
------------------------------------------------
id                  UUID / primary key
pashu_aadhaar_id    VARCHAR / nullable / unique
owner_id            UUID / FK → owners.id
village_id          UUID / FK → villages.id
species             VARCHAR
breed               VARCHAR / nullable
sex                 VARCHAR
date_of_birth       DATE / nullable
created_at          TIMESTAMP
updated_at          TIMESTAMP

Example:

species = cattle
breed = Jersey
sex = female

pashu_aadhaar_id should be treated as an integration-ready external identifier rather than inventing another competing animal identity system.

5. Vaccinations

Purpose:

Stores vaccination history for each animal.

vaccinations
------------------------------------------------
id                  UUID / primary key
animal_id           UUID / FK → animals.id
vaccine_name        VARCHAR
vaccination_date    DATE
next_due_date       DATE / nullable
administered_by     UUID / FK → users.id / nullable
notes               TEXT / nullable
created_at          TIMESTAMP

Relationship:

Animal
  │
  └── Vaccinations
6. Disease Reports

This is one of the most important tables.

Purpose:

Stores a possible disease report submitted by a user.

disease_reports
------------------------------------------------
id                  UUID / primary key
animal_id           UUID / FK → animals.id
reported_by         UUID / FK → users.id
symptoms            TEXT
temperature         DECIMAL / nullable
image_path          TEXT / nullable
latitude            DECIMAL / nullable
longitude           DECIMAL / nullable
status              VARCHAR
created_at          TIMESTAMP
updated_at          TIMESTAMP

Example:

animal_id = animal-123
reported_by = user-456
symptoms = "fever, skin nodules"
temperature = 103.2
image_path = "/uploads/report-123.jpg"
status = PENDING_AI
7. AI Predictions

Purpose:

Stores AI-assisted visual/risk predictions separately from the original report.

ai_predictions
------------------------------------------------
id                  UUID / primary key
report_id           UUID / FK → disease_reports.id
model_name          VARCHAR
model_version       VARCHAR
predicted_disease   VARCHAR
confidence          DECIMAL
probabilities       JSONB / nullable
created_at          TIMESTAMP

Example:

model_name = MobileNetV3
model_version = 1.0
predicted_disease = LSD
confidence = 0.87

This gives us model traceability.

8. Cases

Purpose:

Converts a disease report into a veterinary workflow case.

cases
------------------------------------------------
id                  UUID / primary key
report_id           UUID / FK → disease_reports.id
status              VARCHAR
priority            VARCHAR
assigned_vet        UUID / FK → users.id / nullable
assigned_worker     UUID / FK → users.id / nullable
created_at          TIMESTAMP
updated_at          TIMESTAMP

Statuses:

PENDING_AI
PENDING_VET
UNDER_REVIEW
FIELD_VISIT
CONFIRMED
REJECTED
RESOLVED

Priority:

LOW
MEDIUM
HIGH
CRITICAL
9. Field Visits

Purpose:

Records physical veterinary/field-worker visits.

field_visits
------------------------------------------------
id                      UUID / primary key
case_id                 UUID / FK → cases.id
visited_by              UUID / FK → users.id
visit_date              TIMESTAMP
temperature             DECIMAL / nullable
notes                   TEXT / nullable
isolation_required      BOOLEAN
sample_required         BOOLEAN
created_at              TIMESTAMP

Workflow:

AI
 ↓
Veterinarian
 ↓
Case
 ↓
Field Visit
10. Samples

Purpose:

Tracks samples collected for laboratory confirmation.

samples
------------------------------------------------
id                  UUID / primary key
case_id             UUID / FK → cases.id
sample_type         VARCHAR
collected_by        UUID / FK → users.id
collection_date     TIMESTAMP
lab_name            VARCHAR / nullable
lab_reference       VARCHAR / nullable
result              VARCHAR / nullable
status              VARCHAR
created_at          TIMESTAMP
updated_at          TIMESTAMP

Possible statuses:

COLLECTED
SENT_TO_LAB
PROCESSING
COMPLETED
REJECTED

This is important because:

AI prediction ≠ final diagnosis

Veterinary/laboratory confirmation remains part of the workflow.

11. Alerts

Purpose:

Stores notifications generated by the system.

alerts
------------------------------------------------
id                  UUID / primary key
user_id             UUID / FK → users.id
type                VARCHAR
title               VARCHAR
message             TEXT
severity            VARCHAR
is_read             BOOLEAN
created_at          TIMESTAMP

Types:

HIGH_RISK
CLUSTER
VET_REVIEW
FIELD_VISIT
VACCINATION
SYSTEM
12. Clusters

Purpose:

Represents detected geographic disease clusters.

clusters
------------------------------------------------
id                  UUID / primary key
name                VARCHAR
disease             VARCHAR
latitude            DECIMAL
longitude           DECIMAL
case_count          INTEGER
risk_level          VARCHAR
status              VARCHAR
created_at          TIMESTAMP
updated_at          TIMESTAMP

Possible:

ACTIVE
RESOLVED
MONITORING
13. Sync Queue

Purpose:

Supports offline-first field operations.

sync_queue
------------------------------------------------
id                  UUID / primary key
device_id           VARCHAR
operation            VARCHAR
entity_type          VARCHAR
local_id             VARCHAR
payload              JSONB
status               VARCHAR
created_at           TIMESTAMP
synced_at            TIMESTAMP / nullable

Example:

device_id = SAKHI-001
operation = CREATE
entity_type = disease_report
local_id = LOCAL-123
status = PENDING

Flow:

Mobile
  ↓
Local storage
  ↓
Sync Queue
  ↓
FastAPI
  ↓
PostgreSQL
14. Audit Logs

Purpose:

Tracks important actions for accountability and security.

audit_logs
------------------------------------------------
id                  UUID / primary key
user_id             UUID / FK → users.id / nullable
action              VARCHAR
entity_type         VARCHAR
entity_id           UUID / nullable
metadata            JSONB / nullable
timestamp           TIMESTAMP

Example:

action = CONFIRM_CASE
entity_type = CASE
entity_id = case-123

## Relationships

| Parent | Child | Relationship | Foreign Key |
|---|---|---|---|
| users | owners | One-to-one | owners.user_id |
| villages | owners | One-to-many | owners.village_id |
| owners | animals | One-to-many | animals.owner_id |
| villages | animals | One-to-many | animals.village_id |
| animals | vaccinations | One-to-many | vaccinations.animal_id |
| animals | disease_reports | One-to-many | disease_reports.animal_id |
| users | disease_reports | One-to-many | disease_reports.reported_by |
| disease_reports | ai_predictions | One-to-many | ai_predictions.report_id |
| disease_reports | cases | One-to-one/current case | cases.report_id |
| users | cases | One-to-many as veterinarian | cases.assigned_vet |
| users | cases | One-to-many as field worker | cases.assigned_worker |
| cases | field_visits | One-to-many | field_visits.case_id |
| users | field_visits | One-to-many | field_visits.visited_by |
| cases | samples | One-to-many | samples.case_id |
| users | samples | One-to-many | samples.collected_by |
| users | alerts | One-to-many | alerts.user_id |
| cases | alerts | One-to-many/optional | alerts.case_id |
| clusters | alerts | One-to-many/optional | alerts.cluster_id |
| users | audit_logs | One-to-many | audit_logs.user_id |