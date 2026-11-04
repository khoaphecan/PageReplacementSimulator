from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PageStep:
    """
    Kết quả của một lần truy cập trang.
    """

    step_number: int
    requested_page: int
    frames: list[int | None]
    is_fault: bool
    replaced_page: int | None = None


@dataclass
class PageReplacementResult:
    """
    Kết quả toàn bộ quá trình thay thế trang.
    """

    algorithm: str
    references: list[int]
    frame_count: int
    steps: list[PageStep]
    faults: int
    hits: int

    @property
    def fault_rate(self) -> float:
        if not self.references:
            return 0.0

        return self.faults / len(self.references) * 100

    @property
    def hit_rate(self) -> float:
        if not self.references:
            return 0.0

        return self.hits / len(self.references) * 100


class PageReplacementService:
    """
    Thực hiện các giải thuật thay thế trang:
    - Optimal
    - FIFO
    - Second Chance
    - LRU
    """

    @staticmethod
    def run(
        algorithm: str,
        references: list[int],
        frame_count: int,
    ) -> PageReplacementResult:
        if not references:
            raise ValueError(
                "Chuỗi tham chiếu trang đang trống."
            )

        if frame_count <= 0:
            raise ValueError(
                "Số frame phải lớn hơn 0."
            )

        normalized = algorithm.strip().lower()

        if normalized == "optimal":
            return PageReplacementService._run_optimal(
                references,
                frame_count,
            )

        if normalized == "fifo":
            return PageReplacementService._run_fifo(
                references,
                frame_count,
            )

        if normalized in {
            "second chance",
            "second chance / finufo",
            "finufo",
        }:
            return PageReplacementService._run_second_chance(
                references,
                frame_count,
            )

        if normalized == "lru":
            return PageReplacementService._run_lru(
                references,
                frame_count,
            )

        raise ValueError(
            f"Thuật toán '{algorithm}' chưa được hỗ trợ."
        )

    # ========================================================
    # FIFO
    # ========================================================

    @staticmethod
    def _run_fifo(
        references: list[int],
        frame_count: int,
    ) -> PageReplacementResult:
        frames: list[int | None] = [
            None
            for _ in range(frame_count)
        ]

        next_replace = 0
        faults = 0
        hits = 0
        steps: list[PageStep] = []

        for index, page in enumerate(references):
            replaced_page: int | None = None

            if page in frames:
                hits += 1
                is_fault = False

            else:
                faults += 1
                is_fault = True

                if None in frames:
                    empty_index = frames.index(None)
                    frames[empty_index] = page

                else:
                    replaced_page = frames[next_replace]
                    frames[next_replace] = page

                    next_replace = (
                        next_replace + 1
                    ) % frame_count

            steps.append(
                PageStep(
                    step_number=index + 1,
                    requested_page=page,
                    frames=frames.copy(),
                    is_fault=is_fault,
                    replaced_page=replaced_page,
                )
            )

        return PageReplacementResult(
            algorithm="FIFO",
            references=references.copy(),
            frame_count=frame_count,
            steps=steps,
            faults=faults,
            hits=hits,
        )

    # ========================================================
    # OPTIMAL
    # ========================================================

    @staticmethod
    def _run_optimal(
        references: list[int],
        frame_count: int,
    ) -> PageReplacementResult:
        frames: list[int | None] = [
            None
            for _ in range(frame_count)
        ]

        faults = 0
        hits = 0
        steps: list[PageStep] = []

        for index, page in enumerate(references):
            replaced_page: int | None = None

            if page in frames:
                hits += 1
                is_fault = False

            else:
                faults += 1
                is_fault = True

                if None in frames:
                    empty_index = frames.index(None)
                    frames[empty_index] = page

                else:
                    victim_index = (
                        PageReplacementService
                        ._find_optimal_victim(
                            frames=frames,
                            references=references,
                            current_index=index,
                        )
                    )

                    replaced_page = frames[victim_index]
                    frames[victim_index] = page

            steps.append(
                PageStep(
                    step_number=index + 1,
                    requested_page=page,
                    frames=frames.copy(),
                    is_fault=is_fault,
                    replaced_page=replaced_page,
                )
            )

        return PageReplacementResult(
            algorithm="Optimal",
            references=references.copy(),
            frame_count=frame_count,
            steps=steps,
            faults=faults,
            hits=hits,
        )

    @staticmethod
    def _find_optimal_victim(
        frames: list[int | None],
        references: list[int],
        current_index: int,
    ) -> int:
        """
        Chọn trang có lần sử dụng tiếp theo xa nhất.

        Nếu một trang không xuất hiện lại thì thay trang đó.
        """

        farthest_distance = -1
        victim_index = 0

        for frame_index, page in enumerate(frames):
            if page is None:
                return frame_index

            try:
                next_use = references.index(
                    page,
                    current_index + 1,
                )

            except ValueError:
                # Trang không còn được dùng lại.
                return frame_index

            if next_use > farthest_distance:
                farthest_distance = next_use
                victim_index = frame_index

        return victim_index

    # ========================================================
    # LRU
    # ========================================================

    @staticmethod
    def _run_lru(
        references: list[int],
        frame_count: int,
    ) -> PageReplacementResult:
        frames: list[int | None] = [
            None
            for _ in range(frame_count)
        ]

        # page -> bước truy cập gần nhất
        last_used: dict[int, int] = {}

        faults = 0
        hits = 0
        steps: list[PageStep] = []

        for index, page in enumerate(references):
            replaced_page: int | None = None

            if page in frames:
                hits += 1
                is_fault = False

            else:
                faults += 1
                is_fault = True

                if None in frames:
                    empty_index = frames.index(None)
                    frames[empty_index] = page

                else:
                    victim_page = min(
                        (
                            frame
                            for frame in frames
                            if frame is not None
                        ),
                        key=lambda item: last_used.get(
                            item,
                            -1,
                        ),
                    )

                    victim_index = frames.index(
                        victim_page
                    )

                    replaced_page = victim_page
                    frames[victim_index] = page

                    last_used.pop(
                        victim_page,
                        None,
                    )

            last_used[page] = index

            steps.append(
                PageStep(
                    step_number=index + 1,
                    requested_page=page,
                    frames=frames.copy(),
                    is_fault=is_fault,
                    replaced_page=replaced_page,
                )
            )

        return PageReplacementResult(
            algorithm="LRU",
            references=references.copy(),
            frame_count=frame_count,
            steps=steps,
            faults=faults,
            hits=hits,
        )

    # ========================================================
    # SECOND CHANCE / FINUFO
    # ========================================================

    @staticmethod
    def _run_second_chance(
        references: list[int],
        frame_count: int,
    ) -> PageReplacementResult:
        frames: list[int | None] = [
            None
            for _ in range(frame_count)
        ]

        reference_bits = [
            0
            for _ in range(frame_count)
        ]

        pointer = 0
        faults = 0
        hits = 0
        steps: list[PageStep] = []

        for index, page in enumerate(references):
            replaced_page: int | None = None

            if page in frames:
                hits += 1
                is_fault = False

                frame_index = frames.index(page)
                reference_bits[frame_index] = 1

            else:
                faults += 1
                is_fault = True

                while True:
                    if frames[pointer] is None:
                        frames[pointer] = page
                        reference_bits[pointer] = 1

                        pointer = (
                            pointer + 1
                        ) % frame_count

                        break

                    if reference_bits[pointer] == 0:
                        replaced_page = frames[pointer]

                        frames[pointer] = page
                        reference_bits[pointer] = 1

                        pointer = (
                            pointer + 1
                        ) % frame_count

                        break

                    # Cho trang hiện tại cơ hội thứ hai.
                    reference_bits[pointer] = 0

                    pointer = (
                        pointer + 1
                    ) % frame_count

            steps.append(
                PageStep(
                    step_number=index + 1,
                    requested_page=page,
                    frames=frames.copy(),
                    is_fault=is_fault,
                    replaced_page=replaced_page,
                )
            )

        return PageReplacementResult(
            algorithm="Second Chance",
            references=references.copy(),
            frame_count=frame_count,
            steps=steps,
            faults=faults,
            hits=hits,
        )

    # ========================================================
    # SO SÁNH
    # ========================================================

    @staticmethod
    def compare_all(
        references: list[int],
        frame_count: int,
    ) -> list[PageReplacementResult]:
        algorithms = [
            "Optimal",
            "FIFO",
            "Second Chance",
            "LRU",
        ]

        return [
            PageReplacementService.run(
                algorithm=algorithm,
                references=references,
                frame_count=frame_count,
            )
            for algorithm in algorithms
        ]
