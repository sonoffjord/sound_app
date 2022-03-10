from django.core.exceptions import ValidationError


def get_path_upload_avatar(instance, file):
    """ Построение пути к файлу,
    format: (media)/avatar/user_id/photo.jpg """

    return f'avatar/{instance.id}/{file}'


def validate_size_image(file_obj):
    """ Проверка размера файла """

    MEGABYTE_LIMIT = 2
    if file_obj.size > MEGABYTE_LIMIT * 1024 * 1024:
        raise ValidationError(f'Максимальный размер файла {MEGABYTE_LIMIT}MB')
