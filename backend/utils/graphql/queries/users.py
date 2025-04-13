"""
Queries fetching user data as defined at
https://github.com/Clubs-Council-IIITH/web/blob/master/src/gql/queries/users.jsx
"""

GET_USER_PROFILE = """
  query GetUserProfile($userInput: UserInput!) {
    userProfile(userInput: $userInput) {
      firstName
      lastName
      email
      gender
      batch
      stream
      rollno
    }
    userMeta(userInput: $userInput) {
      uid
      img
      role
      phone
    }
  }
"""


GET_USER_LIST_BY_ROLE = """
  query GetUserListByRole($role: String!) {
    usersByRole(role: $role) {
      uid
      role
    }
  }
"""
