## About the program

Everyone knows the dating app - Tinder.
The application provides a simple interface for choosing the person you like.
There are now more than 100 million installations on Google Play.

Using data from VK, the service was made a little better than Tinder.
This bot can find a couple using the Vkontakte API according to the parameters you specified, such as gender, status, age, city.
The user will receive the top 3 popular photos from the avatar and the account of those people who met the requirements. Popularity is determined by the number of likes.

Created using Python, SQLAlchemy, PostgreSQL, VK API and PyCharm.

## Instruction manual

1. Get a GroupToken from the site vk.com with access rights groups and APP_ID of the application.

2. GroupToken is located in the settings of the VK group and is necessary for the bot to respond to messages sent to the group. APP_ID is required to allow the bot to authenticate the user using a token and to search for users by the specified parameters.

3. The result will be recorded in the PostgreSQL database. The database will record information about the profile for which we are looking for a couple and all the people found. DB is the name of the data source for your PostgreSQL database (for example, postgresql://admin: admin@localhost: 5432/db).

4. The group_token, user_token and DB data are set in the file keys.py

5. The program is started using a file main.py