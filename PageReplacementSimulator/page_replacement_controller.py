from __future__ import annotations

import re

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from page_replacement_service import (
    PageReplacementResult,
    PageReplacementService,
)


class PageReplacementController:
    def __init__(
        self,
        page: QWidget,
    ) -> None:
        self.page = page

        # ====================================================
        # TÌM CONTROL
        # ====================================================

        self.algorithm_combo = self._find(
            QComboBox,
            "cboPageAlgorithm",
        )

        self.frame_spin = self._find(
            QSpinBox,
            "spinFrameCount",
        )

        self.reference_input = self._find(
            QLineEdit,
            "txtPageReference",
        )

        self.btn_sample = self._find(
            QPushButton,
            "btnPageSample",
        )

        self.btn_run = self._find(
            QPushButton,
            "btnPageRun",
        )

        self.btn_step = self._find(
            QPushButton,
            "btnPageStep",
        )

        self.btn_compare = self._find(
            QPushButton,
            "btnPageCompare",
        )

        self.btn_reset = self._find(
            QPushButton,
            "btnPageReset",
        )

        self.simulation_table = self._find(
            QTableWidget,
            "tblPageSimulation",
        )

        self.comparison_table = self._find(
            QTableWidget,
            "tblPageComparison",
        )

        self.lbl_current_page = self._find(
            QLabel,
            "lblCurrentPage",
        )

        self.lbl_current_step = self._find(
            QLabel,
            "lblCurrentStep",
        )

        self.lbl_faults = self._find(
            QLabel,
            "lblPageFaults",
        )

        self.lbl_hits = self._find(
            QLabel,
            "lblPageHits",
        )

        self.lbl_fault_rate = self._find(
            QLabel,
            "lblFaultRate",
        )

        self.lbl_hit_rate = self._find(
            QLabel,
            "lblHitRate",
        )

        self.lbl_status = self._find(
            QLabel,
            "lblPageStatus",
        )

        # ====================================================
        # STATE
        # ====================================================

        self.current_result: (
            PageReplacementResult | None
        ) = None

        self.current_step = 0
        self.data_changed = True

        self._configure_widgets()
        self._connect_events()
        self.reset_output()

    # ========================================================
    # KHỞI TẠO
    # ========================================================

    def _find(
        self,
        widget_type: type,
        object_name: str,
    ):
        widget = self.page.findChild(
            widget_type,
            object_name,
        )

        if widget is None:
            raise RuntimeError(
                f"Không tìm thấy objectName "
                f"'{object_name}' trong "
                "page_replacement.ui"
            )

        return widget

    def _configure_widgets(self) -> None:
        self.algorithm_combo.clear()

        self.algorithm_combo.addItems(
            [
                "Optimal",
                "FIFO",
                "Second Chance",
                "LRU",
            ]
        )

        self.algorithm_combo.setCurrentText(
            "FIFO"
        )

        self.frame_spin.setRange(1, 10)
        self.frame_spin.setValue(3)

        self.simulation_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.comparison_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.comparison_table.setColumnCount(5)

        self.comparison_table.setHorizontalHeaderLabels(
            [
                "Algorithm",
                "Faults",
                "Hits",
                "Fault Rate",
                "Hit Rate",
            ]
        )

        self.comparison_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.comparison_table.setAlternatingRowColors(
            True
        )

        self.comparison_table.horizontalHeader().setStretchLastSection(
            True
        )

    def _connect_events(self) -> None:
        self.btn_sample.clicked.connect(
            self.load_sample
        )

        self.btn_run.clicked.connect(
            self.run_all
        )

        self.btn_step.clicked.connect(
            self.run_step
        )

        self.btn_compare.clicked.connect(
            self.compare_algorithms
        )

        self.btn_reset.clicked.connect(
            self.reset_all
        )

        self.algorithm_combo.currentTextChanged.connect(
            self.mark_data_changed
        )

        self.frame_spin.valueChanged.connect(
            self.mark_data_changed
        )

        self.reference_input.textChanged.connect(
            self.mark_data_changed
        )

    # ========================================================
    # ĐỌC DỮ LIỆU
    # ========================================================

    def parse_references(self) -> list[int]:
        raw_text = self.reference_input.text().strip()

        if not raw_text:
            raise ValueError(
                "Hãy nhập chuỗi tham chiếu trang."
            )

        tokens = re.split(
            r"[\s,;]+",
            raw_text,
        )

        references: list[int] = []

        for position, token in enumerate(tokens):
            if token == "":
                continue

            try:
                page = int(token)

            except ValueError as error:
                raise ValueError(
                    f"Giá trị '{token}' tại vị trí "
                    f"{position + 1} không phải số nguyên."
                ) from error

            if page < 0:
                raise ValueError(
                    "Số trang không được âm."
                )

            references.append(page)

        if not references:
            raise ValueError(
                "Chuỗi tham chiếu trang không hợp lệ."
            )

        return references

    def calculate_result(
        self,
    ) -> PageReplacementResult:
        return PageReplacementService.run(
            algorithm=(
                self.algorithm_combo.currentText()
            ),
            references=self.parse_references(),
            frame_count=self.frame_spin.value(),
        )

    # ========================================================
    # DỮ LIỆU MẪU
    # ========================================================

    def load_sample(self) -> None:
        self.reference_input.setText(
            "5 0 1 2 0 3 0 4 2 3 0 3 2 1 2"
        )

        self.frame_spin.setValue(3)
        self.algorithm_combo.setCurrentText(
            "FIFO"
        )

        self.lbl_status.setText(
            "Trạng thái: Đã nạp dữ liệu mẫu"
        )

    # ========================================================
    # CHẠY TOÀN BỘ
    # ========================================================

    def run_all(self) -> None:
        try:
            self.current_result = (
                self.calculate_result()
            )

            self.current_step = len(
                self.current_result.steps
            )

            self.data_changed = False

            self.display_simulation(
                self.current_result,
                visible_steps=self.current_step,
            )

            self.update_statistics(
                self.current_result,
                self.current_step,
            )

            self.lbl_status.setText(
                "Trạng thái: Hoàn thành "
                f"{self.current_result.algorithm}"
            )

        except Exception as error:
            QMessageBox.critical(
                self.page,
                "Lỗi mô phỏng",
                str(error),
            )

            self.lbl_status.setText(
                "Trạng thái: Có lỗi"
            )

    # ========================================================
    # CHẠY TỪNG BƯỚC
    # ========================================================

    def run_step(self) -> None:
        try:
            if (
                self.current_result is None
                or self.data_changed
            ):
                self.current_result = (
                    self.calculate_result()
                )

                self.current_step = 0
                self.data_changed = False

                self.prepare_simulation_table(
                    self.current_result
                )

            total_steps = len(
                self.current_result.steps
            )

            if self.current_step >= total_steps:
                QMessageBox.information(
                    self.page,
                    "Hoàn thành",
                    "Không còn bước nào để chạy.",
                )
                return

            self.current_step += 1

            self.display_simulation(
                self.current_result,
                visible_steps=self.current_step,
            )

            self.update_statistics(
                self.current_result,
                self.current_step,
            )

            step = self.current_result.steps[
                self.current_step - 1
            ]

            result_text = (
                "Page Fault"
                if step.is_fault
                else "Page Hit"
            )

            self.lbl_status.setText(
                "Trạng thái: Bước "
                f"{self.current_step}/{total_steps} - "
                f"Page {step.requested_page}: "
                f"{result_text}"
            )

        except Exception as error:
            QMessageBox.critical(
                self.page,
                "Lỗi chạy từng bước",
                str(error),
            )

    # ========================================================
    # HIỂN THỊ BẢNG MÔ PHỎNG
    # ========================================================

    def prepare_simulation_table(
        self,
        result: PageReplacementResult,
    ) -> None:
        row_count = result.frame_count + 2
        column_count = len(result.references)

        self.simulation_table.clear()

        self.simulation_table.setRowCount(
            row_count
        )

        self.simulation_table.setColumnCount(
            column_count
        )

        self.simulation_table.setHorizontalHeaderLabels(
            [
                str(page)
                for page in result.references
            ]
        )

        vertical_headers = [
            "Page",
        ]

        vertical_headers.extend(
            [
                f"Frame {index + 1}"
                for index in range(
                    result.frame_count
                )
            ]
        )

        vertical_headers.append("Result")

        self.simulation_table.setVerticalHeaderLabels(
            vertical_headers
        )

        self.simulation_table.horizontalHeader().setDefaultSectionSize(
            55
        )

        self.simulation_table.verticalHeader().setDefaultSectionSize(
            34
        )

    def display_simulation(
        self,
        result: PageReplacementResult,
        visible_steps: int,
    ) -> None:
        self.prepare_simulation_table(result)

        visible_steps = max(
            0,
            min(
                visible_steps,
                len(result.steps),
            ),
        )

        for column in range(visible_steps):
            step = result.steps[column]

            # Hàng Page
            page_item = QTableWidgetItem(
                str(step.requested_page)
            )

            page_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            self.simulation_table.setItem(
                0,
                column,
                page_item,
            )

            # Các hàng Frame
            for frame_index in range(
                result.frame_count
            ):
                frame_value = step.frames[
                    frame_index
                ]

                frame_text = (
                    ""
                    if frame_value is None
                    else str(frame_value)
                )

                frame_item = QTableWidgetItem(
                    frame_text
                )

                frame_item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

                self.simulation_table.setItem(
                    frame_index + 1,
                    column,
                    frame_item,
                )

            # Hàng Result
            result_text = (
                "F"
                if step.is_fault
                else "H"
            )

            result_item = QTableWidgetItem(
                result_text
            )

            result_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            if step.is_fault:
                result_item.setBackground(
                    QColor("#fee2e2")
                )

                result_item.setForeground(
                    QColor("#b91c1c")
                )

            else:
                result_item.setBackground(
                    QColor("#dcfce7")
                )

                result_item.setForeground(
                    QColor("#15803d")
                )

            self.simulation_table.setItem(
                result.frame_count + 1,
                column,
                result_item,
            )

        self.simulation_table.resizeRowsToContents()

    # ========================================================
    # THỐNG KÊ
    # ========================================================

    def update_statistics(
        self,
        result: PageReplacementResult,
        visible_steps: int,
    ) -> None:
        visible_steps = max(
            0,
            min(
                visible_steps,
                len(result.steps),
            ),
        )

        visible = result.steps[
            :visible_steps
        ]

        faults = sum(
            1
            for step in visible
            if step.is_fault
        )

        hits = visible_steps - faults

        if visible_steps == 0:
            fault_rate = 0.0
            hit_rate = 0.0
            current_page = "-"

        else:
            fault_rate = (
                faults / visible_steps * 100
            )

            hit_rate = (
                hits / visible_steps * 100
            )

            current_page = str(
                visible[-1].requested_page
            )

        self.lbl_current_page.setText(
            f"Current Page: {current_page}"
        )

        self.lbl_current_step.setText(
            "Step: "
            f"{visible_steps}/{len(result.steps)}"
        )

        self.lbl_faults.setText(
            f"Page Faults: {faults}"
        )

        self.lbl_hits.setText(
            f"Page Hits: {hits}"
        )

        self.lbl_fault_rate.setText(
            f"Fault Rate: {fault_rate:.2f}%"
        )

        self.lbl_hit_rate.setText(
            f"Hit Rate: {hit_rate:.2f}%"
        )

    # ========================================================
    # SO SÁNH
    # ========================================================

    def compare_algorithms(self) -> None:
        try:
            references = self.parse_references()
            frame_count = self.frame_spin.value()

            results = (
                PageReplacementService.compare_all(
                    references=references,
                    frame_count=frame_count,
                )
            )

            self.comparison_table.setRowCount(
                len(results)
            )

            for row, result in enumerate(results):
                values = [
                    result.algorithm,
                    result.faults,
                    result.hits,
                    f"{result.fault_rate:.2f}%",
                    f"{result.hit_rate:.2f}%",
                ]

                for column, value in enumerate(values):
                    item = QTableWidgetItem(
                        str(value)
                    )

                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                    self.comparison_table.setItem(
                        row,
                        column,
                        item,
                    )

            self.comparison_table.resizeColumnsToContents()

            self.lbl_status.setText(
                "Trạng thái: Đã so sánh "
                "4 thuật toán"
            )

        except Exception as error:
            QMessageBox.critical(
                self.page,
                "Lỗi so sánh",
                str(error),
            )

    # ========================================================
    # RESET
    # ========================================================

    def mark_data_changed(self, *args) -> None:
        self.current_result = None
        self.current_step = 0
        self.data_changed = True

        self.simulation_table.clear()
        self.simulation_table.setRowCount(0)
        self.simulation_table.setColumnCount(0)

        self.reset_statistics()

        self.lbl_status.setText(
            "Trạng thái: Dữ liệu đã thay đổi"
        )

    def reset_statistics(self) -> None:
        self.lbl_current_page.setText(
            "Current Page: -"
        )

        self.lbl_current_step.setText(
            "Step: 0/0"
        )

        self.lbl_faults.setText(
            "Page Faults: 0"
        )

        self.lbl_hits.setText(
            "Page Hits: 0"
        )

        self.lbl_fault_rate.setText(
            "Fault Rate: 0%"
        )

        self.lbl_hit_rate.setText(
            "Hit Rate: 0%"
        )

    def reset_output(self) -> None:
        self.simulation_table.clear()
        self.simulation_table.setRowCount(0)
        self.simulation_table.setColumnCount(0)

        self.comparison_table.setRowCount(0)

        self.reset_statistics()

        self.lbl_status.setText(
            "Trạng thái: Sẵn sàng"
        )

    def reset_all(self) -> None:
        self.algorithm_combo.setCurrentText(
            "FIFO"
        )

        self.frame_spin.setValue(3)
        self.reference_input.clear()

        self.current_result = None
        self.current_step = 0
        self.data_changed = True

        self.reset_output()
