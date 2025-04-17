"""
Queries to post club members data as defined at
https://github.com/Clubs-Council-IIITH/web/blob/master/src/gql/mutations/members.jsx
"""

CREATE_MEMBER = """
  mutation CreateMember($memberInput: FullMemberInput!) {
    createMember(memberInput: $memberInput) {
      _id
    }
  }
"""

EDIT_MEMBER = """
  mutation EditMember($memberInput: FullMemberInput!) {
    editMember(memberInput: $memberInput) {
      _id
    }
  }
"""

DELETE_MEMBER = """
  mutation DeleteMember($memberInput: SimpleMemberInput!) {
    deleteMember(memberInput: $memberInput) {
      _id
    }
  }
"""
