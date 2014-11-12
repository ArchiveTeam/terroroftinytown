# encoding=utf-8
import base64
import calendar
import contextlib
import datetime
import hmac
import json
import os
import random
import subprocess

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.session import make_transient
from sqlalchemy.sql.expression import insert, select, delete
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, Binary, Float, Boolean, Integer, \
    DateTime
from sqlalchemy.sql.type_api import TypeDecorator

from terroroftinytown.tracker.errors import NoItemAvailable, FullClaim, UpdateClient, \
    InvalidClaim
from terroroftinytown.tracker.stats import Stats


# These overrides for major api changes
MIN_VERSION_OVERRIDE = 8  # for terroroftinytown.client
MIN_CLIENT_VERSION_OVERRIDE = 1  # for terrofoftinytown-client-grab/pipeline.py

Base = declarative_base()
Session = sessionmaker()


@contextlib.contextmanager
def new_session():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class JsonType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, engine):
        return json.dumps(value)

    def process_result_value(self, value, engine):
        if value:
            return json.loads(value)
        else:
            return None


class User(Base):
    '''User accounts that manager the tracker.'''
    __tablename__ = 'users'

    username = Column(String, primary_key=True)
    salt = Column(Binary, nullable=False)
    hash = Column(Binary, nullable=False)

    def set_password(self, password):
        self.salt = new_salt()
        self.hash = make_hash(password, self.salt)

    def check_password(self, password):
        test_hash = make_hash(password, self.salt)

        if len(self.hash) != len(test_hash):
            return False

        iterable = [a == b for a, b in zip(self.hash, test_hash)]
        ok = True

        for result in iterable:
            ok &= result

        return ok

    @classmethod
    def no_users_exist(cls):
        with new_session() as session:
            user = session.query(User).first()

            return user is None

    @classmethod
    def is_user_exists(cls, username):
        with new_session() as session:
            user = session.query(User).filter_by(username=username).first()

            return user is not None

    @classmethod
    def all_usernames(cls):
        with new_session() as session:
            users = session.query(User.username)

            return list([user.username for user in users])

    @classmethod
    def save_new_user(cls, username, password):
        with new_session() as session:
            user = User(username=username)
            user.set_password(password)
            session.add(user)

    @classmethod
    def check_account(cls, username, password):
        with new_session() as session:
            user = session.query(User).filter_by(username=username).first()
            if user:
                return user.check_password(password)

    @classmethod
    def update_password(cls, username, password):
        with new_session() as session:
            user = session.query(User).filter_by(username=username).first()
            user.set_password(password)

    @classmethod
    def delete_user(cls, username):
        with new_session() as session:
            session.query(User).filter_by(username=username).delete()


