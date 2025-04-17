import requests

GRAPHQL_ENDPOINT = "https://clubs.iiit.ac.in/graphql"


def query_graphql(query: str, variables: dict = None, headers: dict = None):
    payload = {
        "query": query,
        "variables": variables or {},
    }
    default_headers = {"Content-Type": "application/json"}
    if headers:
        default_headers.update(headers)

    response = requests.post(
        GRAPHQL_ENDPOINT,
        json=payload,
        headers=default_headers,
    )
    response.raise_for_status()
    data = response.json()

    if "errors" in data:
        raise Exception(f"GraphQL Error: {data['errors']}")

    return data["data"]
