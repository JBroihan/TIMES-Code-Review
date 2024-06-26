from pathlib import Path
import pandas as pd
import numpy as np


def get_model_status(status_value):
    status = {
        1: "OPTIMAL",
        2: "LOCALLY OPTIMAL",
        3: "UNBOUNDED",
        4: "INFEASIBLE",
        5: "LOCALLY INFEASIBLE",
        6: "INTERMEDIATE INFEASIBLE",
        7: "FEASIBLE SOLUTION",
        8: "INTEGER SOLUTION",
        9: "INTERMEDIATE NON-INTEGER",
        10: "INTEGER INFEASIBLE",
        11: "LIC PROBLEM - NO SOLUTION",
        12: "ERROR UNKNOWN",
        13: "ERROR NO SOLUTION",
        14: "NO SOLUTION RETURNED",
        15: "SOLVED UNIQUE",
        16: "SOLVED",
        17: "SOLVED SINGULAR",
        18: "UNBOUNDED - NO SOLUTION",
        19: "INFEASIBLE - NO SOLUTION",
    }
    return status[status_value]


def process_lst(lst_file, instance, solvemode, solveLink):
    generation = 0
    solve = 0
    with open(lst_file) as f:
        for line in f.readlines()[-10:]:
            if "STARTUP" in line:
                startup = float(line.split()[-2])
            elif "COMPILATION" in line:
                compilation = float(line.split()[-2])
            elif "EXECUTION" in line:
                execution = float(line.split()[-2])
            elif "CLOSEDOWN" in line:
                closedown = float(line.split()[-2])
            elif "TOTAL SECONDS" in line:
                total_secs = float(line.split()[-3])
            elif "ELAPSED SECONDS" in line:
                elapsed = float(line.split()[-3])
    with open(lst_file) as f:
        for line in f:
            if "GENERATION TIME" in line:
                generation = float(line.split()[3])
            elif "MODEL STATUS" in line:
                model_status = get_model_status(status_value=int(line.split()[3]))
            elif "RESOURCE USAGE" in line:
                usage = line.split()[3]
                if usage != "NA":
                    solve += float(usage)
            elif "SINGLE EQUATIONS" in line:
                rows = int(line.split()[-1].replace(",", ""))
            elif "SINGLE VARIABLES" in line:
                if len(line.split()) == 7:
                    columns = int(line.split()[-1].replace(",", ""))
                else:
                    columns = int(line.split()[-3].replace(",", ""))
            elif "NON ZERO ELEMENT" in line:
                non_zeros = int(line.split()[-1].replace(",", ""))
            elif "[min, max] :" in line:
                min = line.split()[5].replace(",", "")
                max = line.split()[6].replace("]", "")
                if "RHS" in line:
                    rhs = ", ".join([min, max])
                elif "Bound" in line:
                    bound = ", ".join([min, max])
                elif "Matrix" in line:
                    matrix = ", ".join([min, max])

    if solveLink in [1, 2, 5]:
        execution -= solve

    if solvemode == "SOLVE":
        return (
            solve,
            generation,
            compilation,
            execution,
            startup,
            closedown,
            total_secs,
            elapsed,
            model_status,
            rows,
            columns,
            non_zeros,
            rhs,
            bound,
            matrix,
        )
    else:
        return (
            np.nan,
            generation,
            compilation,
            execution,
            startup,
            closedown,
            total_secs,
            elapsed,
            model_status,
            rows,
            columns,
            non_zeros,
            rhs,
            bound,
            matrix,
        )


def process_log(log_file, solvemode):
    with open(log_file) as f:
        for line in f:
            if "Solvelink=" in line:
                sl = int(line.split(" ")[3].replace("):", "").split("=")[-1])
            elif "highwater RSS" in line:
                rss = float(line.split(" ")[-2])
                # check if GB or MB
                if "MB" in line.split(" ")[-1]:
                    # MB to GB
                    rss = round(rss / 1000, 2)
            elif "highwater VSS" in line:
                vss = float(line.split(" ")[-2])
                # check if GB or MB
                if "MB" in line.split(" ")[-1]:
                    # MB to GB
                    vss = round(vss / 1000, 2)
    if solvemode == "SOLVE":
        return sl, rss, vss
    elif solvemode == "LOADSOLUTION":
        return None, rss, vss
    else:
        print("Wrong solvemode")


def process_prf_file(profile_file, out_dir, execution_time):
    a = []
    with open(profile_file, "r") as file:
        for line in file:
            b = line.split()
            if len(b) > 5:
                b[4 : len(b) + 1] = [" ".join(b[4 : len(b) + 1])]
            a.append(b)

    df = pd.DataFrame(
        a, columns=["Line", "# Calls", "Total Time [s]", "Memory", "Description"]
    )
    df = df.astype(
        {"Line": "int", "# Calls": "int", "Total Time [s]": "float", "Memory": "float"}
    )

    profile = (
        df[["Line", "Total Time [s]", "Description"]]
        .sort_values(by="Total Time [s]", ascending=False)
        .set_index("Line")
    )

    profile.insert(
        1,
        "relative to Execution Time [%]",
        round(profile["Total Time [s]"] / execution_time * 100, 2),
    )

    profile.to_markdown(out_dir / "profile_summary.md")

    return profile


