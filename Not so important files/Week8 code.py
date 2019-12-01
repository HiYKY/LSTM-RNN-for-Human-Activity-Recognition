import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import interpolate

import pickle # to serialise objects
from scipy import stats
import seaborn as sns
from sklearn import metrics
from sklearn.model_selection import train_test_split

sns.set(style='whitegrid', palette='muted', font_scale=1.5)

RANDOM_SEED = 42


dataset_train = pd.read_csv('acceleration_labelled_data.csv') 
training_set = pd.DataFrame(dataset_train.iloc[:, 1:6].values)
training_set.columns = ["Activity", "Timeframe", "X axis", "Y axis", "Z axis"]
training_set["Timeframe"] = training_set["Timeframe"] - 0.017856

X = training_set.iloc[:, 2]
X = X.astype(float)
X = (X*1000000).astype('int64')

Y = training_set.iloc[:, 3]
Y = Y.astype(float)
Y = (Y*1000000).astype('int64')

Z = training_set.iloc[:, 4]
Z = Z.astype(float)
Z = (Z*1000000).astype('int64')


Old_T = (training_set.iloc[:, 1]).astype(float)
Old_T = (Old_T * 1000000)
Old_T = Old_T.astype('int64')

New_T = np.arange(0, 1823849096, 50000)
New_T = New_T.astype('int64')

# find interpolation function
interpolate_function = interpolate.interp1d(Old_T, X, axis = 0, fill_value="extrapolate")
X_Final = interpolate_function((New_T))

interpolate_function = interpolate.interp1d(Old_T, Y, axis = 0, fill_value="extrapolate")
Y_Final = interpolate_function((New_T))

interpolate_function = interpolate.interp1d(Old_T, Z, axis = 0, fill_value="extrapolate")
Z_Final = interpolate_function((New_T))

#Original Data Plot
plt.plot(Old_T, X, color = 'red')
plt.plot(Old_T, Y, color = 'red')
plt.plot(Old_T, Z, color = 'red')

#Data Sampled at 20 hz
plt.plot(New_T, X_Final, color = 'blue')
plt.plot(New_T, Y_Final, color = 'blue')
plt.plot(New_T, Z_Final, color = 'blue')

#Combining data into one pandas dataframe
Dataset = pd.DataFrame()
Dataset['X_Final'] = X_Final
Dataset['Y_Final'] = Y_Final
Dataset['Z_Final'] = Z_Final

Dataset['New_Timeframe'] = New_T
Dataset = Dataset/1e6
Dataset = Dataset[['New_Timeframe', 'X_Final', 'Y_Final', 'Z_Final']]
Dataset['New_Activity'] = ""
#Dataset = Dataset.astype('int64')
Dataset = Dataset[['New_Activity', 'New_Timeframe', 'X_Final', 'Y_Final', 'Z_Final']]


#function to fill in new dataset with related 
Dataset = Dataset.to_numpy()
training_set = training_set.to_numpy()

time = 0
temp = training_set[0][0]
var_to_assign = ""
last_row = 0
new_row = 0
for i in range(len(training_set)-1):
    if(training_set[i][0] == temp):
        continue
    
    if (training_set[i][0] != temp):
        var_to_assign = temp
        temp = training_set[i][0]
        time = training_set[i][1]
        
        a1 = [x for x in Dataset[:, 1] if x <= time]
        new_row = len(a1)
        
        Dataset[last_row:new_row+1, 0] = var_to_assign
        last_row = new_row
        continue


#converting both arrays back to Dataframes
Dataset = pd.DataFrame(Dataset)
Dataset.columns = ['New_Activity', 'New_Timeframe', 'X_Final', 'Y_Final', 'Z_Final']
    
training_set = pd.DataFrame(training_set)   
training_set.columns = ["Activity", "Timeframe", "X axis", "Y axis", "Z axis"]

#Dropping unknown values in the start and end
Dataset = Dataset.iloc[919:35927,]
    
#Filling empty Dataset values
#Checking to see which index values are empty
df_missing = pd.DataFrame()
df_missing = Dataset[Dataset.isnull().any(axis=1)]

#Filling all empty values with preceding values
Dataset['New_Activity'].fillna(method = 'ffill', inplace = True)

#Exploring Data

"""
count_of_activity = Dataset['New_Activity'].value_counts()
print(count_of_activity)
   
count_of_activity.plot(kind = 'bar', title = 'Different Activity Types')


def plot_activity(activity, dataframe):
    Rows_of_activity = (dataframe['New_Activity'] == activity)
    data =  dataframe[Rows_of_activity]
    data = data[['X_Final','Y_Final','Z_Final']]
    data = data[:50]
    
    ax = data.plot(subplots = True, figsize =(16,12), title = activity)
    

plot_activity("t_turn", Dataset)
"""

#Data Preprocessing

TIME_STEPS = 200
N_FEATURES = 3
STEP = 20

segments = []
labels = []

for i in range(0, len(Dataset) - TIME_STEPS, STEP): #To give the starting point of each batch
    xs = Dataset['X_Final'].values[i: i + TIME_STEPS]
    ys = Dataset['Y_Final'].values[i: i + TIME_STEPS]
    zs = Dataset['Z_Final'].values[i: i + TIME_STEPS]
    label = stats.mode(Dataset['New_Activity'][i: i + TIME_STEPS]) #this statement returns mode and count
    label = label[0][0] #to ge value of mode
    segments.append([xs, ys, zs])
    labels.append(label)
    
    
    


