class Project(Base):
    '''Project settings.'''
    __tablename__ = 'projects'

    name = Column(String, primary_key=True)
    min_version = Column(Integer, default=MIN_VERSION_OVERRIDE, nullable=False)
    min_client_version = Column(Integer, default=MIN_CLIENT_VERSION_OVERRIDE, nullable=False)
    alphabet = Column(String, default='0123456789abcdefghijklmnopqrstuvwxyz'
                                      'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                      nullable=False)
    url_template = Column(String, default='http://example.com/{shortcode}',
                          nullable=False)
    request_delay = Column(Float, default=0.5, nullable=False)
    redirect_codes = Column(JsonType, default=[301, 302, 303, 307],
                            nullable=False)
    no_redirect_codes = Column(JsonType, default=[404], nullable=False)
    unavailable_codes = Column(JsonType, default=[200])
    banned_codes = Column(JsonType, default=[403, 420, 429])
    body_regex = Column(String)
    method = Column(String, default='head', nullable=False)

    enabled = Column(Boolean, default=False)
    autoqueue = Column(Boolean, default=False)
    num_count_per_item = Column(Integer, default=50, nullable=False)
    max_num_items = Column(Integer, default=100, nullable=False)
    lower_sequence_num = Column(Integer, default=0, nullable=False)
    autorelease_time = Column(Integer, default=60 * 30)

    def to_dict(self):
        return {
            'name': self.name,
            'min_version': self.min_version,
            'min_client_version': self.min_client_version,
            'alphabet': self.alphabet,
            'url_template': self.url_template,
            'request_delay': self.request_delay,
            'redirect_codes': self.redirect_codes,
            'no_redirect_codes': self.no_redirect_codes,
            'unavailable_codes': self.unavailable_codes,
            'banned_codes': self.banned_codes,
            'body_regex': self.body_regex,
            'method': self.method,
            'enabled': self.enabled,
            'autoqueue': self.autoqueue,
            'num_count_per_item': self.num_count_per_item,
            'max_num_items': self.max_num_items,
            'lower_sequence_num': self.lower_sequence_num,
            'autorelease_time': self.autorelease_time,
        }

    @classmethod
    def all_project_names(cls):
        with new_session() as session:
            projects = session.query(Project.name)

            return list([project.name for project in projects])

    @classmethod
    def all_project_infos(cls):
        with new_session() as session:
            projects = session.query(Project)

            return list([project.to_dict() for project in projects])

    @classmethod
    def new_project(cls, name):
        with new_session() as session:
            project = Project(name=name)
            session.add(project)

    @classmethod
    def get_plain(cls, name):
        with new_session() as session:
            project = session.query(Project).filter_by(name=name).first()

            make_transient(project)
            return project

    @classmethod
    @contextlib.contextmanager
    def get_session_object(cls, name):
        with new_session() as session:
            project = session.query(Project).filter_by(name=name).first()
            yield project

    @classmethod
    def delete_project(cls, name):
        # FIXME: need to cascade the deletes
        with new_session() as session:
            session.query(Project).filter_by(name=name).delete()


class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)

    project_id = Column(Integer, ForeignKey('projects.name'), nullable=False)
    project = relationship('Project')

    lower_sequence_num = Column(Integer, nullable=False)
    upper_sequence_num = Column(Integer, nullable=False)
    datetime_claimed = Column(DateTime)
    tamper_key = Column(String)
    username = Column(String)
    ip_address = Column(String)

    def to_dict(self):
        return {
            'id': self.id,
            'project': self.project.to_dict(),
            'lower_sequence_num': self.lower_sequence_num,
            'upper_sequence_num': self.upper_sequence_num,
            'datetime_claimed': calendar.timegm(self.datetime_claimed.utctimetuple()) if self.datetime_claimed else None,
            'tamper_key': self.tamper_key,
            'username': self.username,
            'ip_address': self.ip_address,
        }

    @classmethod
    def get_items(cls, project_name):
        with new_session() as session:
            rows = session.query(Item).filter_by(project_id=project_name).order_by(Item.datetime_claimed)

            return list([item.to_dict() for item in rows])

    @classmethod
    def add_items(cls, project_name, sequence_list):
        with new_session() as session:
            query = insert(Item)
            query_args = []

            for lower_num, upper_num in sequence_list:
                query_args.append({
                    'project_id': project_name,
                    'lower_sequence_num': lower_num,
                    'upper_sequence_num': upper_num,
                })

            session.execute(query, query_args)

    @classmethod
    def delete(cls, item_id):
        with new_session() as session:
            session.query(Item).filter_by(id=item_id).delete()

    @classmethod
    def release(cls, item_id):
        with new_session() as session:
            item = session.query(Item).filter_by(id=item_id).first()
            item.datetime_claimed = None
            item.ip_address = None
            item.username = None

    @classmethod
    def release_all(cls, project_name=None, old_date=None):
        with new_session() as session:
            query = session.query(Item)

            if project_name:
                query = query.filter_by(project_id=project_name)

            if old_date:
                query = query.filter(Item.datetime_claimed <= old_date)

            query.update({
                'datetime_claimed': None,
                'ip_address': None,
                'username': None,
            })

    @classmethod
    def release_old(cls, project_name=None, autoqueue_only=False):
        with new_session() as session:
            # we could probably write this in one query
            # but it would be non-portable across SQL dialects

            projects = session.query(Project) \
                .filter(Project.autorelease_time > 0)

            if project_name:
                projects = projects.filter_by(name=project_name)

            if autoqueue_only:
                projects = projects.filter_by(autoqueue=True)

            for project in projects:
                min_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=project.autorelease_time)
                query = session.query(Item) \
                    .filter(Item.datetime_claimed <= min_time, Item.project == project)
                query.update({
                    'datetime_claimed': None,
                    'ip_address': None,
                    'username': None,
                })

    @classmethod
    def delete_all(cls, project_name):
        with new_session() as session:
            session.query(Item).filter_by(project_id=project_name).delete()


