.PHONY: test
test:
	bash -n src/smoke.sh
	bash -n hpc/job.sbatch
	python3 -m unittest discover -s tests -v
