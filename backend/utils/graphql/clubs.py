from typing import Optional, Dict
from utils.graphql.client import query_graphql
import utils.graphql.queries.clubs as club_queries


def get_active_clubs(headers: Optional[Dict] = None):
    return query_graphql(
        club_queries.GET_ACTIVE_CLUBS,
        headers=headers,
    )


def get_all_clubs(headers: Optional[Dict] = None):
    return query_graphql(
        club_queries.GET_ALL_CLUBS,
        headers=headers,
    )


def get_all_club_ids(headers: Optional[Dict] = None):
    return query_graphql(
        club_queries.GET_ALL_CLUB_IDS,
        headers=headers,
    )


def get_active_club_ids(headers: Optional[Dict] = None):
    return query_graphql(
        club_queries.GET_ACTIVE_CLUB_IDS,
        headers=headers,
    )


def get_club(cid: str, headers: Optional[Dict] = None):
    variables = {"clubInput": {"cid": cid}}
    return query_graphql(
        club_queries.GET_CLUB,
        variables=variables,
        headers=headers,
    )


def get_memberships(uid: str, headers: Optional[Dict] = None):
    return query_graphql(
        club_queries.GET_MEMBERSHIPS,
        variables={"uid": uid},
        headers=headers,
    )


# TODO: remove this later
if __name__ == "__main__":
    import pprint

    pp = pprint.PrettyPrinter(indent=2)

    print("🔍 Testing get_active_clubs()")
    pp.pprint(get_active_clubs())

    print("\n🔍 Testing get_all_clubs()")
    pp.pprint(get_all_clubs())

    print("\n🔍 Testing get_all_club_ids()")
    pp.pprint(get_all_club_ids())

    print("\n🔍 Testing get_active_club_ids()")
    pp.pprint(get_active_club_ids())

    print("\n🔍 Testing get_club() with dummy cid='roboticsclub'")
    pp.pprint(get_club("roboticsclub"))

    print("\n🔍 Testing get_memberships() with dummy uid='samyak.mishra'")
    pp.pprint(get_memberships("samyak.mishra"))
