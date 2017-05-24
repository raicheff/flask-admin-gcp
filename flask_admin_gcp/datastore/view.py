#
# Flask-Admin-GCP
#
# Copyright (C) 2017 Boris Raicheff
# All rights reserved
#


from collections import defaultdict

from flask_admin.model import BaseModelView
from schematics.types import BaseType
from wtforms import Form


class ModelView(BaseModelView):
    """
    https://flask-admin.readthedocs.io/adding_a_new_model_backend
    ---
    https://cloud.google.com/datastore/docs/concepts/metadataqueries
    https://cloud.google.com/datastore/docs/concepts/stats
    """

    def __init__(
            self,
            model,
            client,
            name=None,
            category=None,
            endpoint=None,
            url=None,
            static_folder=None,
            menu_class_name=None,
            menu_icon_type=None,
            menu_icon_value=None,
    ):
        super().__init__(
            model,
            name,
            category,
            endpoint,
            url,
            static_folder,
            menu_class_name,
            menu_icon_type,
            menu_icon_value,
        )

        self.client = client

    def get_pk_value(self, model):
        return self.model.id

    def get_one(self, id):
        return self.model.get_by_id(id)

    def get_list(self, page, sort_field, sort_desc, search, filters, page_size=None):

        # FIXME
        # self._test()
        # from flask_login import current_user
        # namespace = current_user.company.id_hash
        namespace = None

        # Pagination
        limit = page_size or self.page_size
        offset = page * page_size if page and page_size else None

        query = [self.model.from_entity(entity) for entity in self.model.query(namespace=namespace).fetch(limit=limit, offset=offset)]
        return None, query

    def scaffold_sortable_columns(self):
        # TODO
        return None

    def scaffold_list_columns(self):
        return (p for p in dir(self.model) if isinstance(getattr(self.model, p), BaseType))

    def scaffold_form(self):
        # TODO

        class MyForm(Form):
            pass

        # Do something
        return MyForm

    def create_model(self, form):
        # TODO
        pass

    def update_model(self, form, model):
        # TODO
        pass

    def delete_model(self, model):
        self.model.delete()
        return True

    def _test(self):
        """"""

        query = self.client.query(kind='__namespace__')
        query.keys_only()
        namespaces = [entity.key.id_or_name for entity in query.fetch()]
        print('__namespace__:', namespaces)

        query = self.client.query(kind='__kind__')
        # query = self.client.query(kind='__kind__', namespace=namespaces[1])
        query.keys_only()
        kinds = [entity.key.id_or_name for entity in query.fetch()]
        print('__kind__:', kinds)

        query = self.client.query(kind='__property__')
        query.keys_only()
        properties_by_kind = defaultdict(list)
        for entity in query.fetch():
            kind = entity.key.parent.name
            property_ = entity.key.name
            properties_by_kind[kind].append(property_)
        print('__property__:', properties_by_kind)

        ancestor = self.client.key('__kind__', kinds[0])
        query = self.client.query(kind='__property__', ancestor=ancestor)
        representations_by_property = {}
        for entity in query.fetch():
            property_name = entity.key.name
            property_types = entity['property_representation']
            representations_by_property[property_name] = property_types
        print(representations_by_property)


# EOF
