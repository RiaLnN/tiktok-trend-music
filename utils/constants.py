"""Small constants that are referenced by multiple modules."""

# The default keyword if the user has not yet specified his own.
DEFAULT_KEYWORD = "trending"

# How many videos to request from the API in one /feed/search call (maximum
# which consistently returns tiktok-scraper7 in one request).
SEARCH_PAGE_SIZE = 30

# We don’t go into endless pagination for one keyword - this is
# and extra money for requests to RapidAPI, and the risk of hitting the rate limit.
MAX_PAGES_PER_KEYWORD = 3

# Presets for inline buttons in /settings.
TRACK_COUNT_OPTIONS = [3, 5, 10, 15]
VIDEOS_PER_TRACK_OPTIONS = [1, 2, 3, 5]

# Telegram limits callback_data to 64 bytes. Keyword hits
# in callback_data there are delete buttons ("stg:remove_keyword:<word>"), and the Cyrillic
# in UTF-8 it takes 2 bytes per character - so we limit the length with a margin.
MAX_KEYWORD_LENGTH = 20
