from LogComponent import ILog
import time


def main():
    log = ILog()

    # Writing some logs
    log.write("Application started")
    for i in range(10):
        log.write(f"Log entry {i}")
        time.sleep(1)  # Simulate work

    # Stopping the log component after all logs are written
    log.stop(wait=True)
    print("Application finished after waiting for logs to be written")

    # Restarting application and log component for demonstration
    log = ILog()
    log.write("Application started again")

    # Stopping the log component without waiting for all logs to be written
    log.stop(wait=False)
    print("Application finished without waiting for logs")


if __name__ == "__main__":
    main()