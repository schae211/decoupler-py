"""
decouple main function.
Code to run methods simultaneously. 
"""

from decoupler import run_ulm, ulm, run_wmean, run_wsum, run_mlm, run_ora
from anndata import AnnData

import pandas as pd

from .consensus import run_consensus


def decouple(mat, net, source='source', target='target', weight='weight',
             methods = ['wmean', 'wsum', 'ulm', 'mlm', 'ora'], args = {},
             consensus=True, min_n=5, verbose=True):
    """
    Decouple function.
    
    Runs simultaneously several methods of biological activity inference.
    
    Parameters
    ----------
    mat : list, pd.DataFrame or AnnData
        List of [genes, matrix], dataframe (samples x genes) or an AnnData
        instance.
    net : pd.DataFrame
        Network in long format.
    source : str
        Column name with source nodes.
    target : str
        Column name with target nodes.
    weight : str
        Column name with weights.
    methods : list, tuple
        List of methods to run.
    args : dict
        A dict of argument-dicts.
    consensus_score : bool
        Boolean whether to run a consensus score between methods. 
        Obtained scores are -log10(p-values).
    min_n : int
        Minimum of targets per source. If less, sources are removed.
    verbose : bool
        Whether to show progress. 
    
    Returns
    -------
    results : dict of scores and p-values.
    """
    
    # List of available methods
    methods_dict = {
        'wmean' : run_wmean,
        'wsum' : run_wsum,
        'ulm' : run_ulm,
        'mlm' : run_mlm,
        'ora' : run_ora
    }
    
    tmp = mat
    if isinstance(mat, AnnData):
        tmp = pd.DataFrame(mat.X, index=mat.obs.index, columns=mat.var.index)
    
    # Store results
    results = {}
    
    # Run every method
    for methd in methods:
        if methd in methods_dict:
            
            # Init empty args
            if methd not in args:
                a = {}
            else:
                a = args[methd]
                
            # Overwrite min_n and verbose
            a['min_n'] = min_n
            a['verbose'] = verbose
            
            # Get method
            f = methods_dict[methd]
            
            # Run method
            res = f(mat=tmp, net=net, source=source, target=target, weight=weight, **a)
            
            # Store obtained dfs
            for r in res:
                results[r.name] = r
        else:
            raise ValueError('Method {0} not available, please run show_methods() to see the list of available methods.'.format(methd))
            
    # Run consensus score
    if consensus:
        res = run_consensus(results)
        
        # Store obtained dfs
        for r in res:
            results[r.name] = r
                
    
    if isinstance(mat, AnnData):
        # Store obtained dfs
        for r in results:
            mat.obsm[r] = results[r]
    else:
        return results