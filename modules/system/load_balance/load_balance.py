#!/usr/bin/env python

import os.path
from pyomo.environ import Param, Var, Expression, Constraint, NonNegativeReals


def add_model_components(m, d, scenario_directory, horizon, stage):
    """

    :param m:
    :param d:
    :param scenario_directory:
    :param horizon:
    :param stage:
    :return:
    """

    # Penalty variables
    m.Overgeneration_MW = Var(m.LOAD_ZONES, m.TIMEPOINTS, within=NonNegativeReals)
    m.Unserved_Energy_MW = Var(m.LOAD_ZONES, m.TIMEPOINTS, within=NonNegativeReals)

    # TODO: load from file
    m.overgeneration_penalty_per_mw = Param(initialize=99999999)
    m.unserved_energy_penalty_per_mw = Param(initialize=99999999)

    d.energy_generation_components.append("Unserved_Energy_MW")
    d.energy_consumption_components.append("Overgeneration_MW")

    # TODO: figure out which module adds this to the load balance
    # 'energy generation' components
    m.load_mw = Param(m.LOAD_ZONES, m.TIMEPOINTS, within=NonNegativeReals)
    d.energy_consumption_components.append("load_mw")

    def total_generation_power_rule(mod, z, tmp):
        return sum(mod.Power_Provision_MW[g, tmp]
                   for g in mod.OPERATIONAL_GENERATORS_IN_TIMEPOINT[tmp]
                   if mod.load_zone[g] == z)
    m.Generation_in_Zone_MW = Expression(m.LOAD_ZONES, m.TIMEPOINTS,
                                         rule=total_generation_power_rule)
    d.energy_generation_components.append("Generation_in_Zone_MW")

    def total_energy_production_rule(mod, z, tmp):
        """
        Sum across all energy generation components added by other modules for
        each zone and timepoint.
        :param mod:
        :param z:
        :param tmp:
        :return:
        """
        return sum(getattr(mod, component)[z, tmp]
                   for component in d.energy_generation_components)
    m.Total_Energy_Production_MW = Expression(
        m.LOAD_ZONES, m.TIMEPOINTS,
        rule=total_energy_production_rule)

    def total_energy_consumption_rule(mod, z, tmp):
        """
        Sum across all energy consumption components added by other modules
        for each zone and timepoint.
        :param mod:
        :param z:
        :param tmp:
        :return:
        """
        return sum(getattr(mod, component)[z, tmp]
                   for component in d.energy_consumption_components)
    m.Total_Energy_Consumption_MW = Expression(
        m.LOAD_ZONES, m.TIMEPOINTS,
        rule=total_energy_consumption_rule)

    def meet_load_rule(mod, z, tmp):
        return mod.Total_Energy_Production_MW[z, tmp] \
               == mod.Total_Energy_Consumption_MW[z, tmp]

    m.Meet_Load_Constraint = Constraint(m.LOAD_ZONES, m.TIMEPOINTS,
                                        rule=meet_load_rule)


def load_model_data(m, data_portal, scenario_directory, horizon, stage):
    data_portal.load(filename=os.path.join(scenario_directory, horizon, stage,
                                           "inputs", "load_mw.tab"),
                     param=m.load_mw
                     )


def export_results(scenario_directory, horizon, stage, m):
    for z in getattr(m, "LOAD_ZONES"):
        for tmp in getattr(m, "TIMEPOINTS"):
            print("Overgeneration_MW[" + str(z) + ", " + str(tmp) + "]: "
                  + str(m.Overgeneration_MW[z, tmp].value)
                  )

    for z in getattr(m, "LOAD_ZONES"):
        for tmp in getattr(m, "TIMEPOINTS"):
            print("Unserved_Energy_MW[" + str(z) + ", " + str(tmp) + "]: "
                  + str(m.Unserved_Energy_MW[z, tmp].value)
                  )


def save_duals(m):
    m.constraint_indices["Meet_Load_Constraint"] = \
        ["zone", "timepoint", "dual"]