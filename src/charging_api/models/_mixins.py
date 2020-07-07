from typing import Set, Dict, List
from sqlalchemy.orm.state import InstanceState
from ._conversions import to_dict, from_model


class BaseMixin(object):
    def from_model(self, otherStation: object) -> "BaseMixin":
        from_model(self, otherStation)
        return self


class DbMixin(BaseMixin):
    def to_dict(self, ignore_objs: Set[object] = None) -> Dict:
        if ignore_objs is None:
            ignore_objs = set()
        ignore_objs.add(self.__class__)
        ignore_objs.add(InstanceState)
        return to_dict(
            table_dict={k: getattr(self, k) for k in self.get_attributes()},
            ignore_objs=ignore_objs,
        )

    def get_attributes(self) -> List:
        return self.__mapper__.attrs.keys()


class RestMixin(BaseMixin):
    def to_dict(self, ignore_objs: Set[object] = None) -> Dict:
        if ignore_objs is None:
            ignore_objs = set()
        ignore_objs.add(self.__class__)
        ignore_objs.add(InstanceState)
        return to_dict(table_dict=self.__dict__, ignore_objs=ignore_objs)

    def get_attributes(self) -> List:
        return self.__dict__.keys()
