# This is the tinder
This application requests user's data on VK (via protocol oauth).
Then, based on the data that goes into the application, the Tinder will select the right partner for you. 
The selection is based on the analysis of the VK profile (common interests, common music, mutual friends, etc.)
## Setup
* before starting you need install requirements
```bash
$ pip install -r requirements.txt
```
* To run tests, you just need to activate the “tests/tests.py” file. You must add data for tests 
to the file "tests/date.txt". The data substitution pattern is listed in the file itself.

* requirements for database: you should have a database
( in this repository it is called "tinderdb"), role of database 
(in this repository you role is called "tinderuser"). 
You can change any param in "config/config_app"
In config this params are called like "DB_NAME" and "DB_USER"
* For running the app, you need to run the "main.py"
## Example
```bash
$ python main.py
```
and follow the next prompts
```text
1.Follow this link: https://oauth.vk.com/authorize?client_id=5490057&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=friends,photos,groups,pages&response_type=token&v=5.52
2.Confirm the intentions
3.Copy the address of the browser string and paste it here, please: 
 ```
Next step is to enter the token from a browser search line to the dialog: 
```text
3. ... and paste it here, please: https://oauth.vk.com/blank.html#access_token=your token here
```

Next step is following the prompts
```text
There are search settings save only for session
Give number for desired min of search age: your input here
Give number for desired max of search age: your input here
```

And next you will see the result of the app
```text
1.Natalya Bochkareva, vk:https://vk.com/id450257690, photos: ...
2.Alexander Polyarny, vk:https://vk.com/id258482625, photos:...
...
```
