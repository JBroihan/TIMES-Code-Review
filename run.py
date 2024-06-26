import subprocess
from shutil import move
from pathlib import Path
from summarize_results import (
    summarize_results,
    compare_with_ground_truth,
    write_summary_file,
)
import os


def prepare_opt_file(in_dir):
    """If cplex.opt exists in the folder, reuse it but make sure to use consistent threads and reslim settings across all tests."""
    """If no cplex.opt exists, use barrier without crossover."""
    if (in_dir / "cplex.opt").exists():
        options = ["threads 16", "reslim 43200"]
        with open(in_dir / "cplex.opt", "r") as f:
            for line in f:
                if any([o in line.lower() for o in ["*", "threads", "reslim", "datacheck", "quality"]]):
                    pass
                else:
                    options.append(line.strip())

    else:
        options = ["lpmethod 4", "solutiontype 2", "threads 16", "reslim 43200"]

    with open(in_dir / "cplex.op2", "w") as f:
        for o in options:
            print(o, file=f)


if __name__ == "__main__":
    """Runs automated tests for the ETSAP TIMES Code Review Project."""

    # set solvemode to SOLVE or LOADSOLUTION
    # SOLVE completes a full run
    # LOADSOLUTION requires a savepoint file from a previous full run
    # and skips the solve
    solvemode = 'LOADSOLUTION'

    # set data directories (instance_name, run_file)
    instances = [
        ("Instance_1", "Instance_1.RUN"),
        ("Instance_2", "Instance_2.RUN"),
    ]

    # specifies where the TIMES source code is located
    TIMES_SOURCE_PATH = '/path/to/times/source'

    data_dir = [
        (
            i,
            run_file,
            Path(f"code_review/data/{i}").absolute(),
            Path(f"code_review/output/{i}").absolute(),
        )
        for i, run_file in instances
    ]

    # run .run for every data set in data_dir
    for i, run_file, in_dir, out_dir in data_dir:
        # make out directory if not existent
        if not out_dir.is_dir():
            out_dir.mkdir(parents=True, exist_ok=True)

        # Prepare solver option files.
        prepare_opt_file(in_dir)

        os.chdir(in_dir)

        subprocess.run(
            [
                "gams",
                run_file,
                f"idir1={TIMES_SOURCE_PATH}",
                f"--out_dir={out_dir}",
                f"--SOLVEMODE={solvemode}",
                "-savepoint=1",
                "forceoptfile=2",
                f"-optDir={in_dir}",
                f"-putDir={out_dir}",
                f"-gdx={out_dir}/out.gdx",
                f"-o={out_dir}/out.lst",
                f"-logfile={out_dir}/out.log",
                "-logOption=4",
                "-profile=2",
                "-profileTol=0.001",
                "-gdxCompress=1",
                f"-profileFile={out_dir}/out.prf",
                "-procTreeMemMonitor=1",
                "-procTreeMemTicks=100",
                "-stepsum=1",
            ]
        )

        # move savepoint gdx to out_dir
        savepoint_file = "TIMES_p.gdx"
        if Path(savepoint_file).is_file():
            move(Path(savepoint_file), Path(out_dir / savepoint_file))

    os.chdir(TIMES_SOURCE_PATH)
    # write a summary file
    new = summarize_results(data_dir=data_dir, solvemode=solvemode)

    truth, compare = compare_with_ground_truth(new, solvemode=solvemode)

    write_summary_file(truth, new, compare)

    print("done")
