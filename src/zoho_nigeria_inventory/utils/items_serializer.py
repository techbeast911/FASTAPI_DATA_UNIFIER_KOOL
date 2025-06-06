from sqlalchemy.inspection import inspect

def serialize_model(instance):
    return {c.key: getattr(instance, c.key) for c in inspect(instance).mapper.column_attrs}
