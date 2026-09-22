.PHONY: test
test:
	bash -n src/smoke.sh
	bash -n hpc/job.sbatch
	bash -n hpc/defiant-smoke.sbatch
	bash -n hpc/odo-smoke.sbatch
	python3 -m unittest discover -s tests -v
