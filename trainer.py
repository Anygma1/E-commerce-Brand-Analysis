import pandas as pd
import sklearn
from sklearn.linear_model import LinearRegression
trainingdatafile="traindata.xlsx"
df = pd.read_excel(trainingdatafile,sheet_name='Sheet1')
df=df.iloc[:,1:7]
print(df)
print("\n\n\n\n")
target=df.iloc[:,-1]

##print(target)

X= df.iloc[:,0:5]
lm=LinearRegression()
lm
lm.fit(X,target)
print(pd.DataFrame(zip(X.columns,lm.coef_),columns=['attributes','coeff']))
print(lm.intercept_)
