"""
Some users functionality copied over from
https://github.com/IMS-IIITH/backend/blob/master/routers/users_router.py,
courtesy of https://github.com/bhavberi
"""
from cas import CASClient
from fastapi import HTTPException, Response, status

from utils.auth_utils import create_access_token
from utils.ldap_utils import authenticate_user

async def user_login_cas(response: Response, ticket: str, cas_client: CASClient):
    if ticket:
        user, attributes, pgtiou = cas_client.verify_ticket(ticket)
        if user:
            roll = attributes['RollNo']
            email = attributes['E-Mail']
            first_name = attributes['FirstName']
            last_name = attributes['LastName']
            uid = attributes['uid']
            print(roll, email, first_name, last_name, uid)
            # batch = get_batch(roll)
        #     cursor = conn.cursor()
        #     try:
        #         cursor.execute('''
        #                                 SELECT * FROM Login WHERE Uid = ?
        #                                 ''', (uid,))
        #         entry = cursor.fetchone()
        #         conn.commit()
        #         if entry:
        #             fernet = Fernet(key)
        #             token = fernet.encrypt(uid.encode())
        #             session['token'] = token
        #             return redirect(f'{SUBPATH}/upcomingTravels')
        #         else:
        #             message = 'User not found! Please Sign Up.'
        #             return render_template('SignUp.html', roll=roll, email=email, first_name=first_name,
        #                                    last_name=last_name, uid=uid, message=message, subpath=SUBPATH)
        #     except:
        #         message = 'Error with database. Please try again'
        #         return render_template('LogIn.html', message=message, subpath=SUBPATH)
        # else:
        #     message = 'Error with CAS. Please try again'
        #     return render_template('LogIn.html', message=message, subpath=SUBPATH)

    return {"message": "Logged in successfully"}


async def user_logout(response: Response, current_user):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not Logged In!")
    response.delete_cookie("access_token_RMS")
    return {"message": "Logged Out Successfully"}


async def user_extend_cookie(response, username, email):
    # Extend the access token/expiry time
    new_access_token = create_access_token(data={"username": username, "email": email})
    response.set_cookie(key="access_token_RMS", value=new_access_token, httponly=True)
    return {"message": "Cookie Extended Successfully"}