class BlockedUser(Base):
    '''Blocked IP addresses or usernames.'''
    __tablename__ = 'blocked_users'

    username = Column(String, primary_key=True)
    note = Column(String)

    @classmethod
    def block_username(cls, username, note=None):
        with new_session() as session:
            session.add(BlockedUser(username=username, note=note))

    @classmethod
    def unblock_username(cls, username):
        with new_session() as session:
            session.query(BlockedUser).filter_by(username=username).delete()

    @classmethod
    def is_username_blocked(cls, *username):
        with new_session() as session:
            query = select([BlockedUser.username])\
                .where(BlockedUser.username.in_(username))

            result = session.execute(query).first()

            if result:
                return True

    @classmethod
    def all_blocked_usernames(cls):
        with new_session() as session:
            names = session.query(BlockedUser.username)

            return list([row[0] for row in names])


class Result(Base):
    '''Unshortend URL.'''
    __tablename__ = 'results'

    id = Column(Integer, primary_key=True)

    project_id = Column(Integer, ForeignKey('projects.name'), nullable=False)
    project = relationship('Project')

    shortcode = Column(String, nullable=False)
    url = Column(String, nullable=False)
    encoding = Column(String, nullable=False)
    datetime = Column(DateTime)

    @classmethod
    def has_results(cls):
        with new_session() as session:
            result = session.query(Result.id).first()

            return bool(result)


class ErrorReport(Base):
    '''Error report.'''
    __tablename__ = 'error_reports'

    id = Column(Integer, primary_key=True)

    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    item = relationship('Item')

    message = Column(String, nullable=False)
    datetime = Column(DateTime, nullable=False,
                      default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'project': self.item.project_id if self.item else None,
            'message': self.message,
            'datetime': self.datetime,
        }

    @classmethod
    def all_reports(cls):
        with new_session() as session:
            reports = session.query(ErrorReport)

            return list(report.to_dict() for report in reports)

    @classmethod
    def delete_all(cls):
        with new_session() as session:
            session.query(ErrorReport).delete()


class Budget(object):
    '''Budget calculator to help manage available items.

    Warning: This class assumes the application is single instance.
    '''

    projects = {}

    @classmethod
    def calculate_budgets(cls):
        cls.projects = {}

        with new_session() as session:
            query = session.query(
                Project.name, Project.max_num_items,
                Project.min_client_version, Project.min_version,
                Project.max_num_items
            ).filter_by(enabled=True)

            for row in query:
                (name, max_num_items, min_client_version, min_version,
                 max_num_items) = row

                cls.projects[name] = {
                    'max_num_items': max_num_items,
                    'min_client_version': min_client_version,
                    'min_version': min_version,
                    'items': 0,
                    'claims': 0,
                    'ip_addresses': set(),
                }

            query = session.query(Item.project_id, Item.ip_address)

            for row in query:
                project_id, ip_address = row

                if project_id not in cls.projects:
                    continue

                project_info = cls.projects[project_id]

                project_info['items'] += 1

                if ip_address:
                    project_info['ip_addresses'].add(ip_address)
                    project_info['claims'] += 1

    @classmethod
    def get_available_project(cls, ip_address, version, client_version):
        project_names = cls.projects.keys()
        random.shuffle(project_names)

        for project_name in project_names:
            project_info = cls.projects[project_name]

            if ip_address not in project_info['ip_addresses'] and \
                    version >= project_info['min_version'] and \
                    client_version >= project_info['min_client_version'] and \
                    project_info['items'] <= project_info['max_num_items'] and \
                    project_info['claims'] < project_info['items']:

                return (project_name, project_info['claims'],
                        project_info['items'], project_info['max_num_items'])

    @classmethod
    def is_client_outdated(cls, version, client_version):
        if not cls.projects:
            return

        min_version = min(project['min_version']
                          for project in cls.projects.values())
        min_client_version = min(project['min_client_version']
                                 for project in cls.projects.values())

        if version < min_version or client_version < min_client_version:
            return min_version, min_client_version

    @classmethod
    def is_claims_full(cls, ip_address):
        return cls.projects and all(ip_address in project['ip_addresses']
                                    for project in cls.projects.values())

    @classmethod
    def check_out(cls, project_id, ip_address):
        assert project_id
        assert ip_address

        project_info = cls.projects[project_id]

        project_info['items'] += 1
        project_info['ip_addresses'].add(ip_address)

    @classmethod
    def check_in(cls, project_id, ip_address):
        assert project_id
        assert ip_address

        if project_id not in cls.projects:
            # Project was recently disabled but the job hasn't come back
            # yet. Should be safe to ignore.
            return

        project_info = cls.projects[project_id]

        project_info['items'] -= 1
        project_info['ip_addresses'].remove(ip_address)


