from django.conf import settings
from datetime import timedelta

APPLICATION_NAME = 'twitter_wrapper'

# Authentication information
CONSUMER_KEY = 'Jqyp0B96jFxpQfPaYlQKHzYAi'
CONSUMER_SECRET = 'WNvjYzU0m0EntJCwOEUd7ZSt33c2eQNuck1uMfqVJrKBTUuO5p'

# Twitter API delay
RATE_LIMIT_DELAY = timedelta(minutes = 15)

# Amount of time the information in our base is considered up-to-date
UPDATE_INTERVAL = timedelta(minutes = 5)
