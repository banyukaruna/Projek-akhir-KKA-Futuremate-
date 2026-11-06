"""Custom exception FutureMate. Semua turunan FutureMateError agar mudah ditangkap sekaligus."""


class FutureMateError(Exception):
    """Kelas dasar semua error aplikasi."""


class NilaiTidakValidError(FutureMateError):
    """Nilai di luar rentang 0-100."""


class DataTidakValidError(FutureMateError):
    """File data rusak atau formatnya tidak sesuai."""


class DuplikatError(FutureMateError):
    """Data yang sama sudah ada."""
