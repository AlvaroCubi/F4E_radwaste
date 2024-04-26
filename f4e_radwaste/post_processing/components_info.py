from typing import List, Tuple

from f4e_radwaste.data_formats.data_mass import DataMass
from f4e_radwaste.post_processing.calculate_dose_rates import DoseCalculator


class ComponentsInfo:
    def __init__(
        self,
        component_ids: List[List],
        data_mass: DataMass,
        dose_calculator: DoseCalculator,
    ):
        self.names, self.cell_ids = zip(*component_ids)

        mat_id_proportions = data_mass.calculate_material_id_proportions(self.cell_ids)

        self.cdr_factors = dose_calculator.calculate_cdr_factors_list(
            material_id_proportions=mat_id_proportions
        )

    def get_components(self) -> List[Tuple]:
        return list(zip(self.names, self.cell_ids))

    def get_all_cell_ids(self) -> List[int]:
        return list(set(sum(self.cell_ids, [])))
