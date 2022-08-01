## Restaurant Menu Voting API

Run `docker-compose up` to run the project

### Features
- Authentication
POST `http://127.0.0.1:8000//register`

POST `http://127.0.0.1:8000//login`
- Creating restaurant
POST `http://127.0.0.1:8000/create-restaurant`
- Uploading menu for restaurant (There should be a menu for each day)
POST `http://127.0.0.1:8000/create-menu`
- Creating employee
- Getting current day menu
GET `http://127.0.0.1:8000/menus`
- Voting for restaurant menu (Old version api accepted one menu, New one accepts top three menus with respective points (1 to 3)
POST `http://127.0.0.1:8000/vote`
- Getting results for current day
GET `http://127.0.0.1:8000/result`

#### pyrankvote library to get top menu
https://pypi.org/project/pyrankvote/
