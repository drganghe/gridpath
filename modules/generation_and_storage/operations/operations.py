#!/usr/bin/env python

"""
Describe operational constraints on the generation infrastructure.
"""
from csv import reader
import os.path
from pandas import read_csv
from pyomo.environ import Param, Set, Var, Expression, Constraint, \
    NonNegativeReals, PercentFraction, BuildAction

from modules.auxiliary.auxiliary import check_list_items_are_unique, \
    find_list_item_position, make_resource_time_var_df, \
    load_operational_type_modules


def determine_dynamic_components(d, scenario_directory, horizon, stage):
    """
    Determine which operational type modules will be needed based on the
    operational types in the input data.
    :param d:
    :param scenario_directory:
    :param horizon:
    :param stage:
    :return:
    """

    # Generator capabilities
    d.headroom_variables = dict()
    d.footroom_variables = dict()

    with open(os.path.join(scenario_directory, "inputs", "resources.tab"),
              "rb") as generation_capacity_file:
        generation_capacity_reader = reader(generation_capacity_file,
                                            delimiter="\t")
        headers = generation_capacity_reader.next()
        # Check that columns are not repeated
        check_list_items_are_unique(headers)
        for row in generation_capacity_reader:
            # Get generator name; we have checked that columns names are unique
            # so can expect a single-item list here and get 0th element
            generator = row[find_list_item_position(headers, "RESOURCES")[0]]
            # All generators get the following variables
            d.headroom_variables[generator] = list()
            d.footroom_variables[generator] = list()
            # In addition, some generators get the variables associated with
            # provision of other services (e.g. reserves) if flagged
            # Figure out which these are here based on whether a reserve zone
            # is specified ("." = no zone specified, so resource does not
            # contribute to this reserve requirement)
            # Generators that can provide upward load-following reserves
            if row[find_list_item_position(headers, "lf_reserves_up_zone")[0]] \
                    != ".":
                d.headroom_variables[generator].append(
                    "Provide_LF_Reserves_Up_MW")
            # Generators that can provide upward regulation
            if row[find_list_item_position(headers, "regulation_up_zone")[0]] \
                    != ".":
                d.headroom_variables[generator].append(
                    "Provide_Regulation_Up_MW")
            # Generators that can provide downward load-following reserves
            if row[find_list_item_position(
                    headers, "lf_reserves_down_zone")[0]] \
                    != ".":
                d.footroom_variables[generator].append(
                    "Provide_LF_Reserves_Down_MW")
            # Generators that can provide downward regulation
            if row[find_list_item_position(
                    headers, "regulation_down_zone")[0]] \
                    != ".":
                d.footroom_variables[generator].append(
                    "Provide_Regulation_Down_MW")

    # TODO: ugly; make this more uniform with the above rather
    # than having two separate methods
    # Get the operational type of each generator
    dynamic_components = \
        read_csv(os.path.join(scenario_directory, "inputs", "resources.tab"),
                 sep="\t", usecols=["RESOURCES", "operational_type"]
                 )

    # Required modules are the unique set of generator operational types
    # This list will be used to know which operational modules to load
    d.required_operational_modules = \
        dynamic_components.operational_type.unique()


