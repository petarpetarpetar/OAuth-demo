# pacing

The app is in the development stage. 

## How to run it on your machine
#### 1. Virtual enviornment
Like with any other Python project, you should start off by creating a virtual environemnt:
```
python3 -m venv venv
```
And then activate it using:
```
source venv/bin/activate
```
^If you're using Linux!
If you're using Windows, just cd to `venv/Scripts` and run `activate.bat`

#### 2. Installing required libs
Then you should install all the required libraries:
```
pip install -r requirements.txt
```
This will automatically install every library that's in `requirements.txt` file.

#### 3. Running the code
Then simply run the code using:
```
python app.py
```

You should see something like: ![running the code](https://i.imgur.com/Bay6gze.png)

#### 4. Navigation and usage
Then, using your browser of choice, navigate to `http://127.0.0.1:5000/consent`, you should be prompted to log in using your google account and give your consent to the app.

