from datetime import datetime, timezone
from threading import Thread
from time import sleep
from django.shortcuts import redirect, reverse, render
from tweepy import OAuthHandler, API, Cursor, TweepError
from .models import Update, User, Follower
from .settings import *

def add_namespace(wrapped_string):
    return '%s:%s' % (APPLICATION_NAME, wrapped_string)

# {{{ Authorization-related procedures
def check_authorization(view):

    def authorization_checker(request, *args, **kwargs):
        # If we are not signed in:
        if add_namespace('access_token') not in request.session:
            # propose to sign in
            return render(request, 'redirect_button.html', {
                        'text': "Please, sign into your twitter account:",
                        'button_text': 'Sign in',
                        'destination': add_namespace('sign_in') })
        else:
            return view(request, *args, **kwargs)

    return authorization_checker

def signIn(request):
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET,
            request.build_absolute_uri(reverse(add_namespace('authorization'))))
    
    redirect_url = auth.get_authorization_url()

    request.session[add_namespace('request_token')] = auth.request_token

    return redirect(redirect_url)

def authorization(request):
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

    verifier = request.GET.get('oauth_verifier')

    auth.request_token = request.session[add_namespace('request_token')]
    del request.session[add_namespace('request_token')]

    auth.get_access_token(verifier)

    # Store session information
    user = API(auth).me()
    request.session[add_namespace('user_id')] = user.id
    request.session[add_namespace('user_name')] = user.name
    request.session[add_namespace('access_token')] = \
            (auth.access_token, auth.access_token_secret)

    return redirect(add_namespace('index'))

def logOut(request):
    del request.session[add_namespace('user_id')]
    del request.session[add_namespace('user_name')]
    del request.session[add_namespace('access_token')]

    return redirect(add_namespace('index'))

# }}}

# {{{ DB logic

# Save update timestamp
def log_update(user_id, is_completed):
    Update.objects.update_or_create(user_id = user_id, defaults = {
        'timestamp' : datetime.now(timezone.utc),
        'is_completed': is_completed })


# {{{ Check whether we need a update for the currently logged in user
def is_update_needed(user_id):
    try:
        update = Update.objects.get(user_id = user_id)
    # If the user is not in our DB ...
    except Update.DoesNotExist:
        # ... then update is needed
        return True

    # Get amount of time passed since the last update attempt
    time_passed = datetime.now(timezone.utc) - update.timestamp

    # If the last update attempt happened recently ...
    if time_passed < UPDATE_INTERVAL:
        # ... don't update
        return False
    # If the last attempt older than rate limit delay ...
    elif time_passed > RATE_LIMIT_DELAY:
        # ... then update is either completed (and can be repeated)
        # or failed (and must be restarted)
        return True
    # If the last update is completed ...
    elif update.is_completed:
        # ... than we haven't used rate limit up yet, and can repeat
        return True
    else:
        # ... or we have and can't
        return False
# }}}


def store_follower(user_id, follower):
    obj, _ = User.objects.update_or_create(user_id = follower.id,
            defaults = {
                'screen_name':          follower.screen_name,
                'name':                 follower.name,
                'profile_image_url':    follower.profile_image_url,
                'description':          follower.description,
                'location':             follower.location,
                'followers_count':      follower.followers_count })

    Follower.objects.get_or_create(
            followed_user_id = user_id,
            follower         = obj)


# {{{ Read information from twitter until we finish, encounter an error
# or reach rate limit
def db_read_iteration(followers_cursor, user_id):
    followers_ids = set()

    try:
        for follower in followers_cursor:
            store_follower(user_id, follower)
            followers_ids.add(follower.id)

        is_completed = True

    except TweepError:
        is_completed = False

    log_update(user_id, is_completed)
    return followers_ids, is_completed
# }}}


# Remove those who unfollowed current user since the last update
def remove_unfollowed(user_id, followers_ids):
    # Find out who unfollowed us
    former_follower_ids = { i.follower.user_id for i in \
            Follower.objects.filter(followed_user_id = user_id) }
    unfollowed_ids = former_follower_ids - followers_ids

    # Remove them from followers relation
    for follower_id in unfollowed_ids:
        user = User.objects.get(user_id = follower_id)
        Follower.objects.get(followed_user_id = user_id,
                follower = user).delete()


def update_in_background(followers_cursor, user_id, followers_ids):
    is_completed = False
    while not is_completed:
        sleep(60)
        new_followers_ids, is_completed = \
                db_read_iteration(followers_cursor, user_id)

        followers_ids |= new_followers_ids
        log_update(user_id, is_completed)

    remove_unfollowed(user_id, followers_ids)


def sync_db(user_id, access_token, access_token_secret):
    # Get twitter API
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(access_token, access_token_secret)
    twitter_api = API(auth)

    # Get followers generator from the twitter API
    cursor = Cursor(twitter_api.followers, id = user_id).items()

    # Complete at least one update iteration ...
    followers_ids, is_completed = db_read_iteration(cursor, user_id)
    # ... and if the rate limit hasn't allowed us to get all we wanted ...
    if is_completed:
        remove_unfollowed(user_id, followers_ids)
    else:
        # ... put the rest in background task
        Thread(target = update_in_background,
                args = (cursor, user_id, followers_ids)).start()
# }}}


@check_authorization
def forceUpdate(request):
    user_id = request.session[add_namespace('user_id')]
    sync_db(user_id, *request.session[add_namespace('access_token')])

    return redirect(add_namespace('index'))


# Primary view
@check_authorization
def index(request):
    user_id = request.session[add_namespace('user_id')]
    user_name = request.session[add_namespace('user_name')]

    # Syncronize the DB if required
    if is_update_needed(user_id):
        sync_db(user_id, *request.session[add_namespace('access_token')])

    is_updated = Update.objects.get(user_id = user_id).is_completed

    # Output followers
    followers = [ i.follower for i in \
            Follower.objects.filter(followed_user_id = user_id) ]

    return render(request, "index.html", {
        'user_name': user_name,
        'is_updated': is_updated,
        'followers': followers })


# Output information about a follower of the currently logged in user
@check_authorization
def userData(request, screen_name):
    user_id = request.session[add_namespace('user_id')]

    # If a user with the requested screen_name exists ...
    try:
        follower = User.objects.get(screen_name = screen_name)
        # ... and he's following currently logged in user ...
        if Follower.objects.filter(followed_user_id = user_id,
                follower = follower).exists():
            # ... then output his info
            return render(request, 'user_data.html', {
                'user_data': User.objects.get(screen_name = screen_name) })

    except User.DoesNotExist:
        user_name = request.session[add_namespace('user_name')]
        return render(request, 'redirect_button.html', {
            'text': "%s doesn't have the follower '%s'" % \
                    (user_name, screen_name),
            'button_text': 'Back',
            'destination': add_namespace('index') })


# Searching of a follower of the currently logged in user by screen_name
def search(request):
    follower_name = request.GET.get('screen_name_box', None)
    return redirect(add_namespace('user_data'), screen_name = follower_name)
