#!/bin/bash
# this script should be called
# from sbatch

# slurm modules
# for GPU's
# module load cuda-10.0.130-gcc-8.3.0-t6gcqrf
# for python
# module load python-3.7.4-gcc-8.3.0-3tniqr5

# activate virtual enironment, should have CatBoost installed
#
# source /home/jhancoc4/venv/python-3.7.3/bin/activate
#  mv slurm-* ./old_slurm_logs/
#SBATCH -n 108
module_dir=$1
job_id_list=()
for file_name in ${module_dir}/*; do
    echo @@@ starting $file_name;
    # save the sbatch command arguments to a comment so we can restart
    # the failed job;  there seems to be no other way to restart auotmatically
    # that may be for good reasons
    sbatch_options=$(srun -p longq7-mri python get_slurm_options_for_module.py -m ./${module_dir}/${file_name})
    sbatch_cmd="$sbatch_options  one_parallel_exp_no_server.py --module_name ./medicare_experiment_modules/${file_name}"
    echo sbatch_cmd is $sbatch_cmd running ...
    sbatch_str=$(sbatch --comment "$sbatch_cmd" $sbatch_cmd)
    sbatch_str_arr=($sbatch_str)
    job_id=(${sbatch_str_arr[3]})
    job_id_list+=($job_id)
done

len_job_list=${#job_id_list[@]}
echo len_job_list $len_job_list
while [ $len_job_list -gt 0 ];
      do
	  sleep 10s

	  echo job id list
	  echo ${job_id_list[@]}
	  new_job_id_list=()
	  i=0
	  for job_id in  ${job_id_list[@]}; do
	      # | xargs to trim leading or trailing whitespace
	      job_result=$(sacct --job ${job_id} --noheader --format Exit,State | xargs)
	      if [[ $job_result == *"FAILED"* ]]; then
		  echo $job_result
		  echo we are resubmitting
		  job_cmd=$(sacct --noheader --job $job_id --format Comment%5000 | xargs)
		  echo $job_cmd
		  echo $job_id is the id of the failed job
		  # mv slurm-${job_id}.out ./old_slurm_logs
		  # add new job_id to list
		  # if result is not "0:0 COMPLETED 0:0 COMPLETED 0:0 COMPLETED"
		  new_sbatch_str=$(sbatch --comment "$job_cmd" $job_cmd)
		  new_sbatch_str_arr=($new_sbatch_str)
		  new_batch_id=(${new_sbatch_str_arr[3]})
		  new_job_id_list+=($new_batch_id)
		  echo new batch id $new_batch_id
	      elif [ "$job_result" != "0:0 COMPLETED 0:0 COMPLETED 0:0 COMPLETED" ]; then
		  #add job_id to new list		
		  new_job_id_list+=($job_id)
	      else
		  # mv slurm-${job_id}.out ./old_slurm_logs/
		  echo successfully completed $job_id
	      fi
	  done;
	  # we do not understand why, new_job_id__list is appended to job_id_list
	  # unless we delete it here
	  unset job_id_list
	  job_id_list=("${new_job_id_list[@]}")
	  echo new job id list
	  echo ${job_id_list[@]}
	  len_job_list=${#job_id_list[@]}
	  echo $len_job_list
done
    
