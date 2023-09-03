import numpy as np
from sklearn.linear_model import LinearRegression
from pandas import *
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d

def solve_sys(x, y, z):
    A = np.column_stack([np.ones(len(x)), x, x ** 2, y, y ** 2])
    B = z
    result, resid, _, _ = np.linalg.lstsq(A, B)
    return [result, resid]



def make_dictionary(model, x, x_fixed, y, x_name, x_fixed_name, y_name):
    fixed_set = []
    for e in x_fixed:
        fixed_set.append(e)
    fixed_set = set(x_fixed)
    list_of_set = list(fixed_set)
    data_arr = []
    for e in fixed_set:
        x_fixed_arr = grab_where_equal(x.array.reshape((-1, 1)), x_fixed.array.reshape((-1, 1)), e).reshape((-1, 1))
        y_fixed_arr = grab_where_equal(y, x_fixed.array.reshape((-1, 1)), e)
        model_data = [model.fit(x_fixed_arr, y_fixed_arr), x_fixed_arr, y_fixed_arr,
                      x_name + " with " + x_fixed_name + " fixed at " + str(e), y_name]
        data_arr.append(model_data)
    dict = {}
    for idx, entry in enumerate(data_arr):
        dict[list_of_set[idx]] = entry
    return dict


def print_model(entry):
    model = entry[0]
    x = entry[1]
    y = entry[2]
    x_name = entry[3]
    y_name = entry[4]
    model.fit(x, y)
    score = model.score(x, y)
    slope = model.coef_
    intercept = model.intercept_
    print("x: " + x_name)
    print("y: " + y_name)
    print("slope: " + str(slope))
    print("intercept: " + str(intercept))
    print("r2: " + str(score))


def grab_where_equal(grabcol, compcol, val):

    count = 0
    grabbed_vals = []
    for idx, e in enumerate(compcol):
        if e == val:
            grabbed_vals.append(grabcol[idx])
    return np.array(grabbed_vals)


data = read_csv("data.csv")
x_hp = data["hp correct"].array.reshape((-1, 1))
x_fuel = data["diesel"].array.reshape((-1, 1))
x_arr = [x_hp, x_fuel]
y_nox = data['NOx'].array
y_pm = data['PM2.5'].array
y_hc = data['HC'].array
y_co = data['CO'].array
y_co2 = data['CO2'].array
y_arr = [y_nox, y_pm, y_hc, y_co, y_co2]
model = LinearRegression()
hp_dict = make_dictionary(model, data['hp correct'], data['diesel'], y_co, "hp", "fuel", "CO")
entry = hp_dict[5000]
plt.plot(entry[1], entry[2], 'o')


x = []
for e in entry[1]:
    x.append(e.tolist()[0])
results = {}
entry[2] = entry[2].tolist()
x = x[: 6954]
entry[2] = entry[2][: 6954]
print(x)
m = np.polyfit(x, entry[2], 3)
plt.plot(x, m[0]*np.array(x) ** 3 + m[1]*np.array(x) ** 2 + m[2] * np.array(x) ** 1 + m[3])
results = {}
results['polynomial'] = m.tolist()
correlation = np.corrcoef(x, entry[2])[0,1]
 # r
results['correlation'] = correlation
 # r-squared
results['determination'] = correlation**2
plt.xlim(xmax=600)
plt.xlim(xmin=0)
print(results['polynomial'])
print(results['determination'])
plt.title("Horsepower vs. CO Levels \n Fuel Consumption fixed at 5000")
plt.xlabel("Horsepower")
plt.ylabel("CO levels (annual short tons)")
plt.show()