def summarize_results(data_dir, solvemode):
    results = []
    profiles = []

    for i, r, in_dir, out_dir in data_dir:
        log = Path(f"{out_dir}/out.log")
        lst = Path(f"{out_dir}/out.lst")
        prf = Path(f"{out_dir}/out.prf")

        (
            solveLink,
            highwaterRSS,
            highwaterVSS,
        ) = process_log(log_file=log, solvemode=solvemode)
        (
            solver_time,
            generation_time,
            compilation_time,
            execution_time,
            startup,
            closedown,
            total_seconds,
            elapsed_time,
            model_status,
            rows,
            columns,
            non_zeros,
            rhs,
            bound,
            matrix,
        ) = process_lst(
            lst_file=lst, instance=out_dir, solvemode=solvemode, solveLink=solveLink
        )

        results.append(
            [
                i,
                model_status,
                elapsed_time,
                total_seconds,
                compilation_time,
                execution_time,
                generation_time,
                solver_time,
                startup,
                closedown,
                highwaterRSS,
                highwaterVSS,
                rows,
                columns,
                non_zeros,
                rhs,
                bound,
                matrix,
            ]
        )

        profiles.append(
            process_prf_file(
                profile_file=prf, out_dir=out_dir, execution_time=execution_time
            )
        )

    df = pd.DataFrame(
        results,
        columns=[
            "Instance",
            "Model Status",
            "Elapsed Time [s]",
            "Total Seconds [s]",
            "Compilation Time [s]",
            "Execution Time [s]",
            "Generation Time [s]",
            "Solver Time [s]",
            "Startup Time [s]",
            "Closedown Time [s]",
            "Highwater RSS [GB]",
            "Highwater VSS [GB]",
            "# Rows",
            "# Columns",
            "# Non Zeros",
            "RHS [min, max]",
            "Bound [min, max]",
            "Matrix [min, max]",
        ],
    ).set_index("Instance")

    df.insert(
        loc=14,
        column="# Non Zeros per s",
        value=df["# Non Zeros"] / df["Generation Time [s]"],
    )

    df.to_csv(Path("code_review/result_overview.csv"))

    profile_sum = (
        pd.concat(profiles)
        .groupby("Description")
        .sum()
        .sort_values(by="Total Time [s]", ascending=False)
    )
    profile_sum.iloc[:15, :1].to_markdown(
        Path("code_review/profile_results.md"), floatfmt=",.2f"
    )

    return df


def compare_with_ground_truth(new, solvemode):
    if solvemode == 'SOLVE':
        truth = pd.read_csv(Path("code_review/ground_truth_result_overview.csv")).set_index(
            "Instance"
        )
    else:
        truth = pd.read_csv(Path("code_review/ground_truth_savepoint_result_overview.csv")).set_index(
            "Instance"
        )
    numerical_columns = [
        "Elapsed Time [s]",
        "Total Seconds [s]",
        "Compilation Time [s]",
        "Execution Time [s]",
        "Generation Time [s]",
        "Solver Time [s]",
        "Startup Time [s]",
        "Closedown Time [s]",
        "Highwater RSS [GB]",
        "Highwater VSS [GB]",
        "# Rows",
        "# Columns",
        "# Non Zeros",
        "# Non Zeros per s",
    ]

    compare = round(
        (new[numerical_columns] - truth[numerical_columns])
        / truth[numerical_columns]
        * 100,
        2,
    ).rename(
        columns={
            "Elapsed Time [s]": "Elapsed Time [%]",
            "Total Seconds [s]": "Total Seconds [%]",
            "Compilation Time [s]": "Compilation Time [%]",
            "Execution Time [s]": "Execution Time [%]",
            "Generation Time [s]": "Generation Time [%]",
            "Solver Time [s]": "Solver Time [%]",
            "Startup Time [s]": "Startup Time [%]",
            "Closedown Time [s]": "Closedown Time [%]",
            "Highwater RSS [GB]": "Highwater RSS [%]",
            "Highwater VSS [GB]": "Highwater VSS [%]",
            "# Rows": "# Rows [%]",
            "# Columns": "# Columns [%]",
            "# Non Zeros": "# Non Zeros [%]",
            "# Non Zeros per s": "# Non Zeros per s [%]",
        }
    )

    compare.loc["mean"] = round(compare.mean(), 2)

    return truth, compare.dropna(how="all")


def write_summary_file(truth_df, new_df, compare_df):
    header_str = """# Results\n\n## Improvement\n"""
    mid_str = """\n## New\n"""
    end_str = """\n## Ground Truth\n"""

    with open("code_review/results.md", "w") as f:
        f.write(
            header_str
            + compare_df.to_markdown(intfmt=",", floatfmt=",.2f")
            + mid_str
            + new_df.to_markdown(intfmt=",", floatfmt=",.2f")
            + end_str
            + truth_df.to_markdown(intfmt=",", floatfmt=",.2f")
        )


if __name__ == "__main__":
    # choose from [SOLVE, LOADSOLUTION] according to run.py
    solvemode = "LOADSOLUTION"

    # set data directories (instance_name, run_file)
    instances = [
        ("Instance_1", "Instance_1.RUN"),
        ("Instance_2", "Instance_2.RUN"),
    ]

    data_dir = [
        (i, run_file, Path(f"code_review/data/{i}"), Path(f"code_review/output/{i}"))
        for i, run_file in instances
    ]

    new = summarize_results(data_dir, solvemode)

    truth, compare = compare_with_ground_truth(new, solvemode)

    write_summary_file(truth, new, compare)

    print("done")
