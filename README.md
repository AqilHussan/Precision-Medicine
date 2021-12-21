# Precision-Medicine

## ADNI_RF_Ver_1_1
The model has two main layers. Each layer has a classifer based on RF.The First Layer classifes the patient as CN, MCI, or AD based on the whole dataset. 
The Second Layer concentrates further on the MCI cases, fltered from the previous layer.  
First,convert text/categorical data into numerical data.
### Labelling
```
encoders = dict()
for col_name in adni_df.columns:
    le = preprocessing.LabelEncoder()
    le.fit(adni_df[col_name].astype(str))
    adni_df[col_name] = adni_df[col_name].map(lambda x: le.transform([x])[0] if type(x)==str else x)
    encoders[col_name] = le
```
Second,remove the row with nan values in the Y label.  
nan values are labelled as 3

### Dropping rows

```
X=adni_df.copy()
X=X.drop('DX',axis='columns')
X=X.drop('DX_bl',axis='columns')

FirstLevelClasses = adni_df.DX.unique()
FirstLevelClasses_Dictionary = dict(zip(FirstLevelClasses, range(len(FirstLevelClasses))))
First_df=adni_df.replace(FirstLevelClasses_Dictionary)
Y=First_df.DX
X = X.loc[Y != 3]
Y = Y.loc[Y != 3]
```
Third, a feature standardization step on numerical features to normalize them in the same way, which is done by standardizing the random variables with zero mean and unitary standard deviation.
### Standardization
```
from sklearn.preprocessing import StandardScaler
from pandas import DataFrame
trans = StandardScaler()
data = trans.fit_transform(X)
dataset = DataFrame(data)
dataset.columns = X.columns
dataset.index = Y.index
dataset['DX']=Y

```
Note that categorical label 'Y' is excluded from the normalization process.


### Imputation
Handling missing values: For handling missing values, we use the k-nearest neighbors (KNN) algorithm to impute missing values, where 
missing values are replaced using information from neighbor subjects that have the same class.
The mixed Euclidean distance (MED) was used, and k was set to 10.

### SMOTE
Synthetic minority oversampling technique (SMOTE) is used to handle the class imbalance in the  set of the 
First and Second Layer by resampling the original data and creating synthetic instances
```
from imblearn.over_sampling import SMOTE
oversample =SMOTE()
X, Y = oversample.fit_resample(X, Y)
```

## Selected Features

'RID',
 'PTID',
 'SITE',
 'AGE',
 'CDRSB',
 'mPACCtrailsB',
 'CDRSB_bl',
 'mPACCdigit_bl',
 'mPACCtrailsB_bl',
 'Fusiform_bl',
 'EcogSPMem_bl',
 'PTAU_bl',
 'FDG_bl',
 'M'
 
 ## Performance of the RF for the two layers 
 
 Layers | #1 | #2 
--- | --- | --- 
Accuracy | 73% | 91%

## Feature contribution - Layer 1
![alt text](https://github.com/AqilHussan/Precision-Medicine/blob/main/data/Level1Feature.PNG)
## Feature contribution - Layer 2
![alt text](https://github.com/AqilHussan/Precision-Medicine/blob/main/data/Level2Feature.PNG)

## ADNI_ENSEMBLE_Ver_1_2
The model has two main layers. Each layer has a classifer based on Ensemble method with 2 Random Forrest classifiers.
No changes done in the data preprocessing

## Selected Features
Whole

### Ensemble Method
```
rf1 = RandomForestClassifier()
rf2 = RandomForestClassifier()
from sklearn.ensemble import VotingClassifier
#create a dictionary of our models
estimators=[ ('rf1', rf1), ('rf2', rf2)]
#create our voting classifier, inputting our models
ensemble = VotingClassifier(estimators, voting='hard')
```
## Performance of the RF for the two layers 
 
 Layers | #1 | #2 
--- | --- | --- 
Accuracy | 93.9% | 99.4%

## Feature contribution - Layer 1
![alt text](https://github.com/AqilHussan/Precision-Medicine/blob/main/data/EnsembleLayer1.PNG)
## Feature contribution - Layer 2
![alt text](https://github.com/AqilHussan/Precision-Medicine/blob/main/data/EnsembleLayer2.PNG)



