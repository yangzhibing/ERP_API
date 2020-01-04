from flask_script import Manager, Server
from webapp import app

manager = Manager(app)
manager.add_command("server", Server(host='0.0.0.0'))


def make_shell_context():
    return dict(app=app)


if __name__ == '__main__':
    manager.run()
