from memoized_property import memoized_property

import jardin.config as config


class BaseConnection(object):

    DRIVER = None

    _connection = None
    _cursor = None

    def __init__(self, db_config):
        self.db_config = db_config
        self.autocommit = True

    def connection(self):
        if self._connection is None:
            self._connection = self.connect()
        return self._connection

    @memoized_property
    def connect_kwargs(self):
        return dict(
            database=self.db_config.path[1:],
            user=self.db_config.username,
            password=self.db_config.password,
            host=self.db_config.hostname,
            port=self.db_config.port,
            connect_timeout=5
            )

    def connect(self):
        self._cursor = None
        connection = self.DRIVER.connect(**self.connect_kwargs)
        connection.initialize(config.logger)
        return connection

    @memoized_property
    def cursor_kwargs(self):
        return {}

    def cursor(self):
        if self._cursor is None:
            self._cursor = self.connection().cursor(**self.cursor_kwargs)
        return self._cursor

    def execute(self, *query):
        try:
            results = self.cursor().execute(*query)
            if self.autocommit:
                self.connection().commit()
            return results
        except self.DRIVER.InterfaceError:
            self._connection = None
            self._cursor = None
            raise
        except Exception as e:
            self.connection().rollback()
            raise e
