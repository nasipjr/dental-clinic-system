import os
import sys
import atexit
import logging

logger = logging.getLogger(__name__)

_LOCK_FILE_HANDLE = None


def is_pid_running(pid):
    """Check whether a process with the given PID is running on Windows or Unix."""
    if pid <= 0:
        return False
    if sys.platform == "win32":
        import ctypes
        kernel32 = ctypes.windll.kernel32
        SYNCHRONIZE = 0x0010
        process = kernel32.OpenProcess(SYNCHRONIZE, False, pid)
        if process:
            kernel32.CloseHandle(process)
            return True
        return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


def acquire_scheduler_lock(app):
    """
    Ensures that only ONE worker process in multi-worker WSGI environments 
    or desktop instances starts the background threads.
    """
    global _LOCK_FILE_HANDLE
    if _LOCK_FILE_HANDLE is not None:
        return True

    instance_dir = app.instance_path
    os.makedirs(instance_dir, exist_ok=True)
    lock_file_path = os.path.join(instance_dir, "scheduler.lock")

    pid = os.getpid()

    if os.path.exists(lock_file_path):
        try:
            with open(lock_file_path, "r") as f:
                content = f.read().strip()
                existing_pid = int(content) if content.isdigit() else None
            if existing_pid and is_pid_running(existing_pid) and existing_pid != pid:
                logger.info(f"Scheduler lock held by running PID {existing_pid}. Skipping background threads for PID {pid}.")
                return False
            else:
                # Stale lock file from crashed process
                os.remove(lock_file_path)
        except Exception:
            try:
                os.remove(lock_file_path)
            except Exception:
                pass

    try:
        # Create lock file exclusively
        fd = os.open(lock_file_path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
        os.write(fd, str(pid).encode("utf-8"))
        _LOCK_FILE_HANDLE = fd

        def cleanup_lock():
            global _LOCK_FILE_HANDLE
            if _LOCK_FILE_HANDLE is not None:
                try:
                    os.close(_LOCK_FILE_HANDLE)
                except Exception:
                    pass
                _LOCK_FILE_HANDLE = None
            if os.path.exists(lock_file_path):
                try:
                    os.remove(lock_file_path)
                except Exception:
                    pass

        atexit.register(cleanup_lock)
        logger.info(f"Successfully acquired single-instance scheduler lock for PID {pid}.")
        return True
    except FileExistsError:
        logger.info(f"Scheduler lock file exists. Worker PID {pid} will not start background threads.")
        return False
    except Exception as e:
        logger.warning(f"Could not acquire scheduler lock: {e}")
        return False


def start_app_schedulers(app):
    """
    Launches background schedulers safely guaranteed to run in only ONE process.
    """
    if not acquire_scheduler_lock(app):
        return False

    try:
        from utils.backup_helper import schedule_daily_backups
        schedule_daily_backups(app)
        app.logger.info("Database backup scheduler thread started successfully.")
    except Exception as e:
        app.logger.error(f"Failed to start database backup scheduler: {e}")

    try:
        from utils.notification_helper import schedule_appointment_reminders
        schedule_appointment_reminders(app)
        app.logger.info("Appointment reminders scheduler thread started successfully.")
    except Exception as e:
        app.logger.error(f"Failed to start appointment reminders scheduler: {e}")

    try:
        from utils.notification_helper import start_telegram_bot_listener
        start_telegram_bot_listener(app)
        app.logger.info("Telegram Bot listener thread started successfully.")
    except Exception as e:
        app.logger.error(f"Failed to start Telegram Bot listener: {e}")

    try:
        from routes.appointments import schedule_expired_appointments_cleanup
        schedule_expired_appointments_cleanup(app)
        app.logger.info("Expired appointments cleanup scheduler thread started successfully.")
    except Exception as e:
        app.logger.error(f"Failed to start expired appointments cleanup scheduler: {e}")

    return True
