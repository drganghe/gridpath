import csv
import os.path
import sqlite3

SCENARIO_ID = 1
io = sqlite3.connect(
    os.path.join(os.getcwd(), 'io.db')
)
c = io.cursor()

HORIZON_SCENARIO_ID = c.execute(
    """SELECT horizon_scenario_id
       FROM scenarios
       WHERE scenario_id = {};""".format(SCENARIO_ID)
).fetchone()[0]

TIMEPOINT_SCENARIO_ID = c.execute(
    """SELECT timepoint_scenario_id
       FROM scenarios
       WHERE scenario_id = {};""".format(SCENARIO_ID)
).fetchone()[0]

PERIOD_SCENARIO_ID = c.execute(
    """SELECT period_scenario_id
       FROM scenarios
       WHERE scenario_id = {};""".format(SCENARIO_ID)
).fetchone()[0]

LOAD_ZONE_SCENARIO_ID = c.execute(
    """SELECT load_zone_scenario_id
       FROM scenarios
       WHERE scenario_id = {};""".format(SCENARIO_ID)
).fetchone()[0]

LF_RESERVES_UP_BA_SCENARIO_ID = c.execute(
    """SELECT lf_reserves_up_ba_scenario_id
       FROM scenarios
       WHERE scenario_id = {};""".format(SCENARIO_ID)
).fetchone()[0]

LF_RESERVES_DOWN_BA_SCENARIO_ID = c.execute(
    """SELECT lf_reserves_down_ba_scenario_id
       FROM scenarios
       WHERE scenario_id = {};""".format(SCENARIO_ID)
).fetchone()[0]

RPS_ZONE_SCENARIO_ID = c.execute(
    """SELECT rps_zone_scenario_id
       FROM scenarios
       WHERE scenario_id = {};""".format(SCENARIO_ID)
).fetchone()[0]

PROJECT_LOAD_ZONE_SCENARIO_ID = c.execute(
    """SELECT project_load_zone_scenario_id
       FROM scenarios
       WHERE scenario_id = {};""".format(SCENARIO_ID)
).fetchone()[0]

PROJECT_LF_RESERVES_UP_BA_SCENARIO_ID = c.execute(
    """SELECT project_lf_reserves_up_ba_scenario_id
       FROM scenarios
       WHERE scenario_id = {};""".format(SCENARIO_ID)
).fetchone()[0]

PROJECT_LF_RESERVES_DOWN_BA_SCENARIO_ID = c.execute(
    """SELECT project_lf_reserves_down_ba_scenario_id
       FROM scenarios
       WHERE scenario_id = {};""".format(SCENARIO_ID)
).fetchone()[0]

PROJECT_RPS_ZONE_SCENARIO_ID = c.execute(
    """SELECT project_rps_zone_scenario_id
       FROM scenarios
       WHERE scenario_id = {};""".format(SCENARIO_ID)
).fetchone()[0]

EXISTING_PROJECT_SCENARIO_ID = c.execute(
    """SELECT existing_project_scenario_id
       FROM scenarios
       WHERE scenario_id = {};""".format(SCENARIO_ID)
).fetchone()[0]

NEW_PROJECT_SCENARIO_ID = c.execute(
    """SELECT new_project_scenario_id
       FROM scenarios
       WHERE scenario_id = {};""".format(SCENARIO_ID)
).fetchone()[0]

EXISTING_PROJECT_CAPACITY_SCENARIO_ID = c.execute(
    """SELECT existing_project_capacity_scenario_id
       FROM scenarios
       WHERE scenario_id = {};""".format(SCENARIO_ID)
).fetchone()[0]

NEW_PROJECT_COST_SCENARIO_ID = c.execute(
    """SELECT new_project_cost_scenario_id
       FROM scenarios
       WHERE scenario_id = {};""".format(SCENARIO_ID)
).fetchone()[0]


# periods.tab
with open(os.path.join(os.getcwd(), "temp_inputs", "periods.tab"), "w") as \
        periods_tab_file:
    writer = csv.writer(periods_tab_file, delimiter="\t")

    # Write header
    writer.writerow(["PERIODS", "discount_factor", "number_years_represented"])

    periods = c.execute(
        """SELECT period, discount_factor, number_years_represented
           FROM periods
           WHERE period_scenario_id = {};""".format(
            PERIOD_SCENARIO_ID
        )
    ).fetchall()

    for row in periods:
        writer.writerow(row)

# horizons.tab
with open(os.path.join(os.getcwd(), "temp_inputs", "horizons.tab"), "w") as \
        horizons_tab_file:
    writer = csv.writer(horizons_tab_file, delimiter="\t")

    # Write header
    writer.writerow(["HORIZONS", "boundary", "horizon_weight"])

    horizons = c.execute(
        """SELECT horizon, boundary, horizon_weight
           FROM horizons
           WHERE period_scenario_id = {}
           AND horizon_scenario_id = {};""".format(
            PERIOD_SCENARIO_ID, HORIZON_SCENARIO_ID
        )
    ).fetchall()

    for row in horizons:
        writer.writerow(row)

