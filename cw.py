import watchtower, flask, logging

logging.basicConfig(level=logging.INFO)
app = flask.Flask("loggable")
handler = watchtower.CloudWatchLogHandler()
my_session = boto3.Session(region_name = 'us-west-2')
handler._get_session(my_session)
app.logger.addHandler(handler)
logging.getLogger("werkzeug").addHandler(handler)

from watchtower import
@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()