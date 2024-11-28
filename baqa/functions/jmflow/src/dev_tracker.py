
import os
from datetime import datetime
import subprocess
import pandas as pd
import pickle
import shutil

class DevTracker():

    def __init__(self, pipeline_name, dir = '.'):
        self.folder_path = os.path.join(dir, pipeline_name)
    
    def start_session(self):
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
        empty_folders = []
        for root, dirs, _ in os.walk(self.folder_path):
            for dir in dirs:
                if not os.listdir(os.path.join(root, dir)):
                    empty_folders.append(os.path.join(root, dir))
        [os.rmdir(folder) for folder in empty_folders]
        session_folder = os.path.join(self.folder_path, str(datetime.now()).replace(' ', '-').replace(':', '-').replace('.', '-'))
        os.makedirs(session_folder)
        self.session_folder_path = session_folder
        git_branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode().strip()
        git_commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
        self.branch = git_branch
        self.commit = git_commit_hash

    def log(self, var_dict, files = None):
        
        var_dict['git_branch'] = self.branch
        var_dict['git_commit_hash'] = self.commit

        path = os.path.join(self.session_folder_path, 'log.csv')
        for var_name, var in var_dict.items():
            try:
                df = pd.DataFrame()
                df['VarName'] = [var_name]
                df['Var'] = [var]
                if not os.path.isfile(path):
                    df.to_csv(path, header=False,  index = False)
                else:
                    df.to_csv(path, mode='a', header=False, index = False)
            except:
                pickle.dump(var, open(os.path.join(self.session_folder_path, '{}.pkl'.format(var_name)), 'wb+'))

        if files is not None:
            for file in files:
                shutil.copy(file, self.session_folder_path)
    
    def log_batch(self, df):
            
        df['git_branch'] = self.branch
        df['git_commit_hash'] = self.commit
        df['datetime'] = str(datetime.now()).replace(' ', '-').replace(':', '-').replace('.', '-')

        path = os.path.join(self.session_folder_path, 'batch_log.csv')
  
        if not os.path.isfile(path):
            df.to_csv(path, index = False)
        else:
            df.to_csv(path, mode='a', index = False)



