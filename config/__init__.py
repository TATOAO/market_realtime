import os

enable_auto_save_news = True 
db_location = os.environ.get('NEWS_DB_LOCATION', 'database/local/market_data.db')

db_location = os.environ.get('NEWS_DB_LOCATION', 'database/local/market_data.db')

# Check if the location is a directory and create it if it doesn't exist
if os.path.isdir(db_location):
    if not os.path.exists(db_location):
        os.makedirs(db_location)
    db_location = os.path.join(db_location, 'database.db')
else:
    # If it's not a directory, treat it as a file
    db_dir = os.path.dirname(db_location)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

