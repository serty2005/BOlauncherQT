import logging
import os
import subprocess


def launch_anydesk(anydesk_path, anydesk_id, anydesk_password):
    """
    Запускает AnyDesk для указанного ID.

    Если пароль передан, он отправляется в stdin процесса и AnyDesk запускается
    в режиме подключения по паролю. Если пароль пустой, подключение стартует
    без `--with-password`, чтобы подтверждение выполнялось на удаленной стороне.
    """
    logging.info(f"Попытка запуска AnyDesk для ID '{anydesk_id}'")

    if not os.path.exists(anydesk_path):
        logging.error(f"Исполняемый файл AnyDesk не найден по пути '{anydesk_path}'")
        raise FileNotFoundError(f"Исполняемый файл AnyDesk не найден по пути '{anydesk_path}'")

    creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    args = [anydesk_path, anydesk_id]
    use_password = bool(anydesk_password)
    if use_password:
        args.append("--with-password")

    # В лог не выводим сам пароль, только режим запуска.
    logging.debug(
        f"Подготовлена команда AnyDesk: '{anydesk_path}' '{anydesk_id}' "
        f"{'--with-password' if use_password else '(без пароля)'}"
    )

    try:
        process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE if use_password else None,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
            creationflags=creationflags,
        )

        # Передаем пароль только если он был введен пользователем.
        if use_password and process.stdin is not None:
            process.stdin.write(f"{anydesk_password}\n")
            process.stdin.flush()
            process.stdin.close()

        logging.info(
            f"AnyDesk запущен для ID '{anydesk_id}'. PID: {process.pid}. "
            f"Режим: {'подключение по паролю' if use_password else 'с подтверждением на удаленной стороне'}"
        )
        return process.pid
    except FileNotFoundError:
        logging.error(f"Ошибка FileNotFoundError при запуске AnyDesk: '{anydesk_path}'")
        raise FileNotFoundError(f"Исполняемый файл AnyDesk не найден по пути '{anydesk_path}'")
    except Exception as e:
        logging.error(f"Ошибка при запуске AnyDesk для ID '{anydesk_id}': {e}")
        raise RuntimeError(f"Не удалось запустить AnyDesk: {e}")
