import csv
import io
import logging
import os
import subprocess


def _get_no_window_creationflags():
    return subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0


def _list_processes_by_image_name(image_name):
    """Возвращает список процессов Windows с указанным именем образа."""
    if os.name != "nt":
        logging.debug("Получение списка процессов по имени образа доступно только на Windows.")
        return []

    try:
        result = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {image_name}", "/NH", "/FO", "CSV"],
            check=False,
            capture_output=True,
            text=True,
            creationflags=_get_no_window_creationflags(),
        )
    except FileNotFoundError:
        logging.error("Команда 'tasklist' не найдена. Убедитесь, что приложение запущено на Windows.")
        return []
    except Exception as e:
        logging.error(f"Неожиданная ошибка при получении списка процессов '{image_name}': {e}")
        return []

    stdout = result.stdout.strip()
    logging.debug(f"tasklist stdout для {image_name}:\n{stdout}")
    if result.stderr.strip():
        logging.debug(f"tasklist stderr для {image_name}:\n{result.stderr.strip()}")

    if not stdout:
        return []

    csv_lines = [line for line in stdout.splitlines() if line.startswith('"')]
    if not csv_lines:
        return []

    processes = []
    reader = csv.reader(io.StringIO("\n".join(csv_lines)))
    for row in reader:
        if len(row) < 2:
            continue
        if row[0].strip().lower() != image_name.lower():
            continue
        try:
            processes.append({"name": row[0].strip(), "pid": int(row[1])})
        except ValueError:
            logging.debug(f"Не удалось разобрать PID из строки tasklist: {row}")

    return processes


def stop_process_by_pid(pid):
    """Останавливает процесс по его PID в Windows."""
    if pid is None:
        logging.warning("PID процесса BackOffice неизвестен, остановка пропущена.")
        return False

    logging.info(f"Попытка остановить процесс BackOffice (PID: {pid})...")
    try:
        result = subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(pid)],
            check=True,
            capture_output=True,
            text=True,
            creationflags=_get_no_window_creationflags(),
        )
        logging.info(f"Процесс BackOffice (PID: {pid}) успешно остановлен. stdout: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        logging.warning(
            f"Ошибка при остановке процесса BackOffice (PID: {pid}). "
            f"Код выхода: {e.returncode}, stdout: {e.stdout.strip()}, stderr: {e.stderr.strip()}"
        )
        if e.returncode == 128:
            logging.info(f"Процесс (PID: {pid}) не найден и, вероятно, уже завершен.")
            return True
        return False
    except FileNotFoundError:
        logging.error("Команда 'taskkill' не найдена. Убедитесь, что приложение запущено на Windows.")
        return False
    except Exception as e:
        logging.error(f"Неожиданная ошибка при остановке процесса BackOffice (PID: {pid}): {e}")
        return False


def is_anydesk_running():
    """Проверяет, запущен ли сейчас процесс AnyDesk.exe в Windows."""
    if os.name != "nt":
        logging.debug("Проверка процесса AnyDesk доступна только на Windows.")
        return False

    logging.debug("Проверка запущенности процесса AnyDesk.exe...")
    return bool(_list_processes_by_image_name("AnyDesk.exe"))


def stop_anydesk_processes():
    """Принудительно завершает все процессы AnyDesk.exe и возвращает их количество."""
    if os.name != "nt":
        logging.debug("Принудительное завершение AnyDesk доступно только на Windows.")
        return 0

    processes = _list_processes_by_image_name("AnyDesk.exe")
    process_count = len(processes)
    if process_count == 0:
        logging.info("Запущенные процессы AnyDesk.exe не найдены.")
        return 0

    logging.info(f"Попытка принудительно завершить {process_count} процесс(ов) AnyDesk.exe...")
    try:
        result = subprocess.run(
            ["taskkill", "/F", "/T", "/IM", "AnyDesk.exe"],
            check=True,
            capture_output=True,
            text=True,
            creationflags=_get_no_window_creationflags(),
        )
        logging.info(f"Процессы AnyDesk.exe успешно завершены. stdout: {result.stdout.strip()}")
        return process_count
    except subprocess.CalledProcessError as e:
        if e.returncode == 128:
            logging.info("Процессы AnyDesk.exe уже были завершены к моменту выполнения taskkill.")
            return 0
        logging.error(
            f"Ошибка при остановке процессов AnyDesk.exe. "
            f"Код выхода: {e.returncode}, stdout: {e.stdout.strip()}, stderr: {e.stderr.strip()}"
        )
        raise RuntimeError(e.stderr.strip() or e.stdout.strip() or "Не удалось завершить процессы через taskkill")
    except FileNotFoundError:
        logging.error("Команда 'taskkill' не найдена. Убедитесь, что приложение запущено на Windows.")
        raise RuntimeError("Команда taskkill не найдена")
