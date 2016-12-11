from django.db import models

# Update history
class Update(models.Model):
    # Information about the followers of ...
    user_id             = models.BigIntegerField(primary_key = True)
    # ... has been updated at:
    timestamp           = models.DateTimeField()
    # Whether update has been fully completed or interrupted by
    # the rate limit delay
    is_completed        = models.BooleanField()

# Arbitrary subset of twitter user's fields
class User(models.Model):
    user_id             = models.BigIntegerField(primary_key = True)
    screen_name         = models.CharField(max_length = 256,
                                    unique = True, db_index = True)

    name                = models.CharField(max_length = 256)

    profile_image_url   = models.URLField (max_length = 1024)

    description         = models.TextField()
    location            = models.CharField(max_length = 256)

    followers_count     = models.PositiveIntegerField()

# Information about being followed
class Follower(models.Model):
    # User ...
    followed_user_id    = models.BigIntegerField(db_index = True)
    # ... is followed by:
    follower            = models.ForeignKey(User, on_delete = models.CASCADE)

    class Meta:
        unique_together = ( 'followed_user_id', 'follower' )
        index_together = [ 'followed_user_id', 'follower' ]
