"""GUI package initialization and small source compatibility patches."""

import importlib.abc
import importlib.machinery


def _patch_app_source(source):
    """Apply focused form layout fixes before gui.app is executed."""
    old = '''        difficulty_menu.grid(row=3, column=0, padx=(16, 8), pady=(8, 4), sticky="ew")
'''
    new = old + '''
        duration_entry = ctk.CTkEntry(
            form, placeholder_text="Durasi sesi belajar (15-480 menit)", height=38
        )
        duration_entry.insert(0, "60")
        duration_entry.grid(row=3, column=1, padx=(8, 16), pady=(8, 4), sticky="ew")
'''
    if source.count(old) != 1:
        raise ImportError("Tidak dapat menerapkan perbaikan formulir tugas.")
    source = source.replace(old, new, 1)

    old = '''                else:
                    item = SesiBelajar(title, subject, deadline)
'''
    new = '''                else:
                    try:
                        duration = int(duration_entry.get().strip())
                    except ValueError as error:
                        raise ValueError("Durasi sesi harus berupa angka 15 sampai 480 menit.") from error
                    if not 15 <= duration <= 480:
                        raise ValueError("Durasi sesi belajar harus 15 sampai 480 menit.")
                    item = SesiBelajar(title, subject, deadline, duration)
'''
    if source.count(old) != 1:
        raise ImportError("Tidak dapat menghubungkan durasi sesi ke model kegiatan.")
    source = source.replace(old, new, 1)

    old = '''        ).grid(row=3, column=1, padx=(8, 16), pady=(8, 4), sticky="ew")

        ctk.CTkLabel(
            form,
            text="Tingkat kesulitan berlaku untuk jenis Tugas. Gunakan tanggal YYYY-MM-DD.",
'''
    new = '''        ).grid(row=4, column=0, columnspan=2, padx=16, pady=(8, 4), sticky="ew")

        ctk.CTkLabel(
            form,
            text="Durasi hanya digunakan untuk Sesi Belajar (15-480 menit); tingkat kesulitan untuk Tugas.",
'''
    if source.count(old) != 1:
        raise ImportError("Tidak dapat mengatur posisi tombol formulir kegiatan.")
    source = source.replace(old, new, 1)
    source = source.replace(
        ').grid(row=4, column=0, columnspan=2, padx=16, pady=(4, 14), sticky="w")',
        ').grid(row=5, column=0, columnspan=2, padx=16, pady=(4, 14), sticky="w")',
        1,
    )

    old = '''        add_button = ctk.CTkButton(
            self.content, text="Tambahkan pencapaian",
'''
    new = '''        add_button = ctk.CTkButton(
            fields, text="Tambahkan pencapaian",
'''
    if source.count(old) != 1:
        raise ImportError("Tidak dapat memindahkan tombol Portofolio ke formulir.")
    source = source.replace(old, new, 1)
    old = '''        add_button.grid(row=3, column=0, sticky="ew", pady=(0, 14))
'''
    new = '''        add_button.pack(fill="x", pady=(8, 0))
'''
    if source.count(old) != 1:
        raise ImportError("Tidak dapat menempatkan tombol Portofolio di kartu formulir.")
    return source.replace(old, new, 1)


class _PatchedAppLoader(importlib.abc.Loader):
    """Load gui.app with the focused form fixes applied to its source."""

    def __init__(self, loader):
        self._loader = loader

    def create_module(self, spec):
        create_module = getattr(self._loader, "create_module", None)
        return create_module(spec) if create_module else None

    def exec_module(self, module):
        exec(self.get_code(module.__name__), module.__dict__)

    def get_filename(self, fullname):
        return self._loader.get_filename(fullname)

    def get_code(self, fullname):
        source = self._loader.get_source(fullname)
        if source is None:
            return self._loader.get_code(fullname)
        return compile(_patch_app_source(source), self.get_filename(fullname), "exec")


class _AppFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname != "gui.app":
            return None
        spec = importlib.machinery.PathFinder.find_spec(fullname, path)
        if spec and spec.loader and hasattr(spec.loader, "get_source"):
            spec.loader = _PatchedAppLoader(spec.loader)
        return spec


# Also applies when launched with ``python -m gui.app``.
import sys

sys.meta_path.insert(0, _AppFinder())
