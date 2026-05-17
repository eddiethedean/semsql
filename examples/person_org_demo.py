"""Read Person / Organization rows through OntoSQL 0.2 semantic session."""

from __future__ import annotations

from sqlmodel import Session, SQLModel, create_engine

from ontosql import OntoSession
from tests.models import OrgRow, OrganizationMap, Person, PersonMap, PersonRow


def main() -> None:
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as raw:
        raw.add(OrgRow(id=10, name="Analytical Engines Inc."))
        raw.add(PersonRow(id=1, name="Ada Lovelace", org_id=10))
        raw.commit()

    with OntoSession(engine, maps=[PersonMap, OrganizationMap]) as session:
        ada = session.get(Person, id=1)
        assert ada is not None
        print(f"{ada.name} works for {ada.employer.name if ada.employer else 'nobody'}")

        for person in session.find(Person, where=Person.name.startswith("A")):
            print(person.model_dump())


if __name__ == "__main__":
    main()
