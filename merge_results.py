import json
def merge_dicts(a):
     j={}
     for f_name, f_list in a.items():
          for f in f_list:
               s=open(f, 'r').read()
               j.update(json.loads(open(f, 'r').read()))
          with open(f_name,  'w') as f:
               print(f'writing {f_name}')
               f.write(json.dumps(j, indent=2))  

if __name__ == '__main__':
     web_attacks_file_names =\
     {'web_attacks_merged_results.json':
      [
          "results/parallel_experiment_results-1602701152.7844079.txt",
          "results/parallel_experiment_results-1602772623.6207578.txt",
          "results/parallel_experiment_results-1602789483.9404364.txt",
          "results/parallel_experiment_results-1602804534.6025856.txt",
          "results/parallel_experiment_results-1602887594.2105033.txt",
          "results/parallel_experiment_results-1602903617.1261935.txt",
          "results/parallel_experiment_results-1602938799.4818633.txt",
          "results/parallel_experiment_results-1602947687.7545745.txt",
          "results/parallel_experiment_results-1602967026.618354.txt",
          "results/parallel_experiment_results-1602973976.646604.txt",
          "results/parallel_experiment_results-1602985606.2691247.txt",
          "results/parallel_experiment_results-1603028230.3556237.txt",
          "results/parallel_experiment_results-1603039613.3621466.txt",
          "results/parallel_experiment_results-1603052999.640986.txt",
          "results/parallel_experiment_results-1603245358.7179012.txt",
          "results/parallel_experiment_results-1603284336.5380876.txt",
          "results/parallel_experiment_results-1603294387.9741275.txt",
          "results/parallel_experiment_results-1603307861.7300563.txt",
          "results/parallel_experiment_results-1603332936.7238533.txt",
          "results/parallel_experiment_results-1603409392.3141904.txt",
          "results/parallel_experiment_results-1603418501.1248736.txt",
          "results/parallel_experiment_results-1603450928.9662423.txt",
          "results/parallel_experiment_results-1603463816.8881536.txt",
          'results/parallel_experiment_results-2020-11-08-11-19-58.txt',
          'results/parallel_experiment_results-2020-11-08-15-19-56.txt',
          'results/parallel_experiment_results-2020-11-11-22-03-34.txt',
          'results/parallel_experiment_results-2020-11-14-07-30-31.txt'
     ]}

     brute_force_file_names =\
     {'brute_force_merged_results.json':
      [
           "results/parallel_experiment_results-2020-10-26-11-07-56.txt",
           "results/parallel_experiment_results-2020-10-27-21-16-10.txt",
           "results/parallel_experiment_results-2020-10-28-09-01-21.txt",
           "results/parallel_experiment_results-2020-10-29-22-28-26.txt",
           "results/parallel_experiment_results-2020-10-30-18-26-07.txt",
           "results/parallel_experiment_results-2020-10-30-21-37-18.txt",
           "results/parallel_experiment_results-2020-11-01-23-03-18.txt",
           "results/parallel_experiment_results-2020-11-02-08-15-44.txt",
           "results/parallel_experiment_results-2020-11-15-09-43-37.txt"
     ]
     }

     sql_injection_file_names =\
     {'sql_injection_merged_results.json':
      [
           "results/parallel_experiment_results-2020-11-02-22-28-17.txt",
           "results/parallel_experiment_results-2020-11-03-13-14-52.txt",
           "results/parallel_experiment_results-2020-11-06-21-53-54.txt",
           "results/parallel_experiment_results-2020-11-19-21-05-27.txt"
      ]
     }

     xss_file_names =\
     {'xss_merged_results.json':
      [
           'results/xss-parallel_experiment_results-2020-11-05-09-00-52.txt',
           'results/parallel_experiment_results-2020-11-07-10-47-13.txt',
           'results/parallel_experiment_results-2020-11-20-10-29-01.txt'
      ]
     }

     dos_file_names =\
     {'dos_merged_results.json':
      [
           'results/parallel_experiment_results-2020-11-22-13-09-47.txt',
           'results/parallel_experiment_results-2020-11-22-17-49-31.txt',
           'results/parallel_experiment_results-2020-11-23-07-33-23.txt'
      ]
     }

     # files in ~/git/fall-2020-research/iscx/experiments/
     #[brute_force_file_names, web_attacks_file_names, sql_injection_file_names,
     #         xss_file_names, dos_file_names]:

     cognition_no_fs_files = \
     {'cognition_no_fs_results.json':
      [
           'cognition_results/catboost_parallel_experiment_results-2020-12-02-23-11-03.json',
           'cognition_results/xgb_parallel_experiment_results-2020-12-02-23-13-51.json',
           'cognition_results/logistic_regression_parallel_experiment_results-2020-12-02-23-22-38.json',
           'cognition_results/random_forest_parallel_experiment_results-2020-12-02-23-30-04.json',
           'cognition_results/light_gbm_parallel_experiment_results-2020-12-02-23-36-38.json',
           'cognition_results/decision_tree_parallel_experiment_results-2020-12-02-23-47-25.json',
           'cognition_results/naive_bayes_parallel_experiment_results-2020-12-02-23-49-55.json',
      ]
     }
     cognition_all_files =\
     {'cognition_all_results.json':
     [
     'cognition_results/catboost_parallel_experiment_results-2020-12-02-23-11-03.json',
     'cognition_results/xgb_parallel_experiment_results-2020-12-02-23-13-51.json',
     'cognition_results/logistic_regression_parallel_experiment_results-2020-12-02-23-22-38.json',
     'cognition_results/random_forest_parallel_experiment_results-2020-12-02-23-30-04.json',
     'cognition_results/light_gbm_parallel_experiment_results-2020-12-02-23-36-38.json',
     'cognition_results/decision_tree_parallel_experiment_results-2020-12-02-23-47-25.json',
     'cognition_results/naive_bayes_parallel_experiment_results-2020-12-02-23-49-55.json',
     './cognition_fs_results/catboost_parallel_experiment_results-2020-12-03-14-07-49.json',
     './cognition_fs_results/catboost_parallel_experiment_results-2020-12-03-14-10-29.json',
       './cognition_fs_results/catboost_parallel_experiment_results-2020-12-03-14-12-39.json',
       './cognition_fs_results/catboost_parallel_experiment_results-2020-12-03-14-14-50.json',
       './cognition_fs_results/dt_parallel_experiment_results-2020-12-03-14-40-48.json',
       './cognition_fs_results/dt_parallel_experiment_results-2020-12-03-14-40-57.json',
       './cognition_fs_results/dt_parallel_experiment_results-2020-12-03-14-41-06.json',
       './cognition_fs_results/dt_parallel_experiment_results-2020-12-03-14-41-15.json',
       './cognition_fs_results/lgb_dt_parallel_experiment_results-2020-12-03-14-17-22.json',
       './cognition_fs_results/lgb_dt_parallel_experiment_results-2020-12-03-14-18-06.json',
       './cognition_fs_results/lgb_dt_parallel_experiment_results-2020-12-03-14-18-29.json',
       './cognition_fs_results/lgb_dt_parallel_experiment_results-2020-12-03-14-18-51.json',
       './cognition_fs_results/lr_parallel_experiment_results-2020-12-03-14-19-13.json',
       './cognition_fs_results/lr_parallel_experiment_results-2020-12-03-14-20-20.json',
       './cognition_fs_results/lr_parallel_experiment_results-2020-12-03-14-21-24.json',
       './cognition_fs_results/lr_parallel_experiment_results-2020-12-03-14-22-30.json',
       './cognition_fs_results/nb_dt_parallel_experiment_results-2020-12-03-14-23-34.json',
       './cognition_fs_results/nb_dt_parallel_experiment_results-2020-12-03-14-23-41.json',
       './cognition_fs_results/nb_dt_parallel_experiment_results-2020-12-03-14-23-48.json',
       './cognition_fs_results/nb_dt_parallel_experiment_results-2020-12-03-14-23-55.json',
       './cognition_fs_results/rf_dt_parallel_experiment_results-2020-12-03-14-24-02.json',
       './cognition_fs_results/rf_dt_parallel_experiment_results-2020-12-03-14-25-02.json',
       './cognition_fs_results/rf_dt_parallel_experiment_results-2020-12-03-14-25-57.json',
       './cognition_fs_results/rf_dt_parallel_experiment_results-2020-12-03-14-26-57.json',
       './cognition_fs_results/xgb_parallel_experiment_results-2020-12-03-14-27-52.json',
       './cognition_fs_results/xgb_parallel_experiment_results-2020-12-03-14-28-19.json',
       './cognition_fs_results/xgb_parallel_experiment_results-2020-12-03-14-28-39.json',
       './cognition_fs_results/xgb_parallel_experiment_results-2020-12-03-14-28-57.json',
      ]
     }

     iri_expansion_part_b_1_1=\
     {'iri_medicare_expansion_part_b_1_1_multiple_classifiers.json':
      [
         'medicare_part_b_results/parallel_experiment_results-2020-12-08-09-17-12.json',
         'medicare_part_b_results/parallel_experiment_results-2020-12-08-09-17-09.json',
         'medicare_part_b_results/parallel_experiment_results-2020-12-08-09-23-44.json',
         'medicare_part_b_results/parallel_experiment_results-2020-12-10-13-17-00.json',
         'medicare_part_b_results/parallel_experiment_results-2020-12-08-09-23-46.json'
         ]
      }

     iri_expansion_part_d_1_1=\
     {'iri_medicare_expansion_part_d_1_1_multiple_classifiers.json':
      [
           'medicare_part_d_results/parallel_experiment_results-2020-12-08-13-44-31.json',
           'medicare_part_d_results/parallel_experiment_results-2020-12-08-00-06-18.json',
           'medicare_part_d_results/parallel_experiment_results-2020-12-08-12-28-31.json',
           'medicare_part_d_results/parallel_experiment_results-2020-12-08-12-34-48.json'
      ]
     }

     iri_expansion_clf_rus_part_b=\
     {'iri_medicare_expansion_part_b_rus_multiple_classifiers.json':
      [
           'medicare_part_b_results/parallel_experiment_results-2020-12-08-09-17-12.json',
           'medicare_part_b_results/parallel_experiment_results-2020-12-08-09-47-38.json',
           'medicare_part_b_results/parallel_experiment_results-2020-12-08-10-12-54.json',
           'medicare_part_b_results/parallel_experiment_results-2020-12-08-09-17-09.json',
           'medicare_part_b_results/parallel_experiment_results-2020-12-08-09-51-19.json',
           'medicare_part_b_results/parallel_experiment_results-2020-12-08-10-18-33.json',
           'medicare_part_b_results/parallel_experiment_results-2020-12-08-09-23-44.json',
           'medicare_part_b_results/parallel_experiment_results-2020-12-08-09-53-46.json',
           'medicare_part_b_results/parallel_experiment_results-2020-12-08-10-19-03.json',
           'medicare_part_b_results/parallel_experiment_results-2020-12-10-13-17-00.json',
           'medicare_part_b_results/parallel_experiment_results-2020-12-10-17-15-47-9128.json',
           'medicare_part_b_results/parallel_experiment_results-2020-12-10-17-16-12-9836.json',
           'medicare_part_b_results/parallel_experiment_results-2020-12-08-09-23-46.json',
           'medicare_part_b_results/parallel_experiment_results-2020-12-08-10-10-03.json',
           'medicare_part_b_results/parallel_experiment_results-2020-12-08-10-20-18.json',
         ]
      }

     iri_expansion_hcpcs_state_rus_part_b=\
     {'iri_expansion_hcpcs_state_rus_part_b.json':
      [
           'medicare_part_b_results/parallel_experiment_results-2020-12-08-11-00-02.json',
           'medicare_part_b_results/parallel_experiment_results-2020-12-08-11-17-33.json',
           'medicare_part_b_results/parallel_experiment_results-2020-12-08-11-00-40.json',
           'medicare_part_b_results/parallel_experiment_results-2020-12-09-08-28-15.json',
           'medicare_part_b_results/parallel_experiment_results-2020-12-09-08-35-00.json',
           'medicare_part_b_results/parallel_experiment_results-2020-12-08-13-44-29.json',
           'medicare_part_b_results/parallel_experiment_results-2020-12-08-13-39-23.json',
           'medicare_part_b_results/parallel_experiment_results-2020-12-08-13-44-21.json',
         ]
      }

     iri_expansion_part_d_2_factor=\
     {'iri_expansion_part_d_2_factor.json':
      [
           'medicare_part_d_results/parallel_experiment_results-2020-12-08-13-44-31.json',
           'medicare_part_d_results/parallel_experiment_results-2020-12-08-13-00-04.json',
           'medicare_part_d_results/parallel_experiment_results-2020-12-08-13-32-14.json',
           'medicare_part_d_results/parallel_experiment_results-2020-12-08-00-06-18.json',
           'medicare_part_d_results/parallel_experiment_results-2020-12-08-13-33-09.json',
           'medicare_part_d_results/parallel_experiment_results-2020-12-08-13-05-59.json',
           'medicare_part_d_results/parallel_experiment_results-2020-12-08-12-34-48.json',
           'medicare_part_d_results/parallel_experiment_results-2020-12-08-13-17-35.json',
           'medicare_part_d_results/parallel_experiment_results-2020-12-08-13-34-40.json',
           'medicare_part_d_results/parallel_experiment_results-2020-12-08-12-28-31.json',
           'medicare_part_d_results/parallel_experiment_results-2020-12-08-00-55-30.json',
           'medicare_part_d_results/parallel_experiment_results-2020-12-08-13-26-33.json'
         ]
      }

     default_all_features=\
          {'/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/default_all_features.json':
           ['/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/all_features_catboost_default.json',
'/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/all_features_cb_onehot_default.json',
'/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/all_features_dt_default.json',
'/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/all_features_lightgbm_default.json',
'/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/all_features_lr_default.json',
'/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/all_features_mlp_default.json',
'/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/all_features_nb_default.json',
'/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/all_features_rf_default.json',
'/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/all_features_xgboost_default.json']
     }
     
     default_no_calculated=\
          {'/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/default_no_calculated.json':
           ['/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/no_calculated_catboost_default.json',
            '/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/no_calculated_cb_onehot_default.json',
            '/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/no_calculated_dt_default.json',
            '/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/no_calculated_lightgbm_default.json',
          '/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/no_calculated_lr_default.json',
            '/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/no_calculated_mlp_default.json',
            '/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/no_calculated_nb_default.json',
            '/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/no_calculated_rf_default.json',
          '/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/no_calculated_xgboost_default.json']
          }

     tuned_all_features=\
{'/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/tuned_all_features.json':
 [ '/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/all_features_cb_onehot_.json',
   '/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/all_features_dt_.json',
   '/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/all_features_lightgbm_.json',
   '/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/all_features_lr_.json',
'/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/all_features_nb_.json',
   '/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/all_features_mlp_.json',
   '/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/all_features_rf_.json',
   '/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/all_features_xgboost_.json'
 ]
}
     tuned_no_calculated=\
     {'/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/tuned_no_calculated.json':
      ['/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/no_calculated_cb_onehot_.json',
     '/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/no_calculated_dt_.json',
       '/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/no_calculated_lightgbm_.json',
       '/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/no_calculated_lr_.json',
       '/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/no_calculated_mlp_.json',
       '/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/no_calculated_nb_.json',
       '/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/no_calculated_rf_.json',
     '/home/jhancoc4/git/spring-2021-research/iot-botnet-experiments/slurm_exp_test_results/no_calculated_xgboost_.json']
}

     for a in [default_all_features, default_no_calculated, tuned_all_features, tuned_no_calculated]:
          merge_dicts(a)
