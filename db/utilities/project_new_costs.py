#!/usr/bin/env python
# Copyright 2017 Blue Marble Analytics LLC. All rights reserved.

"""
Existing/planned project capacities
"""


def update_project_new_costs(
        io, c,
        project_new_cost_scenario_id,
        scenario_name,
        scenario_description,
        project_period_lifetimes_costs
):
    print("project new costs")

    # Subscenarios
    c.execute(
        """INSERT INTO subscenarios_project_new_cost
         (project_new_cost_scenario_id, name, description)
         VALUES ({}, '{}', '{}');""".format(
            project_new_cost_scenario_id, scenario_name, scenario_description
        )
    )
    io.commit()

    for project in project_period_lifetimes_costs.keys():
        for period in project_period_lifetimes_costs[project].keys():
            c.execute(
                """INSERT INTO inputs_project_new_cost
                (project_new_cost_scenario_id, project, period, lifetime_yrs,
                annualized_real_cost_per_kw_yr,
                annualized_real_cost_per_kwh_yr)
                VALUES ({}, '{}', {}, {}, {}, {});""".format(
                    project_new_cost_scenario_id,
                    project,
                    period,
                    project_period_lifetimes_costs[project][period][0],
                    project_period_lifetimes_costs[project][period][1],
                    'NULL' if project_period_lifetimes_costs[project][
                        period][2] is None
                    else project_period_lifetimes_costs[project][period][2]
                )
            )
    io.commit()