# timepoints.tab
with open(os.path.join(os.getcwd(), "temp_inputs", "timepoints.tab"), "w") as \
        timepoints_tab_file:
    writer = csv.writer(timepoints_tab_file, delimiter="\t")

    # Write header
    writer.writerow(["TIMEPOINTS", "period", "horizon",
                     "number_of_hours_in_timepoint"])

    timepoints = c.execute(
        """SELECT timepoint, period, horizon, number_of_hours_in_timepoint
           FROM timepoints
           WHERE period_scenario_id = {}
           AND horizon_scenario_id = {}
           AND timepoint_scenario_id = {};""".format(
            HORIZON_SCENARIO_ID, PERIOD_SCENARIO_ID, TIMEPOINT_SCENARIO_ID
        )
    ).fetchall()

    for row in timepoints:
        writer.writerow(row)

# load_zones.tab
with open(os.path.join(os.getcwd(), "temp_inputs", "load_zones.tab"), "w") as \
        load_zones_tab_file:
    writer = csv.writer(load_zones_tab_file, delimiter="\t")

    # Write header
    writer.writerow(["load_zone", "overgeneration_penalty_per_mw",
                     "unserved_energy_penalty_per_mw"])

    load_zones = c.execute(
        """SELECT load_zone, overgeneration_penalty_per_mw,
           unserved_energy_penalty_per_mw
           FROM load_zones
           WHERE load_zone_scenario_id = {};""".format(
            LOAD_ZONE_SCENARIO_ID
        )
    ).fetchall()

    for row in load_zones:
        writer.writerow(row)

# load_following_up_balancing_areas.tab
with open(os.path.join(os.getcwd(), "temp_inputs",
                       "load_following_up_balancing_areas.tab"),
          "w") as \
        lf_up_bas_tab_file:
    writer = csv.writer(lf_up_bas_tab_file, delimiter="\t")

    # Write header
    writer.writerow(["balancing_area",
                     "load_following_down_violation_penalty_per_mw"])

    lf_up_bas = c.execute(
        """SELECT lf_reserves_up_ba, lf_reserves_up_violation_penalty_per_mw
           FROM lf_reserves_up_bas
           WHERE lf_reserves_up_ba_scenario_id = {};""".format(
            LF_RESERVES_UP_BA_SCENARIO_ID
        )
    ).fetchall()

    for row in lf_up_bas:
        writer.writerow(row)

# load_following_down_balancing_areas.tab
with open(os.path.join(os.getcwd(), "temp_inputs",
                       "load_following_down_balancing_areas.tab"),
          "w") as \
        lf_down_bas_tab_file:
    writer = csv.writer(lf_down_bas_tab_file, delimiter="\t")

    # Write header
    writer.writerow(["balancing_area",
                     "load_following_down_violation_penalty_per_mw"])

    lf_down_bas = c.execute(
        """SELECT lf_reserves_down_ba,
        lf_reserves_down_violation_penalty_per_mw
           FROM lf_reserves_down_bas
           WHERE lf_reserves_down_ba_scenario_id = {};""".format(
            LF_RESERVES_DOWN_BA_SCENARIO_ID
        )
    ).fetchall()

    for row in lf_down_bas:
        writer.writerow(row)

# rps_zones.tab
with open(os.path.join(os.getcwd(), "temp_inputs", "rps_zones.tab"),
          "w") as \
        rps_zones_tab_file:
    writer = csv.writer(rps_zones_tab_file, delimiter="\t")

    # Write header
    writer.writerow(["rps_zone"])

    rps_zones = c.execute(
        """SELECT rps_zone
           FROM rps_zones
           WHERE rps_zone_scenario_id = {};""".format(
            RPS_ZONE_SCENARIO_ID
        )
    ).fetchall()

    for row in rps_zones:
        writer.writerow(row)


