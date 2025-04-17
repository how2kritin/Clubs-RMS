from typing import Optional, Dict
from utils.graphql.client import query_graphql
import utils.graphql.queries.members as member_queries
import utils.graphql.mutations.members as member_mutations


# GraphQL queries' APIs
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


# GraphQL mutations' APIs
def create_member(member_input: dict, headers: Optional[Dict] = None):
    return query_graphql(
        member_mutations.CREATE_MEMBER,
        variables={"memberInput": member_input},
        headers=headers,
    )


def edit_member(member_input: dict, headers: Optional[Dict] = None):
    return query_graphql(
        member_mutations.EDIT_MEMBER,
        variables={"memberInput": member_input},
        headers=headers,
    )


def delete_member(uid: str, cid: str, headers: Optional[Dict] = None):
    return query_graphql(
        member_mutations.DELETE_MEMBER,
        variables={"memberInput": {"uid": uid, "cid": cid}},
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

    # TODO: test
    dummy_headers = {"Authorization": "Bearer YOUR_SECRET_TOKEN"}

    dummy_member = {
        "uid": "testuser1",
        "cid": "roboticsclub",
        "poc": False,
        "roles": [
            {
                "name": "Member",
                "startYear": 2023,
                "endYear": 2024,
                "approved": True,
                "rejected": False,
                "deleted": False,
            }
        ],
    }

    print("\n👤 Testing create_member()")
    pp.pprint(create_member(dummy_member, headers=dummy_headers))

    print("\n✏️ Testing edit_member()")
    edited_member = dummy_member.copy()
    edited_member["poc"] = True
    pp.pprint(edit_member(edited_member, headers=dummy_headers))

    print("\n🗑️ Testing delete_member()")
    pp.pprint(delete_member("testuser1", "roboticsclub", headers=dummy_headers))