def make_hash(plaintext, salt):
    key = salt
    msg = plaintext.encode('ascii')

    return hmac.new(key, msg).digest()


def new_salt():
    return os.urandom(16)


def new_tamper_key():
    return base64.b16encode(os.urandom(16)).decode('ascii')


def checkout_item(username, ip_address, version=-1, client_version=-1):
    assert version is not None
    assert client_version is not None

    check_min_version_overrides(version, client_version)

    available = Budget.get_available_project(
        ip_address, version, client_version
    )

    if available:
        project_name, num_claims, num_items, max_num_items = available

        with new_session() as session:
            if num_claims >= num_items and num_items < max_num_items:
                project = session.query(Project).get(project_name)

                item_count = project.num_count_per_item
                upper_sequence_num = project.lower_sequence_num + item_count - 1

                item = Item(
                    project=project,
                    lower_sequence_num=project.lower_sequence_num,
                    upper_sequence_num=upper_sequence_num,
                )

                project.lower_sequence_num = upper_sequence_num + 1

                session.add(item)
            else:
                item = session.query(Item) \
                    .filter_by(username=None) \
                    .filter_by(project_id=project_name) \
                    .first()

            if item:
                item.datetime_claimed = datetime.datetime.utcnow()
                item.tamper_key = new_tamper_key()
                item.username = username
                item.ip_address = ip_address

                # Item should be committed now to generate ID for
                # newly generated items
                session.commit()

                Budget.check_out(project_name, ip_address)

                return item.to_dict()

            else:
                raise NoItemAvailable()

    else:
        if Budget.is_claims_full(ip_address):
            raise FullClaim()
        elif Budget.is_client_outdated(version, client_version):
            current_version, current_client_version = \
                Budget.is_client_outdated(version, client_version)

            raise UpdateClient(
                version=version,
                client_version=client_version,
                current_version=current_version,
                current_client_version=current_client_version
            )
        else:
            raise NoItemAvailable()


def checkin_item(item_id, tamper_key, results):
    item_stat = {
        'project': '',
        'username': '',
        'scanned': 0,
        'found': len(results)
    }

    with new_session() as session:
        row = session.query(
            Item.project_id, Item.username, Item.upper_sequence_num,
            Item.lower_sequence_num, Item.ip_address
            ) \
            .filter_by(id=item_id, tamper_key=tamper_key).first()

        (project_id, username, upper_sequence_num, lower_sequence_num,
         ip_address) = row

        item_stat['project'] = project_id
        item_stat['username'] = username
        item_stat['scanned'] = upper_sequence_num - lower_sequence_num + 1

        query_args = []
        time = datetime.datetime.utcnow()

        for shortcode in results.keys():
            url = results[shortcode]['url']
            encoding = results[shortcode]['encoding']
            query_args.append({
                'project_id': project_id,
                'shortcode': shortcode,
                'url': url,
                'encoding': encoding,
                'datetime': time
            })

        if len(query_args) > 0:
            query = insert(Result)
            session.execute(query, query_args)

        session.execute(delete(Item).where(Item.id == item_id))

        Budget.check_in(project_id, ip_address)

    if Stats.instance:
        Stats.instance.update(item_stat)

    return item_stat


def report_error(item_id, tamper_key, message):
    with new_session() as session:
        item = session.query(Item).filter_by(id=item_id, tamper_key=tamper_key).first()

        if not item:
            raise InvalidClaim()

        error_report = ErrorReport(item_id=item_id, message=message)
        session.add(error_report)


def check_min_version_overrides(version, client_version):
    if version < MIN_VERSION_OVERRIDE or client_version < MIN_CLIENT_VERSION_OVERRIDE:
        raise UpdateClient(
            version=version,
            client_version=client_version,
            current_version=MIN_VERSION_OVERRIDE,
            current_client_version=MIN_CLIENT_VERSION_OVERRIDE
        )


def get_git_hash():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()
    except (subprocess.CalledProcessError, OSError) as error:
        return str(error)
