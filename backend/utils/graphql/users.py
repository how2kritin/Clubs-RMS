from typing import Optional, Dict
from utils.graphql.client import query_graphql
import utils.graphql.queries.users as user_queries


def get_user_profile(uid: str, headers: Optional[Dict] = None):
    variables = {"userInput": {"uid": uid}}
    return query_graphql(
        user_queries.GET_USER_PROFILE,
        variables=variables,
        headers=headers,
    )


def get_user_list_by_role(role: str, headers: Optional[Dict] = None):
    variables = {"role": role}
    return query_graphql(
        user_queries.GET_USER_LIST_BY_ROLE,
        variables=variables,
        headers=headers,
    )


# TODO: remove this later
if __name__ == "__main__":
    import pprint

    pp = pprint.PrettyPrinter(indent=2)

    print("🔍 Testing get_user_profile()")
    pp.pprint(get_user_profile("samyak.mishra"))

    print("\n🔍 Testing get_user_list_by_role()")
    pp.pprint(get_user_list_by_role("slc"))
