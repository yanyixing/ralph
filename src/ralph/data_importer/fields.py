from import_export import fields


class ThroughField(fields.Field):

    def __init__(
        self, through_model, through_from_field_name, through_to_field_name,
        attribute=None, column_name=None, widget=None,
        readonly=False
    ):
        """
        Field for through django model import/export

        Args:
            through_model: Django through model for M2M relation

            through_from_field_name: field name model that is
                currently imported

            through_to_field_name: field name the model which is added
                as ManyToMany

            attribute: string of either an instance attribute or callable
                off the object

            column_name: let you provide how this field is named
                in datasource.

            widget: defines widget that will be used to represent field
                data in export

            readonly: boolean value defines that if this field will
                be assigned to object during import
        """
        self.through_model = through_model
        self.through_from_field_name = through_from_field_name
        self.through_to_field_name = through_to_field_name
        super().__init__(attribute, column_name, widget, readonly)

    def save(self, obj, data):
        if not self.readonly:
            value = data.get(self.column_name)
            current = set(self.widget.clean(value))
            old_objs = set([
                getattr(i, self.through_to_field_name) for i in
                self.through_model.objects.all().select_related(
                    self.through_to_field_name
                )
            ])

            to_add = current - old_objs
            to_remove = old_objs - current

            to_add_list = []
            for i in to_add:
                to_add_list.append(self.through_model(
                    **{
                        self.through_from_field_name: obj,
                        self.through_to_field_name: i
                    }
                ))

            if to_add_list:
                self.through_model.objects.bulk_create(to_add_list)
            if to_remove:
                self.through_model.objects.filter(
                    **{'{}__in'.format(self.through_to_field_name): to_remove}
                ).delete()