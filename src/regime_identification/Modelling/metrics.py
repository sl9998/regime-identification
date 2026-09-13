# All the commands and stuff from analysis 1 to be imported

# Libs
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sklearn as skl
from tqdm import tqdm # Loading bars

'''
ANALYSIS & PLOTTING
'''
def plot_roc(y_test, y_pred, title = ""): 
    # Check accuracy etc
    report = skl.metrics.classification_report
    prc = skl.metrics.precision_recall_curve
    auc = skl.metrics.auc
    roc_curve = skl.metrics.roc_curve
    
    # print(report(test[goal], gb_test))
    
    # ROC source: https://xgboosting.com/evaluate-xgboost-performance-with-roc-curve/
    # Calculate the false positive rate, true positive rate, and thresholds
    fpr, tpr, thresholds = roc_curve(y_test, y_pred)
    
    # Calculate the area under the ROC curve (AUC)
    roc_auc = auc(fpr, tpr)
    
    # Plot the ROC curve
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='blue', label=f'ROC curve (AUC = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='red', linestyle='--', label='Random guess')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f"{title} ROC Curve ")
    plt.legend(loc="lower right")
    plt.show()
