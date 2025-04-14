from typing import Optional, Dict
from utils.graphql.client import query_graphql
import utils.graphql.queries.members as member_queries


def get_members(cid: str, headers: Optional[Dict] = None):
    variables = {"clubInput": {"cid": cid}}
    return query_graphql(
        member_queries.GET_MEMBERS,
        variables=variables,
        headers=headers,
    )


def get_current_members(cid: str, headers: Optional[Dict] = None):
    variables = {"clubInput": {"cid": cid}}
    return query_graphql(
        member_queries.GET_CURRENT_MEMBERS,
        variables=variables,
        headers=headers,
    )


# TODO: do we need this?
def download_members_data(details: dict, headers: Optional[Dict] = None):
    # details should match the MemberInputDataReportDetails structure.
    return query_graphql(
        member_queries.DOWNLOAD_MEMBERS_DATA,
        variables={"details": details},
        headers=headers,
    )


# TODO: remove this later
if __name__ == "__main__":
    import pprint

    pp = pprint.PrettyPrinter(indent=2)

    print("🔍 Testing get_members()")
    pp.pprint(get_members("roboticsclub"))

    print("\n🔍 Testing get_current_members()")
    pp.pprint(get_current_members("roboticsclub"))

    # TODO: idk what to pass
    print("\n🔍 Testing download_members_data()")
    pp.pprint(download_members_data({"example": "data"}))
