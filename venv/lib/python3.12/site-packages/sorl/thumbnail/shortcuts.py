from sorl.thumbnail import default


def get_thumbnail(file_, geometry_string, **options):
    """
    A shortcut for the Backend ``get_thumbnail`` method
    """
    return default.backend.get_thumbnail(file_, geometry_string, **options)


def delete(file_, delete_file=True):
    """
    A shortcut for the Backend ``delete`` method
    """
    return default.backend.delete(file_, delete_file)
