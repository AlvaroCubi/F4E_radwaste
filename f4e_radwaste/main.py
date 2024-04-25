from pathlib import Path
from typing import Type

from f4e_radwaste.post_processing.post_processing import (
    ByComponentProcessor,
    FilteredProcessor,
    StandardProcessor,
)


def standard_process(input_path: Path) -> None:
    load_and_process_folder(input_path, StandardProcessor)


def filtered_process(input_path: Path) -> None:
    load_and_process_folder(input_path, FilteredProcessor)


def by_component_process(input_path: Path) -> None:
    load_and_process_folder(input_path, ByComponentProcessor)


def load_and_process_folder(
    input_path: Path, processor_type: Type[StandardProcessor]
) -> None:
    processor = processor_type(input_path)
    processor.process()


# if __name__ == "__main__":
#     by_component_process(Path(r"D:\WORK\test_ivvs_05"))
#     standard_process(Path(r"D:\WORK\tryingSimple\tests\old_data\ivvs_cart"))