# TODO: how to handle optional columns (e.g. lf_reserves_up_ba, rps_zone, etc.)
# projects.tab
with open(os.path.join(os.getcwd(), "temp_inputs", "projects.tab"), "w") as \
        projects_tab_file:
    writer = csv.writer(projects_tab_file, delimiter="\t")

    # Write header
    writer.writerow(
        ["project", "load_zone", "lf_reserves_up_ba", "lf_reserves_down_ba",
         "rps_zone", "capacity_type", "operational_type", "fuel",
         "minimum_input_mmbtu_per_hr", "inc_heat_rate_mmbtu_per_mwh",
         "min_stable_level", "unit_size_mw", "startup_cost_per_mw",
         "shutdown_cost_per_mw", "charging_efficiency",
         "discharging_efficiency"]
    )

    projects = c.execute(
        """SELECT project, load_zone, lf_reserves_up_ba, lf_reserves_down_ba,
        rps_zone, capacity_type, operational_type, fuel,
        minimum_input_mmbtu_per_hr, inc_heat_rate_mmbtu_per_mwh,
        min_stable_level, unit_size_mw, startup_cost, shutdown_cost,
        charging_efficiency, discharging_efficiency
        FROM projects
        JOIN project_load_zones
        USING (existing_project_scenario_id, new_project_scenario_id, project)
        JOIN project_lf_reserves_up_bas
        USING (existing_project_scenario_id, new_project_scenario_id, project)
        JOIN project_lf_reserves_down_bas
        USING (existing_project_scenario_id, new_project_scenario_id, project)
        JOIN project_rps_zones
        USING (existing_project_scenario_id, new_project_scenario_id, project)
        WHERE existing_project_scenario_id = {}
        AND new_project_scenario_id = {}
        AND project_load_zone_scenario_id = {}
        AND project_rps_zone_scenario_id = {};""".format(
            EXISTING_PROJECT_SCENARIO_ID, NEW_PROJECT_SCENARIO_ID,
            PROJECT_LOAD_ZONE_SCENARIO_ID,
            PROJECT_LF_RESERVES_UP_BA_SCENARIO_ID,
            PROJECT_LF_RESERVES_DOWN_BA_SCENARIO_ID,
            PROJECT_RPS_ZONE_SCENARIO_ID
        )
    ).fetchall()

    for row in projects:
        replace_nulls = ["." if i is None else i for i in row]
        writer.writerow(replace_nulls)

# existing_generation_period_params.tab
with open(os.path.join(os.getcwd(), "temp_inputs",
                       "existing_generation_period_params.tab"), "w") as \
        existing_project_capacity_tab_file:
    writer = csv.writer(existing_project_capacity_tab_file, delimiter = "\t")

    # Write header
    writer.writerow(
        ["GENERATORS", "PERIODS", "existing_capacity_mw",
         "fixed_cost_per_mw_yr"]
    )

    ep_capacities = c.execute(
        """SELECT project, period, existing_capacity_mw,
        annual_fixed_cost_per_mw_year
        FROM existing_project_capacity
        WHERE existing_project_scenario_id = {}
        AND period_scenario_id = {}
        AND existing_project_capacity_scenario_id = {};""".format(
            EXISTING_PROJECT_SCENARIO_ID, PERIOD_SCENARIO_ID,
            EXISTING_PROJECT_CAPACITY_SCENARIO_ID
        )
    )
    for row in ep_capacities:
        writer.writerow(row)

# new_build_generator_vintage_costs.tab
with open(os.path.join(os.getcwd(), "temp_inputs",
                       "new_build_generator_vintage_costs.tab"), "w") as \
        new_gen_costs_tab_file:
    writer = csv.writer(new_gen_costs_tab_file, delimiter = "\t")

    # Write header
    writer.writerow(
        ["new_build_generartor", "vintage", "lifetime_yrs",
         "annualized_real_cost_per_mw_yr"]
    )

    # TODO: select only rows with NULL for cost per kWh-yr for generators
    # only (not storage), but need to make this more robust
    new_gen_costs = c.execute(
        """SELECT project, period, lifetime_yrs,
        annualized_real_cost_per_kw_yr * 1000
        FROM new_project_cost
        WHERE annualized_real_cost_per_kwh_yr IS NULL
        AND new_project_scenario_id = {}
        AND period_scenario_id = {}
        AND new_project_cost_scenario_id = {};""".format(
            NEW_PROJECT_SCENARIO_ID, PERIOD_SCENARIO_ID,
            NEW_PROJECT_COST_SCENARIO_ID
        )
    )
    for row in new_gen_costs:
        writer.writerow(row)

# new_build_storage_vintage_costs.tab
with open(os.path.join(os.getcwd(), "temp_inputs",
                       "new_build_storage_vintage_costs.tab"), "w") as \
        new_storage_costs_tab_file:
    writer = csv.writer(new_storage_costs_tab_file, delimiter = "\t")

    # Write header
    writer.writerow(
        ["new_build_storage", "vintage", "lifetime_yrs",
         "annualized_real_cost_per_mw_yr, annualized_real_cost_per_mwh_yr"]
    )

    # TODO: select only rows with non NULL for cost per kWh-yr for storage
    # only (not generators), but need to make this more robust
    new_stor_costs = c.execute(
        """SELECT project, period, lifetime_yrs,
        annualized_real_cost_per_kw_yr * 1000,
        annualized_real_cost_per_kwh_yr * 1000
        FROM new_project_cost
        WHERE annualized_real_cost_per_kwh_yr IS NOT NULL
        AND new_project_scenario_id = {}
        AND period_scenario_id = {}
        AND new_project_cost_scenario_id = {};""".format(
            NEW_PROJECT_SCENARIO_ID, PERIOD_SCENARIO_ID,
            NEW_PROJECT_COST_SCENARIO_ID
        )
    )
    for row in new_stor_costs:
        writer.writerow(row)