def add_model_components(m, d, scenario_directory, horizon, stage):
    """

    :param m:
    :param d:
    :param scenario_directory:
    :param horizon:
    :param stage:
    :return:
    """

    # ### Params defined for all generators ### #
    # These are loaded via the DataPortal, not dynamically
    # Variable O&M cost
    m.variable_om_cost_per_mwh = Param(m.RESOURCES, within=NonNegativeReals)

    # These params will be used to initialize subsets

    # Operational type
    m.operational_type = Param(m.RESOURCES)

    # TODO: this should be built below with the dynamic components
    m.min_stable_level_fraction = Param(m.RESOURCES,
                                        within=PercentFraction)

    ###
    # Services that generators can provide that modify the operational modules
    ###

    def determine_reserve_resources(mod, reserve_type, reserve_resource_set):
        """

        :param mod:
        :param reserve_type:
        :param reserve_resource_set:
        :return:
        """
        dynamic_components = \
            read_csv(
                os.path.join(scenario_directory, "inputs", "resources.tab"),
                sep="\t", usecols=["RESOURCES",
                                   reserve_type]
                )

        for row in zip(dynamic_components["RESOURCES"],
                       dynamic_components[reserve_type]):
            if row[1] != ".":
                getattr(mod, reserve_resource_set).add(row[0])
            else:
                pass


    # TODO: should probably be individual modules
    # Subsets of generators by services they can provide
    # Sets of generators that can provide headroom services
    m.LF_RESERVES_UP_RESOURCES = Set(within=m.RESOURCES)
    m.lf_reserves_up_zone = Param(m.LF_RESERVES_UP_RESOURCES)
    # m.LFReservesUpResourcesBuild = \
    #     BuildAction(rule=
    #                 determine_reserve_resources)
    m.REGULATION_UP_RESOURCES = Set(within=m.RESOURCES)
    m.regulation_up_zone = Param(m.REGULATION_UP_RESOURCES)
    # m.RegulationUpResourcesBuild = \
    #     BuildAction(rule=
    #                 determine_reserve_resources(
    #                     m, "regulation_up_zone","REGULATION_UP_RESOURCES")
    #                 )

    # Sets of generators that can provide footroom services
    m.LF_RESERVES_DOWN_RESOURCES = Set(within=m.RESOURCES)
    m.lf_reserves_down_zone = Param(m.LF_RESERVES_DOWN_RESOURCES)
    # m.LFReservesDownResourcesBuild = \
    #     BuildAction(rule=
    #                 determine_reserve_resources(
    #                     m, "lf_reserves_down_zone","LF_RESERVES_DOWN_RESOURCES")
    #                 )
    m.REGULATION_DOWN_RESOURCES = Set(within=m.RESOURCES)
    m.regulation_down_zone = Param(m.REGULATION_DOWN_RESOURCES)
    # m.RegulationDownResourcesBuild = \
    #     BuildAction(rule=
    #                 determine_reserve_resources(
    #                     m, "regulation_down_zone","REGULATION_DOWN_RESOURCES")
    #                 )

    # TODO: maybe these should be created by the reserves module?
    m.LF_RESERVES_UP_RESOURCE_OPERATIONAL_TIMEPOINTS = \
        Set(dimen=2,
            rule=lambda mod:
            set((g, tmp) for (g, tmp) in mod.RESOURCE_OPERATIONAL_TIMEPOINTS
                if g in mod.LF_RESERVES_UP_RESOURCES))

    m.LF_RESERVES_DOWN_RESOURCE_OPERATIONAL_TIMEPOINTS = \
        Set(dimen=2,
            rule=lambda mod:
            set((g, tmp) for (g, tmp) in mod.RESOURCE_OPERATIONAL_TIMEPOINTS
                if g in mod.LF_RESERVES_DOWN_RESOURCES))

    m.REGULATION_UP_RESOURCE_OPERATIONAL_TIMEPOINTS = \
        Set(dimen=2,
            rule=lambda mod:
            set((g, tmp) for (g, tmp) in mod.RESOURCE_OPERATIONAL_TIMEPOINTS
                if g in mod.REGULATION_UP_RESOURCES))

    m.REGULATION_DOWN_RESOURCE_OPERATIONAL_TIMEPOINTS = \
        Set(dimen=2,
            rule=lambda mod:
            set((g, tmp) for (g, tmp) in mod.RESOURCE_OPERATIONAL_TIMEPOINTS
                if g in mod.REGULATION_DOWN_RESOURCES))

    # TODO: these are used to modify the operational modules and should
    # eventually be taken out into their own submodules
    # Headroom and footroom services
    m.Provide_LF_Reserves_Up_MW = Var(
        m.LF_RESERVES_UP_RESOURCE_OPERATIONAL_TIMEPOINTS,
        within=NonNegativeReals)
    m.Provide_Regulation_Up_MW = Var(
        m.REGULATION_UP_RESOURCE_OPERATIONAL_TIMEPOINTS,
        within=NonNegativeReals)
    m.Provide_LF_Reserves_Down_MW = Var(
        m.LF_RESERVES_DOWN_RESOURCE_OPERATIONAL_TIMEPOINTS,
        within=NonNegativeReals)
    m.Provide_Regulation_Down_MW = Var(
        m.REGULATION_DOWN_RESOURCE_OPERATIONAL_TIMEPOINTS,
        within=NonNegativeReals)

    # Aggregate the headroom and footroom decision variables respectively for
    # use by the operational modules
    def headroom_provision_rule(mod, g, tmp):
        return sum(getattr(mod, c)[g, tmp] for c in d.headroom_variables[g])
    m.Headroom_Provision_MW = Expression(m.RESOURCE_OPERATIONAL_TIMEPOINTS,
                                         rule=headroom_provision_rule)

    def footroom_provision_rule(mod, g, tmp):
        return sum(getattr(mod, c)[g, tmp] for c in d.footroom_variables[g])
    m.Footroom_Provision_MW = Expression(m.RESOURCE_OPERATIONAL_TIMEPOINTS,
                                         rule=footroom_provision_rule)

    # ### ### ### ### #

    # From here, the operational modules determine how the model components are
    # formulated
    m.required_operational_modules = d.required_operational_modules
    # Import needed operational modules
    imported_operational_modules = load_operational_type_modules(m)

    # First, add any components specific to the operational modules
    for op_m in m.required_operational_modules:
        imp_op_m = imported_operational_modules[op_m]
        if hasattr(imp_op_m, "add_module_specific_components"):
            imp_op_m.add_module_specific_components(m, scenario_directory)

    # Then define operational constraints for all generators
    # Get rules from the generator's operational module
    def power_provision_rule(mod, g, tmp):
        """
        Power provision is a variable for some generators, but not others; get
        the appropriate expression for each generator based on its operational
        type.
        :param mod:
        :param g:
        :param tmp:
        :return:
        """
        gen_op_type = mod.operational_type[g]
        return imported_operational_modules[gen_op_type].\
            power_provision_rule(mod, g, tmp)
    m.Power_Provision_MW = Expression(m.RESOURCE_OPERATIONAL_TIMEPOINTS,
                                      rule=power_provision_rule)

    def max_power_rule(mod, g, tmp):
        """
        The maximum power and headroom services from a generator; get the
        appropriate variables to be constrained from the generator's
        operational module.
        :param mod:
        :param g:
        :param tmp:
        :return:
        """
        gen_op_type = mod.operational_type[g]
        return imported_operational_modules[gen_op_type].\
            max_power_rule(mod, g, tmp)
    m.Max_Power_Constraint = Constraint(m.RESOURCE_OPERATIONAL_TIMEPOINTS,
                                        rule=max_power_rule)

    def min_power_rule(mod, g, tmp):
        """
        The minimum amount of power a generator must provide in a timepoint; if
        providing footroom services add those to the minimum level; get the
        appropriate variables to be constrained from the generator's
        operational module.
        :param mod:
        :param g:
        :param tmp:
        :return:
        """
        gen_op_type = mod.operational_type[g]
        return imported_operational_modules[gen_op_type]. \
            min_power_rule(mod, g, tmp)
    m.Min_Power_Constraint = Constraint(m.RESOURCE_OPERATIONAL_TIMEPOINTS,
                                        rule=min_power_rule)

    # Add generation to load balance constraint
    def total_power_production_rule(mod, z, tmp):
        return sum(mod.Power_Provision_MW[g, tmp]
                   for g in mod.OPERATIONAL_RESOURCES_IN_TIMEPOINT[tmp]
                   if mod.load_zone[g] == z)
    m.Power_Production_in_Zone_MW = \
        Expression(m.LOAD_ZONES, m.TIMEPOINTS,
                   rule=total_power_production_rule)
    d.load_balance_production_components.append("Power_Production_in_Zone_MW")

    # Keep track of curtailment
    def curtailment_rule(mod, g, tmp):
        """
        Keep track of curtailment to make it easier to calculate total
        curtailed RPS energy for example.
        :param mod:
        :param g:
        :param tmp:
        :return:
        """
        gen_op_type = mod.operational_type[g]
        return imported_operational_modules[gen_op_type]. \
            curtailment_rule(mod, g, tmp)

    # TODO: possibly create this only if needed by another module?
    m.Curtailment_MW = Expression(m.RESOURCE_OPERATIONAL_TIMEPOINTS,
                                  rule=curtailment_rule)


