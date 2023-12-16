# Parallel Computing
import multiprocessing as mp
from joblib import Parallel, delayed
from tqdm.notebook import tqdm

# Data Ingestion 
import pandas as pd

def batch_file(array,n_workers):
  file_len = len(array)
  batch_size = round(file_len / n_workers)
  batches = [
  array[ix:ix+batch_size]
  for ix in tqdm(range(0, file_len, batch_size))
  ]
  return batches

n_workers = 2 * mp.cpu_count()

print(f"{n_workers} workers are available")

batches = batch_file(df['Description'],n_workers)
