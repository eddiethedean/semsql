# OntoSQL

**Semantic data access for SQL** — map ontology-shaped models onto real database schemas and write CRUD in Python, not RDF.

> **Documentation describes 0.2.0 (in development).** [0.1.0 is deprecated](https://github.com/eddiethedean/ontosql/blob/main/docs/DEPRECATED-0.1.md) and unsupported. Implementation is in progress on `main`; the tree may still contain 0.1 code until the rewrite lands.

Real databases are not one table per ontology class. OntoSQL separates **physical** SQLModel tables from **semantic** Pydantic entities and connects them with an explicit **mapper**. Application code uses semantic types; OntoSQL compiles SQL on the backend.

```bash
pip install ontosql
pip install "ontosql[fastapi]"   # optional API helpers
```

## Quick start

### 1. Physical models (database truth)

```python
from sqlmodel import Field, SQLModel


class OrgRow(SQLModel, table=True):
    __tablename__ = "orgs"
    id: int | None = Field(default=None, primary_key=True)
    name: str


class PersonRow(SQLModel, table=True):
    __tablename__ = "people"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    org_id: int | None = Field(default=None, foreign_key="orgs.id")
```

### 2. Semantic models (what your app uses)

```python
from ontosql import OntoModel, onto_property


class Organization(OntoModel):
    type_iri = "schema:Organization"
    iri_template = "https://data.example.org/org/{id}"

    id: int
    name: str = onto_property("schema:name")


class Person(OntoModel):
    type_iri = "schema:Person"
    iri_template = "https://data.example.org/person/{id}"

    id: int
    name: str = onto_property("schema:name")
    employer: Organization | None = onto_property("schema:worksFor")
```

### 3. Maps (explicit SQL bindings)

```python
from ontosql import Map, OntoMapper


class OrganizationMap(OntoMapper[Organization]):
    entity = Organization
    id = Map(OrgRow.id)
    name = Map(OrgRow.name, property="schema:name")


class PersonMap(OntoMapper[Person]):
    entity = Person
    id = Map(PersonRow.id)
    name = Map(PersonRow.name, property="schema:name")
    employer = Map.nested(
        Organization,
        join=(PersonRow.org_id == OrgRow.id),
        target=OrgRow,
        nested_map=OrganizationMap,
        property="schema:worksFor",
    )
```

### 4. Session (CRUD)

```python
from ontosql import OntoSession

# Target API (0.2.0) — read path first; write path in 0.2.x / 0.3
async with OntoSession(engine, maps=[PersonMap, OrganizationMap]) as session:
    ada = await session.get(Person, id=1)
    team = await session.find(Person, where=Person.name.startswith("A"), limit=20)
    # await session.save(ada)  # planned: nested save policies
```

### 5. Export (same mapping metadata)

```python
# Target API (0.2.0) — derived from semantic instance + map, not table rows
doc = ada.to_jsonld()
ttl = ada.to_rdf(format="turtle")
```

## Features (0.2.0)

- **OntoModel** + **onto_property** — semantic entities with ontology IRIs
- **OntoMapper** / **Map** — declarative bindings to columns, joins, and nested entities
- **OntoSession** — `get`, `find`, `save`, `delete` compiled to SQL
- **Semantic queries** — filter and order on mapped fields
- **PrefixRegistry** — CURIE expansion and JSON-LD `@context`
- **Export** — JSON-LD and RDF from semantic instances via mapper metadata
- **FastAPI** (`ontosql[fastapi]`) — content negotiation for semantic responses

## FastAPI

```python
from fastapi import FastAPI, Depends, Request
from ontosql.fastapi import negotiate_onto_response

app = FastAPI()

@app.get("/person/{person_id}")
async def get_person(person_id: int, request: Request, session: OntoSession = Depends(...)):
    person = await session.get(Person, id=person_id)
    return negotiate_onto_response(request, person)
```

> **Note:** [examples/fastapi_demo.py](https://github.com/eddiethedean/ontosql/blob/main/examples/fastapi_demo.py) still demonstrates the removed 0.1 API. It will be replaced when 0.2 ships.

## Documentation

- [Architecture](https://github.com/eddiethedean/ontosql/blob/main/docs/ARCHITECTURE.md)
- [Technical specification](https://github.com/eddiethedean/ontosql/blob/main/docs/SPECS.md)
- [Roadmap](https://github.com/eddiethedean/ontosql/blob/main/docs/ROADMAP.md)
- [Project plan](https://github.com/eddiethedean/ontosql/blob/main/docs/PLAN.md)
- [Dependency assessment](https://github.com/eddiethedean/ontosql/blob/main/docs/DEPS.md)
- [Deprecated 0.1.0](https://github.com/eddiethedean/ontosql/blob/main/docs/DEPRECATED-0.1.md)
- [Changelog](https://github.com/eddiethedean/ontosql/blob/main/CHANGELOG.md)

## Development

See [Releasing](https://github.com/eddiethedean/ontosql/blob/main/docs/RELEASING.md) for the version publish checklist.

```bash
pip install -e ".[dev]"
ruff check src tests
ruff format src tests
ty check
pytest --cov=ontosql --cov-fail-under=100
```

CI and coverage currently apply to the existing package layout until the 0.2 implementation replaces it.

## License

MIT — see [LICENSE](https://github.com/eddiethedean/ontosql/blob/main/LICENSE).