def load_model_data(m, data_portal, scenario_directory, horizon, stage):
    """
    Traverse required operational modules and load any module-specific data.
    :param m:
    :param data_portal:
    :param scenario_directory:
    :param horizon:
    :param stage:
    :return:
    """

    data_portal.load(filename=os.path.join(scenario_directory,
                                           "inputs", "resources.tab"),
                     index=m.RESOURCES,
                     select=("RESOURCES", "operational_type",
                             "min_stable_level_fraction",
                             "variable_om_cost_per_mwh"),
                     param=(m.operational_type,
                            m.min_stable_level_fraction,
                            m.variable_om_cost_per_mwh)
                     )

    data_portal.load(filename=os.path.join(scenario_directory,
                                           "inputs", "resources.tab"),
                     select=("RESOURCES", "lf_reserves_up_zone"),
                     param=(m.lf_reserves_up_zone,)
                     )

    data_portal.load(filename=os.path.join(scenario_directory,
                                           "inputs", "resources.tab"),
                     select=("RESOURCES", "lf_reserves_down_zone"),
                     param=m.lf_reserves_down_zone
                     )

    data_portal.load(filename=os.path.join(scenario_directory,
                                           "inputs", "resources.tab"),
                     select=("RESOURCES", "regulation_up_zone"),
                     param=m.regulation_up_zone
                     )

    data_portal.load(filename=os.path.join(scenario_directory,
                                           "inputs", "resources.tab"),
                     select=("RESOURCES", "regulation_down_zone"),
                     param=m.regulation_down_zone
                     )

    data_portal.data()['LF_RESERVES_UP_RESOURCES'] = {
        None: data_portal.data()['lf_reserves_up_zone'].keys()
    }
    data_portal.data()['LF_RESERVES_DOWN_RESOURCES'] = {
        None: data_portal.data()['lf_reserves_down_zone'].keys()
    }
    data_portal.data()['REGULATION_UP_RESOURCES'] = {
        None: data_portal.data()['regulation_up_zone'].keys()
    }
    data_portal.data()['REGULATION_DOWN_RESOURCES'] = {
        None: data_portal.data()['regulation_down_zone'].keys()
    }

    imported_operational_modules = load_operational_type_modules(m)
    for op_m in m.required_operational_modules:
        if hasattr(imported_operational_modules[op_m],
                   "load_module_specific_data"):
            imported_operational_modules[op_m].load_module_specific_data(
                m, data_portal, scenario_directory, horizon, stage)
        else:
            pass


