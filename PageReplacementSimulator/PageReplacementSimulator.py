import sys
from pathlib import Path

from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication

from page_replacement_controller import (
    PageReplacementController,
)


def main() -> None:
    app = QApplication(sys.argv)

    ui_path = Path(__file__).resolve().parent / "page_replacement.ui"
    ui_file = QFile(
        str(ui_path) if ui_path.exists() else "page_replacement.ui"
    )

    if not ui_file.open(
        QFile.OpenModeFlag.ReadOnly
    ):
        raise RuntimeError(
            "Không thể mở file page_replacement.ui"
        )

    loader = QUiLoader()

    window = loader.load(
        ui_file
    )

    ui_file.close()

    if window is None:
        raise RuntimeError(
            "Không thể tải giao diện page_replacement.ui"
        )

    controller = PageReplacementController(
        window
    )

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()
