from sklearn.model_selection import RandomizedSearchCV
import copy
class KWRandomizedSearchCV(RandomizedSearchCV):
      """
      wrapper around RandomizedSearchCV so we can use with
      one_parallel_json_obj_exp
      """
      def __init__(self, **args):
            """
            assume args contains arguments for RandomizedSearchCV object
            """
            args_copy = copy.deepcopy(args)
            estimator = args_copy['estimator']
            args_copy.pop('estimator')
            distributions = args_copy['param_distributions']
            args_copy.pop('param_distributions')
            args_copy.pop('model')
            print(f'args_copy = {args_copy}')
            super(KWRandomizedSearchCV, self).__init__(estimator, distributions, **args_copy)
