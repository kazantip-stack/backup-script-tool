import os
import tarfile
import argparse
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_backup(source_dir, backup_dir):
    """
    Создаёт архив .tar.gz из папки source_dir и кладёт его в backup_dir.
    Возвращает путь к созданному архиву, либо None, если что-то пошло не так.
    """
    # Проверяем, что папка, которую хотим бэкапить, вообще существует
    if not os.path.isdir(source_dir):
        logger.error(f"Папка {source_dir} не найдена или это не папка")
        return None

    # Создаём папку для бэкапов, если её ещё нет
    os.makedirs(backup_dir, exist_ok=True)

    # Формируем метку времени для имени архива, например: 2026-09-15_14-30-00
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Собираем имя файла архива с помощью f-строки
    backup_name = f"backup_{timestamp}.tar.gz"

    # Собираем полный путь к архиву через os.path.join, а не вручную через "+"
    backup_path = os.path.join(backup_dir, backup_name)

    try:
        # Открываем новый tar-архив в режиме записи со сжатием gzip
        with tarfile.open(backup_path, 'w:gz') as tar:
            # arcname нужен, чтобы внутри архива папка называлась просто
            # по имени, а не по полному пути с диска
            tar.add(source_dir, arcname=os.path.basename(source_dir))
        logger.info(f"Бэкап создан: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Не удалось создать бэкап: {e}")
        return None

def clean_old_backups(backup_dir, keep_last=5):
    """
    Оставляет только keep_last последних архивов в backup_dir,
    остальные (более старые) удаляет.
    """
    # Собираем список файлов-архивов в папке
    backups = [f for f in os.listdir(backup_dir) if f.endswith('.tar.gz')]

    # Если архивов не больше нормы — ротация не нужна
    if len(backups) <= keep_last:
        logger.info("Ротация не требуется: архивов не больше лимита")
        return

    # Сортируем имена файлов — по алфавиту, что совпадает с сортировкой по дате
    backups = sorted(backups)

    # Всё, кроме последних keep_last штук, считаем "старым" и удаляем
    old_backups = backups[:-keep_last]

    for filename in old_backups:
        path = os.path.join(backup_dir, filename)
        os.remove(path)
        logger.info(f"Удалён старый архив: {path}")

def main():
    parser = argparse.ArgumentParser(
        description='Создаёт бэкап папки в .tar.gz, удаляет старые архивы, оставляя только последние N.'
    )
    parser.add_argument(
        'source',
        help='Путь к папке, которую нужно забэкапить'
    )
    parser.add_argument(
        '-d', '--dest',
        default='backups',
        help='Папка, куда складывать архивы (по умолчанию: backups)'
    )
    parser.add_argument(
        '-k', '--keep',
        type=int,
        default=5,
        help='Сколько последних архивов хранить (по умолчанию: 5)'
    )

    args = parser.parse_args()

    result = create_backup(args.source, args.dest)

    if result is not None:
        clean_old_backups(args.dest, args.keep)
        return 0
    else:
        return 1

if __name__ == '__main__':
    exit(main())