import psutil


class NetworkMonitor:
    @staticmethod
    def get_total_bytes():
        counters = psutil.net_io_counters()
        return counters.bytes_sent + counters.bytes_recv

    @staticmethod
    def bytes_to_megabytes(byte_count):
        return byte_count / (1024 * 1024)
