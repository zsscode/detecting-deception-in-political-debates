from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from estimators.base_estimator import BaseEstimator
from transformers import AuthorsTransformer
from transformers.nela import LIWCTransformer
from utils import get_n_jobs, flatten, merge_features, grid_search_log_reg_c

class LogRegLIWC(BaseEstimator):
    def __init__(self):
        self.params = {
            'description': 'Logistic Regression - LIWC + Authors information',
            'min_max_scaler_params': {
                'feature_range': (0, 1),
            },
            'log_reg': {
                'penalty': 'l2',
                'dual': False,
                'tol': 0.0001,
                'C': 2,
                'fit_intercept': True,
                'intercept_scaling': 1,
                'class_weight': 'balanced',
                'solver': 'sag',
                'max_iter': 20000,
                'multi_class': 'multinomial',
                'random_state': 0,
                'verbose': 0,
                'warm_start': False,
                'n_jobs': get_n_jobs()
            }
        }

    def fit(self, debate_data, y, with_grid_search=False):
        x_texts = flatten([x.texts for x in debate_data])
        x_authors = flatten([x.authors for x in debate_data])
        y = flatten(y)

        train_x = merge_features(LIWCTransformer(x_texts).features, AuthorsTransformer(x_authors).features)

        pipe = Pipeline([
            ('log_reg', LogisticRegression(**self.params['log_reg']))
        ])

        if with_grid_search:
            self.model = grid_search_log_reg_c(pipe, train_x, y, debate_data, 'macro_recall')
        else:
            self.model = pipe
            self.model.fit(train_x, y)

    def predict(self, debate_data, proba=False):
        x_texts = flatten([x.texts for x in debate_data])
        x_authors = flatten([x.authors for x in debate_data])

        test_x = merge_features(LIWCTransformer(x_texts).features, AuthorsTransformer(x_authors).features)

        return self.model.predict_proba(test_x) if proba else self.model.predict(test_x)
