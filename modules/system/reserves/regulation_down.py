#!/usr/bin/env python

import csv
import os.path
from pyomo.environ import Set

from reserve_requirements import add_generic_reserve_components


def add_model_components(m, d, scenario_directory, horizon, stage):
    """

    :param m:
    :param d:
    :param scenario_directory:
    :param horizon:
    :param stage:
    :return:
    """

    # TODO: flexible, as requirement does not have to be specified for all
    # timepoints, but has memory implications
    m.REGULATION_DOWN_ZONE_TIMEPOINTS = Set(dimen=2)
    m.REGULATION_DOWN_ZONES = \
        Set(initialize=
            lambda mod: set(i[0] for i in mod.REGULATION_DOWN_ZONE_TIMEPOINTS)
            )

    add_generic_reserve_components(
        m,
        d,
        reserve_zone_param="regulation_down_zone",
        reserve_zone_timepoint_set="REGULATION_DOWN_ZONE_TIMEPOINTS",
        reserve_violation_variable="Regulation_Down_Violation_MW",
        reserve_violation_penalty_param=
        "regulation_down_violation_penalty_per_mw",
        reserve_requirement_param="regulation_down_requirement_mw",
        reserve_generator_set="REGULATION_DOWN_RESOURCES",
        generator_reserve_provision_variable="Provide_Regulation_Down_MW",
        total_reserve_provision_expression="Total_Regulation_Down_Provision_MW",
        meet_reserve_constraint="Meet_Regulation_Down_Constraint",
        objective_function_reserve_penalty_cost_component=
        "Regulation_Down_Penalty_Cost"
        )


def load_model_data(m, data_portal, scenario_directory, horizon, stage):
    data_portal.load(filename=os.path.join(scenario_directory, horizon, stage,
                                           "inputs",
                                           "regulation_down_requirement.tab"),
                     index=m.REGULATION_DOWN_ZONE_TIMEPOINTS,
                     param=m.regulation_down_requirement_mw
                     )


def export_results(scenario_directory, horizon, stage, m):
    """

    :param scenario_directory:
    :param horizon:
    :param stage:
    :param m:
    :return:
    """
    with open(os.path.join(scenario_directory, horizon, stage, "results",
                           "regulation_down_violation.csv"), "wb") \
            as results_file:
        writer = csv.writer(results_file)
        writer.writerow(["zone", "timepoint",
                         "regulation_down_violation_mw"]
                        )
        for (z, tmp) in getattr(m, "REGULATION_DOWN_ZONE_TIMEPOINTS"):
            writer.writerow([
                z,
                tmp,
                m.Regulation_Down_Violation_MW[z, tmp].value]
            )


def save_duals(m):
    m.constraint_indices["Meet_Regulation_Down_Constraint"] = \
        ["zone", "timepoint", "dual"]
