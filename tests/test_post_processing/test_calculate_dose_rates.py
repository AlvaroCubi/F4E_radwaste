import unittest

import pandas as pd

from f4e_radwaste.constants import KEY_CDR, KEY_DOSE_1_METER, KEY_MASS_GRAMS, KEY_VOXEL
from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity
from f4e_radwaste.post_processing.calculate_dose_rates import DoseCalculator


class CalculateDoseRatesTests(unittest.TestCase):
    def setUp(self):
        dose_1_m_factors = pd.Series(
            index=["He8", "Be7", "Be11", "B12", "B13", "B14"],
            data=[1.40e-08, 8.49e-10, 1.59e-08, 5.87e-10, 3.11e-09, 5.55e-08],
        )
        cdr_factors = pd.DataFrame(
            index=["He8", "Fe55", "Be11", "B12", "B13", "B14"],
            data={
                "H": [1.09e-07, 4.80e-09, 2.59e-07, 1.08e-08, 5.07e-08, 1.24e-06],
                "He": [2.17e-07, 9.53e-09, 5.07e-07, 2.11e-08, 9.98e-08, 2.41e-06],
                "Li": [2.51e-07, 1.10e-08, 5.80e-07, 2.42e-08, 1.15e-07, 2.74e-06],
            },
        )
        material_mix_12 = pd.Series(
            index=["He", "H"],
            data=[0.6, 0.4],
        )
        material_mix_99 = pd.Series(
            index=["Be", "B"],
            data=[0.5, 0.5],
        )
        material_mixes_by_id = {12: material_mix_12, 99: material_mix_99}
        self.dose_calculator = DoseCalculator(
            dose_1_m_factors=dose_1_m_factors,
            cdr_factors=cdr_factors,
            element_mix_by_material_id=material_mixes_by_id,
        )

        # DataMeshActivity
        data = {
            KEY_VOXEL: ["Component 1", "Component 2", "Component 3", "Component 4"],
            KEY_MASS_GRAMS: [5, 5, 5, 3],
            "H3": [4, 4, 4, 4],
            "Be11": [5, 5, 8e12, 5e99],
            "K42": [6, 6, 3, 6],
            "B14": [3, 3, 3, 3],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_VOXEL], inplace=True)
        self.data_mesh_activity = DataMeshActivity(df)

        # Material proportions
        self.material_proportions = [
            pd.Series({12: 1.0}),
            pd.Series({12: 1.0}),
            pd.Series({12: 1.0}),
            pd.Series({0: 1.0}),
        ]

    def test_calculate_doses(self):
        cdr_factors_list = self.dose_calculator.calculate_cdr_factors_list(
            self.material_proportions
        )
        result_data_mesh_activity = self.dose_calculator.calculate_doses(
            self.data_mesh_activity, cdr_factors_list
        )
        result_df = result_data_mesh_activity._dataframe

        # Dose at 1 meter
        expected_comp_1 = 5 * 1.59e-08 + 3 * 5.55e-08
        expected_comp_4 = 5e99 * 1.59e-08 + 3 * 5.55e-08

        self.assertAlmostEqual(
            result_df[KEY_DOSE_1_METER]["Component 1"], expected_comp_1
        )
        self.assertAlmostEqual(
            result_df[KEY_DOSE_1_METER]["Component 4"], expected_comp_4
        )

        # Contact dose rate
        factor_be11 = 5.07e-07 * 0.6 + 2.59e-07 * 0.4
        factor_b14 = 2.41e-06 * 0.6 + 1.24e-06 * 0.4
        expected_comp_1 = 5 * factor_be11 + 3 * factor_b14

        self.assertAlmostEqual(result_df[KEY_CDR][1], expected_comp_1)

    def test_calculate_cdr_factors_list(self):
        material_id_proportions = [pd.Series({12: 1.0}), pd.Series({12: 0.4, 99: 0.6})]
        cdr_factors_list = self.dose_calculator.calculate_cdr_factors_list(
            material_id_proportions
        )

        cdr_fe55_second_row = 0.4 * 0.4 * 4.80e-09 + 0.4 * 0.6 * 9.53e-09

        self.assertAlmostEqual(cdr_fe55_second_row, cdr_factors_list[1]["Fe55"])

    def test_calculate_element_mixes(self):
        material_id_proportions = [pd.Series({12: 1.0}), pd.Series({12: 0.4, 99: 0.6})]
        element_mixes = self.dose_calculator._calculate_element_mixes(
            material_id_proportions
        )

        self.assertAlmostEqual(0.4, element_mixes[0]["H"])
        self.assertAlmostEqual(0.4 * 0.4, element_mixes[1]["H"])
