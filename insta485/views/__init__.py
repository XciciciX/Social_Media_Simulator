"""Views, one for each Insta485 page."""
from insta485.views.index import show_index, show_image
from insta485.views.user import show_user
from insta485.views.post import show_post
from insta485.views.explore import show_explore
from insta485.views.edit import show_edit
from insta485.views.redirect import *
from insta485.views.login import show_login
from insta485.views.logout import logout
from insta485.views.following import show_following
from insta485.views.followers import followers
from insta485.views.create import create
from insta485.views.delete import delete
from insta485.views.password import show_password
from insta485.views.auth import auth
