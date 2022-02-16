"""
This namespace defines the DBFunction abstract class and its subclasses. These subclasses
represent functions that have identifiers, display names and hints, and their instances
hold parameters. Each DBFunction subclass defines how its instance can be converted into an
SQLAlchemy expression.

Hints hold information about what kind of input the function might expect and what output
can be expected from it. This is used to provide interface information without constraining its
user.

These classes might be used, for example, to define a filter for an SQL query, or to
access hints on what composition of functions and parameters should be valid.
"""

from abc import ABC, abstractmethod

from sqlalchemy import column, not_, and_, or_, func, literal

from db.functions import hints


class DBFunction(ABC):
    id = None
    name = None
    hints = None

    # Optionally lists the SQL functions this DBFunction depends on.
    # Will be checked against SQL functions defined on a database to tell if it
    # supports this DBFunction. Either None or a tuple of SQL function name
    # strings.
    depends_on = None

    def __init__(self, parameters):
        if self.id is None:
            raise ValueError('DBFunction subclasses must define an ID.')
        if self.name is None:
            raise ValueError('DBFunction subclasses must define a name.')
        if self.depends_on is not None and not isinstance(self.depends_on, tuple):
            raise ValueError('DBFunction subclasses\' depends_on attribute must either be None or a tuple of SQL function names.')
        self.parameters = parameters

    @property
    def referenced_columns(self):
        """Walks the expression tree, collecting referenced columns.
        Useful when checking if all referenced columns are present in the queried relation."""
        columns = set([])
        for parameter in self.parameters:
            if isinstance(parameter, ColumnReference):
                columns.add(parameter.column)
            elif isinstance(parameter, DBFunction):
                columns.update(parameter.referenced_columns)
        return columns

    @staticmethod
    @abstractmethod
    def to_sa_expression():
        return None


class Literal(DBFunction):
    id = 'literal'
    name = 'Literal'
    hints = tuple([
        hints.parameter_count(1),
        hints.parameter(1, hints.literal),
    ])

    @staticmethod
    def to_sa_expression(primitive):
        return literal(primitive)


class ColumnReference(DBFunction):
    id = 'column_reference'
    name = 'Column Reference'
    hints = tuple([
        hints.parameter_count(1),
        hints.parameter(1, hints.column),
    ])

    @property
    def column(self):
        return self.parameters[0]

    @staticmethod
    def to_sa_expression(column_name):
        return column(column_name)


class List(DBFunction):
    id = 'list'
    name = 'List'

    @staticmethod
    def to_sa_expression(*items):
        return list(items)


class Empty(DBFunction):
    id = 'empty'
    name = 'Empty'
    hints = tuple([
        hints.returns(hints.boolean),
        hints.parameter_count(1),
    ])

    @staticmethod
    def to_sa_expression(value):
        return value.is_(None)


class Not(DBFunction):
    id = 'not'
    name = 'Not'
    hints = tuple([
        hints.returns(hints.boolean),
        hints.parameter_count(1),
    ])

    @staticmethod
    def to_sa_expression(value):
        return not_(value)


class Equal(DBFunction):
    id = 'equal'
    name = 'Equal'
    hints = tuple([
        hints.returns(hints.boolean),
        hints.parameter_count(2),
    ])

    @staticmethod
    def to_sa_expression(value1, value2):
        return value1 == value2


class Greater(DBFunction):
    id = 'greater'
    name = 'Greater'
    hints = tuple([
        hints.returns(hints.boolean),
        hints.parameter_count(2),
        hints.all_parameters(hints.comparable),
    ])

    @staticmethod
    def to_sa_expression(value1, value2):
        return value1 > value2


class Lesser(DBFunction):
    id = 'lesser'
    name = 'Lesser'
    hints = tuple([
        hints.returns(hints.boolean),
        hints.parameter_count(2),
        hints.all_parameters(hints.comparable),
    ])

    @staticmethod
    def to_sa_expression(value1, value2):
        return value1 < value2


class In(DBFunction):
    id = 'in'
    name = 'In'
    hints = tuple([
        hints.returns(hints.boolean),
        hints.parameter_count(2),
        hints.parameter(2, hints.array),
    ])

    @staticmethod
    def to_sa_expression(value1, value2):
        return value1.in_(value2)


class And(DBFunction):
    id = 'and'
    name = 'And'
    hints = tuple([
        hints.returns(hints.boolean),
    ])

    @staticmethod
    def to_sa_expression(*values):
        return and_(*values)


class Or(DBFunction):
    id = 'or'
    name = 'Or'
    hints = tuple([
        hints.returns(hints.boolean),
    ])

    @staticmethod
    def to_sa_expression(*values):
        return or_(*values)


class StartsWith(DBFunction):
    id = 'starts_with'
    name = 'Starts With'
    hints = tuple([
        hints.returns(hints.boolean),
        hints.parameter_count(2),
        hints.all_parameters(hints.string_like),
    ])

    @staticmethod
    def to_sa_expression(string, prefix):
        return string.like(f'{prefix}%')


class ToLowercase(DBFunction):
    id = 'to_lowercase'
    name = 'To Lowercase'
    hints = tuple([
        hints.parameter_count(1),
        hints.all_parameters(hints.string_like),
    ])

    @staticmethod
    def to_sa_expression(string):
        return func.lower(string)