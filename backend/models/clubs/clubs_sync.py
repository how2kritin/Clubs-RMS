import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models.clubs.clubs_model import Club, club_members
from models.users.users_model import User
from utils.graphql.clubs import get_active_clubs, get_club
from utils.graphql.members import get_current_members
from utils.ldap_utils import get_user_by_search_filter

logger = logging.getLogger(__name__)


# fetch the user. create them if they do not exist. If the details are invalid, then return None.
async def get_or_create_user(db: Session, uid: str) -> User | None:
    user = db.query(User).filter(User.uid == uid).first()

    if not user:
        try:
            # get user details from LDAP
            user_details = get_user_by_search_filter(search_filter=f"uid={uid}")
            email = user_details.get('mail', [b''])[0].decode('utf-8') if user_details.get(
                'mail') else f"{uid}@students.iiit.ac.in"
            first_name = user_details.get('givenName', [b''])[0].decode('utf-8') if user_details.get(
                'givenName') else ""
            last_name = user_details.get('sn', [b''])[0].decode('utf-8') if user_details.get('sn') else ""
            roll_number = user_details.get('uidNumber', [b''])[0].decode('utf-8') if user_details.get(
                'uidNumber') else ""

            user = User(uid=uid, email=email, first_name=first_name, last_name=last_name, roll_number=roll_number, )

            db.add(user)
            db.commit()
            db.refresh(user)

        except Exception as e:
            logger.error(f"Error creating user from LDAP data: {e}")
            return None

    return user


# sync from CC APIs to local database.
async def sync_clubs(db: Session):
    try:
        # get all active clubs
        active_clubs_response = get_active_clubs()
        if 'activeClubs' not in active_clubs_response:
            logger.error("Failed to fetch active clubs")
            return

        active_clubs = active_clubs_response['activeClubs']

        for club_info in active_clubs:
            cid = club_info.get('cid')

            # every club MUST have a cid. We are using this as our primary key. Only those clubs are considered valid.
            if not cid:
                logger.warning(f"Club without CID found: {club_info}")
                continue

            # check if club already exists in our database
            existing_club = db.query(Club).filter(Club.cid == cid).first()
            if existing_club:
                logger.info(f"Club {cid} already exists, skipping")
                continue

            # get detailed club information
            club_details_response = get_club(cid)
            if 'club' not in club_details_response:
                logger.warning(f"Failed to fetch details for club {cid}")
                continue

            club_details = club_details_response['club']

            # create new club record
            new_club = Club(cid=cid, name=club_details.get('name', ''), tagline=club_details.get('tagline'),
                            description=club_details.get('description'), category=club_details.get('category'),
                            code=club_details.get('code'), logo=club_details.get('logo'),
                            banner=club_details.get('banner'), banner_square=club_details.get('bannerSquare'),
                            state=club_details.get('state'), email=club_details.get('email'),
                            socials=club_details.get('socials'))

            db.add(new_club)
            db.commit()
            db.refresh(new_club)

            # fetch and link club members
            await sync_club_members(db, new_club)

        logger.info("Clubs sync completed successfully")

    except SQLAlchemyError as e:
        logger.error(f"Database error during clubs sync: {e}")
        db.rollback()
    except Exception as e:
        logger.error(f"Error during clubs sync: {e}")


# sync club members for a specific club
async def sync_club_members(db: Session, club: Club):
    try:
        # get only the current members.
        members_response = get_current_members(club.cid)
        if 'currentMembers' not in members_response:
            logger.warning(f"No members found for club {club.cid}")
            return

        current_members = members_response['currentMembers']

        for member_info in current_members:
            uid = member_info.get('uid')
            if not uid:
                # uid is the primary key in our users table. only those with a uid are valid members.
                continue

            # get or create the user
            user = await get_or_create_user(db, uid)

            # add the member relationship to the club
            if user and user not in club.members:
                club.members.append(user)

                # extract the first role of the member
                roles = member_info.get('roles', [])
                role_name = roles[0].get('name') if roles else None

                # update the many-many association table for club-user linkages.
                if role_name:
                    db.execute(club_members.update().where(
                        (club_members.c.club_id == club.cid) & (club_members.c.user_id == user.uid)).values(
                        role=role_name, is_poc=member_info.get('poc', False)))

        db.commit()
        logger.info(f"Synced {len(current_members)} members for club {club.cid}")

    except SQLAlchemyError as e:
        logger.error(f"Database error during members sync for {club.cid}: {e}")
        db.rollback()
    except Exception as e:
        logger.error(f"Error during members sync for {club.cid}: {e}")
