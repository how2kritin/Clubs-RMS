"""
Queries fetching club data as defined at
https://github.com/Clubs-Council-IIITH/web/blob/master/src/gql/queries/clubs.jsx
"""

GET_ACTIVE_CLUBS = """
  query ActiveClubs {
    activeClubs {
      _id
      cid
      state
      category
      logo
      banner
      bannerSquare
      name
      tagline
    }
  }
"""


GET_ALL_CLUBS = """
  query AllClubs {
    allClubs {
      _id
      cid
      code
      state
      category
      logo
      bannerSquare
      name
      email
      tagline
    }
  }
"""


GET_ALL_CLUB_IDS = """
  query AllClubs {
    allClubs {
      _id
      cid
      name
    }
  }
"""


GET_ACTIVE_CLUB_IDS = """
  query ActiveClubs {
    activeClubs {
      _id
      cid
      name
    }
  }
"""


GET_CLUB = """
  query Club($clubInput: SimpleClubInput!) {
    club(clubInput: $clubInput) {
      _id
      cid
      code
      logo
      banner
      bannerSquare
      category
      description
      email
      name
      socials {
        website
        instagram
        facebook
        youtube
        twitter
        linkedin
        discord
        whatsapp
        otherLinks
      }
      state
      tagline
    }
  }
"""


GET_MEMBERSHIPS = """
  query MemberRoles($uid: String!) {
    memberRoles(uid: $uid) {
      _id
      cid
      poc
      roles {
        startYear
        deleted
        name
        rid
        endYear
      }
    }
  }
"""
