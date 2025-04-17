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


DOWNLOAD_MEMBERS_DATA = """
  query DownloadMembersData($details: MemberInputDataReportDetails!) {
    downloadMembersData(details: $details) {
      csvFile
    }
  }
"""
