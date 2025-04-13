"""
Queries fetching club member data as defined at
https://github.com/Clubs-Council-IIITH/web/blob/master/src/gql/queries/members.jsx
"""

GET_MEMBERS = """
  query Members($clubInput: SimpleClubInput!) {
    members(clubInput: $clubInput) {
      _id
      cid
      uid
      poc
      roles {
        name
        startYear
        endYear
        approved
        rejected
        deleted
      }
    }
  }
"""


GET_CURRENT_MEMBERS = """
  query CurrentMembers($clubInput: SimpleClubInput!) {
    currentMembers(clubInput: $clubInput) {
      _id
      cid
      uid
      poc
      roles {
        name
        startYear
        endYear
        approved
        rejected
        deleted
      }
    }
  }
"""


GET_PENDING_MEMBERS = """
  query PendingMembers {
    pendingMembers {
      _id
      cid
      uid
      poc
      roles {
        rid
        name
        startYear
        endYear
        approved
        rejected
        deleted
      }
    }
  }
"""


GET_MEMBER = """
  query Member($memberInput: SimpleMemberInput!, $userInput: UserInput!) {
    member(memberInput: $memberInput) {
      _id
      uid
      cid
      poc
      roles {
        startYear
        rid
        name
        endYear
        deleted
        approved
        approvalTime
        rejected
        rejectionTime
      }
      creationTime
      lastEditedTime
    }
    userProfile(userInput: $userInput) {
      firstName
      lastName
      gender
      email
    }
    userMeta(userInput: $userInput) {
      img
    }
  }
"""


DOWNLOAD_MEMBERS_DATA = """
  query DownloadMembersData($details: MemberInputDataReportDetails!) {
    downloadMembersData(details: $details) {
      csvFile
    }
  }
"""
