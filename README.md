# Yatube Social Network

A social network for bloggers. Allows writing posts and publishing them in separate groups, subscribing to posts, adding and deleting entries, and commenting on them.
Subscriptions to favorite bloggers.

## Installation Instructions
***- Clone the repository:***
```
git clone git@github.com:PashkaVRN/hw05_final.git
```

***- Install and activate the virtual environment:***
- For MacOS/Linux
```
python3 -m venv venv
```
- For Windows
```
python -m venv venv
source venv/bin/activate
source venv/Scripts/activate
```

***- Install dependencies from the requirements.txt file:***
```
pip install -r requirements.txt
```

***- Apply migrations:***
```
python manage.py migrate
```

***- In the folder with the manage.py file, run the command:***
```
python manage.py runserver
```