def export_results(scenario_directory, horizon, stage, m):
    """
    Export operations results.
    :param scenario_directory:
    :param horizon:
    :param stage:
    :param m:
    :return:
    """

    m.module_specific_df = []

    imported_operational_modules = load_operational_type_modules(m)
    for op_m in m.required_operational_modules:
        if hasattr(imported_operational_modules[op_m],
                   "export_module_specific_results"):
            imported_operational_modules[op_m].export_module_specific_results(
                m)
        else:
            pass

    # Make pandas dataframes for the various operations variables results
    power_df = make_resource_time_var_df(
        m,
        "RESOURCE_OPERATIONAL_TIMEPOINTS",
        "Power_Provision_MW",
        ["resource", "timepoint"],
        "power_mw"
        )

    if len("LF_RESERVES_UP_RESOURCE_OPERATIONAL_TIMEPOINTS") > 0:
        lf_reserves_up_df = make_resource_time_var_df(
            m,
            "LF_RESERVES_UP_RESOURCE_OPERATIONAL_TIMEPOINTS",
            "Provide_LF_Reserves_Up_MW",
            ["resource", "timepoint"],
            "lf_reserves_up_mw"
        )
    else:
        lf_reserves_up_df = []

    if len("LF_RESERVES_DOWN_RESOURCE_OPERATIONAL_TIMEPOINTS") > 0:
        lf_reserves_down_df = make_resource_time_var_df(
            m,
            "LF_RESERVES_DOWN_RESOURCE_OPERATIONAL_TIMEPOINTS",
            "Provide_LF_Reserves_Down_MW",
            ["resource", "timepoint"],
            "lf_reserves_down_mw"
        )
    else:
        lf_reserves_down_df = []

    if len("REGULATION_UP_RESOURCE_OPERATIONAL_TIMEPOINTS") > 0:
        regulation_up_df = make_resource_time_var_df(
            m,
            "REGULATION_UP_RESOURCE_OPERATIONAL_TIMEPOINTS",
            "Provide_Regulation_Up_MW",
            ["resource", "timepoint"],
            "regulation_up_mw"
        )
    else:
        regulation_up_df = []

    if len("REGULATION_DOWN_RESOURCE_OPERATIONAL_TIMEPOINTS") > 0:
        regulation_down_df = make_resource_time_var_df(
            m,
            "REGULATION_DOWN_RESOURCE_OPERATIONAL_TIMEPOINTS",
            "Provide_Regulation_Down_MW",
            ["resource", "timepoint"],
            "regulation_down_mw"
        )
    else:
        regulation_down_df = []

    dfs_to_merge = [power_df] + m.module_specific_df + \
                   [lf_reserves_up_df, lf_reserves_down_df,
                    regulation_up_df, regulation_down_df]

    df_for_export = reduce(lambda left, right:
                           left.join(right, how="outer"),
                           dfs_to_merge)
    df_for_export.to_csv(
        os.path.join(scenario_directory, horizon, stage, "results",
                     "operations.csv"),
        header=True, index=True)
